from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt

class MaskItem(QGraphicsItem):
    def __del__(self):
        print("MaskItem 被析构")
        # 销毁前清理属性，避免成员引用残留
        self.img_rect = None
        self.crop_rect = None

    def __init__(self, img_rect, crop_rect):
        super().__init__()
        self.img_rect = img_rect
        self.crop_rect = crop_rect
        self.darken_color = QColor(0, 0, 0, 128)

    def boundingRect(self):
        # 加健壮性保护
        if self.img_rect is None:
            return super().boundingRect()
        return self.img_rect

    def paint(self, painter, option, widget=None):
        if self.img_rect is None or self.crop_rect is None:
            return  # 如果已被析构，不画
        painter.fillRect(self.img_rect, self.darken_color)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(self.crop_rect, Qt.transparent)