#import sys
import os, datetime
import platform
import re
#import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,  QDialog, QApplication,
    QSpinBox, QFileDialog, QGraphicsScene, QSizePolicy #, QSlider, QCheckBox, QSpacerItem,
    #QLineEdit,QPushButton, QMessageBox,QProgressBar
)
from PyQt5.QtGui import QPixmap, QImage,QIcon #, QPen, QColor
from PyQt5.QtCore import Qt, QRectF #, QTimer
from PIL import Image

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition , #ProgressBar, StrongBodyLabel,TogglePushButton,
    InfoBar, InfoBarPosition, PrimaryPushButton, 
     PushButton, LineEdit, CheckBox, Slider, 
    setTheme, Theme, isDarkTheme, FluentIcon,InfoBarIcon
)

from aspect_ratio_rect import AspectRatioRectItem
from graphics_view import ResizableGraphicsView
from overlay_manager import OverlayManager

class ImageCropper(FluentWindow):
    def __del__(self):
        print("ImageCropper 被析构")
        try:
            if self.crop_rect:
                self.crop_rect.disconnect_all_signals()
        except Exception:
            pass
        self.crop_rect = None
        self.pixmap_item = None
        
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("./icon/KaaCutcut.ico"))
        self.setWindowTitle("KaaCutcut 咔咔切 - 一键实现图片无缝裁切自由")
        self.setMinimumSize(1060, 600)
        
        # 初始化属性
        self.darken_factor = 0.5
        self.image_path = None
        self.original_image = None
        self.crop_rect = None
        self.pixmap_item = None
        
        # 创建主界面
        self.main_interface = QWidget()
        self.main_interface.setObjectName("mainInterface")
        self.main_layout = QVBoxLayout(self.main_interface)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # 添加状态栏
        self.status_bar_text = QLabel('就绪')
        self.status_bar_text.setAlignment(Qt.AlignLeft)
        self.status_bar_text.setStyleSheet("padding: 1px;background-color: rgba(0, 0, 0, 0.05); border-radius: 4px;")
        
        # 初始化UI
        self.init_ui()
        self.overlay_manager = OverlayManager(self)
        self.addSubInterface(
            self.main_interface, 
            icon=FluentIcon.PHOTO,
            text='图片裁切',
            position=NavigationItemPosition.TOP
        )

        # 创建更多信息界面
        self.create_more_interface()
        # 创建关于我们界面
        self.create_aboutme_interface()

        
        # 设置初始页面
        self.navigationInterface.setCurrentItem('图片裁切')
        self.navigationInterface.setExpandWidth(150)  #限制导航栏展开宽度
        self.setMicaEffectEnabled(True)

    def create_aboutme_interface(self):
        """创建关于我们界面"""
        self.aboutme_interface = QWidget()
        self.aboutme_interface.setObjectName("aboutmeInterface")
        layout = QVBoxLayout(self.aboutme_interface)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题 - 使用QLabel并设置大字体
        title_label = QLabel("关于 KaaCutcut 咔咔切")
        title_label.setAlignment(Qt.AlignCenter)
        # title_font = QFont()
        # title_font.setPointSize(16)
        # title_font.setBold(True)
        # title_label.setFont(title_font)
        
        # 应用图标
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("./icon/KaaCutcut.ico").scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)
        
        # 版本信息
        version_label = QLabel("版本: 1.1.0 202505")
        version_label.setAlignment(Qt.AlignCenter)
        
        # 介绍文本
        intro_text = (
            "KaaCutcut 咔咔切是一款简单易用的图片裁剪工具，帮助您快速实现图片任意比例任意数量的自由裁切。\n\n"
            "    摸鱼无聊，写点bug吧。第一次写带界面的bug，核心代码20行、花2h加上UI，又花了2天+2天+2天+2天...修bug...关键是还没修完...\n"
            "累了，就先这样吧\n"
            "摸鱼效率≈修bug效率\n"
            "bug反馈：Datou mail：datouor@gmail.com\n"
            "Github:  https://github.com/Datooo626/KaaCtuctu "
        )
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)
        
        # 开发团队 - 使用小标题样式
        team_label = QLabel("摸鱼：")
        # team_font = QFont()
        # team_font.setPointSize(12)
        # team_font.setBold(True)
        # team_label.setFont(team_font)
        
        team_text = QLabel("Datou、Deepseek、ChatGPT \n@2025")
        team_text.setAlignment(Qt.AlignCenter)
        
        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(icon_label)
        layout.addWidget(version_label)
        layout.addSpacing(20)
        layout.addWidget(intro_label)
        layout.addStretch(1)
        layout.addWidget(team_label)
        layout.addWidget(team_text)
        
        # 添加到导航栏
        self.addSubInterface(
            self.aboutme_interface,
            icon=FluentIcon.INFO,
            text='Aboutme',
            position=NavigationItemPosition.BOTTOM
        )

    def create_more_interface(self):
        """创建更多信息界面"""
        self.more_interface = QWidget()
        self.more_interface.setObjectName("moreInterface")
        layout = QVBoxLayout(self.more_interface)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("More")
        title_label.setAlignment(Qt.AlignCenter)
        # title_font = QFont()
        # title_font.setPointSize(16)
        # title_font.setBold(True)
        # title_label.setFont(title_font)
        
        # 功能特点
        features_label = QLabel("摸鱼成果")
        # subtitle_font = QFont()
        # subtitle_font.setPointSize(12)
        # subtitle_font.setBold(True)
        # features_label.setFont(subtitle_font)
        
        features_text = (
            "• 简单直观的裁剪界面\n"
            "• 支持JPG、JPEG、PNG\n"
            "• 拖拽式交互，软件页面和图片可自由缩放\n"
            "• 实时预览裁剪区域，与背景反差度可调\n"
            "• 可锁定子图片的宽高比例\n"
            "• 一键保存裁剪结果"
        )
        features_content = QLabel(features_text)
        
        # 使用指南
        guide_label = QLabel("摸鱼指南")
        #guide_label.setFont(subtitle_font)
        guide_text = (
            "1. 点击'打开图片'按钮选择图片\n"
            "2. 在图片上拖动选择裁剪区域\n"
            "3. 调整分割数量、设置是否锁定子图像比例\n"
            "4. 调整裁剪框大小和位置\n"
            "5. 使用'保存'按钮保存结果"
        )
        guide_content = QLabel(guide_text)
        
        # 未来计划
        future_label = QLabel("摸鱼计划")
        #future_label.setFont(subtitle_font)
        future_text = (
            "• 解决已知BUG: \n"
            "  - 部分UI未居中、剪裁框的上/左边框拖拽功能异常、导出进度条更新异常，页面布局凌乱，小尺寸缩放时菜单重叠...\n"
            "  - 添加强制约束来保证严格的比例锁定：当前是依靠计算精度来保证比例锁定，\n"
            "    在缩放和图层映射计算时存在小数，理论上可能会导致子图像边缘存在1个像素的偏差或重叠\n"
            "• 添加更多bug:\n"
            "  - 添加复位按钮，目前剪裁框拖到最大之后就不好选中了"
            "  - 支持多种图片导出格式\n"
            "  - 给比例锁定功能添加选项：自由/裁切比例锁定/子图比例锁定\n"
            "  - 切都切了，那拼图功能也加上吧\n"
            "  - 整合胶卷负片一键校色功能？ "
        )
        future_content = QLabel(future_text)
        
        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(features_label)
        layout.addWidget(features_content)
        layout.addWidget(guide_label)
        layout.addWidget(guide_content)
        layout.addWidget(future_label)
        layout.addWidget(future_content)
        layout.addStretch(1)
        
        # 添加到导航栏
        self.addSubInterface(
            self.more_interface,
            icon=FluentIcon.MORE,
            text='More',
            position=NavigationItemPosition.BOTTOM
        )
                
    def _normalize_ratio_text(self, text):
        text = text.replace('：', ':')
        norm = re.sub(r'[^0-9:]', '', text)
        parts = norm.split(':')
        if len(parts) >= 2:
            return f"{parts[0]}:{parts[1]}"
        return norm 

    def init_ui(self):
        # 创建工具栏
        toolbar_layout = self.create_toolbar()
        self.main_layout.addLayout(toolbar_layout)
        
        # 添加图形视图
        self.init_graphics_view()
        
        # 添加状态栏
        self.main_layout.addWidget(self.status_bar_text)
        
        # # 添加主题切换按钮
        # self.theme_btn = PushButton('切换主题')
        # self.theme_btn.setFixedWidth(100)
        # self.theme_btn.clicked.connect(self.toggle_theme)
        # self.main_layout.addWidget(self.theme_btn, alignment=Qt.AlignRight)
        
        # # 添加底部信息
        # footer = QLabel("© 2023 KaaCutcut - 图片裁剪工具")
        # footer.setAlignment(Qt.AlignCenter)
        # footer.setStyleSheet("color: #666; font-size: 10pt; margin-top: 10px;")
        # self.main_layout.addWidget(footer)

        #在图形视图后面加:
        self.progress_overlay = QWidget(self.view)
        self.progress_overlay.setAttribute(Qt.WA_TranslucentBackground)
        self.progress_overlay.setStyleSheet("background: transparent;")
        self.progress_overlay.setLayout(QHBoxLayout())
        self.progress_overlay.layout().setAlignment(Qt.AlignHCenter)
        self.progress_overlay.hide()



    def toggle_theme(self):
        current_theme = Theme.DARK if isDarkTheme() else Theme.LIGHT
        new_theme = Theme.LIGHT if current_theme == Theme.DARK else Theme.DARK
        setTheme(new_theme)
        
        # 更新状态栏样式
        if new_theme == Theme.DARK:
            self.status_bar_text.setStyleSheet("padding: 5px; background-color: rgba(255, 255, 255, 0.1); border-radius: 4px;")
        else:
            self.status_bar_text.setStyleSheet("padding: 5px; background-color: rgba(0, 0, 0, 0.05); border-radius: 4px;")

    def init_graphics_view(self):
        self.scene = QGraphicsScene()
        self.view = ResizableGraphicsView(self.scene)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setStyleSheet("border: 1px solid #e1e1e1; border-radius: 4px;")
        self.main_layout.addWidget(self.view, 1)

    def create_toolbar(self):
        toolbar = QHBoxLayout()
        toolbar.setSpacing(15)

        # 打开图片按钮
        self.open_btn = PrimaryPushButton('打开图片')
        self.open_btn.setFixedWidth(120)
        self.open_btn.clicked.connect(self.open_image_dialog)
        toolbar.addWidget(self.open_btn)

        # 行数列数设置
        toolbar.addWidget(QLabel('行数:'))
        self.rows_spin = QSpinBox()
        self.rows_spin.setFixedWidth(40)
        self.rows_spin.setMinimum(1)
        self.rows_spin.setValue(1)
        self.rows_spin.valueChanged.connect(self.on_grid_param_changed)
        toolbar.addWidget(self.rows_spin)

        toolbar.addWidget(QLabel('列数:'))
        self.cols_spin = QSpinBox()
        self.cols_spin.setFixedWidth(40)
        self.cols_spin.setMinimum(1)
        self.cols_spin.setValue(3)
        self.cols_spin.valueChanged.connect(self.on_grid_param_changed)
        toolbar.addWidget(self.cols_spin)

        # 锁定比例
        self.lock_check = CheckBox('锁定比例')
        self.lock_check.setChecked(False)
        self.lock_check.stateChanged.connect(self.toggle_aspect_lock)
        self.lock_check.stateChanged.connect(self.on_grid_param_changed)
        toolbar.addWidget(self.lock_check)

        # 宽高比例
        toolbar.addWidget(QLabel('宽高比:'))
        self.ratio_edit = LineEdit()
        self.ratio_edit.setFixedWidth(60)
        self.ratio_edit.setText('3:4')
        self.ratio_edit.editingFinished.connect(self.update_aspect_ratio)
        self.ratio_edit.editingFinished.connect(self.on_grid_param_changed)
        toolbar.addWidget(self.ratio_edit)

        # 背景反差度
        toolbar.addWidget(QLabel('背景反差度:'))
        self.brightness_slider = Slider(Qt.Horizontal)
        self.brightness_slider.setFixedWidth(150)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        toolbar.addWidget(self.brightness_slider)

        # todo：还没想好预览功能怎么做
        # self.preview_btn = TogglePushButton('预览')
        # self.preview_btn.setFixedWidth(80)
        # self.preview_btn.clicked.connect(self.show_real_area)
        # toolbar.addWidget(self.preview_btn)
        # 保存和预览按钮

        self.save_btn = PrimaryPushButton('保存裁剪')
        self.save_btn.setFixedWidth(100)
        self.save_btn.clicked.connect(self.save_cropped)
        toolbar.addWidget(self.save_btn)
        # 添加弹性空间使布局更合理
        toolbar.addStretch(1)

        return toolbar

    def open_image_dialog(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, '打开图片', '', 'Images (*.png *.jpg *.jpeg)')
            if path:
                self.image_path = path
                self.display_image()
                self.open_btn.setText("打开新图片")
                self.status_bar_text.setText(f"已加载: {os.path.basename(path)}")
        except Exception as e:
            self.show_error_message(f"加载失败: {str(e)}")

    def show_error_message(self, text):
        InfoBar.error(
            title='错误',
            content=text,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )
        self.status_bar_text.setText(text)

    # ========== UI事件与参数 ==========
    def toggle_aspect_lock(self, state):
        if self.crop_rect:
            self.crop_rect.locked = (state == Qt.Checked)
            if state == Qt.Checked:
                self.crop_rect.updateAspectRatio(self._normalize_ratio_text(self.ratio_edit.text()))
                self.crop_rect.rows = self.rows_spin.value()
                self.crop_rect.cols = self.cols_spin.value()

    def update_aspect_ratio(self):
        if self.lock_check.isChecked() and self.crop_rect:
            clean_ratio = self._normalize_ratio_text(self.ratio_edit.text())
            self.ratio_edit.setText(clean_ratio)
            self.crop_rect.updateAspectRatio(clean_ratio)
            self.crop_rect.rows = self.rows_spin.value()
            self.crop_rect.cols = self.cols_spin.value()

    def on_grid_param_changed(self, *args):
        if not self.crop_rect:
            return
            
        self.crop_rect.rows = self.rows_spin.value()
        self.crop_rect.cols = self.cols_spin.value()
        if self.lock_check.isChecked() and self.crop_rect:
            self.crop_rect.updateAspectRatio(self._normalize_ratio_text(self.ratio_edit.text()))
            self.resize_crop_rect_to_fit()
        self.overlay_manager.update_grid_lines()

    def update_brightness(self):
        self.darken_factor = self.brightness_slider.value() / 100
        self.overlay_manager.update_brightness()

    def show_real_area(self):
        self.overlay_manager.show_real_area()

    def pil2qpixmap(self, img):
        img = img.convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        w, h = img.size
        qimg = QImage(data, w, h, w*4, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
        return pixmap
        
    def _really_clear_scene(self):
        self.overlay_manager.clear_existing_overlays()
        try:
            if self.crop_rect:
                self.crop_rect.disconnect_all_signals()
        except Exception:
            pass
        self.scene.clear()
        self.crop_rect = None
        self.pixmap_item = None
        
    def display_image(self):
        self._really_clear_scene()
        try:
            if not self.image_path:
                return
                
            img = Image.open(self.image_path)
            pixmap = self.pil2qpixmap(img)
            self.pixmap_item = self.scene.addPixmap(pixmap)
            self.pixmap_item.setFlag(self.pixmap_item.ItemIsMovable, False)
            self.scene.setSceneRect(self.pixmap_item.boundingRect())
            self.init_crop_rect()
            self.overlay_manager.create_overlay()
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.resize_crop_rect_to_fit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_error_message(f"图片加载失败: {str(e)}")    

    def init_crop_rect(self):
        if self.crop_rect:
            try:
                self.crop_rect.disconnect_all_signals()
            except Exception:
                pass
            self.scene.removeItem(self.crop_rect)
            self.crop_rect = None
            
        rows = self.rows_spin.value() if hasattr(self, "rows_spin") else 1
        cols = self.cols_spin.value() if hasattr(self, "cols_spin") else 1
        self.crop_rect = AspectRatioRectItem(self.scene.sceneRect(), rows=rows, cols=cols)
        self.crop_rect.rectChanged.connect(self.on_crop_rect_changed)
        self.scene.addItem(self.crop_rect)
        self.resize_crop_rect_to_fit()

    def on_crop_rect_changed(self):
        self.overlay_manager.update_overlay()
        self.overlay_manager.update_grid_lines()
        if self.crop_rect:
            self.crop_rect.rows = self.rows_spin.value()
            self.crop_rect.cols = self.cols_spin.value()

    def resize_crop_rect_to_fit(self):
        if not self.crop_rect or not self.pixmap_item:
            return
            
        rows = max(1, self.rows_spin.value())
        cols = max(1, self.cols_spin.value())
        ratio_text = self._normalize_ratio_text(self.ratio_edit.text())
        if ":" not in ratio_text:
            return
            
        try:
            rw, rh = [float(x) for x in ratio_text.split(":")]
            cell_ratio = rw / rh
        except Exception:
            return
            
        overall_ratio = (cols / rows) * cell_ratio
        img_rect = self.pixmap_item.boundingRect()
        img_w = img_rect.width()
        img_h = img_rect.height()
        tar_w = img_w * 0.65
        tar_h = tar_w / overall_ratio
        if tar_h > img_h:
            tar_h = img_h * 0.65
            tar_w = tar_h * overall_ratio
            
        center = img_rect.center()
        rect = QRectF(center.x() - tar_w/2, center.y() - tar_h/2, tar_w, tar_h)
        if rect.left() < img_rect.left():
            rect.moveLeft(img_rect.left())
        if rect.right() > img_rect.right():
            rect.moveRight(img_rect.right())
        if rect.top() < img_rect.top():
            rect.moveTop(img_rect.top())
        if rect.bottom() > img_rect.bottom():
            rect.moveBottom(img_rect.bottom())
            
        self.crop_rect.setRect(rect)
        self.crop_rect.rows = rows
        self.crop_rect.cols = cols
        self.crop_rect.aspect_ratio = cell_ratio

    def save_cropped(self):
        try:
            if not self.image_path or not self.crop_rect or not self.pixmap_item:
                return

            image_rect = self.pixmap_item.boundingRect()
            crop_rect = self.crop_rect.mapRectToItem(self.pixmap_item, self.crop_rect.rect)
            actual_rect = QRectF(
                max(0, crop_rect.left()),
                max(0, crop_rect.top()),
                min(image_rect.width(), crop_rect.width()),
                min(image_rect.height(), crop_rect.height())
            ).toRect()
            
            img = Image.open(self.image_path)
            rows = self.rows_spin.value()
            cols = self.cols_spin.value()
            cell_w = actual_rect.width() // cols
            cell_h = actual_rect.height() // rows
            output_num = rows * cols
            output_cnt = 0
            
            save_dir = QFileDialog.getExistingDirectory(self, '选择保存目录')
            if save_dir:
                base_name = os.path.splitext(os.path.basename(self.image_path))[0]
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                saved_files = []

                # 进度条
                # 进度条更新异常
                # todo：修复
                # progress_info_bar = InfoBar(
                #     InfoBarIcon.INFORMATION,
                #     title='导出进度',
                #     content='正在导出图片...',
                #     orient=Qt.Horizontal,
                #     isClosable=False,
                #     position=InfoBarPosition.TOP,
                #     duration=-1,
                #     parent=self
                # )
                # progress_bar = ProgressBar()
                # progress_info_bar.addWidget(progress_bar)
                # progress_bar.setMinimum(0)
                # progress_bar.setMaximum(output_num)
                # progress_bar.setValue(0)
                # progress_info_bar.show()
                

                # 构建overlay并定位
                view_geo = self.view.geometry()
                overlay_w, overlay_h = 460, 100
                center_x = view_geo.width() // 2 - overlay_w // 2
                y_posit = int(view_geo.height() * 0.3)
                self.progress_overlay.setGeometry(center_x, y_posit, overlay_w, overlay_h)
                self.progress_overlay.show()

                # 清空旧内容
                for i in reversed(range(self.progress_overlay.layout().count())):
                    w = self.progress_overlay.layout().itemAt(i).widget()
                    if w: w.deleteLater()

                progress_info_bar = InfoBar(
                    InfoBarIcon.INFORMATION,
                    title='导出进度',
                    content='正在导出图片...',
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    duration=-1,
                    parent=self.progress_overlay
                )
                # 进度条更新异常
                # todo：修复
                # progress_bar = ProgressBar(self.progress_overlay)
                # progress_info_bar.addWidget(progress_bar)
                # progress_bar.setMinimum(0)
                # progress_bar.setMaximum(output_num)
                # progress_bar.setValue(0)
                # self.progress_overlay.layout().addWidget(progress_info_bar)
                progress_info_bar.show()



                for i in range(rows):
                    for j in range(cols):
                        output_cnt += 1
                        area = (
                            actual_rect.x() + j * cell_w,
                            actual_rect.y() + i * cell_h,
                            actual_rect.x() + (j+1) * cell_w,
                            actual_rect.y() + (i+1) * cell_h
                        )
                        cropped = img.crop(area)
                        fn = f"{base_name}_{i}_{j}_{timestamp}.png"
                        save_path = os.path.join(save_dir, fn)
                        cropped.save(save_path)
                        saved_files.append(save_path)
                        
                        # # 更新进度
                        # progress_bar.setValue(output_cnt)
                        # progress_bar.repaint()
                        
                        progress_info_bar.contentLabel.setText(f"正在导出第 {output_cnt} 张，总计 {output_num} 张")
                        #底部状态框
                        self.status_bar_text.setText(f"正在导出第 {output_cnt} 张，总计 {output_num} 张")
                        QApplication.processEvents()

                # 关闭进度条
                progress_info_bar.close()
                
                # 显示完成通知
                InfoBar.success(
                    title='导出完成',
                    content=f'成功导出 {output_num} 张图片',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                self.status_bar_text.setText(f"导出完成，总计 {output_num} 张，保存到: {save_dir}")
                
                # 显示导出结果对话框
                self.show_export_dialog(saved_files, save_dir)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_error_message(f"导出失败: {str(e)}")

    def show_export_dialog(self, saved_files, save_dir=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("导出结果")
        dlg.setMinimumWidth(400)
        
        v_layout = QVBoxLayout(dlg)
        v_layout.setContentsMargins(20, 20, 20, 20)
        v_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("<b>导出完成</b>")
        title_label.setStyleSheet("font-size: 14pt;")
        v_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        # 文件计数
        count_label = QLabel(f"已导出 {len(saved_files)} 个文件")
        v_layout.addWidget(count_label, alignment=Qt.AlignCenter)
        
        # 文件名列表
        scroll_area = QWidget()
        scroll_layout = QVBoxLayout(scroll_area)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        export_names = [os.path.basename(f) for f in saved_files]
        for name in export_names:
            file_label = QLabel(name)
            file_label.setStyleSheet("padding: 3px;")
            scroll_layout.addWidget(file_label)
            
        scroll_layout.addStretch(1)
        
        # 存放路径
        path_label = QLabel(f"保存位置: {save_dir}")
        path_label.setStyleSheet("font-size: 10pt; color: #666;")
        v_layout.addWidget(path_label)
        
        # 下方按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_view = PrimaryPushButton("查看导出")
        btn_view.setFixedWidth(120)
        btn_view.clicked.connect(lambda: self.open_folder_with_explorer(save_dir))
        
        btn_ok = PushButton("完成")
        btn_ok.setFixedWidth(120)
        btn_ok.clicked.connect(dlg.accept)
        
        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_view)
        btn_layout.addWidget(btn_ok)
        btn_layout.addStretch(1)
        
        v_layout.addLayout(btn_layout)
        dlg.exec_()

    def _safe_clear_scene_after_export(self):
        try:
            if self.crop_rect:
                self.crop_rect.disconnect_all_signals()
        except Exception:
            pass
        self.scene.clear()
        self.crop_rect = None
        self.pixmap_item = None

    def open_folder_with_explorer(self, path):
        path = os.path.normpath(path)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

