from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt5.QtCore import QRectF, Qt, QPointF, QLineF
from PyQt5.QtGui import QPen, QPixmap


class HandleItem(QGraphicsRectItem):
    def __init__(self, name, parent=None):
        size = ResizableRotatableImageItem.HANDLE_SIZE
        super().__init__(0, 0, size, size, parent)
        self.name = name
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setCursor(Qt.SizeAllCursor)
        self.dragging = False
        self.start_pos = None

    def mousePressEvent(self, event):
        print(f"[DEBUG] Handle {self.name} mousePressEvent")
        self.dragging = True
        self.start_pos = event.scenePos()
        if self.parentItem():
            self.parentItem().handleDragStart(self.name, self.start_pos)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            current_pos = event.scenePos()
            print(f"[DEBUG] Handle {self.name} mouseMoveEvent")
            if self.parentItem():
                self.parentItem().handleDrag(self.name, current_pos)
            self.start_pos = current_pos
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        print(f"[DEBUG] Handle {self.name} mouseReleaseEvent")
        self.dragging = False
        self.start_pos = None
        if self.parentItem():
            self.parentItem().handleDragEnd(self.name)
        event.accept()


class ResizableRotatableImageItem(QGraphicsItemGroup):
    HANDLE_SIZE = 12

    def __init__(self, pixmap: QPixmap, target_width: float, target_height: float):
        super().__init__()

        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.pixmap_item.setTransformationMode(Qt.SmoothTransformation)

        # 缩放图片以适应目标大小
        factor = min(target_width / pixmap.width(), target_height / pixmap.height())
        print(f"[DEBUG] Init pixmap: orig_size={pixmap.size()}, target=({target_width},{target_height}), scale_factor={factor}")
        self.pixmap_item.setScale(factor)
        self.addToGroup(self.pixmap_item)

        self.setFlags(
            self.flags()
            | self.ItemIsMovable
            | self.ItemIsSelectable
            | self.ItemSendsGeometryChanges
        )

        # 旋转中心点初始化为图片中心
        self.setTransformOriginPoint(self.boundingRect().center())

        self.handles = {}

        # 拖动捕捉点时使用的状态
        self.start_pos_for_handle = None

        self.update_handles()

    def boundingRect(self):
        # 返回图片当前在父坐标系的矩形
        return self.pixmap_item.mapRectToParent(self.pixmap_item.boundingRect())

    def update_handles(self):
        # 移除旧捕捉点
        for handle in self.handles.values():
            if handle.scene() is not None:
                self.scene().removeItem(handle)
        self.handles.clear()

        if not self.isSelected():
            print("[DEBUG] Not selected, no handles shown")
            return

        rect = self.boundingRect()
        print(f"[DEBUG] boundingRect = {rect}")

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
            handle = HandleItem(name, self)
            handle.setBrush(Qt.white)
            handle.setPen(QPen(Qt.black, 1))
            handle.setZValue(self.zValue() + 1)
            handle.setPos(pos.x() - self.HANDLE_SIZE / 2, pos.y() - self.HANDLE_SIZE / 2)
            self.handles[name] = handle
            print(f"[DEBUG] Added handle: {name} at {pos}")

    def handleDragStart(self, handle_name, scene_pos):
        print(f"[DEBUG] handleDragStart: {handle_name}, pos={scene_pos}")
        self.start_pos_for_handle = scene_pos

    def handleDrag(self, handle_name, scene_pos):
        if self.start_pos_for_handle is None:
            self.start_pos_for_handle = scene_pos

        center = self.mapToScene(self.boundingRect().center())

        if handle_name in ("top", "bottom", "left", "right"):
            # 缩放捕捉点
            delta = scene_pos - self.start_pos_for_handle
            # 根据捕捉点名称决定使用X还是Y方向增量
            if handle_name in ("top", "bottom"):
                factor = 1 + delta.y() / 200.0
            else:  # left or right
                factor = 1 + delta.x() / 200.0

            # 限制最小缩放比例
            new_scale = max(0.1, self.scale() * factor)
            print(f"[DEBUG] Scaling from {self.scale():.3f} to {new_scale:.3f} by factor {factor:.3f}")
            self.setScale(new_scale)
            self.start_pos_for_handle = scene_pos

        elif handle_name in ("top_left", "top_right", "bottom_left", "bottom_right"):
            # 旋转捕捉点
            line_start = QLineF(center, self.start_pos_for_handle)
            line_end = QLineF(center, scene_pos)
            angle = line_start.angleTo(line_end)
            print(f"[DEBUG] Rotating from {self.rotation():.3f} by angle {angle:.3f}")
            self.setRotation(self.rotation() + angle)
            self.start_pos_for_handle = scene_pos

        self.update_handles()

    def handleDragEnd(self, handle_name):
        print(f"[DEBUG] handleDragEnd: {handle_name}")
        self.start_pos_for_handle = None

    def paint(self, painter, option, widget=None):
        # 由子项绘制，无需额外绘制
        pass

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == self.ItemSelectedHasChanged:
            self.update_handles()
        return super().itemChange(change, value)
