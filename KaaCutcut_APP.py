import sys
import os
import platform
import ctypes
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
# import PyQt5.QtCore

from main_window import ImageCropper
# QFluentWidgets主窗口基类和控件
from qfluentwidgets import (
    # FluentWindow, FluentIcon, PushButton, SpinBox, LineEdit, CheckBox, Slider,
    setTheme, Theme, # InfoBar, InfoBarPosition, setFont
)

myappid = "AppID.KaaCutcut_Datooo.v.1.1"  # 自定义唯一标识符



def resource_path(relative_path):
    try:
        # PyInstaller 在打包后会把资源放在 _MEIPASS 路径下
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



if __name__ == '__main__':
 
    try:
        import pyi_splash
        pyi_splash.close() 
    except ImportError:
        pass 
    try:        
        app = QApplication(sys.argv)
        if platform.system() == "Windows":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        icon_path = resource_path("icon/KaaCutcut.ico")
        app.setWindowIcon(QIcon(icon_path))  # 设置任务栏和可执行文件图标
        #setFont(app, "微软雅黑" if platform.system() == "Windows" else "Arial", 12)  # 12是字号，根据需要设定
        setTheme(Theme.LIGHT)  # LIGHT/ DARK/ AUTO
        print('2. 创建 ImageCropper 主窗口')
        window = ImageCropper()
        window.setWindowIcon(QIcon(icon_path))  # 设置任务栏和可执行文件图标

        # default_path = "./DSC06152.JPG"
        # if os.path.exists(default_path):
        #     print('4. 显示调试照片')
        #     window.image_path = default_path
        #     window.display_image()
        # print('5. 主窗口 show 完毕，进入主循环')
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        print(traceback.format_exc())