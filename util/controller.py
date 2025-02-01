from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget

import sqlite3 as sql
import re

from .window_manager import WindowManager

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
    # attribute_info[0] = a list of all tracker names
    # attribute_info[1] = a list of all internal tracker types
    # attribute_info[2] = a list of all tracker names (in format of DATEM_Month)
    # attribute_info[3] = data type in SQL database
    # attribute_info[4] = column id
    def get_tracker_attribute_info(self, tracker_name) :
        # Execute SQL PRAGMA query to get column details
        res = self.cur.execute(f"PRAGMA table_info({tracker_name});")

        # Fetch rows of column info from result
        columns_info = res.fetchall()

        # Extract column information in format name, data type, column ID
        tracker_name_list = []
        attribute_types = []
        for i in range(len(columns_info)) :
            attribute_type = ''
            tracker_title = ''
            for j in range(len(columns_info[i])) :
                current_char = columns_info[i][j]
                if current_char != ";" :
                    attribute_type += columns_info[i][j]
                    continue
                tracker_title = columns_info[i][j+1:len(columns_info[i])]
                break
            attribute_types.append(attribute_type)
            tracker_name_list.append(tracker_title)
        attribute_info = [[column[1], column[2], column[0]] for column in columns_info]
        attribute_info.insert(0, attribute_types)
        attribute_info.insert(0, tracker_name_list)
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

    def convert_sql_to_attribute_types (self, sql_datatypes) :

        pass

    def convert_attribute_names (self, attributes) :

        pass