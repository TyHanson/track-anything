import sys
import sqlite3 as sql
import re
import datetime

from ui.create_table import CreateTable
from ui.define_data_types import DefineDataTypes
from ui.enter_data import EnterData
from ui.home_screen import HomeScreen
from ui.select_table import SelectTable
from ui.view_data import ViewData

from util.controller import Controller
from util.window_manager import WindowManager

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel,  QVBoxLayout, QGridLayout, QComboBox, QWidget, QApplication, QStackedWidget
from PyQt5.QtSql import QSqlDatabase

# LINKS
# https://docs.python.org/3/library/sqlite3.html

# Class to allow easier switching between the windows in stacked_widget and
# allow transfer of data between different windows.
# Inputs: 
#   stacked_widget (PyQt Stacked Widget): Contains all windows of program
#   data (default to string ''): Can be reassigned to send data between windows


if __name__ == "__main__" :
    app = QApplication(sys.argv)

    # Establish SQLLite3 database connection
    connection = sql.connect("track_anything_center.db")
    cursor = connection.cursor()
    
    # Create stack and controller
    window_stack = QStackedWidget()
    data = ''
    window_manager = WindowManager(window_stack)
    controller = Controller(connection, cursor, window_manager, data)

    # Creating screen widgets
    home_screen = HomeScreen(controller) # index 0

    enter_data = EnterData(controller) # index 1
    data_entry_table_select = SelectTable(controller, mapTo = 1) # index 2
    
    create_table = CreateTable(controller) # index 3
    define_datatypes = DefineDataTypes(controller) # index 4
    
    view_data = ViewData(controller) # index 5
    # edit mode maybe? when we get around to this
    view_edit_data_table_select = SelectTable(controller, mapTo = 6) # index 6

    # Add widgets to window_stack
    window_stack.addWidget(home_screen)                 # index 0
    window_stack.addWidget(enter_data)                  # index 1
    window_stack.addWidget(data_entry_table_select)     # index 2
    window_stack.addWidget(create_table)                # index 3
    window_stack.addWidget(define_datatypes)            # index 4
    window_stack.addWidget(view_data)                   # index 5
    window_stack.addWidget(view_edit_data_table_select) # index 6

    # set up layout
    window = window_stack
    for i in range(controller.wm.stacked_widget.count()) :
        curr_window = controller.wm.stacked_widget.widget(i)
        if hasattr(curr_window, "pre_init") :
            curr_window.pre_init(controller)

    window.show()
    print('Successfully ran pre_init on all windows. Starting application...')

    app.exec()