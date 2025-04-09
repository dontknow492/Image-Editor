from PIL import Image
from PIL.ImageFile import ImageFile
from PySide6.QtGui import QPixmap, QTransform
from loguru import logger
from typing import Union
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

def load_image(file_path):
    try:
        img = Image.open(file_path)
        return img
    except FileNotFoundError:
        logger.exception(f"File not found: {file_path}")
        return None
    except Exception as e:
        logger.exception(f"Error loading image: {e}")
        return None

def save_image(img: ImageFile, file_path):
    try:
        img.save(file_path)
    except Exception as e:
        logger.exception(f"Error saving image: {e}")

def rotate_image(img: ImageFile, angle)->ImageFile:
    try:
        return img.rotate(angle, resample= Image.Resampling.LANCZOS, expand = False)
    except Exception as e:
        logger.exception(f"Error rotating image: {e}")
        return None

def rotate_qimage(qimage: QImage, angle)->Union[QImage, None]:
    try:
        transform = QTransform().rotate(angle)
        return qimage.transformed(transform, Qt.TransformationMode.SmoothTransformation)
    except Exception as e:
        logger.exception(f"Error rotating image: {e}")
        return None

def flip_image(img: ImageFile, direction)->Union[ImageFile, None]:
    try:
        if direction == 'horizontal':
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            logger.error(f"Invalid flip direction: {direction}")
            return None
    except Exception as e:
        logger.exception(f"Error flipping image: {e}")
        return None

def flip_qimage(qimage: QImage, orientation: Qt.Orientation)->Union[QImage, None]:
    try:
        if orientation == Qt.Orientation.Horizontal:
            return qimage.mirrored(True, False)
        elif orientation == Qt.Orientation.Vertical:
            return qimage.mirrored(False, True)
        else:
            logger.error(f"Invalid flip orientation: {orientation}")
            return None
    except Exception as e:
        logger.exception(f"Error flipping image: {e}")
        return None

def resize_image(img: ImageFile, width, height)->ImageFile:
    try:
        return img.resize((width, height), Image.Resampling.LANCZOS)
    except Exception as e:
        logger.exception(f"Error resizing image: {e}")
        return None

def crop_image(img: ImageFile, x, y, width, height)->ImageFile:
    try:
        return img.crop((x, y, x + width, y + height))
    except Exception as e:
        logger.exception(f"Error cropping image: {e}")
        return None


if __name__ == "__main__":
    image = load_image(r"D:\Program\Image Editor\samples\image.jpg")
    image = rotate_image(image, 90)
    image = rotate_image(image, -90)
    # image = rotate_image(image, -32)
    image.show()
