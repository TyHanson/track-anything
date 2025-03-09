from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget


class ViewData(QWidget) :
    def __init__(self, controller):
        super().__init__()
        self.layout = QGridLayout()
        
    def showEvent(self, event):
        super().showEvent(event)
        # Access all tracker information

        # Get title from controller (SelectTable)
        self.stored_title = self.ctrl.data

        # Get information and split it into component parts
        self.tracker_info = self.ctrl.get_tracker_attribute_info(self.stored_title)

        self.attribute_names = [attribute[0] for attribute in self.tracker_info]
        self.attribute_types = [attribute[1] for attribute in self.tracker_info]
        self.encoded_attributes = [attribute[2] for attribute in self.tracker_info]
        self.sql_datatype = [attribute[3] for attribute in self.tracker_info]
        self.column_ids = [attribute[4] for attribute in self.tracker_info]
        
        # Label
        self.view_label = QLabel(f"View Data Central: {self.stored_title}")
        self.layout.addWidget(self.view_label, 0, 0, len(self.attribute_names), 1)

        # although i understand how to navigate pandas better, let's try using SQL for this.
        res = self.ctrl.cur.execute(f"SELECT * FROM {self.stored_title}")
        self.all_rows_unparsed = res.fetchall()
        self.all_rows_unparsed = [list(row) for row in self.all_rows_unparsed]

        # define lists for 
        self.all_info = []
        self.attribute_names_condensed = []

        # Parse data from all_rows and insert into separate list of lists
        # Goal here is to make a framework for row-by-row, transfer data
        # from all_rows into the single row it should be
        cur_entry = 0
        skip_amount = 0
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
                res = self.ctrl.cur.execute(f'SELECT "{self.encoded_attributes[i]}" FROM {self.stored_title}')
                data = res.fetchall()
                float_data = [float(row[0]) for row in data]
                self.all_info.append(float_data)
                self.attribute_names_condensed.append(self.attribute_names[i])
                cur_entry += 1

            # Text handling
            if self.attribute_types[i] == "Text" :
                res = self.ctrl.cur.execute(f'SELECT "{self.encoded_attributes[i]}" FROM {self.stored_title}')
                data = res.fetchall()
                str_data = [str(row[0]) for row in data]
                self.all_info.append(str_data)
                self.attribute_names_condensed.append(self.attribute_names[i])
                cur_entry += 1

            # Integer handling
            if self.attribute_types[i] == "Integer":
                res = self.ctrl.cur.execute(f'SELECT "{self.encoded_attributes[i]}" FROM {self.stored_title}')
                data = res.fetchall()
                int_data = [int(row[0]) for row in data]
                self.all_info.append(int_data)
                self.attribute_names_condensed.append(self.attribute_names[i])
                cur_entry += 1

            # Dropdown handling
            if self.attribute_types[i] == "Dropdown" :
                dropdown_title = self.attribute_names[i]
                cur_attribute_name = self.attribute_names[i]
                cur_index = i
                count = 0
                full = []
                # Access all dropdown options based on the attribute name column attached to tracker_info
                # When it's not that, we stop the loop.
                while cur_attribute_name == dropdown_title :
                    res = self.ctrl.cur.execute(f'SELECT "{self.encoded_attributes[cur_index]}" FROM {self.stored_title}')
                    data = res.fetchall()
                    cur_index += 1
                    count += 1
                    int_data = [int(row[0]) for row in data]
                    full.append(int_data)
                    # Error case if the dropdown is the last attribute in the tracker (would normally crash bc indexing error)
                    if cur_index >= len(self.attribute_names) :
                        break
                    cur_attribute_name = self.attribute_names[cur_index]

                self.all_info.append(full)#convert fullinto what it needs to be)
                self.attribute_names_condensed.append(dropdown_title)
                cur_entry += 1
                skip_amount = count - 1

            # duration handling
            if self.attribute_types[i] == "Duration" :
                split_encoded = self.encoded_attributes[i].split("|")
                included_values = [False, False, False, False, False]
                for j in range(len(split_encoded[2])) :
                    time_unit = ''
                    if split_encoded[2][j] == '5' :
                        included_values[0] = True
                    elif split_encoded[2][j] == '4' :
                        included_values[1] = True
                    elif split_encoded[2][j] == '3' :
                        included_values[2] = True
                    elif split_encoded[2][j] == '2' :
                        included_values[3] = True
                    elif split_encoded[2][j] == '1' :
                        included_values[4] = True

                # Default version handling (one time value per row)
                if split_encoded[1] == '0' :
                    res = self.ctrl.cur.execute(f'SELECT "{self.encoded_attributes[i]}" FROM {self.stored_title}')
                    data = res.fetchall()
                    final = []
                    for entry in data :
                        final.append(self.ctrl.duration_to_split(int(entry[0]), included_values))
                    # convert these into a string that gives each of the time_values
                    self.all_info.append(final)
                    cur_entry += 1

                # Alternative version handling (00:00, 00:00:00 entry)
                if split_encoded[1] == '1' :
                    # 00:00:00 version
                    res = self.ctrl.cur.execute(f'SELECT "{self.encoded_attributes[i]}" FROM {self.stored_title}')
                    data = res.fetchall()
                    self.all_info.append(data)
                    self.attribute_names_condensed.append(self.attribute_names[i])
                    cur_entry += 1

                self.attribute_names_condensed.append(self.attribute_names[i])
                    
            # Date handling
            if self.attribute_types[i] == "Date" :
                all_three = []
                for j in range(3) :
                    index = j+i
                    res = self.ctrl.cur.execute(f'SELECT "{self.encoded_attributes[index]}" FROM {self.stored_title}')
                    data = res.fetchall()
                    int_data = [int(row[0]) for row in data]
                    all_three.append(int_data)
                self.all_info.append(all_three)
                cur_entry += 1
                skip_amount = 2

        for row in self.all_info :
            print(row)

        # Define table view customization
        self.rows_per_view = 10 # default
        self.last_displayed_row_idx = 9
        self.current_row = self.all_rows[0]
        self.next_row = self.all_rows[10]

        # Create table to be displayed
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(self.rows_per_view)
        self.table_widget.setColumnCount(len(self.all_rows[0]))
        self.table_widget.setHorizontalHeaderLabels(self.attribute_names)

        self.update_table()
        
        # Button to Return Home with No Table
        self.home_button = QPushButton("Return Home", self)
        self.layout.addWidget(self.home_button)
        self.home_button.clicked.connect(lambda: self.return_home())

        self.setLayout(self.layout)

    def update_table(self) :
        # Access number of rows
        # into table_widget, get rid of all previous rows
        # replace with all available rows left to be viewed
        # We will need to have a variable that tracks:
        #   Where we are in the full table
        #   The current next element to be displayed
        #       Error case: when next element is none.
        #       If none then we don't run update table?
        self.table_widget.clearContents()
        ''' Add in functionality to read from a qLineEntry for rows_per_view '''
        self.table_widget.setRowCount(self.rows_per_view)
        for row_idx, row in enumerate(self.all_rows, start=self.last_displayed_row_idx) :
            for col_idx, value in enumerate(row) :
                item = QTableWidgetItem(str(value)) 
                self.table_widget.setItem(row_idx, col_idx, item)
                self.last_displayed_row_idx += 1
        try :
            self.layout.removeWidget(self.table_widget)
        except :
            pass
        self.layout.addWidget(self.table_widget, 0, 1)

    def return_home(self) :
        self.deconstruct_layout()
        self.ctrl.wm.navigate_to(0)

    def deconstruct_layout(self) :
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

    def pre_init(self, controller) :
        self.ctrl = controller