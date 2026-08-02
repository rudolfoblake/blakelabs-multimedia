from __future__ import annotations

from dataclasses import dataclass, field

from blakelabs_multimedia.domain.conversion import ProcessingProgress


@dataclass(slots=True)
class FfmpegProgressParser:
    duration_seconds: float | None
    _buffer: str = ""
    _fields: dict[str, str] = field(default_factory=dict)

    def feed(self, chunk: bytes) -> list[ProcessingProgress]:
        self._buffer += chunk.decode(errors="replace")
        lines = self._buffer.split("\n")
        self._buffer = lines.pop()
        snapshots: list[ProcessingProgress] = []
        for raw_line in lines:
            line = raw_line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            self._fields[key] = value
            if key == "progress":
                snapshots.append(self._snapshot())
                self._fields.clear()
        return snapshots

    def _snapshot(self) -> ProcessingProgress:
        processed_seconds = self._processed_seconds()
        speed = _parse_speed(self._fields.get("speed"))
        ratio = 0.0
        eta_seconds: int | None = None
        if self.duration_seconds and self.duration_seconds > 0:
            ratio = min(1.0, max(0.0, processed_seconds / self.duration_seconds))
            if speed and speed > 0:
                eta_seconds = max(0, round((self.duration_seconds - processed_seconds) / speed))
        if self._fields.get("progress") == "end":
            ratio = 1.0
            eta_seconds = 0
        return ProcessingProgress(
            ratio=ratio,
            processed_seconds=processed_seconds,
            speed=speed,
            eta_seconds=eta_seconds,
        )

    def _processed_seconds(self) -> float:
        for key in ("out_time_us", "out_time_ms"):
            raw = self._fields.get(key)
            if raw:
                try:
                    return max(0.0, int(raw) / 1_000_000)
                except ValueError:
                    pass
        raw_time = self._fields.get("out_time")
        if not raw_time:
            return 0.0
        try:
            hours, minutes, seconds = raw_time.split(":")
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        except (ValueError, TypeError):
            return 0.0


def _parse_speed(raw: str | None) -> float | None:
    if not raw:
        return None
    try:
        return float(raw.removesuffix("x"))
    except ValueError:
        return None
