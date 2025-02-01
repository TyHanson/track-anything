from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

class ViewData(QWidget) :
    def __init__(self, controller):
        super().__init__()
        self.layout = QVBoxLayout()
        
        # SQL query, default to all data in order of recency. Have the ability to narrow search.

        # Label
        self.view_label = QLabel("View Data")
        self.layout.addWidget(self.view_label)
        

        # Button to Return Home with No Table
        self.home_button = QPushButton("Return Home", self)
        self.layout.addWidget(self.home_button)
        self.home_button.clicked.connect(lambda: self.ctrl.wm.navigate_to(0))

        self.setLayout(self.layout)

    def pre_init(self, controller) :
        self.ctrl = controller