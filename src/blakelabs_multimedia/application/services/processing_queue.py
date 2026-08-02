from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from blakelabs_multimedia.application.ports.media_probe import CancelHandle
from blakelabs_multimedia.application.ports.media_processor import MediaProcessorPort, ProcessingObserver
from blakelabs_multimedia.domain.conversion import ProcessingProgress, ProcessingRequest


@dataclass(slots=True)
class _QueuedItem:
    request: ProcessingRequest
    observer: ProcessingObserver


class ProcessingQueue:
    """Sequential application service that keeps FFmpeg concurrency predictable."""

    def __init__(self, processor: MediaProcessorPort) -> None:
        self._processor = processor
        self._pending: deque[_QueuedItem] = deque()
        self._active: _QueuedItem | None = None
        self._active_handle: CancelHandle | None = None

    @property
    def active_job_id(self) -> UUID | None:
        return self._active.request.job_id if self._active else None

    def enqueue(self, request: ProcessingRequest, observer: ProcessingObserver) -> None:
        self._pending.append(_QueuedItem(request=request, observer=observer))
        self._start_next()

    def cancel(self, job_id: UUID) -> bool:
        if self._active and self._active.request.job_id == job_id:
            if self._active_handle is not None:
                self._active_handle.cancel()
            return True

        retained: deque[_QueuedItem] = deque()
        cancelled = False
        while self._pending:
            item = self._pending.popleft()
            if item.request.job_id == job_id:
                item.observer.cancelled()
                cancelled = True
            else:
                retained.append(item)
        self._pending = retained
        return cancelled

    def _start_next(self) -> None:
        if self._active is not None or not self._pending:
            return
        item = self._pending.popleft()
        self._active = item
        proxy = _QueueObserver(self, item)
        handle = self._processor.process(item.request, proxy)
        if self._active is item:
            self._active_handle = handle

    def _settle(self, item: _QueuedItem) -> None:
        if self._active is not item:
            return
        self._active = None
        self._active_handle = None
        self._start_next()


class _QueueObserver:
    def __init__(self, queue: ProcessingQueue, item: _QueuedItem) -> None:
        self._queue = queue
        self._item = item
        self._settled = False

    def started(self) -> None:
        self._item.observer.started()

    def progressed(self, progress: ProcessingProgress) -> None:
        self._item.observer.progressed(progress)

    def completed(self, output: Path) -> None:
        if self._settled:
            return
        self._settled = True
        self._item.observer.completed(output)
        self._queue._settle(self._item)

    def failed(self, message: str) -> None:
        if self._settled:
            return
        self._settled = True
        self._item.observer.failed(message)
        self._queue._settle(self._item)

    def cancelled(self) -> None:
        if self._settled:
            return
        self._settled = True
        self._item.observer.cancelled()
        self._queue._settle(self._item)
