from qfluentwidgets import TransparentToolButton, FluentIconBase, FlyoutViewBase, Flyout, FluentIcon

from gui.common.myFrame import VerticalFrame,  HorizontalFrame
from PySide6.QtWidgets import QHBoxLayout
from loguru import logger

class FlyoutWidget(FlyoutViewBase):
    def __init__(self, layout: str = "horizontal", parent=None):
        """
        :param layout: horizontal, vertical
        :param parent: qobject
        """
        super().__init__(parent)
        print(self.layout())
        self._setup_ui(layout)
        # self.setFixedSize(300, 300)

    def _setup_ui(self, layout: str):
        # Add your UI components here
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        if  layout.lower() == "horizontal":
            self.main_container = HorizontalFrame(self)
        elif layout.lower() == "vertical":
            self.main_container = VerticalFrame(self)
        else:
            logger.error("Invalid layout type so setting to default: Horizontal")
            self.main_layout = HorizontalFrame(self)
        self.main_layout.addWidget(self.main_container)

    def add_widget(self, widget):
        self.main_container.addWidget(widget)

class FlyoutButton(TransparentToolButton):
    def __init__(self, icon: FluentIconBase, layout: str = "horizontal", parent=None):
        """
        :param layout: horizontal, vertical
        :param parent: qobject
        """
        super().__init__(parent)
        self.setIcon(icon)
        self.flyout = FlyoutWidget(layout=layout)
        # self.flyout.hide()
        self.clicked.connect(self.show_flyout)

    def show_flyout(self):
        Flyout.make(self.flyout, self, self.parent(), isDeleteOnClose=False)

    def add_flyout_widget(self, widget):
        self.flyout.add_widget(widget)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QPushButton
    app = QApplication([])
    frame = VerticalFrame()
    window = FlyoutButton(FluentIcon.BRUSH, "horizontal",  parent = frame)
    for x in range(3):
    #
        window.add_flyout_widget(QPushButton("Button " + str(x)))
    frame.show()
    app.exec()