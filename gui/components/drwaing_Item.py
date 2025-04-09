from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QCursor, QIcon, QBrush, QFont, QFocusEvent, QMouseEvent
from PySide6.QtCore import Qt, QPoint, QRectF, QPointF
from enum import Enum
from typing import Union
import logging

from qfluentwidgets import FluentIcon

from gui.components.draw import DrawWidget

logger = logging.getLogger(__name__)







class DrawingScene(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DrawingView")

        # Setup scene
        self.scene_stack = list()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Initialize drawing components
        self.draw_option = DrawWidget(self)
        self.draw_option.adjustSize()

        self.draw_mode = DrawMode.Move
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.brush_size: int = 4
        self.eraser_size: int = 10
        self.marker_size: int = 10
        self.last_point: Union[QPoint, None] = None
        self.is_drawing: bool = False

        self.color = QColor("#FF0000")

        # Create pixmap item for drawing
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)


        # Initialize drawing variables
        self._setup_drawing()
        self._draw_option_signal_handler()



        
    def resizeEvent(self, event):
        """Handle widget resizing"""
        super().resizeEvent(event)
        new_pixmap = QPixmap(self.size())
        new_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(new_pixmap)
        painter.drawPixmap(0, 0, self.draw_pixmap)
        painter.end()
        self.draw_pixmap = new_pixmap
        self.pixmap_item.setPixmap(self.draw_pixmap)

        # Center the draw options
        self.draw_option.move(
            (self.width() - self.draw_option.width()) // 2,
            self.height() - self.draw_option.height() - 10
        )

        # Update scene rect
        self.scene.setSceneRect(QRectF(self.rect()))



if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = DrawingView()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())