from __future__ import annotations

import logging
import os
import sys
from importlib.resources import as_file, files
from pathlib import Path
from types import TracebackType

from PySide6.QtCore import QCoreApplication, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from blakelabs_multimedia.application.services.processing_queue import ProcessingQueue
from blakelabs_multimedia.application.use_cases.probe_media import ProbeMedia
from blakelabs_multimedia.infrastructure.diagnostics import configure_logging
from blakelabs_multimedia.infrastructure.ffmpeg.binary_resolver import FfmpegBinaryResolver
from blakelabs_multimedia.infrastructure.ffmpeg.qt_probe import QtFfprobeMediaProbe
from blakelabs_multimedia.infrastructure.ffmpeg.qt_processor import QtFfmpegMediaProcessor
from blakelabs_multimedia.presentation import qml as qml_resources
from blakelabs_multimedia.presentation.qt.media_controller import MediaController
from blakelabs_multimedia.presentation.qt.media_queue_model import MediaQueueModel

LOGGER = logging.getLogger(__name__)


def run() -> int:
    QCoreApplication.setOrganizationName("Blake Labs")
    QCoreApplication.setOrganizationDomain("blakelabs.dev")
    QCoreApplication.setApplicationName("BlakeLabs Multimedia")
    QQuickStyle.setStyle("Fusion")

    app = QGuiApplication(sys.argv)
    app.setApplicationDisplayName("BlakeLabs Multimedia")
    log_file = configure_logging()
    LOGGER.info("Application starting; diagnostics=%s", log_file)

    def report_uncaught(
        exception_type: type[BaseException],
        exception: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        LOGGER.critical(
            "Unhandled exception",
            exc_info=(exception_type, exception, traceback),
        )

    sys.excepthook = report_uncaught

    queue_model = MediaQueueModel()
    resolver = FfmpegBinaryResolver()
    probe_media = ProbeMedia(QtFfprobeMediaProbe(resolver))
    processing_queue = ProcessingQueue(QtFfmpegMediaProcessor(resolver))
    controller = MediaController(probe_media, queue_model, processing_queue)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("mediaController", controller)
    engine.rootContext().setContextProperty("mediaQueueModel", queue_model)

    qml_package = files(qml_resources)
    with as_file(qml_package) as qml_root:
        engine.addImportPath(str(qml_root))
        engine.load(QUrl.fromLocalFile(str(qml_root / "Main.qml")))
        roots = engine.rootObjects()
        if not roots:
            LOGGER.critical("QML root object failed to load")
            return 1

        root_window = roots[0]
        screenshot_path = os.getenv("BLAKELABS_SCREENSHOT_PATH")

        def capture_screenshot() -> bool:
            if not screenshot_path:
                return True
            destination = Path(screenshot_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            grab_window = getattr(root_window, "grabWindow", None)
            if not callable(grab_window):
                LOGGER.error("QML root does not support screenshot capture")
                return False
            image = grab_window()
            if not image.save(str(destination)):
                LOGGER.error("Could not save UI screenshot to %s", destination)
                return False
            LOGGER.info("Saved UI screenshot to %s", destination)
            return True

        smoke_media = os.getenv("BLAKELABS_SMOKE_MEDIA")
        if smoke_media:
            media_url = QUrl.fromLocalFile(str(Path(smoke_media).resolve()))
            QTimer.singleShot(150, lambda: controller.addFiles([media_url]))

        smoke_result_path = os.getenv("BLAKELABS_SMOKE_RESULT_PATH")
        if smoke_result_path:
            result_destination = Path(smoke_result_path)
            result_destination.parent.mkdir(parents=True, exist_ok=True)
            result_destination.unlink(missing_ok=True)
            settled = False
            smoke_watchdog = QTimer(app)
            smoke_watchdog.setSingleShot(True)
            smoke_watchdog.setInterval(30_000)

            def settle_smoke(result: str, exit_code: int) -> None:
                nonlocal settled
                if settled:
                    return
                settled = True
                smoke_watchdog.stop()
                result_destination.write_text(result, encoding="utf-8")
                LOGGER.info("Packaged smoke result: %s", result)

                def capture_and_exit() -> None:
                    final_exit_code = exit_code if capture_screenshot() else 4
                    app.exit(final_exit_code)

                QTimer.singleShot(500, capture_and_exit)

            def inspect_smoke_state() -> None:
                if queue_model.ready_count() > 0:
                    settle_smoke("ready", 0)
                    return
                if queue_model.failed_count() > 0:
                    detail = queue_model.first_failure_detail().replace("\n", " ").strip()
                    settle_smoke(f"failed:{detail}", 2)

            queue_model.summaryChanged.connect(inspect_smoke_state)
            smoke_watchdog.timeout.connect(lambda: settle_smoke("timeout", 3))
            smoke_watchdog.start()
            QTimer.singleShot(0, inspect_smoke_state)
        else:
            if screenshot_path:
                screenshot_delay = max(
                    100,
                    int(os.getenv("BLAKELABS_SCREENSHOT_DELAY_MS", "1200")),
                )
                QTimer.singleShot(screenshot_delay, capture_screenshot)

            smoke_exit_ms = os.getenv("BLAKELABS_SMOKE_EXIT_MS")
            if smoke_exit_ms:
                QTimer.singleShot(max(1, int(smoke_exit_ms)), app.quit)

        return app.exec()
