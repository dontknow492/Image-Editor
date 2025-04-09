from xmlrpc.client import Boolean

from PySide6.QtCore import Qt, Signal
from qfluentwidgets import TransparentToolButton, FluentIcon, TitleLabel, TransparentToggleToolButton
from gui.common.myFrame import VerticalFrame, HorizontalFrame
from gui.common.slider import CenteredSlider
from utils.misc import create_transparent_tool_button
from utils.icon_manager import IconManager

class CropWidget(VerticalFrame):
    flip_signal = Signal(object)
    rotate_signal = Signal(int)
    crop_signal = Signal(Boolean)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentSpacing(0)
        self._setup_ui()
        self.setStyleSheet("background: rgba(25, 33, 42, 150); border-radius: 5px;")
        self.previous_value = 0

    def _setup_ui(self):
        self.degree_label = TitleLabel('0°', self)
        degree_slider = CenteredSlider(Qt.Orientation.Horizontal, self)
        degree_slider.setRange(-45, 45)
        degree_slider.setValue(0)
        degree_slider.valueChanged.connect(self.on_slider_value_changed)

        option_container = HorizontalFrame(self)
        option_container.setStyleSheet("background: transparent;")
        rotate_container = HorizontalFrame(option_container)
        rotate_left_button = create_transparent_tool_button(IconManager.ROTATE_LEFT, parent=rotate_container)
        rotate_left_button.clicked.connect(lambda: self.rotate_signal.emit(-90))
        rotate_right_button = create_transparent_tool_button(IconManager.ROTATE_RIGHT, parent=rotate_container)
        rotate_right_button.clicked.connect(lambda: self.rotate_signal.emit(90))

        rotate_container.addWidget(rotate_left_button)
        rotate_container.addWidget(rotate_right_button)

        self.crop_button = TransparentToggleToolButton(IconManager.CROP, option_container)
        self.crop_button.toggled.connect(self.crop_signal)

        flip_container = HorizontalFrame(option_container)
        flip_horizontal_button = create_transparent_tool_button(IconManager.HORIZONTAL_FLIP, parent=flip_container)
        flip_horizontal_button.clicked.connect(lambda: self.flip_signal.emit(Qt.Orientation.Horizontal))
        flip_vertical_button = create_transparent_tool_button(IconManager.VERTICAL_FLIP, parent=flip_container)
        flip_vertical_button.clicked.connect(lambda: self.flip_signal.emit(Qt.Orientation.Vertical))

        flip_container.addWidget(flip_horizontal_button)
        flip_container.addWidget(flip_vertical_button)

        option_container.addWidget(rotate_container,  alignment=Qt.AlignmentFlag.AlignLeading)
        option_container.addWidget(self.crop_button, alignment=Qt.AlignmentFlag.AlignCenter)
        option_container.addWidget(flip_container, alignment=Qt.AlignmentFlag.AlignTrailing)

        self.addWidget(self.degree_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.addWidget(degree_slider)
        self.addWidget(option_container)

    def on_slider_value_changed(self, value):
        self.degree_label.setText(f"{value}°")
        angle = value - self.previous_value
        self.previous_value = value
        self.rotate_signal.emit(angle)

    def set_crop_state(self, state: bool):
        self.crop_button.setChecked(state)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    widget = CropWidget()
    widget.flip_signal.connect(lambda orientation: print(orientation))
    widget.show()
    app.exec()