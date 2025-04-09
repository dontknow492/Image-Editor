from PySide6.QtCore import Signal, Qt
from qfluentwidgets import PrimaryDropDownPushButton, PushButton, FluentIcon, TransparentPushButton, VerticalSeparator, \
    StrongBodyLabel, SegmentedToolWidget, Action, RoundMenu

from gui.common import HorizontalFrame
from utils.icon_manager import IconManager
from utils.misc import create_transparent_tool_button



class OptionsWidget(HorizontalFrame):
    filter_clicked = Signal()
    crop_clicked = Signal()
    adjustment_clicked = Signal()
    draw_clicked = Signal()
    undo = Signal()
    redo = Signal()
    reset = Signal()

    zoom_in = Signal()
    zoom_out = Signal()

    save_as_signal = Signal()
    save_copy_signal = Signal()
    save_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('options_widget')
        self._init_ui()

    def _init_ui(self):
        container_1 = HorizontalFrame(self)
        zoom_in_button = create_transparent_tool_button(FluentIcon.ZOOM_IN, on_click=self.zoom_in.emit, tooltip="Zoom In", parent=container_1)
        zoom_out_button = create_transparent_tool_button(FluentIcon.ZOOM_OUT, on_click=self.zoom_out.emit, tooltip="Zoom Out", parent=container_1)
        self.zoom_label = StrongBodyLabel("100%", container_1)
        v_seperator = VerticalSeparator(self)
        reset_button = TransparentPushButton("Reset", container_1)
        undo_button = create_transparent_tool_button(IconManager.UNDO, on_click=self.undo.emit, tooltip="Undo", parent=self)
        redo_button = create_transparent_tool_button(IconManager.REDO, on_click=self.redo, tooltip="Redo", parent=self)

        container_1.addWidget(zoom_in_button)
        container_1.addWidget(zoom_out_button)
        container_1.addWidget(self.zoom_label)
        container_1.addWidget(v_seperator)
        container_1.addWidget(reset_button)
        container_1.addWidget(undo_button)
        container_1.addWidget(redo_button)

        container_2 = SegmentedToolWidget(self)
        container_2.addItem(routeKey="crop", icon = IconManager.CROP, onClick= lambda : self.crop_clicked.emit())
        container_2.addItem(routeKey="adjust", icon = FluentIcon.BRIGHTNESS, onClick= lambda : self.adjustment_clicked.emit())
        container_2.addItem(routeKey="filter", icon = FluentIcon.BRUSH, onClick=lambda : self.filter_clicked.emit())
        container_2.addItem(routeKey="draw", icon = FluentIcon.PALETTE, onClick=lambda : self.draw_clicked.emit())

        container_3 = HorizontalFrame(self)
        save_button = PrimaryDropDownPushButton(FluentIcon.SAVE, "Save Options", container_3)
        save_menu = RoundMenu(parent=save_button)
        save_menu.addActions(
            [
                Action("Save As", triggered = lambda : self.save_as_signal.emit()),
                Action("Save",  triggered= lambda : self.save_signal.emit()),
                Action("Save a Copy", triggered= lambda : self.save_copy_signal.emit())
            ]
        )
        save_button.setMenu(save_menu)


        cancel_button = PushButton("Cancel", container_3)
        container_3.addWidget(save_button)
        container_3.addWidget(cancel_button)

        self.addWidget(container_1, alignment=Qt.AlignmentFlag.AlignLeading)
        self.addWidget(container_2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.addWidget(container_3, alignment=Qt.AlignmentFlag.AlignTrailing)

    def set_zoom_label(self, zoom: float | int):
        self.zoom_label.setText(f"{zoom:.2f}%")


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QSizePolicy, QSpacerItem

    app = QApplication([])
    w = OptionsWidget()
    w.show()
    app.exec()
