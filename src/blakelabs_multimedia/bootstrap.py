from __future__ import annotations

import logging
import os
import sys
from importlib.resources import as_file, files
from pathlib import Path

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
        traceback: object,
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
        smoke_media = os.getenv("BLAKELABS_SMOKE_MEDIA")
        if smoke_media:
            media_url = QUrl.fromLocalFile(str(Path(smoke_media).resolve()))
            QTimer.singleShot(150, lambda: controller.addFiles([media_url]))

        screenshot_path = os.getenv("BLAKELABS_SCREENSHOT_PATH")
        if screenshot_path:
            screenshot_delay = max(
                100,
                int(os.getenv("BLAKELABS_SCREENSHOT_DELAY_MS", "1200")),
            )

            def capture_screenshot() -> None:
                destination = Path(screenshot_path)
                destination.parent.mkdir(parents=True, exist_ok=True)
                grab_window = getattr(root_window, "grabWindow", None)
                if not callable(grab_window):
                    LOGGER.error("QML root does not support screenshot capture")
                    return
                image = grab_window()
                if not image.save(str(destination)):
                    LOGGER.error("Could not save UI screenshot to %s", destination)
                else:
                    LOGGER.info("Saved UI screenshot to %s", destination)

            QTimer.singleShot(screenshot_delay, capture_screenshot)

        smoke_exit_ms = os.getenv("BLAKELABS_SMOKE_EXIT_MS")
        if smoke_exit_ms:
            QTimer.singleShot(max(1, int(smoke_exit_ms)), app.quit)
        return app.exec()
