from typing import Callable, Optional, Any, Union

from PIL import Image
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage
from core.convert import convert_qimage_to_pil
from qfluentwidgets import TransparentToolButton, FluentIconBase


def create_transparent_tool_button(icon: FluentIconBase, size:QSize = QSize(16, 16), on_click = None, tooltip: str = None, cursor: Qt.CursorShape = None, parent=None, ):
    """Create a transparent tool button with the given icon."""
    button = TransparentToolButton(icon, parent)
    if on_click:
        button.clicked.connect(on_click)
    if tooltip:
        button.setToolTip(tooltip)
    if cursor:
        button.setCursor(cursor)
    button.setIconSize(size)
    button.setFixedSize(size)
    return button

def create_filter_image(
        image: Union[Image.Image, QImage],
        function: Callable[..., Image.Image],
        parameter: Optional[Any] = None
) -> Image:
    """
    Apply a filter function to the given image with an optional parameter.

    Args:
        image: The input PIL Image.
        function: The filter function to apply.
        parameter: Optional parameter for the filter function.

    Returns:
        The filtered PIL Image.
    """
    try:
        if image is None:
            raise ValueError("Image is None")
        if isinstance(image, QImage):
            image = convert_qimage_to_pil(image)
        if parameter is not None:
            filter_image = function(image, parameter)
        else:
            filter_image = function(image)

        if filter_image is None:
            raise ValueError("Filter function returned None")
            return None
        return filter_image
    except Exception as e:
        print(f"Error applying filter: {e}")