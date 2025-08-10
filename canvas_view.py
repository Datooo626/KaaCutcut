from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsScene, QGraphicsView,
    QPushButton, QFileDialog, QSpinBox, QLabel, QLineEdit, QColorDialog
)
from PyQt5.QtGui import QImage, QPainter, QPixmap, QColor, QPen
from PyQt5.QtCore import Qt, QRectF,QLineF
import os

from resizable_item import ResizableRotatableImageItem


class CanvasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("canvasInterface")

        self.segment_lines = [] 
        self.frame_lines = [] 
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

        self.clear_button = QPushButton("清空画布")
        self.clear_button.clicked.connect(self.clear_canvas)
        self.toolbar.addWidget(self.clear_button)

        self.export_button = QPushButton("导出画布")
        self.export_button.clicked.connect(self.export_canvas)
        self.toolbar.addWidget(self.export_button)

        self.toolbar.addStretch(1)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        self.layout.addWidget(self.view)

        self.update_canvas_geometry()

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if obj == self.view.viewport() and event.type() == QEvent.MouseButtonPress:
            pos = event.pos()
            scene_pos = self.view.mapToScene(pos)
            items = self.scene.items(scene_pos)

            clicked_item = None
            for item in items:
                if isinstance(item, ResizableRotatableImageItem):
                    clicked_item = item
                    break

            if clicked_item is None:
                print("点击空白区域，取消所有选中")
                for image_item in self.image_items:
                    image_item.setSelected(False)
            else:
                print(f"点击图片：{clicked_item}, 选中它")
                for image_item in self.image_items:
                    image_item.setSelected(image_item is clicked_item)

            return False
        return super().eventFilter(obj, event)





    def mouseMoveEvent(self, event):
        if self.dragging_handle and self.start_pos:
            delta = event.scenePos() - self.start_pos
            if self.dragging_handle in ("top", "bottom", "left", "right"):
                # 反转符号，使缩放与鼠标移动方向一致
                factor = 1 - (delta.y() if "top" in self.dragging_handle or "bottom" in self.dragging_handle else delta.x()) / 100
                self.setScale(max(0.1, self.scale() * factor))
            elif self.dragging_handle in ("top_left", "top_right", "bottom_left", "bottom_right"):
                center = self.mapToScene(self.boundingRect().center())
                # 调整旋转角度方向符号
                angle = QLineF(center, event.scenePos()).angleTo(QLineF(center, self.start_pos))
                self.setRotation(self.rotation() + angle)
            self.start_pos = event.scenePos()
            self.update_handles()
        else:
            super().mouseMoveEvent(event)

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
        for line in self.segment_lines:
            self.scene.removeItem(line)
        self.segment_lines.clear()

        pen = QPen(QColor("#999999"), 2, Qt.DashLine)
        for i in range(1, self.block_count):
            x = i * self.scene.width() / self.block_count
            line = self.scene.addLine(x, 0, x, self.scene.height(), pen)
            line.setZValue(1000)
            self.segment_lines.append(line)

    def draw_canvas_frame(self):
        for line in self.frame_lines:
            self.scene.removeItem(line)
        self.frame_lines.clear()

        self.scene.setBackgroundBrush(self.canvas_bg_color)

        rect = self.scene.sceneRect()
        pen = QPen(QColor("#999999"), 2, Qt.DashLine)
        edges = [
            (rect.topLeft(), rect.topRight()),
            (rect.topRight(), rect.bottomRight()),
            (rect.bottomRight(), rect.bottomLeft()),
            (rect.bottomLeft(), rect.topLeft()),
        ]

        for p1, p2 in edges:
            line = self.scene.addLine(p1.x(), p1.y(), p2.x(), p2.y(), pen)
            line.setZValue(999)
            self.frame_lines.append(line)

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
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")
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

    def clear_canvas(self):
        for item in self.image_items:
            self.scene.removeItem(item)
        self.image_items.clear()
        self.canvas_bg_pixmap = None
        self.update_canvas_geometry()

    def export_canvas(self):
        if not self.image_items:
            print("❌ 没有图片，无法导出")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not save_dir:
            return

        scene_rect = self.scene.sceneRect()

        pixel_densities = []
        for item in self.image_items:
            pixmap = item.pixmap_item.pixmap()
            orig_pix_w = pixmap.width()
            orig_pix_h = pixmap.height()

            bounding_rect = item.pixmap_item.mapRectToScene(item.pixmap_item.boundingRect())
            disp_w = bounding_rect.width()
            disp_h = bounding_rect.height()

            if disp_w <= 0 or disp_h <= 0:
                continue

            density_w = orig_pix_w / disp_w
            density_h = orig_pix_h / disp_h
            pixel_densities.append(min(density_w, density_h))

        if not pixel_densities:
            print("❌ 无法计算图片像素密度，导出取消")
            return

        scale_factor = max(pixel_densities)

        max_block_side  = 10000  # 可调整更大
        max_side = max_block_side #* self.block_count
        scale_factor = min(scale_factor, max_side / max(scene_rect.width(), scene_rect.height()))

        export_width = int(scene_rect.width() * scale_factor)
        export_height = int(scene_rect.height() * scale_factor)

        print(f"[DEBUG] Scene rect: {scene_rect}")
        print(f"[DEBUG] calculated scale_factor (max density): {scale_factor}")
        print(f"[DEBUG] export size: {export_width}x{export_height}")

        image = QImage(export_width, export_height, QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        painter = QPainter(image)
        try:
            painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

            # 先画背景色或背景图
            if self.canvas_bg_pixmap:
                painter.drawPixmap(
                    0, 0,
                    self.canvas_bg_pixmap.scaled(export_width, export_height,
                                                Qt.IgnoreAspectRatio, Qt.SmoothPixmapTransform)
                )
            else:
                painter.fillRect(QRectF(0, 0, export_width, export_height), self.canvas_bg_color)

            # 绘制每个图片的原始像素到对应放大后的区域
            for idx, item in enumerate(self.image_items):
                pixmap = item.pixmap_item.pixmap()

                # 获取图片在场景中的显示区域（浮点）
                scene_rect_item = item.pixmap_item.mapRectToScene(item.pixmap_item.boundingRect())

                # 计算导出图像中对应位置和大小（整数像素）
                x = int(scene_rect_item.left() * scale_factor)
                y = int(scene_rect_item.top() * scale_factor)
                w = int(scene_rect_item.width() * scale_factor)
                h = int(scene_rect_item.height() * scale_factor)

                if w <= 0 or h <= 0:
                    continue

                # 将原始pixmap缩放到导出大小（保持高质量）
                scaled_pixmap = pixmap.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

                painter.drawPixmap(x, y, scaled_pixmap)
                print(f"[DEBUG] 绘制图片 {idx} 到 ({x}, {y}, {w}, {h})")

        finally:
            painter.end()

        # 分块保存
        block_w = export_width // self.block_count
        for i in range(self.block_count):
            x = i * block_w
            block_img = image.copy(x, 0, block_w, export_height)
            filename = os.path.join(save_dir, f"segment_{i+1}.png")
            block_img.save(filename, "PNG")
            print(f"[DEBUG] 保存分块: {filename}")

        print(f"[✅ 导出完成] 共导出 {self.block_count} 张图")



