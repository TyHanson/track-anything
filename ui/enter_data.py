from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp

class EnterData(QWidget) :
    def __init__(self, controller):
        super().__init__()
        self.has_init = False
        self.layout = QGridLayout()

    def showEvent(self, event):
        super().showEvent(event)  # Call the parent class's showEvent

        self.stored_title = self.ctrl.data

        self.tracker_info = self.ctrl.get_tracker_attribute_info(self.stored_title)

        # Note that the 0th entry in all of these is the primary key for the tracker. We always will ignore this in UI stuff.
        self.attribute_names = [attribute[0] for attribute in self.tracker_info]
        self.attribute_types = [attribute[1] for attribute in self.tracker_info]
        self.encoded_attributes = [attribute[2] for attribute in self.tracker_info]
        self.sql_datatype = [attribute[3] for attribute in self.tracker_info]
        self.column_ids = [attribute[4] for attribute in self.tracker_info]
        
        self.entry_prompt = QLabel("Please enter the data for each attribute and then press Submit")
        self.layout.addWidget(self.entry_prompt, 0, 0, 2, 1)

        # Create entry dict (for validation of valid input methods)
        self.entry_dict = dict()
        self.entry_dict['Duration_Alternative'] = []
        self.entry_dict['Date'] = []

        # Create entry list (just to have all possible entries, easier to manage/access)
        self.entry_list = []

        # Create list to correspond entry boxes to individual columns
        # This is not a good solution. I should change this. I'm not going to right now but future
        # you will change this for sure.
        self.entry_to_attribute = []
        current_entry = 0

        # Create all input methods
        skip_amount = 0
        current_row = 1
        for i in range(1, len(self.tracker_info)) :
            print('Looking at:', self.tracker_info[i])
            # In case of dropdown or date, we handle all entries for each individual instance of that data type
            # at once. Dates will always skip 2 columns afterward, while dropdowns skip total options - 1 columns.
            if skip_amount != 0 :
                print("Except we're skipping that column.")
                skip_amount -= 1
                continue

            if self.attribute_types[i] == "Float" :
                data_label = QLabel(f"{self.attribute_names[i]}")
                self.layout.addWidget(data_label, current_row, 0, 1, 1)

                data_entry = QLineEdit()
                data_entry.setPlaceholderText('2, 5.3, 0.0053')
                data_entry.setValidator(QDoubleValidator())
                self.entry_list.append([data_entry, 'Float'])
                self.layout.addWidget(data_entry, current_row, 1, 1, 1)
                self.entry_to_attribute.append(current_entry)
                current_entry += 1
                current_row += 1

            if self.attribute_types[i] == "Text" :
                data_label = QLabel(f"{self.attribute_names[i]}")
                self.layout.addWidget(data_label, current_row, 0, 1, 1)

                data_entry = QLineEdit()
                regex = QRegExp(".*")
                validator = QRegExpValidator(regex)
                data_entry.setValidator(validator)
                data_entry.setPlaceholderText('Hi, Woah, 3, L0L...')
                self.entry_list.append([data_entry, 'Text'])
                self.layout.addWidget(data_entry, current_row, 1, 1, 1)
                self.entry_to_attribute.append(current_entry)
                current_entry += 1
                current_row += 1

            if self.attribute_types[i] == "Integer" :
                data_label = QLabel(f"{self.attribute_names[i]}")
                self.layout.addWidget(data_label, current_row, 0, 1, 1)

                data_entry = QLineEdit()
                data_entry.setValidator(QIntValidator())
                data_entry.setPlaceholderText('0, 1, 4, 12...')
                self.entry_list.append([data_entry, 'Integer'])
                self.layout.addWidget(data_entry, current_row, 1, 1, 1)
                self.entry_to_attribute.append(current_entry)
                current_entry += 1
                current_row += 1

            if self.attribute_types[i] == "Dropdown" :
                dropdown_title = self.attribute_names[i]
                current_attribute_name = self.attribute_names[i]
                current_index = i
                options = []
                while current_attribute_name == dropdown_title :
                    split_encoded = self.encoded_attributes[current_index].split("|")
                    dropdown_option_name = split_encoded[2]
                    options.append(dropdown_option_name)
                    current_index += 1
                    current_attribute_name = self.attribute_names[current_index]
                the_dropdown = QComboBox()
                the_dropdown.addItems(options)
                self.entry_list.append([the_dropdown, 'Dropdown'])
                # Is this the best way to go about this? I don't think so. 
                # Let's keep this on the original entry_list and make use of the new
                # second part of list indicating the data type to read it's data
                self.entry_to_attribute.append(current_entry)
                current_entry += 1
                skip_amount = len(options) - 1

                data_label = QLabel(f"{self.attribute_names[i]}")
                self.layout.addWidget(data_label, current_row, 0, 1, 1)

                self.layout.addWidget(the_dropdown, current_row, 1, 1, 1)
                current_row += 1

            if self.attribute_types[i] == "Duration" :
                split_encoded = self.encoded_attributes[i].split("|")
                if split_encoded[1] == '0' :
                    for j in range(len(split_encoded[2])) :
                        time_value = ''
                        if split_encoded[2][j] == '5' :
                            time_value = 'Weeks'
                        elif split_encoded[2][j] == '4' :
                            time_value = 'Days'
                        elif split_encoded[2][j] == '3' :
                            time_value = 'Hours'
                        elif split_encoded[2][j] == '2' :
                            time_value = 'Minutes'
                        elif split_encoded[2][j] == '1' :
                            time_value = 'Seconds'
                        data_label = QLabel(f"{self.attribute_names[i]}, {time_value}")
                        self.layout.addWidget(data_label, current_row, 0, 1, 1)

                        data_entry = QLineEdit()
                        data_entry.setValidator(QIntValidator())
                        # How am I going to make sure it's able to identify this as part of original
                        # What if two durations, 5+4, then 3+2 and are separate?
                        # Access the original encoding, I think.
                        self.entry_list.append([data_entry, f'Duration|{split_encoded[2]}'])
                        data_entry.setPlaceholderText('Time: 0, 1, 4, 12...')
                        self.layout.addWidget(data_entry, current_row, 1, 1, 1)
                        current_row += 1
                        self.entry_to_attribute.append(current_entry)
                    current_entry += 1

                if split_encoded[1] == '1' :
                    if len(split_encoded[2]) == 3 :
                        data_label = QLabel(f"{self.attribute_names[i]}, Hour:Min:Sec")
                        self.layout.addWidget(data_label, current_row, 0, 1, 1)

                        data_entry = QLineEdit()
                        data_entry.setPlaceholderText('00:00:00')
                        self.entry_list.append([data_entry, 'Duration_Alternative'])
                        self.entry_dict['Duration_Alternative'].append([data_entry, 3])
                        self.layout.addWidget(data_entry, current_row, 1, 1, 1)
                    else :
                        time_label = ''
                        for j in range(len(split_encoded[2])) :
                            if split_encoded[2][j] == '3' :
                                time_label += 'Hour:'
                            elif split_encoded[2][j] == '2' :
                                time_label += 'Min'
                            elif split_encoded[2][j] == '1' :
                                time_label += ':Sec'
                        data_label = QLabel(f"{self.attribute_names[i]}, {time_label}")
                        self.layout.addWidget(data_label, current_row, 0, 1, 1)
                        
                        data_entry = QLineEdit()
                        data_entry.setPlaceholderText('00:00')
                        self.entry_list.append([data_entry, 'Duration_Alternative'])
                        self.entry_dict['Duration_Alternative'].append([data_entry, 2])
                        self.layout.addWidget(data_entry, current_row, 1, 1, 1)
                    self.entry_to_attribute.append(current_entry)
                    current_entry += 1
                    current_row += 1
                    

            if self.attribute_types[i] == "Date" :
                for j in range(3) :
                    index = j+i
                    split_encoded = self.encoded_attributes[index].split("|")
                    time_value = split_encoded[1]
                    data_label = QLabel(f"{self.attribute_names[i]}: {time_value}")
                    self.layout.addWidget(data_label, current_row + j, 0, 1, 1)

                    data_entry = QLineEdit()
                    data_entry.setValidator(QIntValidator())
                    data_entry.setPlaceholderText(f"A part of 2/14/2025")
                    self.entry_list.append([data_entry, 'Date'])
                    self.entry_dict['Date'].append([data_entry, 'Date', time_value])
                    self.layout.addWidget(data_entry, current_row + j, 1, 1, 1)
                    self.entry_to_attribute.append(current_entry)
                current_entry += 1
                skip_amount = 2
                current_row += 3

        self.submit_button = QPushButton("Confirm Data Submission", self)
        self.layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(lambda: self.confirm_valid_inputs())
        print(self.entry_to_attribute)

        self.setLayout(self.layout)
        
    # We use validators to ensure other inputs HAVE to be correct. However, we must validate duration alternative and date
    # For date, validate month (1-12), and date (must be 1-31). Maybe add month-by-month functionality too?
    def confirm_valid_inputs(self) :
        is_valid = True
        errors_list = []

        # Ensure that no entry boxes are empty. Note we don't want to worry about anything
        # we cover in the above section.
        for i in range(len(self.entry_list)) :
            entry = self.entry_list[i]
            if entry[1] != 'Dropdown' :
                if entry[0].text() == '' :
                    is_valid = False
                    entry[0].setStyleSheet("border: 2px solid red;")
                    errors_list.append('Empty_Entry')
                else :
                    entry[0].setStyleSheet('')

        # Confirm validity of the specific data types
        for key in self.entry_dict.keys() :
            for j in range(len(self.entry_dict[key])) :
                entry = self.entry_dict[key][j]
                if key == 'Duration_Alternative' :
                    duration_valid = True
                    duration_split = entry[0].text().split(":")
                    print(duration_split)
                    if len(duration_split) == 2 or len(duration_split) == 3 :
                        entry[0].setStyleSheet("")
                    else :
                        print('Duration Alternative Error, in length')
                        duration_valid = False
                        entry[0].setStyleSheet("border:2px solid red;")
                        errors_list.append('Duration_Alternative, Colons')
                    if duration_valid :
                        for i in range(len(duration_split)) :
                            try :
                                int(duration_split[i])
                                entry[0].setStyleSheet("")
                            except :
                                print('Duration Alternative Error: in Int Typing')
                                duration_valid = False
                                entry[0].setStyleSheet("border: 2px solid red;")
                                errors_list.append('Duration_Alternative, Int')
                                break
                    if not duration_valid :
                        is_valid = False

                if key == 'Date' :
                    # months_days_list = [[1, 3, 5, 7, 8, 10, 12], [4, 6, 9, 11], [2]]
                    days_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
                    months_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
                    if entry[2] == 'Month' :
                        if entry[0].text() not in months_list :
                            is_valid = False
                            entry[0].setStyleSheet("border: 2px solid red;")
                            errors_list.append('Date_Month')
                        else : 
                            entry[0].setStyleSheet("")
                    if entry[2] == 'Day' :
                        if entry[0].text() not in days_list :
                            is_valid = False
                            entry[0].setStyleSheet("border: 2px solid red;")
                            errors_list.append('Date_Day')
                        else :
                            entry[0].setStyleSheet("")
                    if entry[2] == 'Year' :
                        # If you want your year to be negative, 0, or 10 billion, go for it. 
                        pass

        if is_valid :
            print("Valid input!")
            self.write_to_db()
        else :
            print("Unvalid input :(")


    def write_to_db(self) :
        '''to_be_entered = []
        for i in range(len(self.column_names)) :
            value = self.entry_dict[i].text()
            to_be_entered.append(value)
        final = tuple(to_be_entered)'''

        entry_list_index = 0
        to_skip = 1
        final_list = []
        for i in range(0, len(self.tracker_info)) :
            print(self.tracker_info[i])
            # Text, Int, Float, Duration_Alternative all are simplest case (access entry_list[0].text())
            # Date insert into 3 columns (int)
            # Dropdown pull from original
            # Duration
            # we're here rn
            
            if to_skip != 0 :
                to_skip -= 1
                continue

            if self.attribute_types[i] == 'Dropdown' :
                # to_be_inserted.append(self.entry_list[0].currentText())
                combo_box = self.entry_list[entry_list_index][0]
                chosen = combo_box.currentIndex()
                for j in range(combo_box.count()) :
                    if j != chosen :
                        final_list.append(0)
                    else :
                        final_list.append(1)
                entry_list_index += 1
                to_skip = combo_box.count() - 1

            elif self.attribute_types[i] == 'Date' :
                for j in range(3) :
                    entry = self.entry_list[entry_list_index][0]
                    final_list.append(int(entry.text()))
                    entry_list_index += 1
                to_skip = 2

            elif self.attribute_types[i] == 'Duration' :
                split_encoded = self.encoded_attributes[i].split("|")
                all_time_values = [0, 0, 0, 0, 0]
                if split_encoded[1] == '0' :
                    for j in range(len(split_encoded[2])) :
                        current_entry = self.entry_list[entry_list_index][0]
                        if split_encoded[2][j] == '5' :
                            all_time_values[0] = int(current_entry.text())
                        elif split_encoded[2][j] == '4' :
                            all_time_values[1] = int(current_entry.text())
                        elif split_encoded[2][j] == '3' :
                            all_time_values[2] = int(current_entry.text())
                        elif split_encoded[2][j] == '2' :
                            all_time_values[3] = int(current_entry.text())
                        elif split_encoded[2][j] == '1' :
                            all_time_values[4] = int(current_entry.text())
                        entry_list_index += 1
                    in_seconds = self.ctrl.duration_to_seconds(all_time_values)
                    final_list.append(in_seconds)
                elif split_encoded[1] == '1' :
                    entry = self.entry_list[entry_list_index][0]
                    duration_split = entry.text().split(":")
                    duration_split_index = 0
                    for j in range(len(split_encoded[2])) :
                        current_split_int = int(duration_split[duration_split_index])
                        if split_encoded[2][j] == '5' :
                            all_time_values[0] = current_split_int
                        elif split_encoded[2][j] == '4' :
                            all_time_values[1] = current_split_int
                        elif split_encoded[2][j] == '3' :
                            all_time_values[2] = current_split_int
                        elif split_encoded[2][j] == '2' :
                            all_time_values[3] = current_split_int
                        elif split_encoded[2][j] == '1' :
                            all_time_values[4] = current_split_int
                        duration_split_index += 1
                    in_seconds = self.ctrl.duration_to_seconds(all_time_values)
                    final_list.append(in_seconds)
                    entry_list_index += 1
            
            elif self.attribute_types[i] == 'Float' :
                print(self.attribute_types[i])
                current_entry = self.entry_list[entry_list_index][0]
                final_list.append(float(current_entry.text()))
                entry_list_index += 1

            elif self.attribute_types[i] == 'Integer' :
                print(self.attribute_types[i])
                current_entry = self.entry_list[entry_list_index][0]
                final_list.append(int(current_entry.text()))
                entry_list_index += 1

            elif self.attribute_types[i] == 'Text' :
                print(self.attribute_types[i])
                current_entry = self.entry_list[entry_list_index][0]
                final_list.append(current_entry.text())
                entry_list_index += 1

            

        final = tuple(final_list)
        del self.encoded_attributes[0]
        used_columns = tuple(self.encoded_attributes)
        print(f'Now Executing...')
        print(f'INSERT INTO "{self.stored_title}" {used_columns} VALUES {final}')
        self.ctrl.cur.execute(f"INSERT INTO {self.stored_title} {used_columns} VALUES {final}")
        self.ctrl.con.commit()
        print(f'Finished adding data into {self.stored_title}. Returning home...')
        self.ctrl.wm.data = ''
        self.deconstruct_layout()
        self.ctrl.wm.navigate_to(0)

    def deconstruct_layout(self) :
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

    def pre_init(self, controller) :
        self.ctrl = controller