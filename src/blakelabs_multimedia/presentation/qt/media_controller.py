from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import (
    Property,
    QObject,
    QSettings,
    QStandardPaths,
    QTimer,
    QUrl,
    Signal,
    Slot,
)
from PySide6.QtGui import QDesktopServices

from blakelabs_multimedia.application.ports.media_probe import CancelHandle
from blakelabs_multimedia.application.services.processing_queue import ProcessingQueue
from blakelabs_multimedia.application.use_cases.probe_media import ProbeMedia
from blakelabs_multimedia.domain.conversion import (
    DEFAULT_PRESETS,
    ProcessingProgress,
    ProcessingRequest,
    find_preset,
)
from blakelabs_multimedia.domain.jobs import MediaJob
from blakelabs_multimedia.domain.media import MediaAsset
from blakelabs_multimedia.infrastructure.ffmpeg.command_builder import choose_output_path
from blakelabs_multimedia.presentation.qt.media_queue_model import MediaQueueModel

LOGGER = logging.getLogger(__name__)


class MediaController(QObject):
    selectedPresetChanged = Signal()
    outputDirectoryChanged = Signal()

    def __init__(
        self,
        probe_media: ProbeMedia,
        queue_model: MediaQueueModel,
        processing_queue: ProcessingQueue,
    ) -> None:
        super().__init__()
        self._probe_media = probe_media
        self._queue_model = queue_model
        self._processing_queue = processing_queue
        self._active_probes: dict[UUID, CancelHandle] = {}
        self._settings = QSettings()

        configured_preset = str(self._settings.value("conversion/preset", "mp4-balanced"))
        try:
            find_preset(configured_preset)
            self._selected_preset_id = configured_preset
        except KeyError:
            self._selected_preset_id = "mp4-balanced"

        configured_output = str(self._settings.value("conversion/outputDirectory", ""))
        output_directory = Path(configured_output) if configured_output else None
        self._output_directory = (
            output_directory if output_directory is not None and output_directory.is_dir() else None
        )

    @Property(list, constant=True)
    def presets(self) -> list[dict[str, object]]:
        return [
            {
                "id": preset.id,
                "title": preset.title,
                "description": preset.description,
                "group": preset.group.value,
                "extension": preset.extension.upper(),
            }
            for preset in DEFAULT_PRESETS
        ]

    @Property(str, notify=selectedPresetChanged)
    def selectedPresetId(self) -> str:
        return self._selected_preset_id

    @Property(str, notify=selectedPresetChanged)
    def selectedPresetTitle(self) -> str:
        return find_preset(self._selected_preset_id).title

    @Property(str, notify=selectedPresetChanged)
    def selectedPresetDescription(self) -> str:
        return find_preset(self._selected_preset_id).description

    @Property(str, notify=selectedPresetChanged)
    def selectedPresetExtension(self) -> str:
        return find_preset(self._selected_preset_id).extension.upper()

    @Property(str, notify=outputDirectoryChanged)
    def outputDirectoryLabel(self) -> str:
        return str(self._output_directory) if self._output_directory else "Same folder as source"

    @Slot(list)
    def addFiles(self, urls: list[object]) -> None:
        accepted = 0
        for raw_url in urls:
            path = self._to_local_path(raw_url)
            if path is not None and path.is_file():
                self._add_file(path)
                accepted += 1
        LOGGER.info("Accepted %s local media file(s) from the UI", accepted)

    @Slot(str)
    def selectPreset(self, preset_id: str) -> None:
        try:
            find_preset(preset_id)
        except KeyError:
            LOGGER.warning("Ignoring unknown preset selected by UI: %s", preset_id)
            return
        if self._selected_preset_id == preset_id:
            return
        self._selected_preset_id = preset_id
        self._settings.setValue("conversion/preset", preset_id)
        self.selectedPresetChanged.emit()

    @Slot(QUrl)
    def setOutputDirectory(self, url: QUrl) -> None:
        local_path = url.toLocalFile()
        if not local_path:
            return
        candidate = Path(local_path)
        if not candidate.is_dir():
            return
        self._output_directory = candidate
        self._settings.setValue("conversion/outputDirectory", str(candidate))
        self.outputDirectoryChanged.emit()

    @Slot()
    def resetOutputDirectory(self) -> None:
        self._output_directory = None
        self._settings.remove("conversion/outputDirectory")
        self.outputDirectoryChanged.emit()

    @Slot()
    def startReady(self) -> None:
        preset = find_preset(self._selected_preset_id)
        for job_id, asset in self._queue_model.ready_entries():
            if not preset.accepts(asset.kind):
                self._queue_model.mark_failed(
                    job_id,
                    f"{preset.title} does not support {asset.kind.value} input.",
                )
                continue
            output = choose_output_path(asset.path, preset.extension, self._output_directory)
            request = ProcessingRequest(
                job_id=job_id,
                source=asset.path,
                output=output,
                duration_seconds=asset.duration_seconds,
                preset=preset,
            )
            self._queue_model.mark_queued(job_id, preset, output)
            self._processing_queue.enqueue(request, _ModelObserver(job_id, self._queue_model))

    @Slot(str)
    def cancelJob(self, raw_job_id: str) -> None:
        try:
            job_id = UUID(raw_job_id)
        except ValueError:
            return
        probe = self._active_probes.pop(job_id, None)
        if probe is not None:
            probe.cancel()
            self._queue_model.mark_cancelled(job_id)
            LOGGER.info("Cancelled media analysis for job %s", job_id)
            return
        self._processing_queue.cancel(job_id)

    @Slot(str)
    def openOutputFolder(self, raw_job_id: str) -> None:
        try:
            job_id = UUID(raw_job_id)
        except ValueError:
            return
        output = self._queue_model.output_for(job_id)
        if output is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(output.parent)))

    @Slot()
    def openDiagnosticsFolder(self) -> None:
        diagnostics = Path(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        ) / "logs"
        diagnostics.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(diagnostics)))

    @Slot()
    def clearFinished(self) -> None:
        self._queue_model.clear_finished()

    def _add_file(self, path: Path) -> None:
        job = MediaJob(source=path)
        self._queue_model.add_analyzing(job)
        QTimer.singleShot(0, lambda current_job=job: self._begin_probe(current_job))

    def _begin_probe(self, job: MediaJob) -> None:
        settled = False

        def completed(asset: MediaAsset, job_id: UUID = job.id) -> None:
            nonlocal settled
            settled = True
            self._queue_model.mark_ready(job_id, asset)
            self._active_probes.pop(job_id, None)

        def failed(message: str, job_id: UUID = job.id) -> None:
            nonlocal settled
            settled = True
            self._queue_model.mark_failed(job_id, message)
            self._active_probes.pop(job_id, None)

        try:
            handle = self._probe_media.execute(job.source, completed=completed, failed=failed)
        except Exception:
            LOGGER.exception("Unexpected media analysis failure for %s", job.source)
            failed("Unexpected error while analyzing this file. See diagnostics for details.")
            return
        if not settled:
            self._active_probes[job.id] = handle

    @staticmethod
    def _to_local_path(raw_url: object) -> Path | None:
        url = raw_url if isinstance(raw_url, QUrl) else QUrl(str(raw_url))
        local_path = url.toLocalFile()
        return Path(local_path) if local_path else None


class _ModelObserver:
    def __init__(self, job_id: UUID, model: MediaQueueModel) -> None:
        self._job_id = job_id
        self._model = model

    def started(self) -> None:
        self._model.mark_processing(self._job_id)

    def progressed(self, progress: ProcessingProgress) -> None:
        self._model.mark_progress(self._job_id, progress)

    def completed(self, output: Path) -> None:
        self._model.mark_completed(self._job_id, output)

    def failed(self, message: str) -> None:
        self._model.mark_failed(self._job_id, message)

    def cancelled(self) -> None:
        self._model.mark_cancelled(self._job_id)
