from __future__ import annotations

import logging
import sys
from importlib.resources import as_file, files

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from blakelabs_multimedia.application.use_cases.probe_media import ProbeMedia
from blakelabs_multimedia.infrastructure.ffmpeg.binary_resolver import FfmpegBinaryResolver
from blakelabs_multimedia.infrastructure.ffmpeg.qt_probe import QtFfprobeMediaProbe
from blakelabs_multimedia.presentation.qt.media_controller import MediaController
from blakelabs_multimedia.presentation.qt.media_queue_model import MediaQueueModel


def run() -> int:
    """Compose concrete adapters and start the Qt event loop."""
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
    binary_resolver = FfmpegBinaryResolver()
    probe_adapter = QtFfprobeMediaProbe(binary_resolver)
    probe_media = ProbeMedia(probe_adapter)
    media_controller = MediaController(probe_media, queue_model)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("mediaController", media_controller)
    engine.rootContext().setContextProperty("mediaQueueModel", queue_model)

    qml_package = files("blakelabs_multimedia.presentation.qml")
    with as_file(qml_package) as qml_root:
        engine.addImportPath(str(qml_root))
        main_qml = qml_root / "Main.qml"
        engine.load(QUrl.fromLocalFile(str(main_qml)))
        if not engine.rootObjects():
            return 1
        return app.exec()
