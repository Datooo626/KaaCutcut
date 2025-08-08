# resizable_item.py

from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt5.QtCore import QRectF, Qt, QPointF, QLineF
from PyQt5.QtGui import QPen, QPixmap


class ResizableRotatableImageItem(QGraphicsItemGroup):
    HANDLE_SIZE = 12

    def __init__(self, pixmap: QPixmap, target_width: float, target_height: float):
        super().__init__()

        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.pixmap_item.setTransformationMode(Qt.SmoothTransformation)

        # 缩放
        factor = min(target_width / pixmap.width(), target_height / pixmap.height())
        self.pixmap_item.setScale(factor)
        self.addToGroup(self.pixmap_item)

        self.setFlags(
            self.flags()
            | self.ItemIsMovable
            | self.ItemIsSelectable
            | self.ItemSendsGeometryChanges
        )

        self.setTransformOriginPoint(self.boundingRect().center())
        self.handles = {}
        self.dragging_handle = None
        self.start_pos = None
        self.update_handles()

    def update_handles(self):
        for handle in self.handles.values():
            self.scene().removeItem(handle)
        self.handles.clear()

        if not self.isSelected():
            return

        rect = self.boundingRect()
        positions = {
            "top_left": rect.topLeft(),
            "top": QPointF(rect.center().x(), rect.top()),
            "top_right": rect.topRight(),
            "right": QPointF(rect.right(), rect.center().y()),
            "bottom_right": rect.bottomRight(),
            "bottom": QPointF(rect.center().x(), rect.bottom()),
            "bottom_left": rect.bottomLeft(),
            "left": QPointF(rect.left(), rect.center().y()),
        }

        for name, pos in positions.items():
            handle = QGraphicsRectItem(0, 0, self.HANDLE_SIZE, self.HANDLE_SIZE)
            handle.setParentItem(self)
            handle.setBrush(Qt.white)
            handle.setPen(QPen(Qt.black, 1))
            handle.setZValue(self.zValue() + 1)
            handle.setPos(pos.x() - self.HANDLE_SIZE / 2, pos.y() - self.HANDLE_SIZE / 2)
            self.handles[name] = handle

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.pixmap_item.mapRectToParent(self.pixmap_item.boundingRect())

    def mousePressEvent(self, event):
        for name, handle in self.handles.items():
            if handle.contains(event.pos() - handle.pos()):
                self.dragging_handle = name
                self.start_pos = event.scenePos()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging_handle and self.start_pos:
            delta = event.scenePos() - self.start_pos
            if self.dragging_handle in ("top", "bottom", "left", "right"):
                factor = 1 + (delta.y() if "top" in self.dragging_handle or "bottom" in self.dragging_handle else delta.x()) / 100
                self.setScale(max(0.1, self.scale() * factor))
            elif self.dragging_handle in ("top_left", "top_right", "bottom_left", "bottom_right"):
                center = self.mapToScene(self.boundingRect().center())
                angle = QLineF(center, self.start_pos).angleTo(QLineF(center, event.scenePos()))
                self.setRotation(self.rotation() + angle)
            self.start_pos = event.scenePos()
            self.update_handles()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging_handle = None
        self.start_pos = None
        self.update_handles()
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == self.ItemSelectedChange:
            self.update_handles()
        return super().itemChange(change, value)
