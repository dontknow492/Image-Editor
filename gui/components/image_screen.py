from enum import Enum
from pathlib import Path
from typing import Union

from PIL.ImageQt import ImageQt
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QCursor, QBrush, QPen, QPainterPath
from PySide6.QtCore import Qt, Signal, QPoint, QRectF, QPointF, QRect
from loguru import logger
from core.adjustment import (adjust_hue, adjust_saturation, adjust_temperature, adjust_sharpness,
                                            adjust_blur, adjust_noise, adjust_brightness, adjust_contrast, adjust_exposure,
                                            adjust_shadows, adjust_highlight, adjust_vignette, adjust_gamma, adjust_red,
                                            adjust_green, adjust_blue)

from gui.components.overlay import CropOverlay, SizeOverlay
from core.convert import convert_qimage_to_pil, convert_pil_to_qimage
from utils.enums import FilterType
from utils.screen import get_screen_size, get_screen_dpi

class DrawMode(Enum):
    Move = 0
    Brush = 1
    Marker = 2
    Eraser = 3
    Text = 4


class ImageScreen(QGraphicsView):
    image_changed = Signal(QImage)
    image_updated = Signal(QImage)
    zoom_value = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.move_offset = None
        self.dragging = False
        self.moving = False
        self.is_cropping = False
        self.history = list()
        self.is_image_adjusted = None
        self.is_image_filtered = False
        self.current_filter: FilterType = None
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.screen_dpi = get_screen_dpi()

        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)

        self.image_path: Union[Path, None] = None
        self.source_image: Union[QImage, None] = None
        self.zoom_factor: float = 1.0
        self.MIN_ZOOM: float = 0.1
        self.MAX_ZOOM: float = 5.0

        self.start = QPointF()
        self.end = QPointF()
        self.crop_rect_item = QGraphicsRectItem()
        self.overlay_color = QColor(0, 0, 0, 150)
        self.crop_rect_overlay = CropOverlay(self.sceneRect(), self.image_item.boundingRect(), self.overlay_color)

        self.adjustments = {
            "hue": {'default': 0, 'current': 0, 'function': adjust_hue},
            "saturation": {'default': 0, 'current': 0, 'function': adjust_saturation},
            "temperature": {'default': 0, 'current': 0, 'function': adjust_temperature},
            "sharpness": {'default': 0, 'current': 0, 'function': adjust_sharpness},
            "blur": {'default': 0, 'current': 0, 'function': adjust_blur},
            "noise": {'default': 0, 'current': 0, 'function': adjust_noise},
            "brightness": {'default': 0, 'current': 0, 'function': adjust_brightness},
            "contrast": {'default': 0, 'current': 0, 'function': adjust_contrast},
            "exposure": {'default': 0, 'current': 0, 'function': adjust_exposure},
            "shadows": {'default': 0, 'current': 0, 'function': adjust_shadows},
            "highlights": {'default': 0, 'current': 0, 'function': adjust_highlight},
            "vignette": {'default': 0, 'current': 0, 'function': adjust_vignette},
            "gamma": {'default': 0, 'current': 0, 'function': adjust_gamma},
            "red": {'default': 0, 'current': 0, 'function': adjust_red},
            "green": {'default': 0, 'current': 0, 'function': adjust_green},
            "blue": {'default': 0, 'current': 0, 'function': adjust_blue}
        }

        # Explicitly enable drop events
        self.setAcceptDrops(True)
        logger.debug("ImageScreen initialized with drop acceptance enabled")

        self.scene.addItem(self.crop_rect_overlay)

        self.size_overlay = SizeOverlay(parent = self)




    def dragEnterEvent(self, event):
        """Handle drag enter events for file drops."""
        logger.debug(f"Drag enter event received: {event.mimeData().formats()}")
        if event.mimeData().hasUrls():
            logger.debug("URLs detected in drag event")
            event.acceptProposedAction()
        else:
            logger.debug("No URLs in drag event, rejecting")
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events to keep accepting drops."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle file drop events."""
        logger.debug("Drop event received")
        try:
            if event.mimeData().hasUrls():
                urls = event.mimeData().urls()
                logger.debug(f"Number of URLs dropped: {len(urls)}")
                if urls:
                    file_path = Path(urls[0].toLocalFile())
                    logger.info(f"File dropped: {file_path}")

                    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
                    if file_path.exists() and file_path.suffix.lower() in valid_extensions:
                        self.load_image(file_path)
                        event.acceptProposedAction()
                        logger.info("Drop accepted and image loaded")
                    else:
                        logger.error(f"Invalid file: {file_path}")
                        event.ignore()
                else:
                    logger.error("No valid URLs in drop event")
                    event.ignore()
            else:
                logger.error("Drop event has no URLs")
                event.ignore()
        except Exception as e:
            logger.exception(f"Error handling drop event: {e}")
            event.ignore()

    def load_image(self, file_path: Union[str, Path]):
        """Load an image from a file path."""
        try:
            file_path = Path(file_path) if isinstance(file_path, str) else file_path
            logger.info(f"Loading image from: {file_path}")
            self.reset_screen_state()
            self.image_path = file_path
            image = QImage(str(self.image_path))

            if image.isNull():
                raise ValueError("Failed to load image: Image is null")
            self.image_changed.emit(image)
            self.update_source_image(image)
            self.scale(1/self.screen_dpi, 1/self.screen_dpi)
        except Exception as e:
            logger.exception(f"Error loading image: {e}")

    def update_source_image(self, image: QImage):
        """Update the source image and refresh the display.
        Use this when you want to confirm a filter or other changes."""
        if image.isNull():
            logger.error("Provided image is null. Update aborted.")
            return

        self.source_image = image
        self._update_display_image(self.source_image)

    def set_image(self, image: QImage):
        """Set the image to be displayed."""
        if image.isNull():
            logger.error("Provided image is null. Setting image aborted.")
            return
        self._update_display_image(image)

    def _update_display_image(self, display_image: Union[QImage, None] = None):
        """Update the displayed image."""
        if self.source_image is None:
            return

        source = display_image if display_image is not None else self.source_image
        if not source.isNull():
            if self.is_image_filtered:
                logger.info(f"Applying display filter: {self.current_filter.name}")
                source = self.current_filter.apply(source)
                source = FilterType.pil_to_qimage(source)
            if self.is_image_adjusted:
                source = self.create_adjustments_image(source)
            pixmap = QPixmap.fromImage(source)
            self.image_item.setPixmap(pixmap)
            self.image_item.setTransformationMode(Qt.SmoothTransformation)
            self.scene.setSceneRect(self.image_item.boundingRect())
            self.image_updated.emit(source)
            self.save_current_state()
        else:
            logger.error("Cannot update display: Source image is null")

    def get_source_image(self) -> Union[QImage, None]:
        """Return the source image."""
        return self.source_image

    def get_current_image(self) -> Union[QImage, None]:
        """Return the current image from the pixmap item."""
        pixmap = self.image_item.pixmap()
        return pixmap.toImage() if not pixmap.isNull() else None

    def apply_filter(self, filter_type: FilterType):
        """
        Apply a filter function to the source image.

        Args:
            filter_type: A enum of filter type.
        """
        if self.source_image.isNull():
            return  # Skip if no image is loaded

        try:
            logger.info(f"Applying filter: {filter_type.name}")
            if filter_type.name == "ORIGINAL":
                self.is_image_filtered = False
                self.current_filter = None
                logger.info("Resetting to original image")
                self.update_source_image(self.source_image)
            else:
                self.is_image_filtered = True
                self.current_filter = filter_type
                filter_image = filter_type.apply(self.source_image)
                filter_qimage = FilterType.pil_to_qimage(filter_image)
                self._update_display_image(filter_qimage)
        except Exception as e:
            logger.exception("Error applying filter: %s", e)


    def apply_adjustments(self):
        """
        Checks all adjustments and applies the associated function if current value differs from default.
        Assumes self.adjustments is the dictionary containing adjustment settings.
        """
        adjusted_image = self.create_adjustments_image(self.source_image)
        if adjusted_image:
            self._update_display_image(adjusted_image)

    def create_adjustments_image(self, image: QImage):
        adjusted_image = convert_qimage_to_pil(image)
        apply = list()
        for key, settings in self.adjustments.items():
            default_value = settings["default"]
            current_value = settings["current"]
            adjustment_function = settings["function"]

            if current_value != default_value:
                try:
                    # Apply the adjustment function with the current value
                    apply.append(key)
                    adjusted_image = adjustment_function(adjusted_image, current_value)
                except Exception as e:
                    print(f"Error applying {key} adjustment: {str(e)}")

        if adjusted_image:
            if len(apply) > 0:
                self.is_image_adjusted = True
            logger.info(f"Applied adjustments: {apply}")
            return convert_pil_to_qimage(adjusted_image)
        else:

            logger.info("No adjustments to apply")

    def set_red(self, red: int):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting red: {red}")
            self.adjustments["red"]["current"] = red
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting red: {str(e)}")

    def set_blue(self, blue: int):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting blue: {blue}")
            self.adjustments["blue"]["current"] = blue
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting blue: {str(e)}")

    def set_green(self, green: int):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting green: {green}")
            self.adjustments["green"]["current"] = green
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting green: {str(e)}")

    def set_temperature(self, temperature_shift: int):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting temperature: {temperature_shift}")
            self.adjustments["temperature"]["current"] = temperature_shift
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting temperature: {str(e)}")

    def set_brightness(self, brightness_factor: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting brightness: {brightness_factor}")
            self.adjustments["brightness"]["current"] = brightness_factor
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting brightness: {str(e)}")

    def set_contrast(self, contrast_factor: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting contrast: {contrast_factor}")
            self.adjustments["contrast"]["current"] = contrast_factor
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting contrast: {str(e)}")

    def set_saturation(self, saturation_factor: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting saturation: {saturation_factor}")
            self.adjustments["saturation"]["current"] = saturation_factor
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting saturation: {str(e)}")

    def set_hue(self, hue_shift: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting hue: {hue_shift}")
            self.adjustments["hue"]["current"] = hue_shift
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting hue: {str(e)}")

    def set_sharpness(self, sharpness_factor: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting sharpness: {sharpness_factor}")
            self.adjustments["sharpness"]["current"] = sharpness_factor
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting sharpness: {str(e)}")

    def set_exposure(self, exposure_factor: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting exposure: {exposure_factor}")
            self.adjustments["exposure"]["current"] = exposure_factor
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting exposure: {str(e)}")

    def set_gamma(self, gamma: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting gamma: {gamma}")
            self.adjustments["gamma"]["current"] = gamma
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting gamma: {str(e)}")

    def set_vignette(self, vignette_strength: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting vignette: {vignette_strength}")
            self.adjustments["vignette"]["current"] = vignette_strength
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting vignette: {str(e)}")

    def set_blur(self, blur_radius: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting blur: {blur_radius}")
            self.adjustments["blur"]["current"] = blur_radius
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting blur: {str(e)}")

    def set_noise(self, noise_level: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting noise: {noise_level}")
            self.adjustments["noise"]["current"] = noise_level
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting noise: {str(e)}")

    def set_shadows(self, shadow_intensity: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting shadows: {shadow_intensity}")
            self.adjustments["shadows"]["current"] = shadow_intensity
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting shadows: {str(e)}")

    def set_highlights(self, highlight_intensity: float):
        if self.source_image is None:
            return
        try:
            logger.info(f"Setting highlights: {highlight_intensity}")
            self.adjustments["highlights"]["current"] = highlight_intensity
            self.apply_adjustments()
        except Exception as e:
            logger.exception(f"Error setting highlights: {str(e)}")

    def reset_adjustments(self):
        """Reset all adjustments to their default values."""
        for key, settings in self.adjustments.items():
            settings["current"] = settings["default"]
        self.is_image_adjusted = False
        self._update_display_image()
        logger.info("Adjustments reset to default values.")


    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()
        event.accept()

    def zoom_in(self):
        """Increase zoom level."""
        if self.zoom_factor < self.MAX_ZOOM and  not self.image_item.pixmap().isNull():
            self.zoom_factor = min(self.MAX_ZOOM, self.zoom_factor * 1.1)
            self.scale(1.1, 1.1)
            self.zoom_value.emit(self.zoom_factor * 100)
            # image_size = self.image_item.pixmap().size()
            # logger.info(f"Image size: {image_size * self.zoom_factor}")

    def zoom_out(self):
        """Decrease zoom level."""
        if self.zoom_factor > self.MIN_ZOOM and  not self.image_item.pixmap().isNull():
            self.zoom_factor = max(self.MIN_ZOOM, self.zoom_factor * 0.9)
            self.scale(0.9, 0.9)
            self.zoom_value.emit(self.zoom_factor * 100)

    def rotate_flip(self, angle):
        """Rotate the scene by the given angle."""
        self.rotate(angle)
        # Update scene rect

    def flip_view(self, orientation: Qt.Orientation):
        if orientation == Qt.Orientation.Horizontal:
            self.scale(-1, 1)  # Flip horizontally
        elif orientation == Qt.Orientation.Vertical:
            self.scale(1, -1)

    def reset_transformation(self):
        self.resetTransform()

    def save_current_state(self):
        state = {
            "filter": self.current_filter,
            "adjustments": self.adjustments,
            "is_image_filtered": self.is_image_filtered,
            "is_image_adjusted": self.is_image_adjusted,
            "zoom_factor": self.zoom_factor
        }
        self.history.append(state)
        logger.info("Current state saved to history")

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()  # Remove the current state
            previous_state = self.history.pop()  # Get the previous state
            self.current_filter = previous_state["filter"]
            self.adjustments = previous_state["adjustments"]
            self.is_image_filtered = previous_state["is_image_filtered"]
            self.is_image_adjusted = previous_state["is_image_adjusted"]
            self.zoom_factor = previous_state["zoom_factor"]
            self._update_display_image()
            logger.info("Undo performed")

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())

        if event.button() == Qt.MouseButton.LeftButton and self.is_cropping:
            if self.crop_rect_item and self.crop_rect_item.rect().contains(scene_pos):
                # Start moving
                self.moving = True
                self.move_offset = scene_pos - self.crop_rect_item.rect().topLeft()
            else:
                # Start drawing a new rectangle
                self.dragging = True
                self.start = scene_pos
                if self.crop_rect_item:
                    self.scene.removeItem(self.crop_rect_item)
                if self.crop_rect_overlay:
                    self.scene.removeItem(self.crop_rect_overlay)

                self.crop_rect_overlay = CropOverlay(self.sceneRect(), self.image_item.sceneBoundingRect())
                self.crop_rect_item = QGraphicsRectItem()
                self.crop_rect_item.setPen(QPen(Qt.GlobalColor.red, 2, Qt.DashLine))
                self.crop_rect_item.setBrush(QColor(0, 0, 0, 10))
                self.scene.addItem(self.crop_rect_item)
                self.scene.addItem(self.crop_rect_overlay)
                self.crop_rect_item.setZValue(20)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        scene_pos = self.mapToScene(event.pos())

        if self.dragging and self.crop_rect_item:
            self.end = scene_pos
            rect = QRectF(self.start, self.end).normalized()
            self.crop_rect_item.setRect(rect)
            self.crop_rect_overlay.setCropRect(rect)
            self.crop_rect_overlay.setOuterRect(self.sceneRect())
        elif self.moving and self.crop_rect_item:
            top_left = scene_pos - self.move_offset
            rect = QRectF(top_left, self.crop_rect_item.rect().size())
            self.crop_rect_item.setRect(rect)
            self.crop_rect_overlay.setCropRect(rect)
            self.crop_rect_overlay.setOuterRect(self.sceneRect())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging and self.crop_rect_item:
                self.end = self.mapToScene(event.pos())
                rect = QRectF(self.start, self.end).normalized()
                self.crop_rect_item.setRect(rect)
            self.dragging = False
            self.moving = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.dragging = False
            self.moving = False
            if self.crop_rect_item:
                self.scene.removeItem(self.crop_rect_item)
                self.crop_rect_item = None
            if self.crop_rect_overlay:
                self.crop_rect_overlay.hide()
                self.crop_rect_overlay = None

    def get_crop_rect(self):
        if self.crop_rect_item:
            return self.crop_rect_item.rect().toRect()
        return None

    def set_cropping(self, is_cropping: bool):
        logger.info(f"Setting cropping: {is_cropping}")
        self.is_cropping = is_cropping
        # if not is_cropping and self.crop_rect_item:
        #     self.scene.removeItem(self.crop_rect_item)
        #     self.crop_rect_item = None

    # def size_overlay(self):
    #

    def reset_screen_state(self):
        self.reset_adjustments()
        self.reset_transformation()
        self.set_cropping(False)
        self.scene.removeItem(self.crop_rect_item)
        self.scene.removeItem(self.crop_rect_overlay)
        self.image_item.setPixmap(QPixmap())
        self.is_image_filtered = False
        self.is_image_adjusted = False
        self.current_filter = None
        self.crop_rect_item = None
        self.crop_rect_overlay = None
        self.history = []
        self.source_image = None
        self.image_path  = None
        self.move_offset = None
        self.dragging = False
        self.moving = False
        self.zoom_factor= 1.0
        self.zoom_value.emit(self.zoom_factor * 100)

    def screen_overlay(self):
        pixmap = self.image_item.pixmap()
        if pixmap.isNull():
            return
        pixmap_size = pixmap.size()
        return pixmap_size * self.zoom_factor

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        overlay_size = self.size_overlay.size()
        parent_size = self.size()
        # self.size_overlay.move()

    def get_image(self):
        pixmap = self.image_item.pixmap()
        if pixmap.isNull():
            return None
        return pixmap

    def get_image_path(self):
        return self.image_path

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ImageScreen()
    window.setMinimumSize(800, 600)  # Set a reasonable size for testing
    window.show()
    logger.info("Application started")
    sys.exit(app.exec())