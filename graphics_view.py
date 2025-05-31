from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from aspect_ratio_rect import AspectRatioRectItem
#import weakref

class ResizableGraphicsView(QGraphicsView):
    def __del__(self):
        print("ResizableGraphicsView 被析构")
        # 防止C++侧已析构scene导致的潜在安全问题
        try:
            self.setScene(None)
        except Exception:
            pass

    def __init__(self, scene):
        super().__init__(scene)
        self.last_scale = 1.0
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)

    def resizeEvent(self, event):
        # 检查scene是否还存活
        scene = self.scene()
        if scene is not None:
            try:
                self.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
            except Exception:
                pass
        super().resizeEvent(event)

    def wheelEvent(self, event):
        scene = self.scene()
        if scene is None:
            return
        factor = 1.25
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)
        self.last_scale *= factor
        for item in scene.items() if scene is not None else []:
            # 增加弱引用有效性检测
            if isinstance(item, AspectRatioRectItem):
                item.view_scale = self.last_scale
                item.updateHandles()

    def mouseMoveEvent(self, event):
        scene = self.scene()
        if scene is not None:
            current_transform = self.transform()
            for item in scene.items():
                if isinstance(item, AspectRatioRectItem):
                    item.viewport_transform = current_transform
        super().mouseMoveEvent(event)