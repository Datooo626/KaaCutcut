# KaaCutcut 咔咔切 
![KaaCutcut_icon](./icon/KaaCutcut.png)
## 介绍

​	**一键实现图片无缝裁切自由**  

​			Github发布链接：[点击下载预编译文件](https://github.com/Datooo626/KaaCutcut/releases)

​			项目主页：[Github-KaaCutcut](https://github.com/Datooo626/KaaCutcut)

​	KaaCutcut 咔咔切是一款简单易用的图片裁剪工具，帮助您快速实现图片任意比例任意数量的自由裁切。

​	摸鱼无聊，写点bug吧。第一次写带界面的bug，图片切割核心代码20行、花2h加上UI，又花了2天+2天+2天+2天...修bug...关键是还没修完...一行api能解决的事，被ui折腾累了，先这样吧。

​	在小红书发布3：4的图片时，可以实现相邻图的“无缝切换”效果。对于切成2张图，可以先切成6：4，然后再选3：4，划到最左切一张再划到最右切一张来实现。对于想切成3份及以上的，就很考验操作精度了，帕金森患者表示放弃，懒癌表示PS不值当，那就用代码解决吧。



### 摸鱼成果：

20250530: v1.1.0

- 简单直观的裁剪界面
- 支持JPG、JPEG、PNG
- 拖拽式交互，软件页面和图片可自由缩放
- 实时预览裁剪区域，与背景反差度可调
- 可锁定**“子图片”**的宽高比例
- 一键保存裁剪结果，输出文件以<原文件名-行-列-导出时的年月日时分秒.png>命名

20250525: v1.0

- 完成图片分割函数功能验证

### 摸鱼指南：

1. 点击'打开图片'按钮选择图片
2. 调整分割数量、设置是否锁定子图像比例
3. 在图片上拖动选择裁剪区域，调整裁剪框大小和位置
4. 使用'保存'按钮保存结果

### 摸鱼计划：

- **解决已知bug：**

  - 部分UI未居中、页面布局凌乱，小尺寸缩放时菜单重叠...

  - 剪裁框的上/左边框拖拽功能异常，裁剪框左上、左中、上中吸附点功能异常。

  - 导出进度条更新异常。

  - 添加强制约束来保证严格的比例锁定：当前是依靠计算精度来保证比例锁定，在缩放和图层映射计算时存在小数，理论上可能会导致子图像边缘存在1个像素的偏差或重叠。

    ...

- **添加更多bug:**

  - 添加剪裁框复位按钮，目前剪裁框拖到最大之后就不好选中了

  - 支持多种图片导出格式

  - 给比例锁定功能添加选项：自由/裁切比例锁定/子图比例锁定

  - 添加强制约束来保证严格的比例锁定

  - 自由比例时，实时输出当前剪裁比例（显示最小整数比？还是1：xx.xxx ?）

  - live图的无缝裁切？
  
  - ios：HEIC+H265的mov ？
    - android：[动态照片格式规范1.0](https://developer.android.com/media/platform/motion-photo-format?hl=zh-cn)

  - 切都切了，那拼图功能也加上吧？

  - 整合负片根据胶片参数的一键校色功能？
  
    ...

### 绝不空军：

- Datou：datouor@gmail.com  、https://github.com/Datooo626
- Deepseek：https://chat.deepseek.com/
- ChatGPT：https://chatgpt.com/



## 目录结构

~~~bash
KaaCutcut/
├─ KaaCutcut_APP.py         # 程序入口
├─ main_window.py           # ImageCropper主窗口
├─ graphics_view.py         # ResizableGraphicsView视图
├─ aspect_ratio_rect.py     # 裁剪区域 QGraphicsItem
├─ mask_item.py             # 遮罩层 Item
└─ constants.py             # 相关常量
~~~



### 开发环境

```bash
python：python-3.10.11
pyQt：5.15.11
PyQt-Fluent-Widgets[full]：1.8.1
pyinstaller：6.13.0
```





### 构建：

#### 1、创建干净的python环境到隐藏目录中

```bash
python -m venv --clear .venv
```

#### 2、使终端进入python环境

```bash
./.venv/Scripts/Activate
```

​		进入环境后，终端应当以环境名<(.venv)>开头，示例：

```bash
(.venv) PS C:\Users\UserName\KaaCutcut> 
```

​		**------若无特殊备注，后续命令默认在本环境中执行-----**

#### 3、安装所需库

```python
pip install PyQt5
pip install "PyQt-Fluent-Widgets[full]" -i https://pypi.org/simple/
pip install pyinstaller
```

安装示例：

```powershell
进入环境：
PS C:\Users\UserName\KaaCutcut> ./.venv/Scripts/Activate

安装PyQt5：
(.venv) PS C:\Users\UserName\KaaCutcut> pip install PyQt5
Collecting PyQt5
  Using cached PyQt5-5.15.11-cp38-abi3-win_amd64.whl (6.9 MB)
Collecting PyQt5-sip<13,>=12.15
  Using cached PyQt5_sip-12.17.0-cp310-cp310-win_amd64.whl (59 kB)
Collecting PyQt5-Qt5<5.16.0,>=5.15.2
  Using cached PyQt5_Qt5-5.15.2-py3-none-win_amd64.whl (50.1 MB)
Installing collected packages: PyQt5-Qt5, PyQt5-sip, PyQt5
Successfully installed PyQt5-5.15.11 PyQt5-Qt5-5.15.2 PyQt5-sip-12.17.0

安装PyQt-Fluent-Widgets：
(.venv) PS C:\Users\UserName\KaaCutcut> pip install "PyQt-Fluent-Widgets[full]" -i https://pypi.org/simple/
Looking in indexes: https://pypi.org/simple/
Collecting PyQt-Fluent-Widgets[full]
  Downloading pyqt_fluent_widgets-1.8.1-py3-none-any.whl.metadata (5.8 kB)
Requirement already satisfied: PyQt5>=5.15.0 in c:\users\UserName\KaaCutcut\.venv\lib\site-packages (from PyQt-Fluent-Widgets[full]) (5.15.11)
Collecting PyQt5-Frameless-Window>=0.4.0 (from PyQt-Fluent-Widgets[full])
  Downloading pyqt5_frameless_window-0.7.3-py3-none-any.whl.metadata (5.8 kB)
Collecting darkdetect (from PyQt-Fluent-Widgets[full])
  Downloading darkdetect-0.8.0-py3-none-any.whl.metadata (3.6 kB)
Collecting scipy (from PyQt-Fluent-Widgets[full])
  Downloading scipy-1.15.3-cp310-cp310-win_amd64.whl.metadata (60 kB)
Collecting pillow (from PyQt-Fluent-Widgets[full])
  Downloading pillow-11.2.1-cp310-cp310-win_amd64.whl.metadata (9.1 kB)
Collecting colorthief (from PyQt-Fluent-Widgets[full])
  Downloading colorthief-0.2.1-py2.py3-none-any.whl.metadata (816 bytes)
Requirement already satisfied: PyQt5-sip<13,>=12.15 in c:\users\UserName\KaaCutcut\.venv\lib\site-packages (from PyQt5>=5.15.0->PyQt-Fluent-Widgets[full]) (12.17.0)
Requirement already satisfied: PyQt5-Qt5<5.16.0,>=5.15.2 in c:\users\UserName\KaaCutcut\.venv\lib\site-packages (from PyQt5>=5.15.0->PyQt-Fluent-Widgets[full]) (5.15.2)
Collecting pywin32 (from PyQt5-Frameless-Window>=0.4.0->PyQt-Fluent-Widgets[full])
  Downloading pywin32-310-cp310-cp310-win_amd64.whl.metadata (9.4 kB)
Collecting numpy<2.5,>=1.23.5 (from scipy->PyQt-Fluent-Widgets[full])
  Using cached numpy-2.2.6-cp310-cp310-win_amd64.whl.metadata (60 kB)
Downloading pyqt_fluent_widgets-1.8.1-py3-none-any.whl (1.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.7/1.7 MB 3.6 MB/s eta 0:00:00
Downloading pyqt5_frameless_window-0.7.3-py3-none-any.whl (40 kB)
Downloading colorthief-0.2.1-py2.py3-none-any.whl (6.1 kB)
Downloading darkdetect-0.8.0-py3-none-any.whl (9.0 kB)
Downloading pillow-11.2.1-cp310-cp310-win_amd64.whl (2.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.7/2.7 MB 5.9 MB/s eta 0:00:00
Downloading pywin32-310-cp310-cp310-win_amd64.whl (9.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 9.6/9.6 MB 8.9 MB/s eta 0:00:00
Downloading scipy-1.15.3-cp310-cp310-win_amd64.whl (41.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 41.3/41.3 MB 15.9 MB/s eta 0:00:00
Using cached numpy-2.2.6-cp310-cp310-win_amd64.whl (12.9 MB)
Installing collected packages: pywin32, PyQt5-Frameless-Window, pillow, numpy, darkdetect, scipy, PyQt-Fluent-Widgets, colorthief
Successfully installed PyQt-Fluent-Widgets-1.8.1 PyQt5-Frameless-Window-0.7.3 colorthief-0.2.1 darkdetect-0.8.0 numpy-2.2.6 pillow-11.2.1 pywin32-310 scipy-1.15.3

使用pyinstaller进行打包：
(.venv) PS C:\Users\UserName\KaaCutcut> pip install pyinstaller
Collecting pyinstaller
  Downloading pyinstaller-6.13.0-py3-none-win_amd64.whl.metadata (8.3 kB)
Requirement already satisfied: setuptools>=42.0.0 in c:\users\UserName\KaaCutcut\.venv\lib\site-packages (from pyinstaller) (65.5.0)
Collecting altgraph (from pyinstaller)
  Downloading altgraph-0.17.4-py2.py3-none-any.whl.metadata (7.3 kB)
Collecting pefile!=2024.8.26,>=2022.5.30 (from pyinstaller)
  Downloading pefile-2023.2.7-py3-none-any.whl.metadata (1.4 kB)
Collecting pywin32-ctypes>=0.2.1 (from pyinstaller)
  Downloading pywin32_ctypes-0.2.3-py3-none-any.whl.metadata (3.9 kB)
Collecting pyinstaller-hooks-contrib>=2025.2 (from pyinstaller)
  Downloading pyinstaller_hooks_contrib-2025.4-py3-none-any.whl.metadata (16 kB)
Collecting packaging>=22.0 (from pyinstaller)
  Downloading packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Downloading pyinstaller-6.13.0-py3-none-win_amd64.whl (1.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.4/1.4 MB 1.7 MB/s eta 0:00:00
Downloading packaging-25.0-py3-none-any.whl (66 kB)
Downloading pefile-2023.2.7-py3-none-any.whl (71 kB)
Downloading pyinstaller_hooks_contrib-2025.4-py3-none-any.whl (434 kB)
Downloading pywin32_ctypes-0.2.3-py3-none-any.whl (30 kB)
Downloading altgraph-0.17.4-py2.py3-none-any.whl (21 kB)
Installing collected packages: altgraph, pywin32-ctypes, pefile, packaging, pyinstaller-hooks-contrib, pyinstaller
Successfully installed altgraph-0.17.4 packaging-25.0 pefile-2023.2.7 pyinstaller-6.13.0 pyinstaller-hooks-contrib-2025.4 pywin32-ctypes-0.2.3

```

#### 4、运行

```
python .\KaaCutcut_APP.py
```

#### 5、打包：

```bash
pyinstaller -F -w --splash .\icon\KaaCutcut.png --add-data ".\icon;icon"  -i .\icon\KaaCutcut.ico  KaaCutcut_APP.py
```

​	执行该命令后，打包的同时会在同目录下生成xxxx.spec配置文件，可直接在配置文件中修改打包参数，后续可直接使用该配置文件打包：

```bash
pyinstaller KaaCutcut_APP.spec
```

​	**参数解释：**

```bash
-F 单文件模式。在打包完成后只会生成一个单独的exe文件,与之对应的是-D，打包成含exe和相关依赖资源的文件夹。
-w 打包程序运行后隐藏控制台窗口
--splash .\icon\KaaCutcut.png  添加启动过度动画，需在程序跑起来后通过pyi_splash.close() 手动关闭
--add-data ".\icon;icon"  将资源文件夹一起打包，.\icon是资源路径，icon是打包后的虚拟存储路径，使用分号分割，如果有多个文件夹，就继续添加--add-data ".\newDir;newDir"
-i .\icon\KaaCutcut.ico 设置打包后exe程序文件的图标
KaaCutcut_APP.py  程序入口
```

​	打包完成后，生成的可执行文件存放在同目录下的```\dist```文件夹中。

打包过程示例：

```bash
(.venv) PS C:\Users\UserName\KaaCutcut> pyinstaller -F -w --splash .\icon\KaaCutcut.png --add-data ".\icon;icon"  -i .\icon\KaaCutcut.ico  KaaCutcut_APP.py
313 INFO: PyInstaller: 6.13.0, contrib hooks: 2025.4
313 INFO: Python: 3.10.11
320 INFO: Platform: Windows-10-10.0.26200-SP0
320 INFO: Python environment:C:\Users\UserName\KaaCutcut\.venv
.....省略若干.........
32459 INFO: Copying icon to EXE
32463 INFO: Copying 0 resources to EXE
32463 INFO: Embedding manifest in EXE
33209 INFO: Appending PKG archive to EXE
33262 INFO: Fixing EXE headers
37280 INFO: Building EXE from EXE-00.toc completed successfully.
37284 INFO: Build complete! The results are available in: C:\Users\UserName\KaaCutcut\dist
```



## 资源链接：

[QFluentWidgets](https://qfluentwidgets.com/)





## 许可：

### MIT License



Copyright (c) 2025 Datooo



​	Permission is hereby granted, free of charge, to any person obtaining a copy

of this software and associated documentation files (the "Software"), to deal

in the Software without restriction, including without limitation the rights

to use, copy, modify, merge, publish, distribute, sublicense, and/or sell

copies of the Software, and to permit persons to whom the Software is

furnished to do so, subject to the following conditions:

​	The above copyright notice and this permission notice shall be included in all

copies or substantial portions of the Software.

​	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR

IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,

FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE

AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER

LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,

OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE

SOFTWARE.