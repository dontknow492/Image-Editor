from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QPixmap, QPainter, QColor

from gui.common.myFrame import HorizontalFrame
from gui.common.flyout_button import FlyoutButton
from qfluentwidgets import  FluentIcon, ColorDialog, ColorPickerButton, Slider, SpinBox, SegmentedToolWidget
from utils.misc import create_transparent_tool_button
from utils.icon_manager import IconManager
from loguru import logger

class BrushSizeSlider(HorizontalFrame):
    def __init__(self, slider_range=(1, 50), default_value=10, parent=None):
        super().__init__(parent = parent)

        # Brush Preview
        self.brush_preview = QLabel(self)
        self.brush_preview.setFixedSize(50, 50)  # Smaller size for compact UI

        # Slider & Spinbox Container
        self.spin_box = SpinBox(self)
        self.spin_box.setRange(*slider_range)
        self.spin_box.setValue(default_value)

        self.slider = Slider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(*slider_range)
        self.slider.setValue(default_value)

        # Sync spinbox and slider
        self.slider.valueChanged.connect(self.spin_box.setValue)
        self.spin_box.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.update_brush_preview)

        # Add widgets to layout
        self.addWidget(self.spin_box)
        self.addWidget(self.slider)
        self.addWidget(self.brush_preview)

        # Initialize preview
        self.update_brush_preview(default_value)

    def update_brush_preview(self, size):
        """ Update the brush size preview based on slider value """
        pixmap = QPixmap(50, 50)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(0, 0, 0))  # Black brush preview
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(25 - size // 2, 25 - size // 2, size, size)
        painter.end()

        self.brush_preview.setPixmap(pixmap)


class DrawWidget(HorizontalFrame):
    Brush_Signal = Signal()
    Marker_Signal = Signal()
    Eraser_Signal = Signal()
    Text_Signal = Signal()
    Color_Signal = Signal(QColor)
    Move_Signal = Signal()
    def __init__(self, parent, **kwargs):
        HorizontalFrame.__init__(self, parent, **kwargs)

        self.parent = parent
        self.setup_ui()
        self.setStyleSheet("background: rgba(25, 33, 42, 0.6);")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def setup_ui(self):
        pivot =  SegmentedToolWidget(self)
        pivot.addItem("brush", IconManager.BRUSH, lambda : self.Brush_Signal.emit())
        pivot.addItem("marker", IconManager.MARKER, lambda : self.Marker_Signal.emit())
        pivot.addItem("eraser", FluentIcon.ERASE_TOOL, lambda : self.Eraser_Signal.emit())
        pivot.addItem("Text", IconManager.TEXT, lambda : self.Text_Signal.emit())
        pivot.addItem('move', FluentIcon.ZOOM_IN, lambda : self.Move_Signal.emit())
        logger.info(f"text: {IconManager.TEXT.path()}")
        color_dialog_button = ColorPickerButton("#000000", "Select Color")
        color_dialog_button.colorChanged.connect(self.Color_Signal.emit)

        self.addWidget(pivot, alignment=Qt.AlignmentFlag.AlignCenter)
        self.addWidget(color_dialog_button)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QLabel

    app = QApplication([])
    widget = DrawWidget(None)
    widget.show()
    widget.Color_Signal.connect(print)
    app.exec()

