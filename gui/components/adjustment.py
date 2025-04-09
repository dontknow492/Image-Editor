from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSpacerItem, QSizePolicy, QVBoxLayout
from qfluentwidgets import StrongBodyLabel, FluentIconBase, TransparentToolButton, FluentIcon, Slider, PrimaryPushButton
from gui.common.myFrame import VerticalFrame, HorizontalFrame
from gui.common.myGroupBox import GroupBox
from gui.common.myScroll import VerticalScrollWidget
from gui.common.slider import CenteredSlider


def create_adjustment_widget(
    icon: FluentIconBase,
    title: str,
    value_range: tuple[int, int],
    default_value: int = 0,
    value_changed_callback=None,
    slider_type: str = "centered",
    parent=None
) -> VerticalFrame:
    """
    Creates a UI widget with an icon, title, value label, and a slider for image adjustments.

    Args:
        icon: The icon to display
        title: The title text
        value_range: Tuple of (min, max) values for the slider
        default_value: Initial value for the slider
        value_changed_callback: Function to call when slider value changes with the difference
        slider_type: Type of slider ("centered" or "default")
        parent: Parent widget

    Returns:
        VerticalFrame containing the adjustment widget
    """
    # Validate inputs
    min_val, max_val = value_range
    if not min_val <= default_value <= max_val:
        default_value = min_val if slider_type == "default" else (min_val + max_val) // 2

    # Create containers
    container = VerticalFrame(parent)
    container.setObjectName("AdjustmentWidget")
    container.setLayoutMargins(0, 9, 0, 9)

    header_container = HorizontalFrame(container)
    header_container.setLayoutMargins(0, 0, 9, 0)
    header_container.setContentSpacing(0)

    # Create UI elements
    icon_button = TransparentToolButton(icon, header_container)
    title_label = StrongBodyLabel(title, header_container)
    value_label = StrongBodyLabel(f"{default_value:.2f}", header_container)

    # Arrange header elements
    header_container.addWidget(icon_button)
    header_container.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignLeft)
    header_container.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignRight)

    # Store default and previous values
    container.default_value = default_value
    container.previous_value = default_value

    # Create and configure slider
    slider_class = CenteredSlider if slider_type == "centered" else Slider
    slider = slider_class(Qt.Orientation.Horizontal, parent=container)
    slider.setObjectName("AdjustmentSlider")
    slider.setRange(min_val, max_val)
    slider.setValue(default_value)
    slider.wheelEvent = lambda event: event.ignore()

    # Define value changed handler
    def on_value_changed(value: int):
        value_label.setText(f"{value:.2f}")
        if value_changed_callback:
            value_changed_callback(value)

    # Connect slider signal
    slider.valueChanged.connect(on_value_changed)

    # Assemble widget
    container.addWidget(header_container)
    container.addWidget(slider)
    container.addSpacerItem(
        QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    )

    return container

class AdjustmentWindow(VerticalScrollWidget):
    """Window containing image adjustment controls organized in groups."""

    # Signals
    contrast_signal = Signal(float)
    brightness_signal = Signal(float)
    exposure_signal = Signal(float)
    shadows_signal = Signal(float)
    highlights_signal = Signal(float)
    vignette_signal = Signal(float)
    gamma_signal = Signal(float)
    red_signal = Signal(float)
    green_signal = Signal(float)
    blue_signal = Signal(float)
    saturation_signal = Signal(float)
    hue_signal = Signal(float)
    temperature_signal = Signal(float)
    sharpness_signal = Signal(float)
    noise_signal = Signal(float)
    blur_signal = Signal(float)

    #reset
    reset_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("background: rgb(25, 33, 42); border-radius: 5px;")
        self.setObjectName("AdjustmentWindow")
        self._setup_ui()

    def _setup_ui(self):
        """Initialize and configure the UI components."""
        # Light adjustments group
        light_group = GroupBox("Light", self)
        light_group.setObjectName("LightGroup")
        light_layout = QVBoxLayout(light_group)

        light_adjustments = [
            ("Brightness", (0, 200), 100, self._on_brightness_changed),
            ("Contrast", (0, 300), 100, self._on_contrast_changed),
            ("Exposure", (0, 200), 100, self._on_exposure_changed),
            ("Shadows", (0, 100), 50, self._on_shadows_changed),
            ("Highlights", (0, 100), 50, self._on_highlights_changed),
            ("Vignette", (0, 100), 0, self._on_vignette_changed, "default"),
            ("Gamma", (0, 200), 100, self._on_gamma_changed),
        ]

        for adjustment in light_adjustments:
            title, range_, default, callback = adjustment[:4]
            slider_type = adjustment[4] if len(adjustment) > 4 else "centered"
            widget = create_adjustment_widget(
                FluentIcon.BRUSH, title, range_, default, callback, slider_type
            )
            light_layout.addWidget(widget)

        # Color adjustments group
        color_group = GroupBox("Color", self)
        color_group.setObjectName("ColorGroup")
        color_layout = QVBoxLayout(color_group)

        color_adjustments = [
            ("Red", (0, 100), 0, self.red_signal.emit, "default"),
            ("Green", (0, 100), 0, self.green_signal.emit, "default"),
            ("Blue", (0, 100), 0, self.blue_signal.emit, "default"),
            ("Saturation", (0, 300), 100, self._on_saturation_changed),
            ("Hue", (-180, 180), 0, self.hue_signal.emit),
            ("Temperature", (-100, 100), 0, self.temperature_signal.emit),
            ("Sharpness", (0, 200), 100, self._on_sharpness_changed),
            ("Noise", (0, 100), 0, self._on_noise_changed, "default"),
            ("Blur", (0, 10), 0, self.blur_signal.emit, "default"),
        ]

        for adjustment in color_adjustments:
            title, range_, default, callback = adjustment[:4]
            slider_type = adjustment[4] if len(adjustment) > 4 else "centered"
            widget = create_adjustment_widget(
                FluentIcon.BRUSH, title, range_, default, callback, slider_type
            )
            color_layout.addWidget(widget)

        reset_button = PrimaryPushButton("Reset", self)
        reset_button.clicked.connect(self.reset_to_default)

        self.addWidget(light_group)
        self.addWidget(color_group)
        self.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignCenter)

    # Signal handlers
    def _on_brightness_changed(self, value: int):
        self.brightness_signal.emit(round(value / 100, 2))

    def _on_contrast_changed(self, value: int):
        self.contrast_signal.emit(round(value / 100, 2))

    def _on_exposure_changed(self, value: int):
        self.exposure_signal.emit(round(value / 100, 2))

    def _on_shadows_changed(self, value: int):
        self.shadows_signal.emit(round(value / 100, 2))

    def _on_highlights_changed(self, value: int):
        self.highlights_signal.emit(round(value / 100, 2))

    def _on_vignette_changed(self, value: int):
        self.vignette_signal.emit(round(value / 100, 2))

    def _on_gamma_changed(self, value: int):
        self.gamma_signal.emit(round(value / 100, 2))

    def _on_saturation_changed(self, value: int):
        self.saturation_signal.emit(round(value / 100, 2))

    def _on_sharpness_changed(self, value: int):
        self.sharpness_signal.emit(round(value / 100, 2))

    def _on_noise_changed(self, value: int):
        self.noise_signal.emit(round(value / 100, 2))

    def reset_to_default(self):
        """Reset all sliders to their default values."""
        for widget in self.findChildren(VerticalFrame, "AdjustmentWidget"):
            slider = widget.findChild(Slider, "AdjustmentSlider")
            if slider:
                slider.setValue(widget.default_value)
            else:
                slider = widget.findChild(CenteredSlider, "AdjustmentSlider")
                if slider:
                    slider.setValue(widget.default_value)
        self.reset_signal.emit()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from qfluentwidgets import setTheme, Theme
    import sys

    setTheme(Theme.DARK)
    app = QApplication(sys.argv)
    window = AdjustmentWindow()
    window.gamma_signal.connect(lambda v: print(v))
    window.contrast_signal.connect(lambda v: print(v))
    window.brightness_signal.connect(lambda v: print(v))
    window.exposure_signal.connect(lambda v: print(v))
    window.shadows_signal.connect(lambda v: print(v))
    window.highlights_signal.connect(lambda v: print(v))
    window.vignette_signal.connect(lambda v: print(v))
    window.gamma_signal.connect(lambda v: print(v))
    window.red_signal.connect(lambda v: print(v))
    window.green_signal.connect(lambda v: print(v))
    window.blue_signal.connect(lambda v: print(v))
    window.saturation_signal.connect(lambda v: print(v))
    window.hue_signal.connect(lambda v: print(v))
    window.temperature_signal.connect(lambda v: print(v))
    window.sharpness_signal.connect(lambda v: print(v))
    window.noise_signal.connect(lambda v: print(v))
    window.blur_signal.connect(lambda v: print(v))
    window.show()
    sys.exit(app.exec())