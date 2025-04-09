from PySide6.QtWidgets import QGroupBox
from qfluentwidgets import isDarkTheme


class GroupBox(QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _apply_qss(self):
        color = "white" if isDarkTheme() else "black"  # Fix color selection
        style_sheet = f"""
            QGroupBox {{
                font: bold 16px;   
                color: {color};    
                border: 2px solid gray;
                border-radius: 5px;
                margin-top: 10px; 
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left; 
                padding: 5px; 
            }}
        """
        self.setStyleSheet(style_sheet)

    def paintEvent(self, event):
        self._apply_qss()
        super().paintEvent(event)