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
    ConversionOptions,
    PresetGroup,
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
    advancedOptionsChanged = Signal()

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

        self._audio_bitrate = self._read_int("advanced/audioBitrate", 0)
        self._audio_sample_rate = self._read_int("advanced/audioSampleRate", 0)
        self._audio_channels = self._read_int("advanced/audioChannels", 0)
        self._video_crf = self._read_int("advanced/videoCrf", 0)
        self._video_bitrate = self._read_int("advanced/videoBitrate", 0)
        self._video_max_width = self._read_int("advanced/videoMaxWidth", 0)
        self._video_encoder_preset = str(
            self._settings.value("advanced/videoEncoderPreset", "")
        )
        self._normalize_audio = self._read_bool("advanced/normalizeAudio", False)
        self._preserve_metadata = self._read_bool("advanced/preserveMetadata", True)

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

    @Property(str, notify=selectedPresetChanged)
    def selectedPresetGroup(self) -> str:
        return find_preset(self._selected_preset_id).group.value

    @Property(bool, notify=selectedPresetChanged)
    def selectedPresetSupportsVideo(self) -> bool:
        return find_preset(self._selected_preset_id).group is PresetGroup.VIDEO

    @Property(bool, notify=selectedPresetChanged)
    def selectedPresetSupportsAudio(self) -> bool:
        return find_preset(self._selected_preset_id).group is not PresetGroup.QUICK_TOOL

    @Property(bool, notify=selectedPresetChanged)
    def selectedPresetIsLossless(self) -> bool:
        return find_preset(self._selected_preset_id).extension in {"flac", "wav"}

    @Property(str, notify=outputDirectoryChanged)
    def outputDirectoryLabel(self) -> str:
        return str(self._output_directory) if self._output_directory else "Same folder as source"

    @Property(int, notify=advancedOptionsChanged)
    def audioBitrate(self) -> int:
        return self._audio_bitrate

    @Property(int, notify=advancedOptionsChanged)
    def audioSampleRate(self) -> int:
        return self._audio_sample_rate

    @Property(int, notify=advancedOptionsChanged)
    def audioChannels(self) -> int:
        return self._audio_channels

    @Property(int, notify=advancedOptionsChanged)
    def videoCrf(self) -> int:
        return self._video_crf

    @Property(int, notify=advancedOptionsChanged)
    def videoBitrate(self) -> int:
        return self._video_bitrate

    @Property(int, notify=advancedOptionsChanged)
    def videoMaxWidth(self) -> int:
        return self._video_max_width

    @Property(str, notify=advancedOptionsChanged)
    def videoEncoderPreset(self) -> str:
        return self._video_encoder_preset

    @Property(bool, notify=advancedOptionsChanged)
    def normalizeAudio(self) -> bool:
        return self._normalize_audio

    @Property(bool, notify=advancedOptionsChanged)
    def preserveMetadata(self) -> bool:
        return self._preserve_metadata

    @Property(str, notify=advancedOptionsChanged)
    def advancedSummary(self) -> str:
        preset = find_preset(self._selected_preset_id)
        parts: list[str] = []
        if preset.group is PresetGroup.VIDEO:
            if self._video_bitrate:
                parts.append(f"{self._video_bitrate / 1000:g} Mbps video")
            elif self._video_crf:
                parts.append(f"CRF {self._video_crf}")
            if self._video_max_width:
                parts.append(f"max {self._video_max_width}px")
            if self._video_encoder_preset:
                parts.append(self._video_encoder_preset)
        if preset.group is not PresetGroup.QUICK_TOOL:
            if self._audio_bitrate and not self.selectedPresetIsLossless:
                parts.append(f"{self._audio_bitrate} kbps audio")
            if self._audio_sample_rate:
                parts.append(f"{self._audio_sample_rate // 1000:g} kHz")
            if self._audio_channels:
                parts.append("mono" if self._audio_channels == 1 else "stereo")
            if self._normalize_audio:
                parts.append("loudness normalized")
        if not self._preserve_metadata:
            parts.append("metadata removed")
        return " · ".join(parts) if parts else "Preset defaults"

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
        self.advancedOptionsChanged.emit()

    @Slot(int)
    def setAudioBitrate(self, value: int) -> None:
        self._set_int_option("_audio_bitrate", "advanced/audioBitrate", value)

    @Slot(int)
    def setAudioSampleRate(self, value: int) -> None:
        self._set_int_option("_audio_sample_rate", "advanced/audioSampleRate", value)

    @Slot(int)
    def setAudioChannels(self, value: int) -> None:
        self._set_int_option("_audio_channels", "advanced/audioChannels", value)

    @Slot(int)
    def setVideoCrf(self, value: int) -> None:
        normalized = max(0, value)
        if normalized and self._video_bitrate:
            self._video_bitrate = 0
            self._settings.setValue("advanced/videoBitrate", 0)
        self._set_int_option("_video_crf", "advanced/videoCrf", normalized)

    @Slot(int)
    def setVideoBitrate(self, value: int) -> None:
        normalized = max(0, value)
        if normalized and self._video_crf:
            self._video_crf = 0
            self._settings.setValue("advanced/videoCrf", 0)
        self._set_int_option("_video_bitrate", "advanced/videoBitrate", normalized)

    @Slot(int)
    def setVideoMaxWidth(self, value: int) -> None:
        self._set_int_option("_video_max_width", "advanced/videoMaxWidth", value)

    @Slot(str)
    def setVideoEncoderPreset(self, value: str) -> None:
        valid = {"", "ultrafast", "fast", "medium", "slow", "veryslow"}
        normalized = value if value in valid else ""
        if self._video_encoder_preset == normalized:
            return
        self._video_encoder_preset = normalized
        self._settings.setValue("advanced/videoEncoderPreset", normalized)
        self.advancedOptionsChanged.emit()

    @Slot(bool)
    def setNormalizeAudio(self, enabled: bool) -> None:
        if self._normalize_audio == enabled:
            return
        self._normalize_audio = enabled
        self._settings.setValue("advanced/normalizeAudio", enabled)
        self.advancedOptionsChanged.emit()

    @Slot(bool)
    def setPreserveMetadata(self, enabled: bool) -> None:
        if self._preserve_metadata == enabled:
            return
        self._preserve_metadata = enabled
        self._settings.setValue("advanced/preserveMetadata", enabled)
        self.advancedOptionsChanged.emit()

    @Slot()
    def resetAdvancedOptions(self) -> None:
        self._audio_bitrate = 0
        self._audio_sample_rate = 0
        self._audio_channels = 0
        self._video_crf = 0
        self._video_bitrate = 0
        self._video_max_width = 0
        self._video_encoder_preset = ""
        self._normalize_audio = False
        self._preserve_metadata = True
        self._settings.remove("advanced")
        self.advancedOptionsChanged.emit()

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
        options = self._current_options()
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
                options=options,
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
        diagnostics = (
            Path(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.AppLocalDataLocation
                )
            )
            / "logs"
        )
        diagnostics.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(diagnostics)))

    @Slot()
    def clearFinished(self) -> None:
        self._queue_model.clear_finished()

    def _current_options(self) -> ConversionOptions:
        return ConversionOptions(
            audio_bitrate_kbps=self._audio_bitrate or None,
            audio_sample_rate_hz=self._audio_sample_rate or None,
            audio_channels=self._audio_channels or None,
            video_crf=self._video_crf or None,
            video_bitrate_kbps=self._video_bitrate or None,
            video_encoder_preset=self._video_encoder_preset or None,
            video_max_width=self._video_max_width or None,
            normalize_audio=self._normalize_audio,
            preserve_metadata=self._preserve_metadata,
        )

    def _set_int_option(self, attribute: str, key: str, value: int) -> None:
        normalized = max(0, value)
        if getattr(self, attribute) == normalized:
            return
        setattr(self, attribute, normalized)
        self._settings.setValue(key, normalized)
        self.advancedOptionsChanged.emit()

    def _read_int(self, key: str, default: int) -> int:
        try:
            return max(0, int(self._settings.value(key, default)))
        except (TypeError, ValueError):
            return default

    def _read_bool(self, key: str, default: bool) -> bool:
        value = self._settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

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
