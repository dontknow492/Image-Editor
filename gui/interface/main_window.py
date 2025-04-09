from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QImage, QWheelEvent
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QSlider, QFileDialog, QMessageBox
from qfluentwidgets import (setTheme, Theme, FluentWindow, ScrollArea, ImageLabel, TransparentToolButton, FluentIcon,
                            BodyLabel, TransparentPushButton, VerticalSeparator, PushButton, TitleLabel,
                            FluentIconBase, StrongBodyLabel, PrimaryDropDownPushButton)
from pathlib import Path
from loguru import logger

from core.basic_operations import flip_qimage, rotate_qimage, rotate_image
from core.convert import convert_qimage_to_pil
from gui.common.myFrame import HorizontalFrame, VerticalFrame
from gui.components.crop import CropWidget
from gui.components.filter import FilterWindow
from gui.components.adjustment import AdjustmentWindow
from gui.components.draw import DrawWidget
# from gui.components.image_screen import ImageScreen
from gui.components.image_screen import ImageScreen
from gui.components.options import OptionsWidget
from utils.stack import Stack
from gui.common.infoBarMsg import InfoTime



class MainWindow(FluentWindow):
    def __init__(self,  parent = None):
        super().__init__(parent)
        self.setWindowTitle('Imagify')
        self.info_bar = InfoTime(self)
        self.image_stack = Stack()
        self.display = ImageScreen(self)
        self.options = OptionsWidget(self)
        self.filters = FilterWindow(self)
        self.adjustment = AdjustmentWindow(self)
        self.draw_widget = DrawWidget(self)
        self.crop_widget = CropWidget(self)
        self.init_ui()
        self.navigationInterface.hide()
        self._signal_handler()
        # self.display.set_image(r'D:\Java\DukeWithHelmet.png')
        self._show_option(self.crop_widget)
        self.crop_widget.set_crop_state(True)
    #
    def init_ui(self):
        main_container = VerticalFrame(self)


        h_container = HorizontalFrame(self)
        h_container.addWidget(self.display, stretch=7)
        h_container.addWidget(self.filters, stretch=3)
        h_container.addWidget(self.adjustment, stretch=3)

        main_container.addWidget(self.options, alignment=Qt.AlignmentFlag.AlignTop)
        main_container.addWidget(h_container, stretch=1)

        self.stackedWidget.addWidget(main_container)
        self.stackedWidget.setCurrentWidget(main_container)

    def _signal_handler(self):
        self.filters.filter_clicked.connect(self.display.apply_filter)
        self.display.image_changed.connect(self.filters.set_image)
        self.display.image_updated.connect(self.on_image_changed)
        self.display.zoom_value.connect(self.options.set_zoom_label)
        self._option_signal_handler()
        self._adjustment_signal_handler()
        self._crop_widget_signal_handler()

    def _crop_widget_signal_handler(self):
        self.crop_widget.flip_signal.connect(self.flip_image)
        self.crop_widget.rotate_signal.connect(self.rotate_image)
        self.crop_widget.crop_signal.connect(self.display.set_cropping)

    def _option_signal_handler(self):
        self.hide_all_widgets()
        self.options.filter_clicked.connect(lambda : self._show_option(self.filters))
        self.options.crop_clicked.connect(lambda : self._show_option(self.crop_widget))
        self.options.adjustment_clicked.connect(lambda :self._show_option(self.adjustment))
        self.options.draw_clicked.connect(lambda :self._show_option(self.draw_widget))

        #
        self.options.undo.connect(self.undo)
        self.options.zoom_in.connect(self.display.zoom_in)
        self.options.zoom_out.connect(self.display.zoom_out)

        self.options.save_as_signal.connect(lambda : self.save_image(mode = "save_as"))
        self.options.save_signal.connect(lambda : self.save_image(mode = "save"))
        self.options.save_copy_signal.connect(lambda : self.save_image(mode = "save_copy"))
        # self.options.draw_clicked.connect(self.draw_widget.show)

    from PySide6.QtWidgets import QFileDialog, QMessageBox

    def save_image(self, mode: str = "save_copy"):
        image = self.display.get_image()
        file_path = None
        if image is None:
            logger.warning("No image to save.")
            self.info_bar.error_msg("No image to save.")
            return
        crop_rect = self.display.get_crop_rect()
        if crop_rect:
            image = image.copy(crop_rect)
        logger.info(f"Saving image, mode: {mode}, size: {image.size()}")


        if mode == "save":
            image_path = self.display.get_image_path()
            if not image_path:
                logger.warning("Image path not found for 'save' mode.")
                self.info_bar.error_msg("Failed to Save", "Image path not found for 'save' mode.")
                return
            file_path = image_path

        elif mode == "save_as":
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image Copy", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)")

        elif mode == "save_copy":
            image_path =  self.display.get_image_path()
            file_name = ""
            if image_path:
                file_name = Path(image_path).name
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image Copy", file_name,
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)")

        else:
            logger.warning(f"Unknown save mode: {mode}")
            self.info_bar.error_msg("Save Error", f"Unknown save mode: {mode}")

        if  file_path:
            if self.save_file(image, file_path):
                self.display.reset_screen_state()
                self.display.load_image(file_path)
        else :
            logger.warning("Save operation cancelled by user.")
            self.info_bar.error_msg("Save Cancelled", "Save operation cancelled by user.")

    def save_file(self, image: QPixmap, file_path):
        if not image.save(file_path):
            self.info_bar.error_msg(self, "Save Copy Error", f"Failed to save copy to {file_path}")
            return False
        else:
            logger.info(f"Image copy saved to {file_path}")
            self.info_bar.success_msg( "Save Copy Success", f"Image copy saved to {file_path}")
            return True

    def _adjustment_signal_handler(self):
        # self.adjustment.reset_signal.connect(self.display.reset_adjustment)
        self.adjustment.brightness_signal.connect(self.display.set_brightness)
        self.adjustment.contrast_signal.connect(self.display.set_contrast)
        self.adjustment.exposure_signal.connect(self.display.set_exposure)
        self.adjustment.shadows_signal.connect(self.display.set_shadows)
        self.adjustment.highlights_signal.connect(self.display.set_highlights)
        self.adjustment.vignette_signal.connect(self.display.set_vignette)
        self.adjustment.gamma_signal.connect(self.display.set_gamma)
        self.adjustment.red_signal.connect(self.display.set_red)
        self.adjustment.green_signal.connect(self.display.set_green)
        self.adjustment.blue_signal.connect(self.display.set_blue)
        self.adjustment.saturation_signal.connect(self.display.set_saturation)
        self.adjustment.hue_signal.connect(self.display.set_hue)
        self.adjustment.temperature_signal.connect(self.display.set_temperature)
        self.adjustment.sharpness_signal.connect(self.display.set_sharpness)
        self.adjustment.noise_signal.connect(self.display.set_noise)
        self.adjustment.blur_signal.connect(self.display.set_blur)

    def _show_option(self, widget):
        if not widget.isHidden():
            return
        print("clicked")
        self.hide_all_widgets()
        widget.show()
        logger.info(widget.pos())

    def hide_all_widgets(self):
        self.crop_widget.set_crop_state(False)
        self.filters.hide()
        self.adjustment.hide()
        self.crop_widget.hide()
        self.draw_widget.hide()

    def on_image_changed(self, image: QImage):
        if image is None:
            return
        # logger.info(f"Image changed: {image.size()}")
        # logger.info(f"Image pushed to stack: {image.size()}")
        # self.image_stack.push(image)

    def undo(self):
        self.display.undo()

    def flip_image(self, orientation):
        logger.debug(f"Flip image: {orientation}")
        self.display.flip_view(orientation)
        # image = self.display.get_source_image()
        # if image is None:
        #     return
        # if orientation == Qt.Orientation.Horizontal:
        #     image = flip_qimage(image, Qt.Orientation.Horizontal)
        #     self.display.set_image(image)
        # elif  orientation == Qt.Orientation.Vertical:
        #     image = flip_qimage(image, Qt.Orientation.Vertical)
        #     self.display.set_image(image)

    def rotate_image(self, angle):
        logger.info(f"Rotate at ange: {angle}")
        self.display.rotate(angle)
        # image = self.display.get_source_image()
        # if image is None:
        #     return
        # size = image.size()
        # logger.info(f"image size: {size}")
        # image = convert_qimage_to_pil(image)
        # image = rotate_image(image, angle)
        # if image is None:
        #     return
        # image = ImageQt(image)
        # image.scaled(QSize(800, 800), Qt.KeepAspectRatio)
        # logger.info(f"image size: {image.size()}")
        # self.display.set_image(image)



    def resizeEvent(self, e):
        self.updateGeometry()
        logger.info(f"Window size: {self.size()}")
        # if not self.draw_widget.isHidden():
        self.draw_widget.adjustSize()
        self.crop_widget.adjustSize()
        self.draw_widget.move((self.width() - self.draw_widget.width())//2, self.height() - self.draw_widget.height())
        self.crop_widget.setFixedWidth(self.width() // 2)
        self.crop_widget.move((self.width() - self.crop_widget.width())//2, self.height() - self.crop_widget.height())

        # self.draw_widget.resize(400, 100)

        super().resizeEvent(e)


