from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

import sqlite3 as sql
import re

from .window_manager import WindowManager

'''
Text;MyText
Float;MyFloat
Integer;MyInt
Dropdown;Float;DropdownFloat;MyDropdown
Dropdown;Text;DropdownText;MyDropdown
Dropdown;Int;DropdownInteger;MyDropdown
Duration;0;54321;MyDuration1
Duration;1;321;MyDuration2
Date;Month1;MyDate
Date;Day2;MyDate
Date;Year3;MyDate
'''

class Controller(QWidget) :
    def __init__(self, connection = sql.Connection, cursor = sql.Cursor, window_manager = WindowManager, data=str) :
        super().__init__()
        self.con = connection
        self.cur = cursor
        self.wm = window_manager
        self.data = data
        self.attribute_types = ["Float", "Int", "Text", "Date", "Duration", "Dropdown"]

    # Returns a list containing 1 elements.
    #   1. table_list : list of all table names in the database
    def get_all_tracker_names(self) :
        # Query for all tables names from central database.
        res = self.cur.execute("SELECT name FROM sqlite_master")
        trackers = res.fetchall()

        # Put all table names into list
        join = ';'.join(str(tracker) for tracker in trackers)
        res = re.sub(r'[^a-zA-Z0-9;]', '', join) + ';'
        current = ''
        tracker_list = []
        for i in range(len(res)) :
            if res[i] != ';' :
                current += res[i]
            else :
                tracker_list.append(current)
                current = ''
    
        return tracker_list

    
    # returns a list of attributes related to each tracker containing the following information
    # attribute_info[0] = a list of all tracker names (without encoding)
    # attribute_info[1] = a list of all attribute types (duration, date, dropdown, etc)
    # attribute_info[2] = a list of all tracker names (with encoding)
    # attribute_info[3] = data type in SQL database
    # attribute_info[4] = column id
    def get_tracker_attribute_info(self, tracker_name) :
        # Execute SQL PRAGMA query to get column details
        res = self.cur.execute(f"PRAGMA table_info({tracker_name});")

        # Fetch rows of column info from result
        columns_info = res.fetchall()
        #print(columns_info)

        # Extract column information in format name, data type, column ID
        attribute_names = []
        attribute_types = []
        for i in range(1, len(columns_info)) :
            encoded_column = columns_info[i][1]
            current_char = ''
            attribute_type = ''
            current_index = 0
            while current_char != '|' :
                attribute_type += current_char
                current_char = encoded_column[current_index]
                current_index += 1
            attribute_types.append(attribute_type)

            current_char = ''
            attribute_name = ''
            current_index = -1
            while current_char != '|' :
                attribute_name = current_char + attribute_name
                current_char = encoded_column[current_index]
                current_index -= 1
            attribute_names.append(attribute_name)

        
        attribute_info = [[column[1], column[2], column[0]] for column in columns_info]
        for i in range(1, len(attribute_info)) :
            attribute_info[i].insert(0, attribute_types[i - 1])
            attribute_info[i].insert(0, attribute_names[i - 1])
        attribute_info[0].insert(0, 'Integer')
        attribute_info[0].insert(0, 'id')
        print(attribute_info)
        return attribute_info

    # convert list of attributes and names to two lists of SQL datatype and the Database-formatted column title
    def convert_attributes_to_sql (self, attributes, titles) :
        sql_datatypes = []
        column_titles = []
        for i in range(len(attributes)) :

            # Float
            if attributes[i] == "Float" :
                sql_datatypes.append("REAL")
                column_titles.append("Float;" + titles[i])
                continue

            # Int
            if attributes[i] == "Integer" :
                sql_datatypes.append("INTEGER")
                column_titles.append("Integer;" + titles[i])
                continue

            # Text
            if attributes[i] == "Text" :
                sql_datatypes.append("TEXT")
                column_titles.append("Text;" + titles[i])
                continue

            # Date
            if attributes[i] == "Date" :
                sql_datatypes.append("INTEGER")
                column_titles.append("Date;" + titles[i])
                continue

            # Duration
            if attributes[i] == "Duration" :
                sql_datatypes.append("INTEGER")
                column_titles.append("Duration;" + titles[i])
                continue

            # Dropdown
            if attributes[i] == "Dropdown" :
                sql_datatypes.append("INTEGER")
                column_titles.append("Dropdown;" + titles[i])
                continue
            
        return column_titles, sql_datatypes

    # to, as in to seconds [Weeks, Days, Hours, Minutes, Seconds]
    def duration_to_seconds(self, time_values) :
        total_seconds = 0
        total_seconds += time_values[0] * 7 * 24 * 60 * 60
        total_seconds += time_values[1] * 24 * 60 * 60
        total_seconds += time_values[2] * 60 * 60
        total_seconds += time_values[3] * 60
        total_seconds += time_values[4]
        return total_seconds

    # THIS DOESNT WORK YET, you need to implement functionality to indicate which one is the "last" time value and assign the remainder to that.
    # Seconds isn't guaranteed to always be last!
    def duration_to_split(self, total_seconds, weeks, days, hours, minutes, seconds) :
        time_values = [0, 0, 0, 0, 0]
        remainder = total_seconds
        if weeks :
            time_values[0] = remainder // (7 * 24 * 60 * 60)
            remainder = remainder % (7 * 24 * 60 * 60)
        if days :
            time_values[1] = remainder // (24 * 60 * 60)
            remainder = remainder % (24 * 60 * 60)
        if hours :
            time_values[2] = remainder // (60 * 60)
            remainder = remainder % (60 * 60)
        if minutes :
            time_values[3] = remainder // (60)
            remainder = remainder % (60)
        if seconds :
            time_values[4] = remainder
    
    def convert_sql_to_attribute_types (self, sql_datatypes) :

        pass

    def convert_attribute_names (self, attributes) :

        pass