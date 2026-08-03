from __future__ import annotations

from enum import IntEnum
from pathlib import Path
from typing import Any
from uuid import UUID

from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
)

from blakelabs_multimedia.domain.conversion import ConversionPreset, ProcessingProgress
from blakelabs_multimedia.domain.jobs import JobStatus, MediaJob
from blakelabs_multimedia.domain.media import MediaAsset


class _Role(IntEnum):
    ID = Qt.ItemDataRole.UserRole + 1
    NAME = Qt.ItemDataRole.UserRole + 2
    PATH = Qt.ItemDataRole.UserRole + 3
    OUTPUT_PATH = Qt.ItemDataRole.UserRole + 4
    STATUS = Qt.ItemDataRole.UserRole + 5
    STATUS_LABEL = Qt.ItemDataRole.UserRole + 6
    DETAIL = Qt.ItemDataRole.UserRole + 7
    KIND = Qt.ItemDataRole.UserRole + 8
    DURATION = Qt.ItemDataRole.UserRole + 9
    FILE_SIZE = Qt.ItemDataRole.UserRole + 10
    PROGRESS = Qt.ItemDataRole.UserRole + 11
    PROGRESS_LABEL = Qt.ItemDataRole.UserRole + 12
    PRESET_TITLE = Qt.ItemDataRole.UserRole + 13
    SPEED = Qt.ItemDataRole.UserRole + 14
    ETA = Qt.ItemDataRole.UserRole + 15
    CAN_CANCEL = Qt.ItemDataRole.UserRole + 16
    CAN_OPEN = Qt.ItemDataRole.UserRole + 17


_ROLE_KEYS: dict[int, str] = {
    int(_Role.ID): "jobId",
    int(_Role.NAME): "name",
    int(_Role.PATH): "sourcePath",
    int(_Role.OUTPUT_PATH): "outputPath",
    int(_Role.STATUS): "status",
    int(_Role.STATUS_LABEL): "statusLabel",
    int(_Role.DETAIL): "detail",
    int(_Role.KIND): "kind",
    int(_Role.DURATION): "duration",
    int(_Role.FILE_SIZE): "fileSize",
    int(_Role.PROGRESS): "progress",
    int(_Role.PROGRESS_LABEL): "progressLabel",
    int(_Role.PRESET_TITLE): "presetTitle",
    int(_Role.SPEED): "speed",
    int(_Role.ETA): "eta",
    int(_Role.CAN_CANCEL): "canCancel",
    int(_Role.CAN_OPEN): "canOpen",
}


class MediaQueueModel(QAbstractListModel):
    countChanged = Signal()
    summaryChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._items: list[dict[str, Any]] = []
        self._assets: dict[UUID, MediaAsset] = {}

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._items)

    @Property(int, notify=summaryChanged)
    def readyCount(self) -> int:
        return self.ready_count()

    @Property(int, notify=summaryChanged)
    def failedCount(self) -> int:
        return self.failed_count()

    @Property(int, notify=summaryChanged)
    def activeCount(self) -> int:
        active = {JobStatus.QUEUED.value, JobStatus.PROCESSING.value, JobStatus.ANALYZING.value}
        return sum(item["status"] in active for item in self._items)

    def ready_count(self) -> int:
        return sum(item["status"] == JobStatus.READY.value for item in self._items)

    def failed_count(self) -> int:
        return sum(item["status"] == JobStatus.FAILED.value for item in self._items)

    def first_failure_detail(self) -> str:
        for item in self._items:
            if item["status"] == JobStatus.FAILED.value:
                return str(item.get("detail", "Media analysis failed."))
        return ""

    def roleNames(self) -> dict[int, QByteArray]:
        return {role: QByteArray(key.encode()) for role, key in _ROLE_KEYS.items()}

    def rowCount(
        self,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),  # noqa: B008
    ) -> int:
        return 0 if parent.isValid() else len(self._items)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        key = _ROLE_KEYS.get(role)
        return self._items[index.row()].get(key) if key else None

    def add_analyzing(self, job: MediaJob) -> None:
        row = len(self._items)
        self.beginInsertRows(QModelIndex(), row, row)
        self._items.append(
            {
                "jobId": str(job.id),
                "name": job.source.name,
                "sourcePath": str(job.source),
                "outputPath": "",
                "status": JobStatus.ANALYZING.value,
                "statusLabel": "Analyzing",
                "detail": "Reading format, duration and codecs",
                "kind": "unknown",
                "duration": "—",
                "fileSize": _format_size(_safe_size(job.source)),
                "progress": 0.08,
                "progressLabel": "Analyzing",
                "presetTitle": "",
                "speed": "",
                "eta": "",
                "canCancel": True,
                "canOpen": False,
            }
        )
        self.endInsertRows()
        self.countChanged.emit()
        self.summaryChanged.emit()

    def mark_ready(self, job_id: UUID, asset: MediaAsset) -> None:
        self._assets[job_id] = asset
        details = [asset.container.upper() or "MEDIA"]
        if asset.width and asset.height:
            details.append(f"{asset.width}x{asset.height}")
        if asset.video_codec:
            details.append(asset.video_codec.upper())
        if asset.audio_codec:
            details.append(asset.audio_codec.upper())
        self._update(
            job_id,
            status=JobStatus.READY.value,
            statusLabel="Ready",
            detail=" · ".join(details),
            kind=asset.kind.value,
            duration=_format_duration(asset.duration_seconds),
            fileSize=_format_size(asset.size_bytes),
            progress=1.0,
            progressLabel="Ready",
            canCancel=False,
        )

    def mark_queued(self, job_id: UUID, preset: ConversionPreset, output: Path) -> None:
        self._update(
            job_id,
            outputPath=str(output),
            status=JobStatus.QUEUED.value,
            statusLabel="Queued",
            detail=f"Waiting to run · {preset.title}",
            presetTitle=preset.title,
            progress=0.0,
            progressLabel="Queued",
            speed="",
            eta="",
            canCancel=True,
            canOpen=False,
        )

    def mark_processing(self, job_id: UUID) -> None:
        self._update(
            job_id,
            status=JobStatus.PROCESSING.value,
            statusLabel="Processing",
            detail="Converting in the background",
            progressLabel="Starting",
            canCancel=True,
        )

    def mark_progress(self, job_id: UUID, progress: ProcessingProgress) -> None:
        percentage = round(progress.ratio * 100)
        self._update(
            job_id,
            progress=progress.ratio,
            progressLabel=f"{percentage}%",
            speed=f"{progress.speed:.2f}x" if progress.speed else "",
            eta=_format_eta(progress.eta_seconds),
        )

    def mark_completed(self, job_id: UUID, output: Path) -> None:
        self._update(
            job_id,
            outputPath=str(output),
            status=JobStatus.COMPLETED.value,
            statusLabel="Completed",
            detail=f"Saved as {output.name}",
            progress=1.0,
            progressLabel="100%",
            speed="",
            eta="",
            canCancel=False,
            canOpen=True,
        )

    def mark_cancelled(self, job_id: UUID) -> None:
        self._update(
            job_id,
            status=JobStatus.CANCELLED.value,
            statusLabel="Cancelled",
            detail="The operation was cancelled",
            progress=0.0,
            progressLabel="Cancelled",
            speed="",
            eta="",
            canCancel=False,
            canOpen=False,
        )

    def mark_failed(self, job_id: UUID, message: str) -> None:
        self._update(
            job_id,
            status=JobStatus.FAILED.value,
            statusLabel="Failed",
            detail=message,
            progress=0.0,
            progressLabel="Failed",
            speed="",
            eta="",
            canCancel=False,
            canOpen=False,
        )

    def ready_entries(self) -> list[tuple[UUID, MediaAsset]]:
        result: list[tuple[UUID, MediaAsset]] = []
        for item in self._items:
            if item["status"] != JobStatus.READY.value:
                continue
            job_id = UUID(str(item["jobId"]))
            asset = self._assets.get(job_id)
            if asset is not None:
                result.append((job_id, asset))
        return result

    def output_for(self, job_id: UUID) -> Path | None:
        item = self._find(job_id)
        raw = str(item.get("outputPath", "")) if item else ""
        return Path(raw) if raw else None

    def clear_finished(self) -> None:
        finished = {JobStatus.COMPLETED.value, JobStatus.CANCELLED.value, JobStatus.FAILED.value}
        retained = [item for item in self._items if item["status"] not in finished]
        if len(retained) == len(self._items):
            return
        retained_ids = {UUID(str(item["jobId"])) for item in retained}
        self.beginResetModel()
        self._items = retained
        self._assets = {
            job_id: asset for job_id, asset in self._assets.items() if job_id in retained_ids
        }
        self.endResetModel()
        self.countChanged.emit()
        self.summaryChanged.emit()

    def _find(self, job_id: UUID) -> dict[str, Any] | None:
        return next((item for item in self._items if item["jobId"] == str(job_id)), None)

    def _update(self, job_id: UUID, **values: object) -> None:
        row = next(
            (index for index, item in enumerate(self._items) if item["jobId"] == str(job_id)),
            None,
        )
        if row is None:
            return
        self._items[row].update(values)
        model_index = self.index(row, 0)
        changed_roles = [role for role, key in _ROLE_KEYS.items() if key in values]
        self.dataChanged.emit(model_index, model_index, changed_roles)
        self.summaryChanged.emit()


def _safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _format_size(size_bytes: int) -> str:
    value = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return "0 B"


def _format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    rounded = max(0, round(seconds))
    hours, remainder = divmod(rounded, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def _format_eta(seconds: int | None) -> str:
    if seconds is None:
        return ""
    minutes, secs = divmod(max(0, seconds), 60)
    return f"ETA {minutes}:{secs:02d}"
