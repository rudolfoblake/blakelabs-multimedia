from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from uuid import UUID, uuid4


class JobStatus(StrEnum):
    """Lifecycle shared by probe and processing queue views."""

    PENDING = "pending"
    ANALYZING = "analyzing"
    READY = "ready"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class MediaJob:
    """Queue item independent from the concrete GUI model."""

    source: Path
    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    message: str = ""
