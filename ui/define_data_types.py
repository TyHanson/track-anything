from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

# This code is a bit messy and will be edited eventually. Some changes that will come...
# Separate each of the different definition sections so this file isn't so LONG!!!
# Nested Dropdowns
# Money Data Type
# Add return home options on all screens
# Ensure variables are cleaned up after every single usage
# Implement editing of data types (currently only works on creation)
# Allow for reordering of attributes after data type definition completion.

class DefineDataTypes(QWidget) :
    def __init__(self, controller):
        super().__init__()
        self.layout = QGridLayout()
        self.attribute_types = ["Float", "Integer", "Text", "Date", "Duration", "Dropdown"]


    # All functions below are built off of this. Users are funneled through this to eventually define all data types.
    def showEvent(self, event):
        super().showEvent(event)

        self.home = QPushButton("Return Home", self)
        self.layout.addWidget(self.home, 0, 0, 1, 2)
        self.home.clicked.connect(lambda: self.return_home())

        tt2 = QLabel("Now, Select the Attribute Type for each of your attributes. The available options are:")
        tt3 = QLabel("Float: Any number including decimals, such as 1, -5.24, and 200.166666.")
        tt4 = QLabel("Integer: Any whole numbers (1, 2, 3, 500). Saves 7 bytes of storage per entry!")
        tt5 = QLabel("Text: Any text with ASCII characters. Do not use this option if you will ONLY be entering numbers.")
        tt6 = QLabel("Date: 03/02/2011, or 02/2011/03, or anything other combo. You can choose the order of month, day, and year.")
        tt7 = QLabel("Duration: A time that can include any strictly decreasing combination of: weeks, days, hours, minutes, and seconds.")
        tt8 = QLabel("Dropdown: A dropdown list of any amount of options to select. Dropdown options be any data type, including another dropdown (max of 5).")

        self.layout.addWidget(tt2, 1, 0, 1, 2)
        self.layout.addWidget(tt3, 2, 0, 1, 2)
        self.layout.addWidget(tt4, 3, 0, 1, 2)
        self.layout.addWidget(tt5, 4, 0, 1, 2)
        self.layout.addWidget(tt6, 5, 0, 1, 2)
        self.layout.addWidget(tt7, 6, 0, 1, 2)
        self.layout.addWidget(tt8, 7, 0, 1, 2)

        self.setLayout(self.layout)

        self.create_table_rq = False
        self.stored_data = self.ctrl.data
        self.tracker_name = None
        self.attribute_names = None

        # Future: Implement ability to tell if this is an edit / create
        if isinstance(self.stored_data, list) :
            self.tracker_name = self.stored_data[0]
            self.attribute_names = self.stored_data[1]
            self.create_table_rq = True
        elif isinstance(self.stored_data, str) :
            self.tracker_name = self.stored_data
            self.attribute_names = [tracker[0] for tracker in self.ctrl.get_tracker_attribute_info()]
        else :
            raise Exception(f"Controller's stored_data didn't contain string or list (via edit data). Instead contained {type(self.stored_data)}")
        
        self.header = QLabel(f"Please set the data types for {self.tracker_name}'s attributes.")
        self.layout.addWidget(self.header, 8, 0, 1, 2)

        # Create option for data type selection for each column name
        self.attribute_to_button = dict()
        final_index = 0
        for i in range(len(self.attribute_names)) :
            self.data_label = QLabel(f"{self.attribute_names[i]}")
            self.layout.addWidget(self.data_label, i + 9, 0, 1, 1)

            # add functionality to show previous type later
            self.choice = QComboBox()
            self.choice.addItems(self.attribute_types)
            self.layout.addWidget(self.choice, i + 9, 1, 1, 1)
            
            self.attribute_to_button[i] = self.choice
            final_index = i+10

        self.submit_button = QPushButton("Confirm Data Submission", self)
        self.layout.addWidget(self.submit_button, final_index, 0, 1, 2)

        if self.create_table_rq :
            # Get Attributes begins funnel into defining all datatypes. write_to_db() is currently unused. I don't know if I'll ever need it...?
            self.submit_button.clicked.connect(lambda: self.get_selected_types())
        else :
            self.submit_button.clicked.connect(lambda: self.write_to_db())


    # Gets selected data types from QComboBox's above. Upon finishing, begins the process of further_definitions.
    def get_selected_types(self) : 
        self.current_index = -1
        self.attributes_final = []
        self.entered_attributes = []
        for i in range(len(self.attribute_to_button)) :
            value = self.attribute_to_button[i].currentText()
            self.entered_attributes.append(value)
        self.further_definitions(self.entered_attributes)


    # Recursive function that goes through all selected data types. Has different functionality based on every data type.
    #   On Float, Int, Text, no need for further definition is required, as each can be input into SQLite database with simple defintions.
    #   On Dropdown, Date, and Duration, each require some user input for customization. See each separate section for specifics.
    def further_definitions(self, remaining_attributes) :
        self.current_index += 1
        if remaining_attributes :
            self.current_attribute_name = self.attribute_names[self.current_index]
            current_attribute = remaining_attributes[0]
            del remaining_attributes[0]
            if current_attribute == "Date" :
                self.define_date(remaining_attributes)
            elif current_attribute == "Duration" :
                self.define_duration(remaining_attributes)
            elif current_attribute == "Dropdown" :
                self.define_dropdown(remaining_attributes, dict())
            elif current_attribute == "Float" :
                self.attributes_final.append(f'Float|{self.current_attribute_name}')
                self.further_definitions(remaining_attributes)
            elif current_attribute == "Text" :
                self.attributes_final.append(f'Text|{self.current_attribute_name}')
                self.further_definitions(remaining_attributes)
            elif current_attribute == "Integer" :
                self.attributes_final.append(f'Integer|{self.current_attribute_name}')
                self.further_definitions(remaining_attributes)
            else :
                raise ValueError("Somehow you managed to have a type that wasn't covered by the main six? What did you do???")
        else :
            # After exhausting remaining_attributes, we reach here which will break the loop and create the database.
            self.create_db()

    # -------------------------------------------------------------------------------------------------- #
    # Define Date Section (Three Functions: define_date, define_date_rewrite_preview, define_date_wrapup)

    # Dates are, well, dates. 1/23/2025, 2025/21/11, or anything else.

    # Dates are inputted in the SQLite3 database in the following format:
    #   Each column variable attached to the "Date" datatype comes with three columns.
    #   Each column corresponds to Month, Day, and Year. The order can be changed to match user desires.
    #   The format of each column title in the SQLite3 database is...
    #       Date|(Day/Month/Year)|(Name of Tracker Attribute)
    # The data type of each of these columns is INTEGER.
    # -------------------------------------------------------------------------------------------------- #

    # Allows you to select the order of the three main date parameters: day, month, year. Defaults to Month, Day, Year.
    # Does not allow the input to pass unless all three of day, month, year are selected.
    def define_date(self, remaining_attributes) :
        self.deconstruct_layout()
        self.home = QPushButton("Return Home", self)
        self.layout.addWidget(self.home)
        self.home.clicked.connect(lambda: self.return_home())
        self.date_title = self.current_attribute_name

        p1 = QLabel("Select Your Date Input Order")
        p2 = QLabel("You will enter dates into your tracker as three independent integer values of Month, Day, and Year.")
        p3 = QLabel("Please choose the order in which you would like to input the three values.")
        
        self.layout.addWidget(p1, 1, 0, 1, 2)
        self.layout.addWidget(p2, 2, 0, 1, 2)
        self.layout.addWidget(p3, 3, 0, 1, 2)

        self.firstTime = QLabel(f"{self.date_title}: Month")
        self.secondTime = QLabel(f"{self.date_title}: Day")
        self.thirdTime = QLabel(f"{self.date_title}: Year")
        self.labels = [self.firstTime, self.secondTime, self.thirdTime]
        
        # Build order of selections. When a box's current text is changed, the preview is updated to reflect it.
        self.choices = ['Month', 'Day', 'Year']
        self.answers = dict()
        self.finished = False
        for i in range(len(self.choices)) :
            choice = QComboBox()
            choice.addItems(self.choices)
            choice.currentTextChanged.connect(lambda: self.define_date_rewrite_preview())
            choice.setCurrentIndex(i)
            self.answers[i] = choice
            self.layout.addWidget(choice, i+4, 0, 1, 1)
        self.finished = True

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
        submit.clicked.connect(lambda: self.define_date_wrapup(remaining_attributes))
        self.layout.addWidget(submit, 11, 0, 1, 2)

    # Supporter function to rewrite the input preview upon changes of QComboBox (containing Month, Day, Year as above)
    def define_date_rewrite_preview(self) :
        if self.finished :
            for i in range(len(self.labels)) :
                current_time = self.answers[i].currentText()
                self.labels[i].setText(f"{self.date_title}: {current_time}")

    # Adds the fully formatted columns to attributes_final. 
    def define_date_wrapup(self, remaining_attributes) :
        time_entries = [entry.currentText() for entry in self.answers.values()]
        if set(time_entries) == set(self.choices) :
            try :
                self.layout.removeWidget(self.error)
            except :
                pass
            
            for i in range(len(time_entries)) :
                if time_entries[i] == "Month" :
                    self.attributes_final.append(f"Date|Month|{self.current_attribute_name}")
                if time_entries[i] == "Day" :
                    self.attributes_final.append(f"Date|Day|{self.current_attribute_name}")
                if time_entries[i] == "Year" :
                    self.attributes_final.append(f"Date|Year|{self.current_attribute_name}")
            
            # Continue down remaining attributes that still need to be defined.
            self.further_definitions(remaining_attributes)
        else :
            # Error case if all three of Day, Month, and Year are not included.
            self.error = QLabel("You need to have all three of: Month, Day, and Year selected to proceed. Please select all three.")
            self.layout.addWidget(self.error, 12, 0, 1, 2)



    # -------------------------------------------------------------------------------------------------- #
    # Define Duration Section (Four Functions: define_duration, define_duration_determine_valid_order, 
    #                           define_duration_choose_input_format, define_duration_wrapup)

    # Durations measure an amount of time, you normally think of it as 12:24, or 12 minutes and 24 seconds.
    # Every value in this column in the databse itself will be a representation of the duration in seconds.

    # Durations support Weeks, Days, Hours, Minutes, and Seconds.
    # You can have any strictly decreasing combination of these. That is, you can have any combination of these
    # where there is not any missing element in between them (like Weeks, Hours as a combination is not valid,
    # because it does not include days. However, Weeks, Days, Hours is valid.)

    # Durations are inputted in the SQLite3 database in the following format:
    #   Each column variable attached to the "Duration" datatype comes with one column.
    #   The format of each column title in the SQLite3 database is...
    #       Duration|(format)|(final_numerical_representation)|(Name of Tracker Attribute)
    #           format refers to the input method. It is either 0 or 1. 0 is default, 1 is alternative.
    #               Refer to define_duration_choose_input_format for more information
    #           final_numerical_representation will be of the form "54321"
    #               5 corresponds to weeks, 4 for days, etc.
    #               This indicates which of the time values to include in the input method.
    # The data type of this column is INTEGER.
    # -------------------------------------------------------------------------------------------------- #

    # Beginning function. This is where the user chooses which of the 5 given time values to include in this definition.
    def define_duration(self, remaining_attributes) :
        self.deconstruct_layout()
        
        self.duration_title = self.current_attribute_name
        l1 = QLabel("Define Duration")
        l2 = QLabel("This comes in multiple parts. First please select the units of time you will be tracking for this attribute.")
        l3 = QLabel("You can do any strictly decreasing combination of: Weeks, Days, Hours, Minutes, and Seconds.")
        l4 = QLabel("That is, you can do (Hours, Minutes, Seconds) or (Weeks, Days) but you can't do (Weeks, Hours, Minutes).")

        self.layout.addWidget(l1, 0, 0, 1, 2)
        self.layout.addWidget(l2, 1, 0, 1, 2)
        self.layout.addWidget(l3, 2, 0, 1, 2)
        self.layout.addWidget(l4, 3, 0, 1, 2)

        # Create the option menu to select which time values to include.
        self.time_values = ['Weeks', 'Days', 'Hours', 'Minutes', 'Seconds']
        self.time_values_dict = dict()
        for i in range(len(self.time_values)) :
            time_value = QLabel(self.time_values[i])
            use_or_not = QComboBox()
            use_or_not.addItems(['Use', "Don't Use"])
            use_or_not.setCurrentIndex(1)
            self.time_values_dict[time_value] = use_or_not
            self.layout.addWidget(time_value, i+4, 0, 1, 1)
            self.layout.addWidget(use_or_not, i+4, 1, 1, 1)

        submit = QPushButton("Submit Time Values", self)
        submit.clicked.connect(lambda: self.define_duration_determine_valid_order(remaining_attributes))
        self.layout.addWidget(submit, 9, 0, 1, 2)

    # Validation function to ensure that the chosen time values are strictly decreasing. Also obtains each of the chosen time values.
    def define_duration_determine_valid_order(self, remaining_attributes) :
        use_or_nots = [value.currentText() for value in self.time_values_dict.values()]
        numerical = []
        self.used_values = []
        is_valid = True
        for i in range(len(use_or_nots)) :
            if use_or_nots[i] == 'Use' :
                numerical.append(i)
                self.used_values.append(self.time_values[i])
        for i in range(len(numerical) - 1) :
            if numerical[i+1] != numerical[i] + 1 :
                is_valid = False
        if not numerical :
            is_valid = False
        
        if is_valid :
            self.define_duration_choose_input_format(remaining_attributes)
        else :
            # Error case that will add to the UI if the order is not strictly decreasing.
            try :
                self.layout.removeWidget(self.error)
                self.error = QLabel("Your chosen time values are not strictly decreasing. Please ensure you have no patterns of (Use, Don't Use, Use) in your time values.")
                self.layout.addWidget(self.error, 10, 0, 1, 2)
            except :
                self.error = QLabel("Your chosen time values are not strictly decreasing. Please ensure you have no patterns of (Use, Don't Use, Use) in your time values.")
                self.layout.addWidget(self.error, 10, 0, 1, 2)
            
    # Allows the user to choose the format of input. If the input contains Week or Days, there is only one available input method, so they just confirm their time values.
    # However, if the input has any combination that ONLY at least two of Hours, Minutes, and/or Seconds, the alternative input method is offered.
    #   Default: Each of Weeks, Days, Hours, etc. is a separate line in data entry to enter a value into.
    #   Alternative: Takes the form of 00:00:00 or 00:00. From left to right in order of size (so Hours:Minutes:Seconds, or Hours:Minutes, or Minutes:Seconds)
    def define_duration_choose_input_format(self, remaining_attributes) :
        self.deconstruct_layout()
        l1 = QLabel("Define Duration")
        
        self.layout.addWidget(l1, 0, 0, 1, 4)
        
        # Check if alternative input method should be offered
        if 'Weeks' not in self.used_values and 'Days' not in self.used_values and len(self.used_values) >= 2 :
            l2 = QLabel("You can choose between two different formats for how you will input your duration.")
            self.layout.addWidget(l2, 1, 0, 1, 4)

            # Option 1, Normal.
            l3 = QLabel("Default: Input is separated by time value, with you inputting numbers as needed.")
            l4 = QLabel("For your chosen time values, inputing data would look like this.")
            self.layout.addWidget(l3, 2, 0, 1, 2)
            self.layout.addWidget(l4, 3, 0, 1, 2)
            current_row = 4

            for value in self.used_values :
                time_value = QLabel(f'{self.duration_title}: {value}')
                empty_entry = QLineEdit()
                self.layout.addWidget(time_value, current_row, 0, 1, 1)
                self.layout.addWidget(empty_entry, current_row, 1, 1, 1)
                current_row += 1

            # Option 2, 00:00:00
            l5 = QLabel("Alternative: Input is done on a 00:00:00 basis, corresponding to hours, minutes, seconds.")
            l6 = QLabel("For your chosen time values, you would be requested to input data in this format.")
            
            input_str = '00'
            for i in range(len(self.used_values) - 1) :
                input_str += ":00"
            empty_entry = QLineEdit()
            empty_entry.setPlaceholderText(input_str)
            title = QLabel(self.duration_title)
            l8 = QLabel('Note that "00" does not have to be only 2 digits. As long as you have colons separating each value it will be valid.')
            l9 = QLabel('For example, if 00:00 is minutes and seconds, you can do 110:15 to signify 1 hour, 50 minutes and 15 seconds.')
            l10 = QLabel("Similarly, if you have 00:00:00, you could do 00:120:12 for 2 hours and 12 seconds. Don't know why you would, but you could!")

            self.layout.addWidget(l5, 2, 2, 1, 2)
            self.layout.addWidget(l6, 3, 2, 1, 2)
            self.layout.addWidget(title, 4, 2, 1, 1)
            self.layout.addWidget(empty_entry, 4, 3, 1, 1)
            self.layout.addWidget(l8, 5, 2, 1, 2)
            self.layout.addWidget(l9, 6, 2, 1, 2)
            self.layout.addWidget(l10, 7, 2, 1, 2)

            submit1 = QPushButton("Choose Default Option", self)
            submit1.clicked.connect(lambda: self.define_duration_wrapup(remaining_attributes, self.used_values, 0))
            self.layout.addWidget(submit1, 8, 0, 1, 2)

            submit2 = QPushButton("Choose Alternative Option", self)
            submit2.clicked.connect(lambda: self.define_duration_wrapup(remaining_attributes, self.used_values, 1))
            self.layout.addWidget(submit2, 8, 2, 1, 2)

            submit3 = QPushButton("Return to Time Value Selection", self)
            submit3.clicked.connect(lambda: self.define_duration(remaining_attributes))
            self.layout.addWidget(submit3, 9, 0, 1, 4)
        else :
            # Default case, alternative method is not offered.
            l2 = QLabel("You will be inputting duration data as so.")
            self.layout.addWidget(l2, 1, 0, 1, 2)

            l3 = QLabel("Input is separated by time value, with you inputting numbers as needed.")
            l4 = QLabel("For your chosen time values, inputing data would look like this.")
            self.layout.addWidget(l3, 2, 0, 1, 2)
            self.layout.addWidget(l4, 3, 0, 1, 2)
            current_row = 4

            for value in self.used_values :
                time_value = QLabel(f'{self.duration_title}: {value}')
                empty_entry = QLineEdit()
                self.layout.addWidget(time_value, current_row, 0, 1, 1)
                self.layout.addWidget(empty_entry, current_row, 1, 1, 1)
                current_row += 1
            
            l5 = QLabel("Please confirm that these are your desired selections.")
            l6 = QLabel("If not, you can return back to the time value selection screen.")
            
            submit = QPushButton("Confirm Selections", self)
            submit.clicked.connect(lambda: self.define_duration_wrapup(remaining_attributes, self.used_values, 0))
            self.layout.addWidget(submit, current_row, 0, 1, 2)
            current_row += 1

            submit = QPushButton("Return to Time Value Selection", self)
            submit.clicked.connect(lambda: self.define_duration(remaining_attributes))
            self.layout.addWidget(submit, current_row, 0, 1, 2)

    # Adds the fully formatted column into attributes_final.
    def define_duration_wrapup(self, remaining_attributes, time_values, format) :
        final_numerical_representation = ''
        for i in range(len(time_values)) :
            if time_values[i] == 'Weeks' :
                final_numerical_representation += '5'
            if time_values[i] == 'Days' :
                final_numerical_representation += '4'
            if time_values[i] == 'Hours' :
                final_numerical_representation += '3'
            if time_values[i] == 'Minutes' :
                final_numerical_representation += '2'
            if time_values[i] == 'Seconds' :
                final_numerical_representation += '1'
        self.attributes_final.append(f"Duration|{format}|{final_numerical_representation}|{self.current_attribute_name}")
        self.further_definitions(remaining_attributes)



    # -------------------------------------------------------------------------------------------------- #
    # Define Dropdown Section (Three Functions: define_dropdown, define_dropdown_add_element, define_dropdown_wrapup)

    # A dropdown takes the form of a QComboBox (or just a dropdown). Rather than typing an input, you select from
    # a predetermined list of inputs that a user define in this section.
    # Those inputs can be of the forms: Integer, Text, and Float. (Dropdowns will come later)

    # Dropdowns are inputted in the SQLite3 database in the following format:
    #   Each column variable attached to the "Dropdown" datatype comes with x columns, where x is the number of dropdown options added.
    #   The format of each option column in the SQLite3 database is...
    #       Dropdown|(Dropdown Option Data Type)|(Dropdown Option Name/Value)|(Name of Tracker Attribute)
    # The datatype of each column is INTEGER, but moreso as a Boolean with 1 indicating that option was chosen, and 0 indicating it wasn't.
    # -------------------------------------------------------------------------------------------------- #

    # Note that there are many commented out functions right now. This is because I was implemented nested dropdowns, but
    # then I decided to come back to that for another time. Leaving it here so I can pick work back up on it easier.

    # Beginning function. Where each of the dropdown options are defined with their datatype and name.
    def define_dropdown(self, remaining_attributes, dropdown_dict) :
        self.deconstruct_layout()
        self.current_layer = 1
        self.dropdown_attributes = ['Float', 'Integer', 'Text']
        self.home = QPushButton("Return Home", self)
        self.layout.addWidget(self.home, 0, 0, 1, 2)
        self.home.clicked.connect(lambda: self.return_home())

        title = QLabel("Define Your Dropdown")
        lab1 = QLabel("Please enter a name and data type for your dropdown options. Note every dropdown must have at least two options to choose from.")
        '''lab2 = QLabel("You may have different data types in your dropdown if you want, including another dropdown. There is no limit to how many layers of dropdowns you can have.")
        lab3 = QLabel("If you choose one of your dropdown options to be another dropdown, you will return to this screen to define that next dropdown's options.")'''
        lab4 = QLabel("After resolving all dropdown options, you will be shown an example of how your dropdown will function, and then be prompted to submit after review.")

        self.layout.addWidget(title, 1, 0, 1, 2)
        self.layout.addWidget(lab1, 2, 0, 1, 2)
        '''self.layout.addWidget(lab2, 3, 0, 1, 2)
        self.layout.addWidget(lab3, 4, 0, 1, 2)'''
        self.layout.addWidget(lab4, 5, 0, 1, 2)

        # Begin Dropdown Option Entries

        labOptionName = QLabel("Option Name")
        labOptionType = QLabel("Option Data Type")
        self.layout.addWidget(labOptionName, 6, 0, 1, 1)
        self.layout.addWidget(labOptionType, 6, 1, 1, 1)

        self.current_pos = 7
        self.count_options = 0
        self.dropdown_options = dict()
        # There must be a minimum of two dropdown entries. The button to add more dropdown entries is defined in the function below.
        for i in range(2) :
            self.define_dropdown_add_element(remaining_attributes, dropdown_dict)

    # Builds each new potential entry to the dropdown, while moving the button to access this function down each time a new one is added.
    def define_dropdown_add_element(self, remaining_attributes, dropdown_dict) :
        try :
            self.layout.removeWidget(self.addElement)
            self.layout.removeWidget(self.confirmType)
        except :
            pass

        name = QLineEdit()
        choice = QComboBox()
        choice.addItems(self.dropdown_attributes)
        '''choice.currentTextChanged.connect(lambda: self.define_dropdown_check_types())'''
        self.dropdown_options[self.count_options] = [name, choice]
        self.layout.addWidget(name, self.current_pos, 0, 1, 1)
        self.layout.addWidget(choice, self.current_pos, 1, 1, 1)
        self.current_pos += 1
        self.count_options += 1

        self.addElement = QPushButton("Add Dropdown Option", self)
        self.layout.addWidget(self.addElement, self.current_pos, 0, 1, 2)
        self.addElement.clicked.connect(lambda: self.define_dropdown_add_element(remaining_attributes, dropdown_dict))

        self.confirmType = QPushButton("Confirm Dropdown Option Selections", self)
        self.layout.addWidget(self.confirmType, self.current_pos + 1, 0, 1, 2)
        self.confirmType.clicked.connect(lambda: self.define_dropdown_wrapup(remaining_attributes))

    '''def define_dropdown_confirmation(self, remaining_attributes, dropdown_dict) :
        # using layers_list, build out each off the q_combo boxes.
        # initialize len(layers_list) QComboBoxs
        pass

    def define_dropdown_check_types(self) :
        pass'''
 
    # Adds the fully formatted column into attributes_final. Used to have input parameter "dropdown_dict"
    def define_dropdown_wrapup(self, remaining_attributes) :
        options = self.dropdown_options.values()
        option_names = [option[0].text() for option in options]
        option_types = [option[1].currentText() for option in options]
        for i in range(len(option_names)) :
            if option_types[i] == 'Float' :
                self.attributes_final.append(f"Dropdown|Float|{option_names[i]}|{self.current_attribute_name}")
            elif option_types[i] == 'Integer' :
                self.attributes_final.append(f"Dropdown|Integer|{option_names[i]}|{self.current_attribute_name}")
            elif option_types[i] == 'Text' :
                self.attributes_final.append(f"Dropdown|Text|{option_names[i]}|{self.current_attribute_name}")
            '''if option_types[i] == 'Dropdown' :
                self.attributes_final.append(f"DD|Float|{self.tracker_name}")'''
            
        self.further_definitions(remaining_attributes)
        '''if not "Dropdown" in option_types :
            pass
            # add the columns based on the current_layer
            self.further_definitions(remaining_attributes)
        else :
            self.current_layer += 1
            self.further_definitions(remaining_attributes)'''
        

    # After finishing further_definitions (i.e. all data types have been fully defined), we create the table in the database for this tracker.
    # All trackers will have an id column for a primary key.
    def create_db(self) :
        # Create beginning of the final command (a SQL query that we build from each of the datatypes)
        final_command = f'CREATE TABLE "{self.tracker_name}" (id INTEGER PRIMARY KEY AUTOINCREMENT, '
        for i in range(len(self.attributes_final)) :
            current_char = ''
            total_str = ''
            str_index = 0

            # Acquire the data type from the beginning of the string in attributes_final
            while current_char != '|' :
                total_str += current_char
                current_char = self.attributes_final[i][str_index]
                str_index += 1
            
            # Depending on the tracker data type, define the SQLite3 data type as described in function descriptions. And also what it says here.
            add_on = ''
            if total_str == "Float" :
                add_on = f'"{self.attributes_final[i]}" REAL, '
            if total_str == "Integer" or total_str == "Dropdown" or total_str == "Date" or total_str == "Duration" :
                add_on = f'"{self.attributes_final[i]}" INTEGER, '
            if total_str == "Text" :
                add_on = f'"{self.attributes_final[i]}" TEXT, '
            final_command += add_on

        # Remove the ", " from the final_command and then close the SQL statement
        final_command = final_command[:-2]
        final_command += ")"

        # keeping this here bc I think it's useful and important
        print('Executing this command onto SQLite3:', final_command)

        # Push the command to the cursor
        self.ctrl.cur.execute(final_command)

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