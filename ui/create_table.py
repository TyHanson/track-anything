from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

class CreateTable(QWidget):
    # after returning to this after moving to enter_data, the submit a column button doesn't work
    def __init__(self, controller):
        super().__init__()
        self.layout = QVBoxLayout()
        self.accepting_entries = True
        self.entries = []
        self.title = ""

        # Error Creation (if necessary)
        self.error = QLabel("Your either do not have at least one column name, or your tracker has no title.")

        # Prompt for Titles
        self.title_prompt = QLabel("Please enter a Title")
        self.layout.addWidget(self.title_prompt)

        # Current Title
        self.current_title = QLabel("Current Title: N/A")
        self.layout.addWidget(self.current_title)

        # Entry box for Title
        self.title_entry = QLineEdit()
        self.title_entry.setPlaceholderText("Enter a Title for your Tracker")
        self.layout.addWidget(self.title_entry)

        # Button for Title Submit
        self.title_button = QPushButton("Submit A Tracker Title", self)
        self.layout.addWidget(self.title_button)
        self.title_button.clicked.connect(self.title_input)
        
        # Prompt for Entry
        self.prompt = QLabel("Please Enter Column Titles")
        self.layout.addWidget(self.prompt)

        # History of Entries
        self.history_label = QLabel("History:")
        self.layout.addWidget(self.history_label)

        # Entry Line
        self.line_entry = QLineEdit()
        self.line_entry.setPlaceholderText("Enter your text")
        self.layout.addWidget(self.line_entry)

        # Button for Submit
        self.submit_button = QPushButton("Submit A Column Title", self)
        self.layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_input)

        # Button for End
        self.end_button = QPushButton("Finish", self)
        self.layout.addWidget(self.end_button)
        self.end_button.clicked.connect(self.end_input)

        # Button to Return Home with No Table
        self.home_button = QPushButton("Return Home", self)
        self.layout.addWidget(self.home_button)
        self.home_button.clicked.connect(lambda: self.ctrl.wm.navigate_to(0))

        self.setLayout(self.layout)

    def submit_input(self) :
        if self.accepting_entries :
            entry = self.line_entry.text()
            self.entries.append(entry)
            self.history_label.setText(f"History:\n" + "\n".join(self.entries))
            self.line_entry.clear()

    def title_input(self) :
        self.title = self.title_entry.text()
        self.current_title.setText(f"Current Title: " + self.title)
        self.title_entry.clear()
    
    def end_input(self) :
        # Clean up entry phase
        if self.title != "" and len(self.entries) > 0 :
            self.error.hide()
            self.accepting_entries = False
            self.history_label.setText("History:")
            self.current_title.setText("Current Title:")
            self.ctrl.data = list([self.title, self.entries])
            print(self.title, self.entries)
            print(self.ctrl.data)
            self.title = ""
            self.entries = []
            print(f'now controller data is {self.ctrl.data}')
            self.ctrl.wm.navigate_to(4)
            # COMMENTED OUT FOR TESTING ON VIEWING TABLES W/O DATA TYPE MODS self.ctrl.wm.navigate_to(4)
        else :
            self.layout.addWidget(self.error)
            self.error.show()

    def pre_init(self, controller) :
        self.ctrl = controller