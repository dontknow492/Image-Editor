from PySide6.QtWidgets import QApplication, QSlider, QWidget, QVBoxLayout, QLabel, QStyleOptionSlider, QStyle
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QRadialGradient, QMouseEvent


# from PyQt5.QtWidgets import QSlider
# from PyQt5.QtCore import QRect, Qt, QPoint
# from PyQt5.QtGui import QPainter, QColor, QPen,


class CenteredSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setRange(-100, 100)
        # self.setValue(0)  # Start at center
        self.setMinimumHeight(40)
        self._handler_inside_radius = 3
        # Optional: Remove default styling for a cleaner custom look
        self.setStyleSheet("QSlider { background: transparent; }")

        # super().enterEvent(event)

    # self.update()

    def enterEvent(self, event, /):
        self._handler_inside_radius = 5
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event, /):
        self._handler_inside_radius = 3
        self.update()
        super().leaveEvent(event)

    def wheelEvent(self, event):
        event.ignore()

    def paintEvent(self, event):
        max_range = self.maximum()
        min_range = self.minimum()

        center_value =  int((max_range + min_range) / 2)

        # print(f"Max: {max_range}, Min: {min_range}, Center: {center_value}, Current: {self.value()}")

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Slider geometry
        rect = self.rect()
        groove_height = 4
        groove_rect = QRect(10, (rect.height() - groove_height) // 2, rect.width() - 20, groove_height)

        # Colors
        groove_color = QColor(200, 200, 200)  # Lighter gray groove
        handle_color = QColor(80, 80, 80)  # Slightly lighter handle
        slider_color = QColor("#42A5F5")
        handle_color_inside = QColor("#2196F3")

        # Draw groove
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(groove_color)
        painter.drawRoundedRect(groove_rect, 1, 1)

        # Draw center line
        center_x = rect.width() // 2
        painter.setPen(QPen(QColor(120, 120, 120), 1))
        painter.drawLine(center_x, groove_rect.y() - 10, center_x, groove_rect.y() + groove_rect.height() + 10)

        # Draw fill based on value
        painter.setPen(Qt.PenStyle.NoPen) #no outline 
        slider_pos = self.value()- center_value
        handle_x = self._value_to_position(slider_pos)
        center_x = self._value_to_position(0)  # Center at value 0

        # print(f"Handle_x pos: {handle_x}, Center_x: {center_x}")
        painter.setBrush(slider_color)
        if slider_pos < center_value:
            rect = QRect(handle_x, groove_rect.y(), center_x - handle_x, groove_rect.height())
        elif slider_pos >= center_value:
            rect = QRect(center_x, groove_rect.y(), handle_x - center_x, groove_rect.height())

        painter.drawRoundedRect(rect, 1, 1)
        # print(f"Rect: {rect.width(), rect.height(), rect.x(), rect.y()}")

        # Draw handle
        handle_radius = 7
        painter.setBrush(handle_color)
        painter.drawEllipse(handle_x - handle_radius, groove_rect.y() + (groove_height - 2 * handle_radius) // 2,
                            2 * handle_radius, 2 * handle_radius)

        # #draw handle inside
        handle_radius_inside = self._handler_inside_radius
        painter.setBrush(handle_color_inside)
        painter.drawEllipse(handle_x - handle_radius_inside, groove_rect.y() + (groove_height - 2 * handle_radius_inside) // 2,
                            2 * handle_radius_inside, 2 * handle_radius_inside)

        painter.end()

    def _value_to_position(self, value):
        """Maps slider value (min to max) to x-coordinate."""
        rect = self.rect()
        total =  rect.width() - 20  # Total width minus padding
        diff = self.maximum() - self.minimum()
        inc = int(diff/2)
        return int((value + inc) / diff * (rect.width() - 20)) + 10


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Centered Slider")

        # Slider
        self.slider = CenteredSlider(Qt.Horizontal)
        self.slider.setMinimum(-100)
        self.slider.setMaximum(100)
        self.slider.setValue(10)
        # self.slider.setValue(0)

        # Label
        self.label = QLabel("Value: 0", self)
        self.slider.valueChanged.connect(lambda v: self.label.setText(f"Value: {v}"))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
