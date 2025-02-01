from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

# Homescreen window. Contains buttons and redirects to following windows:
#   Enter Data: (maps to SelectTableEntry, index 2)
#   Create Tracker: (maps to CreateNew, index 1)
#   View/Edit Tracker: (maps to)
class HomeScreen(QWidget) :
    def __init__(self, controller):
        super().__init__()
        self.layout = QVBoxLayout()

        # Label
        self.home_label = QLabel("Track Anything")
        self.layout.addWidget(self.home_label)

        # Enter Data Button
        self.enter_button = QPushButton("Enter Data", self)
        self.layout.addWidget(self.enter_button)
        self.enter_button.clicked.connect(lambda: self.ctrl.wm.navigate_to(2))

        # Create Tracker Button
        self.create_button = QPushButton("Create Tracker", self)
        self.layout.addWidget(self.create_button)
        self.create_button.clicked.connect(lambda: self.ctrl.wm.navigate_to(3))

        # Choose Tracker Button
        self.choose_button = QPushButton("Choose A Tracker to View/Edit", self)
        self.layout.addWidget(self.choose_button)
        self.choose_button.clicked.connect(lambda: self.ctrl.wm.navigate_to(6))

        self.setLayout(self.layout)

    def pre_init(self, controller) :
        self.ctrl = controller