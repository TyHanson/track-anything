from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

class DefineDataTypes(QWidget) :
    def __init__(self, controller):
        super().__init__()
        self.layout = QGridLayout()
        self.attribute_types = ["Float", "Integer", "Text", "Date", "Duration", "Dropdown"]


    def showEvent(self, event):
        super().showEvent(event)

        # Draw all persisting objects
        self.home = QPushButton("Return Home", self)
        self.layout.addWidget(self.home)
        self.home.clicked.connect(lambda: self.return_home())

        tt2 = QLabel("Now, Select the Attribute Type for each of your attributes. The available options are:")
        tt3 = QLabel("Float: Any number including decimals, such as 1, -5.24, and 200.166666.")
        tt4 = QLabel("Integer: Any whole numbers (1, 2, 3, 500). Saves 7 bytes of storage per entry!")
        tt5 = QLabel("Text: Any text with ASCII characters. Do not use this option if you will ONLY be entering numbers.")
        tt6 = QLabel("Date: 03/02/2011, or 02/2011/03, or anything other combo. You can choose the order of month, day, and year.")
        tt7 = QLabel("Duration: A time that can include any strictly decreasing combination of: weeks, days, hours, minutes, and seconds.")
        tt8 = QLabel("Dropdown: A dropdown list of any amount of options to select. Dropdown options be any data type, including another dropdown (max of 5).")

        self.layout.addWidget(tt2)
        self.layout.addWidget(tt3)
        self.layout.addWidget(tt4)
        self.layout.addWidget(tt5)
        self.layout.addWidget(tt6)
        self.layout.addWidget(tt7)
        self.layout.addWidget(tt8)

        self.setLayout(self.layout)

        self.create_table_rq = False
        self.stored_data = self.ctrl.data
        self.tracker_name = None
        self.attribute_names = None

        if isinstance(self.stored_data, list) :
            print('found list')
            self.tracker_name = self.stored_data[0]
            self.attribute_names = self.stored_data[1]
            self.create_table_rq = True
        elif isinstance(self.stored_data, str) :
            print('found string')
            self.tracker_name = self.stored_data
            self.attribute_names = [tracker[0] for tracker in self.ctrl.get_tracker_attribute_info()]
        else :
            raise Exception(f"Controller's stored_data didn't contain string or list (via edit data). Instead contained {type(self.stored_data)}")
        
        self.header = QLabel(f"Please set the data types for {self.tracker_name}'s attributes.")
        self.layout.addWidget(self.header, 9, 0, 2, 1)

        # for each column name, create a entry box and prompt
        self.attribute_to_button = dict()
        for i in range(len(self.attribute_names)) :
            self.data_label = QLabel(f"{self.attribute_names[i]}")
            self.layout.addWidget(self.data_label, i + 10, 0, 1, 1)

            # add functionality to show previous type
            self.choice = QComboBox()
            self.choice.addItems(self.attribute_types)
            self.layout.addWidget(self.choice, i + 10, 1, 1, 1)
            
            self.attribute_to_button[i] = self.choice

        self.submit_button = QPushButton("Confirm Data Submission", self)
        self.layout.addWidget(self.submit_button)

        if self.create_table_rq :
            self.submit_button.clicked.connect(lambda: self.get_attributes())
        else :
            self.submit_button.clicked.connect(lambda: self.write_to_db())

    # note we have tracker name as self.tracker_name and attribute titles as self.attribute_names
    def get_attributes(self) : 
        # acquire inputted datatypes
        self.current_index = -1
        self.attributes_final = [] # may not need this one?
        self.attributes_divided = []
        self.entered_attributes = []
        for i in range(len(self.attribute_to_button)) :
            value = self.attribute_to_button[i].currentText()
            self.entered_attributes.append(value)
        self.further_definitions(self.entered_attributes)

    # iterates through the entered attributes one attribute at a time and 
    def further_definitions(self, remaining_attributes) :
        self.current_index += 1
        if remaining_attributes :
            current_attribute = remaining_attributes[0]
            del remaining_attributes[0]
            if current_attribute == "Date" :
                print('define_date')
            # Need 3 different columns for each part of the date. 1DateM_, 2DateD_, 3DateY_
                self.define_date(remaining_attributes)
            elif current_attribute == "Duration" :
                print('define duration')
                self.define_duration(remaining_attributes)
            elif current_attribute == "Dropdown" :
                print('define dropdown')
                # Need n diff columns, or map an integer to each entry in the dropdown.
                # Where do we store the correlation between integers to entries? Only thing saved is the column.
                # Primary key corresponds to entry in the dropdown?
                # When we choose an option in dropdown option and getCurrentText, retrieve a dictionary defined as
                # entire reference column with each option serving as the key to get the value for the int.
                # That column that stores the dropdown key reference, all following entries should be called "IGNORE THIS" or something.
                self.define_dropdown(remaining_attributes)
            else :
                print(f'defined {current_attribute}')
                self.attributes_final.append(current_attribute)
                self.further_definitions(remaining_attributes)
        else :
            # empty list case so move to create database
            print('finished')
            #self.create_db()

    def define_date(self, remaining_attributes) :
        self.deconstruct_layout()
        self.home = QPushButton("Return Home", self)
        self.layout.addWidget(self.home)
        self.home.clicked.connect(lambda: self.return_home())

        p1 = QLabel("Select Your Date Input Order")
        p2 = QLabel("You will enter dates into your tracker as three independent integer values of Month, Day, and Year.")
        p3 = QLabel("Please choose the order in which you would like to input the three values.")
        
        self.layout.addWidget(p1, 1, 0, 1, 2)
        self.layout.addWidget(p2, 2, 0, 1, 2)
        self.layout.addWidget(p3, 3, 0, 1, 2)

        self.firstTime = QLabel(f"{self.attribute_names[self.current_index]}: Month")
        self.secondTime = QLabel(f"{self.attribute_names[self.current_index]}: Day")
        self.thirdTime = QLabel(f"{self.attribute_names[self.current_index]}: Year")
        self.labels = [self.firstTime, self.secondTime, self.thirdTime]
        
        choices = ['Month', 'Day', 'Year']
        self.answers = dict()
        self.finished = False
        for i in range(len(choices)) :
            print(self.answers)
            choice = QComboBox()
            choice.addItems(choices)
            choice.currentTextChanged.connect(lambda: self.define_date_rewrite_preview())
            choice.setCurrentIndex(i)
            self.answers[i] = choice
            self.layout.addWidget(choice, i+4, 0, 1, 1)
        self.finished = True
        print('answers is', self.answers)

        p4 = QLabel("With your chosen order, entering in date data in your tracker will look like this:")
        self.layout.addWidget(p4, 7, 0, 1, 2)


        emptyFill1 = QLineEdit()
        emptyFill2 = QLineEdit()
        emptyFill3 = QLineEdit()

        self.layout.addWidget(self.firstTime, 8, 0, 1, 1)
        self.layout.addWidget(self.secondTime, 9, 0, 1, 1)
        self.layout.addWidget(self.thirdTime, 10, 0, 1, 1)
        self.layout.addWidget(emptyFill1, 8, 1, 1, 1)
        self.layout.addWidget(emptyFill2, 9, 1, 1, 1)
        self.layout.addWidget(emptyFill3, 10, 1, 1, 1)
        
        submit = QPushButton("Submit Date Order", self)
        submit.clicked.connect(lambda: self.further_definitions(remaining_attributes))
        self.layout.addWidget(submit, 11, 0, 1, 2)
        # self.further_definitions(remaining_attributes)

    def define_date_rewrite_preview(self) :
        # implement functionality to change the value of the choices to always have all 3 input at once. It should switch things around.
        if self.finished :
            for i in range(len(self.labels)) :
                current_time = self.answers[i].currentText()
                self.labels[i].setText(f"{self.attribute_names[self.current_index]}: {current_time}")
            print("Changed define_data QComboBox Value")

    def define_date_wrapup(self) :
        pass

    def define_duration(self, remaining_attributes) :

        self.further_definitions(remaining_attributes)
        pass

    def define_dropdown(self, remaining_attributes) :

        self.further_definitions(remaining_attributes)
        pass
    
    def create_db(self, attributes, attributes_divided) :
        sql_attribute_names, sql_datatypes = self.ctrl.convert_attributes_to_sql(attributes, attribute_names)
        print(f'sql attributues is {sql_attribute_names}')
        print(f'data_types is {sql_datatypes}')

        final_command = f"CREATE TABLE {title} ("
        for i in range(len(sql_datatypes)) :
            add_on = f'{sql_attribute_names[i]} {sql_datatypes[i]}, '
            final_command += add_on
        final_command = final_command[:-2]
        final_command += ")"

        # This code works, the final_command as-is will create the database as we want it. The issue is how we're going to internally manage
        # the new attribute types.
        print(final_command)

        # create the full db
        # create_command = f"CREATE TABLE {title}({", ".join(entries)})"
        #self.ctrl.cur.execute(create_command)

        # clean everything up and send back to home
        self.deconstruct_layout()
        self.ctrl.wm.navigate_to(0)

    def write_to_db(self, title, entries, attributes) :
        pass

    def deconstruct_layout(self) :
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

    def return_home(self) :
        # self.layout.removeWidget(self.dropdown)
        self.ctrl.wm.navigate_to(0)

    def pre_init(self, controller) :
        self.ctrl = controller