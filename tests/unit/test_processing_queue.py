from pathlib import Path
from uuid import uuid4

from blakelabs_multimedia.application.services.processing_queue import ProcessingQueue
from blakelabs_multimedia.domain.conversion import (
    ProcessingProgress,
    ProcessingRequest,
    find_preset,
)


class Handle:
    def __init__(self) -> None:
        self.cancelled = False

    def cancel(self) -> None:
        self.cancelled = True


class Processor:
    def __init__(self) -> None:
        self.calls: list[tuple[ProcessingRequest, object, Handle]] = []

    def process(self, request: ProcessingRequest, observer: object) -> Handle:
        handle = Handle()
        self.calls.append((request, observer, handle))
        return handle


class Observer:
    def __init__(self) -> None:
        self.events: list[str] = []

    def started(self) -> None:
        self.events.append("started")

    def progressed(self, _progress: ProcessingProgress) -> None:
        self.events.append("progress")

    def completed(self, _output: Path) -> None:
        self.events.append("completed")

    def failed(self, _message: str) -> None:
        self.events.append("failed")

    def cancelled(self) -> None:
        self.events.append("cancelled")


def request(name: str) -> ProcessingRequest:
    return ProcessingRequest(
        uuid4(),
        Path(f"/{name}.mkv"),
        Path(f"/{name}.mp4"),
        10.0,
        find_preset("mp4-balanced"),
    )


def test_queue_runs_one_job_at_a_time() -> None:
    processor = Processor()
    queue = ProcessingQueue(processor)  # type: ignore[arg-type]
    first_observer = Observer()
    second_observer = Observer()
    first = request("first")
    second = request("second")
    queue.enqueue(first, first_observer)
    queue.enqueue(second, second_observer)
    assert len(processor.calls) == 1
    processor.calls[0][1].completed(first.output)  # type: ignore[union-attr]
    assert len(processor.calls) == 2


def test_pending_job_can_be_cancelled() -> None:
    processor = Processor()
    queue = ProcessingQueue(processor)  # type: ignore[arg-type]
    first = request("first")
    second = request("second")
    second_observer = Observer()
    queue.enqueue(first, Observer())
    queue.enqueue(second, second_observer)
    assert queue.cancel(second.job_id)
    assert second_observer.events == ["cancelled"]
