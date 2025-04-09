from qfluentwidgets import FluentIconBase, Theme, getIconColor, ToolButton
from PySide6.QtWidgets import QApplication
from pathlib import Path
from enum import Enum

class IconManager(FluentIconBase, Enum):
    CROP = "crop-minimalistic"
    HORIZONTAL_FLIP = "flip-horizontal"
    VERTICAL_FLIP = "flip-vertical"
    ROTATE_LEFT = "rotate-left"
    ROTATE_RIGHT = "rotate-right"
    ZOOM_IN = "zoom-plus"
    ZOOM_OUT = "zoom-minus"
    UNDO = "undo-left-round"
    REDO = "redo"
    BRIGHTNESS = "brightness-setting"
    BRUSH = "brush"
    PENCIL_ALT = "pencil-alt"
    PEN = "pen-2"
    ERASER = "eraser"
    MARKER = "marker"
    TEXT = "text-size"
    def path(self, theme=Theme.AUTO):
        # getIconColor() return "white" or "black" according to current theme
        return f'resources/icons/{getIconColor(theme)}/{self.value}-svgrepo-com.svg'
    pass

if __name__ == "__main__":
    app = QApplication()
    p = Path("resources/icons/black/flip-vertical-svgrepo-com.svg")
    print(getIconColor())
    print(p.exists())
    win = ToolButton(IconManager.CROP)
    win.show()
    app.exec()


