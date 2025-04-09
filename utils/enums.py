from enum import Enum
from typing import Callable, Any, Optional, Union

from PIL import Image
from PIL import ImageQt
from PySide6.QtGui import QImage

from core.filters import (
    filter_blur, filter_contour, filter_detail, filter_edge_enhance,
    filter_edge_enhance_more, filter_emboss, filter_find_edges, filter_sharpen,
    filter_smooth, filter_smooth_more, filter_pixelation, filter_glitch,
    filter_invert, filter_cartoon, filter_sepia, filter_grayscale
)

class FilterType(Enum):
    ORIGINAL = ("Original", None, None)
    BLUR = ("Blur", filter_blur, 5)
    CONTOUR = ("Contour", filter_contour, None)
    DETAIL = ("Detail", filter_detail, None)
    EDGE_ENHANCE = ("Edge Enhance", filter_edge_enhance, None)
    EDGE_ENHANCE_MORE = ("Edge Enhance More", filter_edge_enhance_more, None)
    EMBOSS = ("Emboss", filter_emboss, None)
    FIND_EDGES = ("Find Edges", filter_find_edges, None)
    SHARPEN = ("Sharpen", filter_sharpen, 1.5)
    SMOOTH = ("Smooth", filter_smooth, None)
    SMOOTH_MORE = ("Smooth More", filter_smooth_more, None)
    PIXELATE = ("Pixelate", filter_pixelation, 10)
    GLITCH = ("Glitch", filter_glitch, None)
    INVERT = ("Invert", filter_invert, None)
    CARTOON = ("Cartoon", filter_cartoon, None)
    SEPIA = ("Sepia", filter_sepia, None)
    GRAYSCALE = ("Grayscale", filter_grayscale, None)

    def __init__(self, name: str, func: Optional[Callable], parameter: Optional[Any]):
        self._name = name
        self.func = func
        self.parameter = parameter

    def apply(self, img: Union[QImage, Image.Image]):
        if self.func:
            if isinstance(img, QImage):
                img = self.qimage_to_pil(img)
            if self.parameter is not None:
                return self.func(img, self.parameter)
            return self.func(img)
        return img  # No processing for "Original"

    @staticmethod
    def qimage_to_pil(qimage: QImage) -> Image.Image:
        """Convert QImage to PIL Image."""
        return ImageQt.fromqimage(qimage)

    @staticmethod
    def pil_to_qimage(pil_image: Image.Image) -> QImage:
        """Convert PIL Image to QImage."""
        return ImageQt.toqimage(pil_image)

if __name__ == "__main__":
    image = Image.open("D:/Downloads/Images/nature-images.jpg")
    filter =  FilterType.BLUR.apply(image)
    filter.show()
