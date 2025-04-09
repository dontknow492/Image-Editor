from qfluentwidgets import FluentIcon, SegmentedToolWidget

from PySide6.QtWidgets import QApplication

app = QApplication([])
sw = SegmentedToolWidget()

# Add tab items
sw.addItem(routeKey="songInterface", icon=FluentIcon.TRANSPARENT, onClick=lambda: print("Song"))
sw.addItem(routeKey="albumInterface", icon=FluentIcon.CHECKBOX, onClick=lambda: print("Album"))
sw.addItem(routeKey="artistInterface", icon=FluentIcon.CONSTRACT, onClick=lambda: print("Artist"))

# Set the current tab item
sw.setCurrentItem("albumInterface")

# Get the current tab item
print(sw.currentItem())
sw.show()
app.exec()
