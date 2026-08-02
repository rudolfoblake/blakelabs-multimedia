from __future__ import annotations

from pathlib import Path
from uuid import UUID

from PySide6.QtCore import QObject, QUrl, Slot

from blakelabs_multimedia.application.ports.media_probe import CancelHandle
from blakelabs_multimedia.application.use_cases.probe_media import ProbeMedia
from blakelabs_multimedia.domain.jobs import MediaJob
from blakelabs_multimedia.domain.media import MediaAsset
from blakelabs_multimedia.presentation.qt.media_queue_model import MediaQueueModel


class MediaController(QObject):
    """Translate QML user intents into application use cases."""

    def __init__(self, probe_media: ProbeMedia, queue_model: MediaQueueModel) -> None:
        super().__init__()
        self._probe_media = probe_media
        self._queue_model = queue_model
        self._active: dict[UUID, CancelHandle] = {}

    @Slot("QVariantList")
    def addFiles(self, urls: list[object]) -> None:
        for raw_url in urls:
            path = self._to_local_path(raw_url)
            if path is not None:
                self._add_file(path)

    def _add_file(self, path: Path) -> None:
        job = MediaJob(source=path)
        self._queue_model.add_analyzing(job)
        settled = False

        def completed(asset: MediaAsset, job_id: UUID = job.id) -> None:
            nonlocal settled
            settled = True
            self._queue_model.mark_ready(job_id, asset)
            self._active.pop(job_id, None)

        def failed(message: str, job_id: UUID = job.id) -> None:
            nonlocal settled
            settled = True
            self._queue_model.mark_failed(job_id, message)
            self._active.pop(job_id, None)

        handle = self._probe_media.execute(path, completed=completed, failed=failed)
        if not settled:
            self._active[job.id] = handle

    @staticmethod
    def _to_local_path(raw_url: object) -> Path | None:
        url = raw_url if isinstance(raw_url, QUrl) else QUrl(str(raw_url))
        local_path = url.toLocalFile()
        if not local_path:
            return None
        return Path(local_path)
