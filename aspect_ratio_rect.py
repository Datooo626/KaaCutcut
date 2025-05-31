from PyQt5.QtWidgets import QGraphicsObject, QGraphicsItem, QMessageBox
from PyQt5.QtGui import QPen #, QColor
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from constants import Qt

class AspectRatioRectItem(QGraphicsObject):
    rectChanged = pyqtSignal(QRectF)
    handleSize = 20.0
    handleMargin = 20.0 
    HANDLE_SIZE = handleMargin

    handleCursors = {
        Qt.TopLeftCorner: Qt.SizeFDiagCursor,
        Qt.TopRightCorner: Qt.SizeBDiagCursor,
        Qt.BottomLeftCorner: Qt.SizeBDiagCursor,
        Qt.BottomRightCorner: Qt.SizeFDiagCursor,
        Qt.MidLeftHandle: Qt.SizeHorCursor,
        Qt.MidRightHandle: Qt.SizeHorCursor,
        Qt.MidTopHandle: Qt.SizeVerCursor,
        Qt.MidBottomHandle: Qt.SizeVerCursor,
        Qt.LeftEdge: Qt.SizeHorCursor,
        Qt.RightEdge: Qt.SizeHorCursor,
        Qt.TopEdge: Qt.SizeVerCursor,
        Qt.BottomEdge: Qt.SizeVerCursor
    }

    def __init__(self, scene_rect, aspect_ratio=None, rows=1, cols=1):
        super().__init__()
        self._rect = QRectF()
        self._signal_connections = []
        self.scene_rect = scene_rect
        self.aspect_ratio = aspect_ratio
        self.locked = False
        self.mousePressPos = None
        self.mousePressRect = None
        self.handleSelected = None
        self.view_scale = 1.0
        self.draw_handles = {}
        self.visual_handles = {}

        self.rows = rows
        self.cols = cols

        self._rect = QRectF(
            scene_rect.center().x() - scene_rect.width()/4,
            scene_rect.center().y() - scene_rect.height()/4,
            scene_rect.width()/2,
            scene_rect.height()/2
        )

        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)        
        self.updateHandles()

    # 修改析构方法，析构时断开信号
    def __del__(self):
        print("AspectRatioRectItem 被析构，断开信号链")
        self.disconnect_all_signals()
        
    # 新增安全断开方法
    def disconnect_all_signals(self):
        # 如果以后有外部信号连接的槽，也在这里统一断开
        try:
            self.rectChanged.disconnect()
        except Exception:
            pass

    def get_handle_at(self, pos):
        r = self.rect
        x0, y0 = r.left(), r.top()
        x1, y1 = r.right(), r.bottom()
        cx, cy = r.center().x(), r.center().y()
        handles = {
            'TopLeft':     QPointF(x0, y0),
            'Top':         QPointF(cx, y0),
            'TopRight':    QPointF(x1, y0),
            'Right':       QPointF(x1, cy),
            'BottomRight': QPointF(x1, y1),
            'Bottom':      QPointF(cx, y1),
            'BottomLeft':  QPointF(x0, y1),
            'Left':        QPointF(x0, cy),
        }
        for name, point in handles.items():
            rect = QRectF(point.x() - self.HANDLE_SIZE/2, point.y() - self.HANDLE_SIZE/2,
                          self.HANDLE_SIZE, self.HANDLE_SIZE)
            if rect.contains(pos):
                return name
        return None

    def hoverMoveEvent(self, event):
        handle = self.handleAt(event.pos())
        cursor = self.handleCursors.get(handle, Qt.ArrowCursor)
        if handle == "body":
            cursor = Qt.SizeAllCursor
        self.setCursor(cursor)
        super().hoverMoveEvent(event)

    def updateHandles(self):
        s = self.handleSize
        m = self.handleMargin
        rect = self.rect
        left = rect.left()
        top = rect.top()
        width = rect.width()
        height = rect.height()
        right = left + width
        bottom = top + height
        center_x = left + width / 2
        center_y = top + height / 2

        self.draw_handles = {
            Qt.TopLeftCorner:     QRectF(left-m, top-m, s+2*m, s+2*m),
            Qt.TopRightCorner:    QRectF(right-s-m, top-m, s+2*m, s+2*m),
            Qt.BottomLeftCorner:  QRectF(left-m, bottom-s-m, s+2*m, s+2*m),
            Qt.BottomRightCorner: QRectF(right-s-m, bottom-s-m, s+2*m, s+2*m),
            Qt.MidLeftHandle:     QRectF(left-m, center_y-s/2-m, s+2*m, s+2*m),
            Qt.MidRightHandle:    QRectF(right-s-m, center_y-s/2-m, s+2*m, s+2*m),
            Qt.MidTopHandle:      QRectF(center_x-s/2-m, top-m, s+2*m, s+2*m),
            Qt.MidBottomHandle:   QRectF(center_x-s/2-m, bottom-s-m, s+2*m, s+2*m),
        }
        self.visual_handles = {
            k: QRectF(v.x()+m, v.y()+m, s, s) for k,v in self.draw_handles.items()
            if k in (Qt.TopLeftCorner, Qt.TopRightCorner, Qt.BottomLeftCorner, Qt.BottomRightCorner,
                    Qt.MidLeftHandle, Qt.MidRightHandle, Qt.MidTopHandle, Qt.MidBottomHandle)
        }

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.cyan, 2, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)  
        painter.drawRect(self.rect)
        painter.setBrush(Qt.white)
        painter.setPen(QPen(Qt.darkCyan, 1.5))
        for rect in self.visual_handles.values():
            painter.drawRect(rect)

    def boundingRect(self):
        return self.scene().sceneRect()

    def handleAt(self, pos):
        r = self.rect
        corner_margin_x,corner_margin_y = r.width()*0.02,r.height()*0.02
        corners = [
            (Qt.TopLeftCorner,     QRectF(r.left() - corner_margin_x, r.top() - corner_margin_y, corner_margin_x * 2, corner_margin_y * 2)),
            (Qt.TopRightCorner,    QRectF(r.right() - corner_margin_x, r.top() - corner_margin_y, corner_margin_x * 2, corner_margin_y * 2)),
            (Qt.BottomLeftCorner,  QRectF(r.left() - corner_margin_x, r.bottom() - corner_margin_y, corner_margin_x * 2, corner_margin_y * 2)),
            (Qt.BottomRightCorner, QRectF(r.right() - corner_margin_x, r.bottom() - corner_margin_y, corner_margin_x * 2, corner_margin_y * 2)),
        ]
        for handle, rect in corners:
            if rect.contains(pos):
                return handle
        width, height = r.width(), r.height()
        left_margin = right_margin = width * 0.02
        top_margin = bottom_margin = height * 0.02
        x, y = pos.x(), pos.y()
        if (r.left() - left_margin <= x <= r.left() + left_margin and r.top() + top_margin < y < r.bottom() - bottom_margin):
            return Qt.LeftEdge
        if (r.right() - right_margin <= x <= r.right() + right_margin and r.top() + top_margin < y < r.bottom() - bottom_margin):
            return Qt.RightEdge
        if (r.top() - top_margin <= y <= r.top() + top_margin and r.left() + left_margin < x < r.right() - right_margin):
            return Qt.TopEdge
        if (r.bottom() - bottom_margin <= y <= r.bottom() + bottom_margin and r.left() + left_margin < x < r.right() - right_margin):
            return Qt.BottomEdge
        if r.contains(pos):
            return "body"
        return None

    @property
    def rect(self):
        return self._rect

    def setRect(self, rect):
        img_rect = self.scene_rect
        min_w = img_rect.width() * 0.05
        min_h = img_rect.height() * 0.05
        if rect.width() < min_w:
            c = rect.center()
            rect.setLeft(c.x() - min_w/2)
            rect.setRight(c.x() + min_w/2)
        if rect.height() < min_h:
            c = rect.center()
            rect.setTop(c.y() - min_h/2)
            rect.setBottom(c.y() + min_h/2)
        left, right = min(rect.left(), rect.right()), max(rect.left(), rect.right())
        top, bottom = min(rect.top(), rect.bottom()), max(rect.top(), rect.bottom())
        rect = QRectF(QPointF(left, top), QPointF(right, bottom))
        self.prepareGeometryChange()
        self._rect = rect
        self.updateHandles()
        self.update()
        self.rectChanged.emit(self.rect)

    def mousePressEvent(self, event):
        self.handleSelected = self.handleAt(event.pos())
        if self.handleSelected:
            view = self.scene().views()[0]
            self.mousePressPos = event.pos()
            self.mousePressRect = self.rect
            self.view_transform = view.transform()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.handleSelected and self.mousePressPos:
            delta = self.getDelta(event)
            if self.handleSelected == "body":
                new_rect = QRectF(self.mousePressRect)
                new_rect.moveTopLeft(self.mousePressRect.topLeft() + delta)
                img_rect = self.scene_rect
                if new_rect.left() < img_rect.left():
                    new_rect.moveLeft(img_rect.left())
                if new_rect.right() > img_rect.right():
                    new_rect.moveRight(img_rect.right())
                if new_rect.top() < img_rect.top():
                    new_rect.moveTop(img_rect.top())
                if new_rect.bottom() > img_rect.bottom():
                    new_rect.moveBottom(img_rect.bottom())
                self.setRect(new_rect)
            else:
                new_rect = self.calcNewRectByHandle(delta)
                if self.locked and self.aspect_ratio:
                    new_rect = self.adjustRectForBlockAspect(new_rect, self.rows, self.cols, self.handleSelected, self.aspect_ratio)
                self.setRect(new_rect)
            event.accept()
        else:
            event.ignore()

    def getDelta(self, event):
        view = self.scene().views()[0]
        cur_trans = view.transform()
        dx = (event.pos().x() - self.mousePressPos.x()) * (self.view_transform.m11() / cur_trans.m11())
        dy = (event.pos().y() - self.mousePressPos.y()) * (self.view_transform.m22() / cur_trans.m22())
        return QPointF(dx, dy)

    def calcNewRectByHandle(self, delta):
        new_rect = QRectF(self.mousePressRect)
        scene_rect = self.scene().sceneRect()
        dx, dy = delta.x(), delta.y()
        if self.handleSelected in (Qt.LeftEdge, Qt.TopLeftCorner, Qt.BottomLeftCorner, Qt.MidLeftHandle):
            new_left = max(scene_rect.left(), self.mousePressRect.left() + dx)
            new_rect.setLeft(new_left)
        if self.handleSelected in (Qt.RightEdge, Qt.TopRightCorner, Qt.BottomRightCorner, Qt.MidRightHandle):
            new_right = min(scene_rect.right(), self.mousePressRect.right() + dx)
            new_rect.setRight(new_right)
        if self.handleSelected in (Qt.TopEdge, Qt.TopLeftCorner, Qt.TopRightCorner, Qt.MidTopHandle):
            new_top = max(scene_rect.top(), self.mousePressRect.top() + dy)
            new_rect.setTop(new_top)
        if self.handleSelected in (Qt.BottomEdge, Qt.BottomLeftCorner, Qt.BottomRightCorner, Qt.MidBottomHandle):
            new_bottom = min(scene_rect.bottom(), self.mousePressRect.bottom() + dy)
            new_rect.setBottom(new_bottom)
        return new_rect

    def adjustRectForBlockAspect(self, new_rect, rows, cols, handle, aspect_ratio):
        if rows < 1: rows = 1
        if cols < 1: cols = 1
        block_target_ratio = aspect_ratio
        overall_target_ratio = (cols / rows) * block_target_ratio
        wr = new_rect.width()
        hr = new_rect.height()
        cur_ratio = wr / hr if hr>0 else 1
        scene_rect = self.scene().sceneRect()
        rect = QRectF(new_rect)
        if cur_ratio > overall_target_ratio + 1e-8:
            nw = hr * overall_target_ratio
            if handle in (Qt.LeftEdge, Qt.TopLeftCorner, Qt.BottomLeftCorner):
                rect.setLeft(rect.right() - nw)
            else:
                rect.setRight(rect.left() + nw)
        else:
            nh = wr / overall_target_ratio
            if handle in (Qt.TopEdge, Qt.TopLeftCorner, Qt.TopRightCorner):
                rect.setTop(rect.bottom() - nh)
            else:
                rect.setBottom(rect.top() + nh)
        return rect

    def mouseReleaseEvent(self, event):
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        event.accept()
        
    def updateAspectRatio(self, ratio):
        if ratio and ":" in ratio:
            try:
                w, h = map(float, ratio.split(":"))
                self.aspect_ratio = w / h
                self.adjustToAspectRatio()
            except:
                QMessageBox.warning(None, "错误", "无效的长宽比格式，请使用'宽度:高度'格式")

    def adjustToAspectRatio(self):
        if not self.aspect_ratio:
            return
        current_rect = self.rect
        new_width = current_rect.height() * self.aspect_ratio
        new_height = current_rect.width() / self.aspect_ratio
        center = current_rect.center()
        if new_width > current_rect.width():
            self.setRect(QRectF(
                center.x() - new_width/2,
                current_rect.top(),
                new_width,
                current_rect.height()
            ))
        else:
            self.setRect(QRectF(
                current_rect.left(),
                center.y() - new_height/2,
                current_rect.width(),
                new_height
            ))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.rectChanged.emit(self.rect)
        return super().itemChange(change, value)