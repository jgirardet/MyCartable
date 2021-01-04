from PySide2.QtCore import (
    QObject,
    QSize,
    QUrl,
    QByteArray,
    QCoreApplication,
    QEventLoop,
)
from PySide2.QtGui import (
    QSurfaceFormat,
    QOpenGLContext,
    QOffscreenSurface,
    QOpenGLFramebufferObject,
)
from PySide2.QtQml import (
    QQmlComponent,
    QQmlEngine,
    QQmlIncubator,
    QQmlIncubationController,
)
from PySide2.QtQuick import QQuickItem, QQuickRenderControl, QQuickWindow
from .wimage import WImage


class Grabber(QObject):
    def __init__(self, context_dict: dict = {}):
        super().__init__()

        self.qml_comp: QQmlComponent = None
        self.rootItem: QQuickItem = None

        # setup opengl
        self.format = QSurfaceFormat()
        self.format.setDepthBufferSize(16)
        self.format.setStencilBufferSize(8)
        self.m_context = QOpenGLContext(parent=self)
        self.m_context.setFormat(self.format)
        self.m_context.create()
        self.m_offscreenSurface = QOffscreenSurface()
        self.m_offscreenSurface.setFormat(self.m_context.format())
        self.m_offscreenSurface.create()

        # setup renderControl/Window
        self.m_renderControl = QQuickRenderControl(parent=self)
        self.m_quickWindow = QQuickWindow(self.m_renderControl)

        # setup engine and context
        self.m_qmlEngine = QQmlEngine()
        self.context = self.m_qmlEngine.rootContext()
        for k, v in context_dict.items():
            self.context.setContextProperty(k, v)

        # needed for async load
        self.incubationController = QQmlIncubationController()
        if not self.m_qmlEngine.incubationController():
            self.m_qmlEngine.setIncubationController(self.incubationController)

    def load_component(
        self,
        url: str = "",
        data: bytes = b"",
        width: int = 0,
        height: int = 0,
        initial_prop={},
    ):
        self.qml_comp = QQmlComponent(self.m_qmlEngine)
        if url:
            self.qml_comp.loadUrl(
                QUrl.fromLocalFile(url),
                QQmlComponent.Asynchronous,
            )
        elif data:
            self.qml_comp.setData(QByteArray(data), QUrl(url))

        while self.qml_comp.isLoading():
            QCoreApplication.processEvents(QEventLoop.AllEvents, 50)

        if self.qml_comp.isError():
            raise Exception(self.qml_comp.errorString())

        self.incubator = QQmlIncubator()
        self.incubator.setInitialProperties(initial_prop)

        self.qml_comp.create(self.incubator)
        self.incubationController.incubateFor(1000)
        self.rootItem = self.incubator.object()

        # synchronous way
        # self.rootItem = self.qml_comp.createWithInitialProperties(initial_prop)

        self._set_size(width, height)

    def to_image(self) -> WImage:
        img = self.m_renderControl.grab()
        return WImage(img)

    def comp_to_image(self, **kwargs) -> WImage:
        """Render a Component to WImage
        :param kwargs: see load_component
        """
        self.load_component(**kwargs)
        self.render_component()
        return self.to_image()

    def render_component(self):
        self.rootItem.setParentItem(self.m_quickWindow.contentItem())
        self.m_renderControl.polishItems()
        self.m_renderControl.sync()
        self.m_renderControl.render()
        self.m_context.functions().glFlush()

    def _set_fbo(self, width, height):
        self.m_fbo = QOpenGLFramebufferObject(
            QSize(width, height), QOpenGLFramebufferObject.CombinedDepthStencil
        )
        self.m_quickWindow.setRenderTarget(self.m_fbo)

    def _set_size(self, width: int, height: int):
        """
        Adapte les tailles  si nécessaire. Les dimension du composant
        seront écrasées par width ou height.
        La Window s'adapte aux dimension retenues pour fitter le composer
        :param width: largeur
        :param height: hauteur
        :return: None
        """
        if width:
            self.rootItem.setWidth(width)
        if height:
            self.rootItem.setHeight(height)
        r_width = self.rootItem.width()
        r_height = self.rootItem.height()
        self._set_fbo(r_width, r_height)
        self.m_quickWindow.setGeometry(0, 0, r_width, r_height)

    def __enter__(self):
        self.m_context.makeCurrent(self.m_offscreenSurface)
        self.m_renderControl.initialize(self.m_context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.m_renderControl.invalidate()
