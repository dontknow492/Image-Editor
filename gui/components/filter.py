from typing import Callable, Optional, Union, Dict, Any

from PIL import Image
from PIL.ImageQt import ImageQt  # Use ImageQt for QImage conversion
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from qfluentwidgets import ImageLabel, StrongBodyLabel

from gui.common.myScroll import FlowScrollWidget
from gui.common.myFrame import VerticalFrame
from utils.enums import FilterType

from loguru import logger

class FilterWidget(VerticalFrame):
    """
    A widget to display a filter thumbnail and its name.
    """
    clicked = Signal()

    def __init__(self, size: QSize = QSize(100, 100), parent: Optional[Any] = None) -> None:
        """
        Initialize the FilterWidget.

        Args:
            size: The desired size of the thumbnail.
            parent: The parent widget.
        """
        super().__init__(parent=parent)
        self.size = size
        self.setLayoutMargins(0, 0, 0, 0)
        self.setContentSpacing(0)
        self._setup_ui()
        self.setMaximumWidth(size.width())

    def _setup_ui(self) -> None:
        """
        Setup UI elements of the filter widget.
        """
        # Set up thumbnail image label
        self.thumbnail_label = ImageLabel(
            r"D:\Program\Image Editor\resources\images\no_image_placeholder.jpg", self
        )
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setFixedSize(self.size)
        self.thumbnail_label.setBorderRadius(10, 10, 10, 10)

        # Set up title label
        self.title_label = StrongBodyLabel("Name", self)
        self.addWidget(self.thumbnail_label)
        self.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignHCenter)

    def set_image(self, image: ImageQt) -> None:
        """
        Set the image to be displayed as thumbnail.

        Args:
            image: A QImage converted from a PIL Image.
        """
        self.thumbnail_label.setPixmap(image)
        self.thumbnail_label.setFixedSize(self.size)

    def set_title(self, title: str) -> None:
        """
        Set the title of the filter.

        Args:
            title: The name of the filter.
        """
        self.title_label.setText(title)
        self.setObjectName(title)

    def mousePressEvent(self, event) -> None:
        """
        Handle mouse press events and emit a signal if left-clicked.
        """
        # logger.info(f"Clicked on filter: {self.title_label.text()}")
        if event.button() == Qt.MouseButton.LeftButton:
            logger.info(f"Clicked on filter: {self.title_label.text()}")
            self.clicked.emit()


class FilterWindow(FlowScrollWidget):
    """
    A window that displays multiple filter widgets and applies filters to an image.
    """
    filter_clicked = Signal(object) #return a function, parameter
    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the FilterWindow with predefined filters.

        Args:
            parent: The parent widget.
        """
        super().__init__("", parent=parent)
        self.setStyleSheet("background: rgba(25, 33, 42, 0.6); border-radius: 5px;")
        self.image: Optional[Image.Image] = None
        self._create_filter_widgets()

    def set_image(self, image: Union[Image.Image, ImageQt, str, QImage]) -> None:
        """
        Set the image to apply filters on.

        Args:
            image: A PIL Image, QImage, or file path string.
        """
        logger.info("Setting image for filters.")
        if isinstance(image, str):
            image = Image.open(image)
        elif isinstance(image, ImageQt):
            image = Image.fromqimage(image)
        elif isinstance(image, QImage):
            image = Image.fromqimage(image)
        self.image = image
        self.update_image()

    def update_image(self) -> None:
        """
        Update all filter widgets with the filtered thumbnails.
        """
        if self.image is None:
            logger.warning("No image set to update filters.")
            return

        resized_image = self._resize_image(self.image)
        logger.info("Updating filter widgets with new image.")

        for i in range(self.count()):
            widget = self.itemAt(i).widget()
            if isinstance(widget, FilterWidget):
                filter_type = getattr(FilterType, widget.objectName(), None)
                if filter_type:
                    filtered_image = filter_type.apply(resized_image)
                    widget.set_image(ImageQt(filtered_image))

    def _resize_image(self, image: Image.Image, size: tuple = (100, 100)) -> Image.Image:
        return image.resize(size, Image.Resampling.LANCZOS)

    def _create_filter_widgets(self) -> None:
        """
        Create and add all filter widgets to the layout.
        """
        for filter_type in FilterType:
            widget = self._create_filter_widget(filter_type)
            self.addWidget(widget)

    def _create_filter_widget(self, filter_type: FilterType) -> FilterWidget:
        """
        Create an individual filter widget.

        Args:
            filter_type: The FilterType enum value.

        Returns:
            An instance of FilterWidget.
        """
        widget = FilterWidget()
        widget.set_title(filter_type.name)
        widget.setObjectName(filter_type.name)  # Use enum name for reference

        if self.image:
            logger.info(f"Applying filter {filter_type.name} to create thumbnail.")
            filtered_image = filter_type.apply(self.image.resize((100, 100), Image.Resampling.LANCZOS))
            widget.set_image(ImageQt(filtered_image))

        widget.clicked.connect(lambda f=filter_type: self.apply_filter(f))
        return widget

    def apply_filter(self, filter_type: FilterType) -> Optional[FilterType]:
        """
        Apply the selected filter to the image.

        Args:
            filter_type: The FilterType enum to apply.

        Returns:
            The applied FilterType if successful, otherwise None.
        """
        if self.image is not None and filter_type:
            self.filter_clicked.emit(filter_type)
            return filter_type  # Return the applied filter for tracking

        logger.warning("No image available or no valid filter function to apply.")
        return None  # Return None if no filter was applied

if  __name__ == "__main__":
    app = QApplication([])
    # window = FilterWidget()
    # window.clicked.connect(lambda : print("clicked"))
    img = "D:/Downloads/Images/nature-images.jpg"
    window = FilterWindow()

    window.set_image(img)
    window.filter_clicked.connect(lambda f: print("this is signal:", f))
    window.show()
    app.exec()
