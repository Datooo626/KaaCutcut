from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsRectItem, QGraphicsLineItem, QGraphicsItem

class OverlayManager(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.darken_window = None
        self.light_window = None
        self.grid_lines = []

    def create_overlay(self):
        mw = self.main_window
        self.clear_existing_overlays()
        if not mw.pixmap_item or not mw.crop_rect:
            return

        img_rect = mw.pixmap_item.boundingRect()
        crop_rect = mw.crop_rect.mapRectToItem(mw.pixmap_item, mw.crop_rect.rect)

        # == 修改点1：所有item直接scene.addItem，不用parentItem ==
        # self.darken_window = QGraphicsPathItem(mask_path, mw.pixmap_item)  # ←【删除parentItem参数】
        # ↓↓↓
        full_path = QPainterPath()
        full_path.addRect(img_rect)
        crop_path = QPainterPath()
        crop_path.addRect(crop_rect)
        mask_path = full_path.subtracted(crop_path)
        self.darken_window = QGraphicsPathItem(mask_path)
        # == 修改点1 END ==

        self.darken_window.setBrush(QColor(0, 0, 0, int(255 * mw.darken_factor)))
        self.darken_window.setPen(QPen(Qt.NoPen))
        self.disable_item_interaction(self.darken_window)

        self.light_window = QGraphicsRectItem(crop_rect)
        self.light_window.setBrush(QBrush(Qt.NoBrush))
        self.light_window.setPen(QPen(Qt.NoPen))
        self.light_window.setOpacity(1.0)
        self.disable_item_interaction(self.light_window)

        # z-value调整保持不变
        mw.pixmap_item.setZValue(0)
        self.darken_window.setZValue(1)
        self.light_window.setZValue(2)
        mw.crop_rect.setZValue(3)

        # == 修改点2：仅scene.addItem
        mw.scene.addItem(self.darken_window)
        mw.scene.addItem(self.light_window)
        # == 修改点2 END ==

        self.update_grid_lines()

    def update_overlay(self):
        self.create_overlay()

    def update_grid_lines(self):
        # 清理原有
        mw = self.main_window
        scene = mw.scene
        for line in self.grid_lines:
            # == 修改点3：先判scene再removeItem ==
            if line and line.scene() == scene:
                scene.removeItem(line)
        self.grid_lines = []

        if not mw.crop_rect:
            return
        rect = mw.crop_rect.rect
        rows = max(1, getattr(mw.crop_rect, 'rows', 1))
        cols = max(1, getattr(mw.crop_rect, 'cols', 1))
        # 画竖线
        for c in range(1, cols):
            x = rect.left() + c * rect.width() / cols
            line = QGraphicsLineItem(x, rect.top(), x, rect.bottom())
            line.setPen(QPen(QColor(255, 255, 255, 255), 6,Qt.DashLine))
            scene.addItem(line)
            self.grid_lines.append(line)
        # 画横线
        for r in range(1, rows):
            y = rect.top() + r * rect.height() / rows
            line = QGraphicsLineItem(rect.left(), y, rect.right(), y)
            line.setPen(QPen(QColor(255, 255, 255, 255), 6,Qt.DashLine))
            scene.addItem(line)
            self.grid_lines.append(line)

    def clear_existing_overlays(self):
        scene = getattr(self.main_window, "scene", None)
        # == 修改点4：所有removeItem前检查scene ==
        if self.darken_window and (self.darken_window.scene() == scene):
            scene.removeItem(self.darken_window)
        if self.light_window and (self.light_window.scene() == scene):
            scene.removeItem(self.light_window)
        for line in self.grid_lines:
            if line and line.scene() == scene:
                scene.removeItem(line)
        self.darken_window = None
        self.light_window = None
        self.grid_lines.clear()

    def disable_item_interaction(self, item):
        item.setAcceptedMouseButtons(Qt.NoButton)
        item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        item.setFlag(QGraphicsItem.ItemIsMovable, False)

    def update_brightness(self):
        if self.darken_window:
            mw = self.main_window
            self.darken_window.setBrush(QColor(0, 0, 0, int(255 * mw.darken_factor)))

    def show_real_area(self):
        # todo：添加预览功能
        pass







