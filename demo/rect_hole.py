from PySide6.QtWidgets import QGraphicsItem, QGraphicsView, QGraphicsScene, QApplication
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen


class RectangleWithHole(QGraphicsItem):
    def __init__(self, outer_rect, inner_rect, color=Qt.blue):
        super().__init__()
        if isinstance(outer_rect, tuple):
            outer_rect = QRectF(*outer_rect)
        if isinstance(inner_rect, tuple):
            inner_rect = QRectF(*inner_rect)
        self.outer_rect = outer_rect  # Outer rectangle (main shape)
        self.inner_rect = inner_rect  # Inner rectangle (the hole)
        self.color = QColor(color)

    def boundingRect(self):
        # Return the bounding rectangle of the outer shape
        return self.outer_rect

    def paint(self, painter, option, widget=None):
        # Set the fill color
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)

        # Draw the outer rectangle
        painter.drawRect(self.outer_rect)

        # Draw the inner rectangle (hole) by using the even-odd fill rule
        # or by using composition mode to clear that area
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.drawRect(self.inner_rect)

        # Alternative method using path with even-odd fill rule:
        # path = QPainterPath()
        # path.addRect(self.outer_rect)
        # path.addRect(self.inner_rect)
        # painter.setBrush(QBrush(self.color))
        # painter.drawPath(path)


# Example usage
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    scene = QGraphicsScene()
    view = QGraphicsView(scene)

    # Create a rectangle with a hole
    outer_rect = (0, 0, 200, 150)  # x, y, width, height
    inner_rect = (50, 50, 100, 50)
    color = QColor(0, 0, 0, 150)
    # hole position and size
    view.setSceneRect(0, 0, 300, 200)
    scene.update()
    print(view.sceneRect())

    item = RectangleWithHole((0, 0, 300, 200), inner_rect, color)

    scene.addItem(item)


    view.show()

    sys.exit(app.exec())