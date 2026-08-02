from blakelabs_multimedia.infrastructure.ffmpeg.progress_parser import FfmpegProgressParser


def test_progress_parser_handles_split_chunks() -> None:
    parser = FfmpegProgressParser(duration_seconds=20.0)
    assert parser.feed(b"out_time_us=500") == []
    snapshots = parser.feed(b"0000\nspeed=2.0x\nprogress=continue\n")
    assert len(snapshots) == 1
    assert snapshots[0].ratio == 0.25
    assert snapshots[0].speed == 2.0
    assert snapshots[0].eta_seconds == 8


def test_end_event_is_complete() -> None:
    parser = FfmpegProgressParser(duration_seconds=None)
    snapshot = parser.feed(b"progress=end\n")[0]
    assert snapshot.ratio == 1.0
    assert snapshot.eta_seconds == 0
