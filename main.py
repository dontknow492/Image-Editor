from PySide6.QtWidgets import QApplication  # ✅ Correct application class
import sys
from PySide6.QtCore import Qt, QCoreApplication
from gui.interface import MainWindow
from qfluentwidgets import setTheme, Theme
from loguru import logger
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 1 for system DPI, 2 for per-monitor DPI
def main():
    setTheme(Theme.DARK)

    # ✅ Use QApplication instead of QGuiApplication
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseOpenGLES)  # Set before creating QApplication
    app = QApplication(sys.argv)  # ✅ QApplication is required for widgets
    screen = app.primaryScreen()
    dpr = screen.devicePixelRatio()
    logger.info(f"Screen size: {screen.size() }")
    logger.info(f"Device pixel ratio: {dpr}")
    window = MainWindow()
    window.display.load_image(r'D:\Java\DukeWithHelmet.png')
    window.show()

    sys.exit(app.exec())  # ✅ Use sys.exit() to properly close the app

if __name__ == "__main__":
    logger.add(
        "logs/app_{time}.log",  # File name pattern
        rotation="20 MB",  # Rotate after 10MB
        retention="7 days",  # Keep logs for 7 days
        compression="zip",  # Compress old logs with zip
        enqueue=True,  # Better for multithreaded apps
        backtrace=True,  # Show full stacktrace on errors
        diagnose=True,  # Show variable values on exceptions
        level="DEBUG"  # Log level threshold
    )
    main()
