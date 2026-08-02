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

from blakelabs_multimedia.domain.jobs import JobStatus, MediaJob
from blakelabs_multimedia.domain.media import MediaAsset


class _Role(IntEnum):
    ID = Qt.ItemDataRole.UserRole + 1
    NAME = Qt.ItemDataRole.UserRole + 2
    PATH = Qt.ItemDataRole.UserRole + 3
    STATUS = Qt.ItemDataRole.UserRole + 4
    STATUS_LABEL = Qt.ItemDataRole.UserRole + 5
    DETAIL = Qt.ItemDataRole.UserRole + 6
    KIND = Qt.ItemDataRole.UserRole + 7
    DURATION = Qt.ItemDataRole.UserRole + 8
    FILE_SIZE = Qt.ItemDataRole.UserRole + 9
    PROGRESS = Qt.ItemDataRole.UserRole + 10


_ROLE_KEYS: dict[int, str] = {
    int(_Role.ID): "jobId",
    int(_Role.NAME): "name",
    int(_Role.PATH): "sourcePath",
    int(_Role.STATUS): "status",
    int(_Role.STATUS_LABEL): "statusLabel",
    int(_Role.DETAIL): "detail",
    int(_Role.KIND): "kind",
    int(_Role.DURATION): "duration",
    int(_Role.FILE_SIZE): "fileSize",
    int(_Role.PROGRESS): "progress",
}


class MediaQueueModel(QAbstractListModel):
    """Observable queue state consumed by QML."""

    countChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._items: list[dict[str, Any]] = []

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._items)

    def roleNames(self) -> dict[int, QByteArray]:
        return {role: QByteArray(key.encode()) for role, key in _ROLE_KEYS.items()}

    def rowCount(  # noqa: B008
        self,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
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
        if key is None:
            return None
        return self._items[index.row()].get(key)

    def add_analyzing(self, job: MediaJob) -> None:
        row = len(self._items)
        self.beginInsertRows(QModelIndex(), row, row)
        self._items.append(
            {
                "jobId": str(job.id),
                "name": job.source.name,
                "sourcePath": str(job.source),
                "status": JobStatus.ANALYZING.value,
                "statusLabel": "Analyzing",
                "detail": "Reading streams and codecs",
                "kind": "unknown",
                "duration": "—",
                "fileSize": _format_size(_safe_size(job.source)),
                "progress": 0.14,
            }
        )
        self.endInsertRows()
        self.countChanged.emit()

    def mark_ready(self, job_id: UUID, asset: MediaAsset) -> None:
        detail_parts = [asset.container.upper() or "MEDIA"]
        if asset.width and asset.height:
            detail_parts.append(f"{asset.width}x{asset.height}")
        if asset.video_codec:
            detail_parts.append(asset.video_codec.upper())
        if asset.audio_codec:
            detail_parts.append(asset.audio_codec.upper())
        self._update(
            job_id,
            status=JobStatus.READY.value,
            statusLabel="Ready",
            detail=" · ".join(detail_parts),
            kind=asset.kind.value,
            duration=_format_duration(asset.duration_seconds),
            fileSize=_format_size(asset.size_bytes),
            progress=1.0,
        )

    def mark_failed(self, job_id: UUID, message: str) -> None:
        self._update(
            job_id,
            status=JobStatus.FAILED.value,
            statusLabel="Needs attention",
            detail=message,
            progress=0.0,
        )

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
