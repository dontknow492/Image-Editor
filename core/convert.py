from PIL import Image
from PIL import Image
from PySide6.QtGui import QPixmap, QImage


def convert_pil_to_pixmap(pil_image: Image.Image):
    return pil_image.toqpixmap()

def convert_pil_to_qimage(pil_image: Image.Image):
    return pil_image.toqimage()

def convert_qimage_to_pil(qimage: QImage):
    return Image.fromqimage(qimage)

def convert_pixmap_to_pil(pixmap: QPixmap):
    return Image.fromqpixmap(pixmap)

def convert_numpy_to_pil(numpy_array):
    return Image.fromarray(numpy_array)