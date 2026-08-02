from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from uuid import UUID, uuid4


class JobStatus(StrEnum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    READY = "ready"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class MediaJob:
    source: Path
    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    message: str = ""
