# canvas_view.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsScene, QGraphicsView,
    QPushButton, QFileDialog, QSpinBox, QLabel, QLineEdit, QColorDialog
)
from PyQt5.QtGui import QImage, QPainter, QPixmap, QColor, QPen
from PyQt5.QtCore import Qt
import os

from resizable_item import ResizableRotatableImageItem


class CanvasView(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("canvasInterface")

        self.segment_lines = [] #子图分割线
        self.frame_lines = [] #画布边框线
        self.image_items = []
        self.block_count = 3
        self.aspect_ratio = 4 / 3
        self.canvas_bg_color = QColor("#f2f2f2")
        self.canvas_bg_pixmap = None

        self.layout = QVBoxLayout(self)
        self.toolbar = QHBoxLayout()
        self.layout.addLayout(self.toolbar)

        self.toolbar.addWidget(QLabel("子图数量:"))
        self.block_spin = QSpinBox()
        self.block_spin.setMinimum(1)
        self.block_spin.setValue(self.block_count)
        self.block_spin.valueChanged.connect(self.update_canvas_geometry)
        self.toolbar.addWidget(self.block_spin)

        self.toolbar.addWidget(QLabel("宽高比:"))
        self.ratio_edit = QLineEdit("4:3")
        self.ratio_edit.setFixedWidth(60)
        self.ratio_edit.editingFinished.connect(self.update_aspect_ratio)
        self.toolbar.addWidget(self.ratio_edit)

        self.import_button = QPushButton("导入图片")
        self.import_button.clicked.connect(self.import_images)
        self.toolbar.addWidget(self.import_button)

        self.bg_color_btn = QPushButton("设置背景色")
        self.bg_color_btn.clicked.connect(self.choose_background_color)
        self.toolbar.addWidget(self.bg_color_btn)

        self.bg_image_btn = QPushButton("设置背景图片")
        self.bg_image_btn.clicked.connect(self.choose_background_image)
        self.toolbar.addWidget(self.bg_image_btn)

        self.clear_button = QPushButton("清空画布")  # ✅ 清空按钮
        self.clear_button.clicked.connect(self.clear_canvas)
        self.toolbar.addWidget(self.clear_button)

        self.export_button = QPushButton("导出画布")
        self.export_button.clicked.connect(self.export_canvas)
        self.toolbar.addWidget(self.export_button)

        self.toolbar.addStretch(1)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

        self.update_canvas_geometry()

    def update_aspect_ratio(self):
        text = self.ratio_edit.text().replace("：", ":")
        if ":" in text:
            try:
                w, h = map(float, text.split(":"))
                self.aspect_ratio = w / h
                self.update_canvas_geometry()
            except:
                pass

    def update_canvas_geometry(self):
        self.block_count = self.block_spin.value()
        block_w = 300
        block_h = block_w / self.aspect_ratio
        total_w = block_w * self.block_count
        self.scene.setSceneRect(0, 0, total_w, block_h)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.draw_segment_lines()
        self.draw_canvas_frame()

    def draw_segment_lines(self):
        # ✅ 删除旧分割线
        for line in self.segment_lines:
            self.scene.removeItem(line)
        self.segment_lines.clear()

        pen = QPen(QColor("#999999"), 2, Qt.DashLine)  # ✅ 虚线灰色

        # ✅ 添加新分割线
        for i in range(1, self.block_count):
            x = i * self.scene.width() / self.block_count
            line = self.scene.addLine(x, 0, x, self.scene.height(),pen)
            line.setZValue(1000)
            self.segment_lines.append(line)

    def draw_canvas_frame(self):
        # ✅ 清除旧边框（无视 scene.items）
        for line in self.frame_lines:
            self.scene.removeItem(line)
        self.frame_lines.clear()

        self.scene.setBackgroundBrush(self.canvas_bg_color)

        rect = self.scene.sceneRect()
        pen = QPen(QColor("#999999"), 2, Qt.DashLine)  # ✅ 虚线灰色
        edges = [
            (rect.topLeft(), rect.topRight()),
            (rect.topRight(), rect.bottomRight()),
            (rect.bottomRight(), rect.bottomLeft()),
            (rect.bottomLeft(), rect.topLeft()),
        ]

        for p1, p2 in edges:
            line = self.scene.addLine(p1.x(), p1.y(), p2.x(), p2.y(), pen)
            line.setZValue(999)
            self.frame_lines.append(line)  # ✅ 保存边框线


    def choose_background_color(self):
        color = QColorDialog.getColor(initial=self.canvas_bg_color, parent=self, title="选择画布背景色")
        if color.isValid():
            self.canvas_bg_color = color
            self.canvas_bg_pixmap = None
            self.update_canvas_geometry()

    def choose_background_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择背景图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.canvas_bg_pixmap = QPixmap(path)
            self.update_canvas_geometry()

    def import_images(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)", options=options)
        for path in files:
            pixmap = QPixmap(path)
            block_w = self.scene.width() / self.block_count
            block_h = self.scene.height()
            target_w = block_w * 0.6
            target_h = block_h * 0.6
            item = ResizableRotatableImageItem(pixmap, target_w, target_h)
            self.scene.addItem(item)
            item.setPos(self.scene.width() / 2, self.scene.height() / 2)
            self.image_items.append(item)

    def clear_canvas(self):  # ✅ 清空按钮逻辑
        for item in self.image_items:
            self.scene.removeItem(item)
        self.image_items.clear()
        self.canvas_bg_pixmap = None
        self.update_canvas_geometry()

    def export_canvas(self):
        if not self.image_items:
            return
        save_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not save_dir:
            return
        block_w = self.scene.width() / self.block_count
        block_h = self.scene.height()
        total_size = self.scene.sceneRect().size().toSize()
        final_image = QImage(total_size, QImage.Format_ARGB32)
        painter = QPainter(final_image)
        if self.canvas_bg_pixmap:
            painter.drawPixmap(0, 0, self.canvas_bg_pixmap.scaled(total_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            final_image.fill(self.canvas_bg_color)
        self.scene.render(painter)
        painter.end()
        for i in range(self.block_count):
            x = int(i * block_w)
            y = 0
            w = int(block_w)
            h = int(block_h)
            block_img = final_image.copy(x, y, w, h)
            block_img.save(os.path.join(save_dir, f"segment_{i+1}.png"))
