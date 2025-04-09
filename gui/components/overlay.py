from PySide6.QtCore import QRectF, Qt, QSize
from PySide6.QtGui import QColor, QBrush, QPainterPath
from PySide6.QtWidgets import QGraphicsItem
from qfluentwidgets import StrongBodyLabel


class CropOverlay(QGraphicsItem):
    def __init__(self, outer_rect: QRectF | tuple, inner_rect: QRectF | tuple, color=QColor(0, 0, 0, 150)):

        super().__init__()
        if isinstance(outer_rect, tuple):
            outer_rect = QRectF(*outer_rect)
        if isinstance(inner_rect, tuple):
            inner_rect = QRectF(*inner_rect)
        self.outer_rect = outer_rect  # Outer rectangle (main shape)
        self.inner_rect = inner_rect  # Inner rectangle (the hole)
        self.color = QColor(color)
        self.setZValue(0)

    def boundingRect(self):
        return self.outer_rect.united(self.inner_rect)

    def setCropRect(self, rect: QRectF):
        self.inner_rect = rect
        self.update()

    def setOuterRect(self, rect: QRectF):
        self.outer_rect = rect
        self.update()

    def paint(self, painter, option, widget=None):
        path = QPainterPath()
        path.addRect(self.outer_rect)
        path.addRect(self.inner_rect)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)


class SizeOverlay(StrongBodyLabel):
    def __init__(self, size: QSize | None = None, parent=None):
        super().__init__(parent)
        if size:
            self.set_size(size)

    def set_size(self, size: QSize):
        text = f"{size.width()} x {size.height()}"
        self.setText(text)

    def get_size(self):
        text = self.text()
        width, height = text.split(" x ")
        return QSize(int(width), int(height))
