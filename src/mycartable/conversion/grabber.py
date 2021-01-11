import time
from typing import Union

from PyQt5.QtCore import (
    QUrl,
    QEventLoop,
    QCoreApplication,
    Qt,
)
from PyQt5.QtQuick import QQuickView
from loguru import logger

from . import WImage


class Grabber(QQuickView):
    def __init__(self, url: Union[QUrl, str], params: dict = {}, timeout: int = 5000):
        super().__init__()
        self.image_grabbed = None
        self.res_grab = None
        self.url = url
        self.timeout = timeout
        self.setInitialProperties(params)
        self.setFlags(
            Qt.FramelessWindowHint
            | Qt.WindowTransparentForInput  # input passe à travers
            | Qt.WindowDoesNotAcceptFocus
            | Qt.Popup  # pour préserver la barre des tâches
            | Qt.WindowStaysOnBottomHint  # le + caché en arrière possible
        )

    def __call__(self, *args, **kwargs):
        self.setSource(self.url)
        obj = self.rootObject()

        # handle error in obj creation
        if not obj:
            for err in self.errors():
                logger.error(err.toString())
            return

        # check sync or async
        if obj.property("status") is None or obj.property("status") == 1:
            # sync: no status prop or complete run grab sync
            self.grab()
        else:
            # async
            obj.loaded.connect(self.grab)

        # attend la completion du grab (timeout = 5000)
        t1 = time.time()
        while self.image_grabbed is None and (
            ((time.time() - t1) * 1000) < self.timeout
        ):
            QCoreApplication.processEvents(QEventLoop.AllEvents, 50)

        # le résultat est retourné
        self.deleteLater()
        return self.image_grabbed

    def grab(self, *args):  # ne pas enlevé le args pour parrer aux arguement du loaded
        self.setOpacity(0)
        self.setVisible(True)
        self.res_grab = self.rootObject().grabToImage()
        if not self.res_grab:
            return
        self.res_grab.ready.connect(self.on_grab)

    def on_grab(self):
        self.image_grabbed = WImage(self.res_grab.image())
        self.close()
