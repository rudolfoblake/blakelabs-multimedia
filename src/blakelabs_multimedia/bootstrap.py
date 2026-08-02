from __future__ import annotations

import logging
import os
import sys
from importlib.resources import as_file, files

from PySide6.QtCore import QCoreApplication, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from blakelabs_multimedia.application.services.processing_queue import ProcessingQueue
from blakelabs_multimedia.application.use_cases.probe_media import ProbeMedia
from blakelabs_multimedia.infrastructure.ffmpeg.binary_resolver import FfmpegBinaryResolver
from blakelabs_multimedia.infrastructure.ffmpeg.qt_probe import QtFfprobeMediaProbe
from blakelabs_multimedia.infrastructure.ffmpeg.qt_processor import QtFfmpegMediaProcessor
from blakelabs_multimedia.presentation import qml as qml_resources
from blakelabs_multimedia.presentation.qt.media_controller import MediaController
from blakelabs_multimedia.presentation.qt.media_queue_model import MediaQueueModel


def run() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    QCoreApplication.setOrganizationName("Blake Labs")
    QCoreApplication.setOrganizationDomain("blakelabs.dev")
    QCoreApplication.setApplicationName("BlakeLabs Multimedia")
    QQuickStyle.setStyle("Fusion")

    app = QGuiApplication(sys.argv)
    app.setApplicationDisplayName("BlakeLabs Multimedia")

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
        if not engine.rootObjects():
            return 1
        smoke_exit_ms = os.getenv("BLAKELABS_SMOKE_EXIT_MS")
        if smoke_exit_ms:
            QTimer.singleShot(max(1, int(smoke_exit_ms)), app.quit)
        return app.exec()
