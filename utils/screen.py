from PySide6.QtWidgets import QApplication
def get_screen_size():
    screen = QApplication.primaryScreen()
    dpr = screen.devicePixelRatio()
    return screen.size() * dpr

def get_screen_dpi():
    screen = QApplication.primaryScreen()
    return screen.devicePixelRatio()