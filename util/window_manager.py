from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

class WindowManager:
    def __init__(self, stacked_widget):
        self.stacked_widget = stacked_widget

    def navigate_to(self, index):
        self.stacked_widget.setCurrentIndex(index)