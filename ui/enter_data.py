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
        super().showEvent(event)

        print("Confirming current entriesin enter_data...")

        # Get tracker info (ctrl.data is from select_table)
        self.tracker_name = self.ctrl.data
        self.tracker_info = self.ctrl.get_tracker_attribute_info(self.tracker_name)

        # Note that the 0th entry in all of these is the primary key for the tracker. We always will ignore this in UI stuff.
        self.attribute_names = [attribute[0] for attribute in self.tracker_info]
        self.attribute_types = [attribute[1] for attribute in self.tracker_info]
        self.encoded_attributes = [attribute[2] for attribute in self.tracker_info]
        self.sql_datatype = [attribute[3] for attribute in self.tracker_info]
        self.column_ids = [attribute[4] for attribute in self.tracker_info]
        
        self.prompt = QLabel("Please enter the data for each attribute and then press Submit")
        self.layout.addWidget(self.prompt, 0, 0, 2, 1)

        # Create entry dict (for any external validition of input methods beyond QInt + QTextValidators)
        self.unique_text_validators = dict()
        self.unique_text_validators['Duration_Alternative'] = []
        self.unique_text_validators['Date'] = []

        # Create entry list (to access each QLineEdit for each entry)
        self.entry_list = []

        # Logs where in self.attribute_types we are. Essentially is responsible to ensuring every column in the tracker is hit
        cur_entry = 0

        # Create all input methods
        skip_amount = 0
        cur_row = 1
        for i in range(1, len(self.tracker_info)) :
            # print('Looking at:', self.tracker_info[i])

            # In case of dropdown or date, we handle all entries for each individual instance of that data type
            # at once. Dates will always skip 2 columns afterward, while dropdowns skip (total options) - 1 columns.
            if skip_amount != 0 :
                # print("Except we're skipping that column.")
                skip_amount -= 1
                continue

            # Float handling
            if self.attribute_types[i] == "Float" :
                attribute_name = QLabel(f"{self.attribute_names[i]}")
                self.layout.addWidget(attribute_name, cur_row, 0, 1, 1)

                entry_box = QLineEdit()
                entry_box.setPlaceholderText('2, 5.3, 0.0053')
                entry_box.setValidator(QDoubleValidator())
                self.layout.addWidget(entry_box, cur_row, 1, 1, 1)

                self.entry_list.append([entry_box, 'Float'])
                cur_entry += 1
                cur_row += 1

            # Text handling
            if self.attribute_types[i] == "Text" :
                attribute_name = QLabel(f"{self.attribute_names[i]}")
                self.layout.addWidget(attribute_name, cur_row, 0, 1, 1)

                entry_box = QLineEdit()
                regex = QRegExp(".*")
                validator = QRegExpValidator(regex)
                entry_box.setValidator(validator)
                entry_box.setPlaceholderText('Hi, Woah, 3, L0L...')
                self.layout.addWidget(entry_box, cur_row, 1, 1, 1)
                
                self.entry_list.append([entry_box, 'Text'])
                cur_entry += 1
                cur_row += 1

            # Integer handling
            if self.attribute_types[i] == "Integer" :
                attribute_name = QLabel(f"{self.attribute_names[i]}")
                self.layout.addWidget(attribute_name, cur_row, 0, 1, 1)

                entry_box = QLineEdit()
                entry_box.setValidator(QIntValidator())
                entry_box.setPlaceholderText('0, 1, 4, 12...')
                self.layout.addWidget(entry_box, cur_row, 1, 1, 1)
                
                self.entry_list.append([entry_box, 'Integer'])
                cur_entry += 1
                cur_row += 1

            # Dropdown handling
            if self.attribute_types[i] == "Dropdown" :
                dropdown_title = self.attribute_names[i]
                cur_attribute_name = self.attribute_names[i]
                cur_index = i
                options = []
                # Access all dropdown options based on the attribute name column attached to tracker_info
                # When it's not that, we stop the loop.
                while cur_attribute_name == dropdown_title :
                    split_encoded = self.encoded_attributes[cur_index].split("|")
                    dropdown_option = split_encoded[2]
                    options.append(dropdown_option)
                    cur_index += 1
                    # Error case if the dropdown is the last attribute in the tracker (would normally crash bc indexing error)
                    if cur_index >= len(self.attribute_names) :
                        break
                    cur_attribute_name = self.attribute_names[cur_index]
                    
                attribute_name = QLabel(f"{self.attribute_names[i]}")
                self.layout.addWidget(attribute_name, cur_row, 0, 1, 1)
                
                dropdown = QComboBox()
                dropdown.addItems(options)
                self.entry_list.append([dropdown, 'Dropdown'])
                self.layout.addWidget(dropdown, cur_row, 1, 1, 1)

                cur_entry += 1
                skip_amount = len(options) - 1
                cur_row += 1

            # duration handling
            if self.attribute_types[i] == "Duration" :
                split_encoded = self.encoded_attributes[i].split("|")

                # Default version handling (one time value per row)
                if split_encoded[1] == '0' :
                    for j in range(len(split_encoded[2])) :
                        time_unit = ''
                        if split_encoded[2][j] == '5' :
                            time_unit = 'Weeks'
                        elif split_encoded[2][j] == '4' :
                            time_unit = 'Days'
                        elif split_encoded[2][j] == '3' :
                            time_unit = 'Hours'
                        elif split_encoded[2][j] == '2' :
                            time_unit = 'Minutes'
                        elif split_encoded[2][j] == '1' :
                            time_unit = 'Seconds'
                        
                        attribute_name = QLabel(f"{self.attribute_names[i]}, {time_unit}")
                        entry_box = QLineEdit()
                        entry_box.setValidator(QIntValidator())
                        entry_box.setPlaceholderText('Time: 0, 1, 4, 12...')
                        self.layout.addWidget(attribute_name, cur_row, 0, 1, 1)
                        self.layout.addWidget(entry_box, cur_row, 1, 1, 1)
                        
                        self.entry_list.append([entry_box, f'Duration|{split_encoded[2]}'])
                        cur_row += 1
                    cur_entry += 1

                # Alternative version handling (00:00, 00:00:00 entry)
                if split_encoded[1] == '1' :
                    # 00:00:00 version
                    if len(split_encoded[2]) == 3 :
                        attribute_name = QLabel(f"{self.attribute_names[i]}, Hour:Min:Sec")
                        self.layout.addWidget(attribute_name, cur_row, 0, 1, 1)

                        entry_box = QLineEdit()
                        entry_box.setPlaceholderText('00:00:00')
                        self.entry_list.append([entry_box, 'Duration_Alternative'])
                        self.unique_text_validators['Duration_Alternative'].append([entry_box, 3])
                        self.layout.addWidget(entry_box, cur_row, 1, 1, 1)
                    # 00:00 version
                    else :
                        time_label = ''
                        for j in range(len(split_encoded[2])) :
                            if split_encoded[2][j] == '3' :
                                time_label += 'Hour:'
                            elif split_encoded[2][j] == '2' :
                                time_label += 'Min'
                            elif split_encoded[2][j] == '1' :
                                time_label += ':Sec'
                        attribute_name = QLabel(f"{self.attribute_names[i]}, {time_label}")
                        self.layout.addWidget(attribute_name, cur_row, 0, 1, 1)
                        
                        entry_box = QLineEdit()
                        entry_box.setPlaceholderText('00:00')
                        self.entry_list.append([entry_box, 'Duration_Alternative'])
                        self.unique_text_validators['Duration_Alternative'].append([entry_box, 2])
                        self.layout.addWidget(entry_box, cur_row, 1, 1, 1)

                    cur_entry += 1
                    cur_row += 1
                    
            # Date handling
            if self.attribute_types[i] == "Date" :
                for j in range(3) :
                    index = j+i
                    split_encoded = self.encoded_attributes[index].split("|")
                    time_unit = split_encoded[1]
                    attribute_name = QLabel(f"{self.attribute_names[i]}: {time_unit}")
                    self.layout.addWidget(attribute_name, cur_row + j, 0, 1, 1)

                    entry_box = QLineEdit()
                    entry_box.setValidator(QIntValidator())
                    entry_box.setPlaceholderText(f"A part of 2/14/2025")
                    self.entry_list.append([entry_box, 'Date'])
                    self.unique_text_validators['Date'].append([entry_box, 'Date', time_unit])
                    self.layout.addWidget(entry_box, cur_row + j, 1, 1, 1)

                cur_entry += 1
                skip_amount = 2
                cur_row += 3

        self.submit = QPushButton("Confirm Data Submission", self)
        self.layout.addWidget(self.submit)
        self.submit.clicked.connect(lambda: self.confirm_valid_inputs())

        self.setLayout(self.layout)
        
    # We use validators to ensure the correct input on some columns. There are exceptions though.
    #   Dropdowns
    #   Durations
    def confirm_valid_inputs(self) :
        is_valid = True
        errors_list = []

        # Ensure that no entry boxes are empty (ignoring dropdown boxes)
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
        for key in self.unique_text_validators.keys() :
            for j in range(len(self.unique_text_validators[key])) :
                entry = self.unique_text_validators[key][j]

                # Duration Handling (Alternative)
                # Note we don't need to confirm default because it's just split rows.
                if key == 'Duration_Alternative' :
                    duration_valid = True
                    duration_split = entry[0].text().split(":")
                    print(duration_split)
                    # Check to see if entry was of form 00:00:00 or 00:00
                    if len(duration_split) == 2 or len(duration_split) == 3 :
                        entry[0].setStyleSheet("")
                    else :
                        print('Duration Alternative Error, in length')
                        duration_valid = False
                        entry[0].setStyleSheet("border:2px solid red;")
                        errors_list.append('Duration_Alternative, Colons')

                    # Check to ensure that whatever is in xx:xx:xx or xx:xx is an integer    
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

                # Date handling
                if key == 'Date' :
                    # months_days_list = [[1, 3, 5, 7, 8, 10, 12], [4, 6, 9, 11], [2]]
                    days_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
                    months_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
                    # Make sure the month is between 1-12
                    if entry[2] == 'Month' :
                        if entry[0].text() not in months_list :
                            is_valid = False
                            entry[0].setStyleSheet("border: 2px solid red;")
                            errors_list.append('Date_Month')
                        else : 
                            entry[0].setStyleSheet("")
                    
                    # Make sure day is between 1-31
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
            print("The input is valid!")
            self.write_to_db()
        else :
            print("Invalid input... :(")


    def write_to_db(self) :
        cur_entry = 0
        to_skip = 1
        all_entries = []
        for i in range(0, len(self.tracker_info)) :
            
            if to_skip != 0 :
                to_skip -= 1
                continue

            # Dropdown handling
            if self.attribute_types[i] == 'Dropdown' :
                combo_box = self.entry_list[cur_entry][0]
                chosen = combo_box.currentIndex()
                for j in range(combo_box.count()) :
                    if j != chosen :
                        all_entries.append(0)
                    else :
                        all_entries.append(1)
                cur_entry += 1
                to_skip = combo_box.count() - 1

            # Date handling
            elif self.attribute_types[i] == 'Date' :
                for j in range(3) :
                    entry = self.entry_list[cur_entry][0]
                    all_entries.append(int(entry.text()))
                    cur_entry += 1
                to_skip = 2

            # Duration handling
            elif self.attribute_types[i] == 'Duration' :
                split_encoded = self.encoded_attributes[i].split("|")
                all_time_units = [0, 0, 0, 0, 0]
                
                # Default duration
                if split_encoded[1] == '0' :
                    for j in range(len(split_encoded[2])) :
                        cur_entry = self.entry_list[cur_entry][0]
                        #optimize this part UDmby
                        
                        if split_encoded[2][j] == '5' :
                            all_time_units[0] = int(cur_entry.text())
                        elif split_encoded[2][j] == '4' :
                            all_time_units[1] = int(cur_entry.text())
                        elif split_encoded[2][j] == '3' :
                            all_time_units[2] = int(cur_entry.text())
                        elif split_encoded[2][j] == '2' :
                            all_time_units[3] = int(cur_entry.text())
                        elif split_encoded[2][j] == '1' :
                            all_time_units[4] = int(cur_entry.text())
                        cur_entry += 1
                    in_seconds = self.ctrl.duration_to_seconds(all_time_units)
                    all_entries.append(in_seconds)
                
                # Alternate duration
                elif split_encoded[1] == '1' :
                    entry = self.entry_list[cur_entry][0]
                    duration_split = entry.text().split(":")
                    duration_split_index = 0
                    for j in range(len(split_encoded[2])) :
                        current_split_int = int(duration_split[duration_split_index])
                        if split_encoded[2][j] == '5' :
                            all_time_units[0] = current_split_int
                        elif split_encoded[2][j] == '4' :
                            all_time_units[1] = current_split_int
                        elif split_encoded[2][j] == '3' :
                            all_time_units[2] = current_split_int
                        elif split_encoded[2][j] == '2' :
                            all_time_units[3] = current_split_int
                        elif split_encoded[2][j] == '1' :
                            all_time_units[4] = current_split_int
                        duration_split_index += 1
                    in_seconds = self.ctrl.duration_to_seconds(all_time_units)
                    all_entries.append(in_seconds)
                    cur_entry += 1
            
            # Float, Integer, Text handling
            elif self.attribute_types[i] == 'Float' :
                print(self.attribute_types[i])
                cur_entry = self.entry_list[cur_entry][0]
                all_entries.append(float(cur_entry.text()))
                cur_entry += 1

            elif self.attribute_types[i] == 'Integer' :
                print(self.attribute_types[i])
                cur_entry = self.entry_list[cur_entry][0]
                all_entries.append(int(cur_entry.text()))
                cur_entry += 1

            elif self.attribute_types[i] == 'Text' :
                print(self.attribute_types[i])
                cur_entry = self.entry_list[cur_entry][0]
                all_entries.append(cur_entry.text())
                cur_entry += 1

            
        # Convert list of entered text into tuple for SQLite3 command creation
        final = tuple(all_entries)
        
        # Because we ignore primary index, take tracker's encoded column titles and delete index from it
        del self.encoded_attributes[0]
        used_columns = tuple(self.encoded_attributes)
        
        print(f'Now Executing...')
        print(f'INSERT INTO "{self.tracker_name}" {used_columns} VALUES {final}')
        self.ctrl.cur.execute(f"INSERT INTO {self.tracker_name} {used_columns} VALUES {final}")
        self.ctrl.con.commit()
        print(f'Finished adding data into {self.tracker_name}. Returning home...')
        self.ctrl.wm.data = ''
        self.deconstruct_layout()
        self.ctrl.wm.navigate_to(0)

    # Remove all objects on screen to be repainted again next open
    def deconstruct_layout(self) :
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

    def pre_init(self, controller) :
        self.ctrl = controller