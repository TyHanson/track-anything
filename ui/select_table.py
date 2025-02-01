from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

# SelectTable Class. Can be called multiple times to be redirected to a different window/index.
# Inputs:
#   controller: allows for easy transfer between windows
#   mapTo: will define what index of stacked_widget the "Submit" button after selection will 
#   redirect the user to
class SelectTable(QWidget) :
    def __init__(self, controller, mapTo):
        super().__init__()
        self.layout = QVBoxLayout()
        self.mapTo = mapTo

        # Button to Return Home with No Table
        self.home = QPushButton("Return Home", self)
        self.layout.addWidget(self.home)
        self.home.clicked.connect(lambda: self.return_home())

        prompt = QLabel("Select Your Desired Tracker and Then Press Submit")
        self.layout.addWidget(prompt)

        self.setLayout(self.layout)
    ''''''     
    # Runs every time the widget switches to this window.
    def showEvent(self, event):
        super().showEvent(event)
        self.dropdown = QComboBox()
        tracker_names = self.ctrl.get_all_tracker_names()
        self.dropdown.addItems(tracker_names)
        self.layout.addWidget(self.dropdown)

        # Add submit button, map to SendTo function for different indexes
        self.submit = QPushButton("Submit", self)
        self.layout.addWidget(self.submit)
        self.submit.clicked.connect(lambda: self.reset_and_send())
    
    # Send chosen table to new window with the selected table name contained
    # in controller attribute "data", remove all widgets added in showEvent,
    # close opened connection.
    def reset_and_send(self) :
        title = self.dropdown.currentText()
        print(f'Title is {title}')
        self.ctrl.data = title
        self.layout.removeWidget(self.dropdown)
        self.layout.removeWidget(self.submit)
        self.ctrl.wm.navigate_to(self.mapTo)

    def return_home(self) :
        self.layout.removeWidget(self.dropdown)
        self.ctrl.wm.navigate_to(0)

    def pre_init(self, controller) :
        self.ctrl = controller