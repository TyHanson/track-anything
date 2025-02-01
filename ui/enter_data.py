from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

class EnterData(QWidget) :
    def __init__(self, controller):
        super().__init__()
        self.has_init = False
        self.layout = QGridLayout()

    def showEvent(self, event):
        super().showEvent(event)  # Call the parent class's showEvent

        stored_title = self.ctrl.data

        self.column_names = [tracker[0] for tracker in self.ctrl.get_tracker_attribute_info(stored_title)]
        
        self.entry_prompt = QLabel("Please enter the data for each attribute and then press Submit")
        self.layout.addWidget(self.entry_prompt, 0, 0, 2, 1)

        # for each column name, create a entry box and prompt
        self.entry_dict = dict()
        for i in range(len(self.column_names)) :
            self.data_label = QLabel(f"{self.column_names[i]}")
            self.layout.addWidget(self.data_label, i + 1, 0, 1, 1)

            self.data_entry = QLineEdit()
            self.layout.addWidget(self.data_entry, i + 1, 1, 1, 1)
            
            self.entry_dict[i] = self.data_entry


        self.submit_button = QPushButton("Confirm Data Submission", self)
        self.layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(lambda: self.write_to_db())

        self.setLayout(self.layout)
        
    def write_to_db(self) :
        to_be_entered = []
        for i in range(len(self.column_names)) :
            value = self.entry_dict[i].text()
            to_be_entered.append(value)
        final = tuple(to_be_entered)

        print(f"INSERT INTO {self.ctrl.data} VALUES {final}")
        self.ctrl.cur.execute(f"INSERT INTO {self.ctrl.data} VALUES {final}")
        self.ctrl.con.commit()
        self.ctrl.wm.data = ''
        self.deconstruct_layout()
        self.ctrl.wm.navigate_to(0)

    def deconstruct_layout(self) :
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

    def pre_init(self, controller) :
        self.ctrl = controller