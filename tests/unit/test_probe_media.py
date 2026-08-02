from collections.abc import Callable
from pathlib import Path

from blakelabs_multimedia.application.ports.media_probe import CancelHandle
from blakelabs_multimedia.application.use_cases.probe_media import ProbeMedia
from blakelabs_multimedia.domain.media import MediaAsset, MediaKind


class FakeHandle:
    def cancel(self) -> None:
        return None


class FakeProbe:
    def __init__(self) -> None:
        self.received: Path | None = None

    def probe(
        self,
        path: Path,
        *,
        completed: Callable[[MediaAsset], None],
        failed: Callable[[str], None],
    ) -> CancelHandle:
        self.received = path
        completed(MediaAsset(path, MediaKind.AUDIO, "mp3", 10))
        return FakeHandle()


def test_probe_media_delegates_existing_file(tmp_path: Path) -> None:
    media_file = tmp_path / "demo.mp3"
    media_file.write_bytes(b"not-real-media")
    adapter = FakeProbe()
    use_case = ProbeMedia(adapter)
    completed: list[MediaAsset] = []

    use_case.execute(media_file, completed=completed.append, failed=lambda _: None)

    assert adapter.received == media_file.resolve()
    assert completed[0].kind is MediaKind.AUDIO


def test_probe_media_rejects_missing_file(tmp_path: Path) -> None:
    adapter = FakeProbe()
    use_case = ProbeMedia(adapter)
    failures: list[str] = []

    use_case.execute(
        tmp_path / "missing.mp4",
        completed=lambda _: None,
        failed=failures.append,
    )

    assert adapter.received is None
    assert failures == ["The selected file no longer exists."]
