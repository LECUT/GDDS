import platform
import subprocess
from PyQt5.QtCore import QLocale, QDate, QDateTime
from PyQt5.QtGui import QFont, QStandardItemModel
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QIcon
import gnsscal
from datetime import *
from time import sleep
import requests
import requests_ftp
import threading
import os
from retrying import retry
import shutil
from pathlib import Path
import json
import resources_rc
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QLocale
from station_info_table import *
JD = 3.21
MJD = 1.23
global curdir
curdir = os.getcwd()

'''
-----------------------------------------------------------------------------------------------------------------------
Function: Custom download of GNSS data
Principle: 1. The user configures the URL of the target GNSS data (including the protocol, domain name, file path and file name)
2. The software replaces the tags in the URL configured by the user with specific values to generate a complete URL
3. Transfer and download the file corresponding to the URL
-----------------------------------------------------------------------------------------------------------------------
'''

class Custom_Download(QWidget):
    global start_time
    start_time = 1
    global end_time
    end_time = 1
    global self_step
    self_step = 0
    global successful_library
    successful_library = []
    global failed_library
    failed_library = []
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Download")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        if win_width <= 720:
            if win_height <= 450:
                self.setFixedSize(940/1280*win_width, 900/1080*win_height)
            elif win_height <= 480:
                self.setFixedSize(940/1150*win_width, 900/1080*win_height)
            elif win_height <= 500:
                self.setFixedSize(940/1150*win_width, 800/1080*win_height)
            elif win_height <= 512:
                self.setFixedSize(940/1150*win_width, 900/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(940/1150*win_width, 800/1080*win_height)
            else:
                self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        elif win_width <= 800 and win_width > 720:
            if win_height <= 500:
                self.setFixedSize(940/1320*win_width, 900/1080*win_height)
            elif win_height <= 515:
                self.setFixedSize(940/1460*win_width, 890/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(940/1080*win_width, 880/1080*win_height)
            self.move((screen.width() - 935/1040*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 840 and win_width > 800:
            self.setFixedSize(940/1300*win_width, 850/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 830/1080*win_height)/2)
        elif win_width <= 960 and win_width > 840:
            if win_height <= 550:
                self.setFixedSize(940/1420*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 600:
                self.setFixedSize(940/1360*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 720:
                self.setFixedSize(940/1120*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            else:
                self.setFixedSize(940/1740*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1024 and win_width > 960:
            self.setFixedSize(940/1150*win_width, 870/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1152 and win_width > 1024:
            self.setFixedSize(940/1300*win_width, 850/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1176 and win_width > 1152:
            self.setFixedSize(940/1350*win_width, 870/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1280 and win_width > 1176:
            self.setFixedSize(940/1435*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1320*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1366 and win_width > 1280:
            self.setFixedSize(940/1550*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1440 and win_width > 1366:
            self.setFixedSize(940/1620*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1600 and win_width > 1440:
            self.setFixedSize(940/1800*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1420*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1680 and win_width > 1600:
            self.setFixedSize(940/1800*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1792 and win_width > 1680:
            self.setFixedSize(940/1720*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 2048 and win_width > 1920:
            self.setFixedSize(940/1820*win_width, 810/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)
        elif win_width <= 2560 and win_width > 2048:
            self.setFixedSize(940/1920*win_width, 810/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)
        else:
            self.setFixedSize(940/1920*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)

        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))


        # self.setFixedSize(940/1920*win_width, 800/1080*win_height)
        # self.move((screen.width() - 940/1920*win_width) / 2, (screen.height() - 840/1080*win_height) / 2)

        global Now_Code_Surrind
        Now_Code_Surrind = os.getcwd()
        self.setup_ui()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        if win_width <= 700:
            # win_width = win_width + 630
            if win_height <= 480:
                win_width = win_width + 420
                win_height = win_height + 60
            elif win_height <= 500:
                win_width = win_width + 420
                win_height = win_height + 60
            elif win_height <= 600:
                win_width = win_width + 470
                win_height = win_height + 60
            else:
                win_width = win_width + 630
        elif win_width <= 800:
            # win_width = win_width + 630
            if win_height <= 500:
                win_width = win_width + 350
                win_height = win_height + 60
            elif win_height <= 500:
                win_width = win_width + 250
                win_height = win_height + 60
            elif win_height < 600:
                win_width = win_width + 250
                win_height = win_height + 60
            else:
                win_width = win_width + 610
                win_height = win_height + 60
        elif win_width <= 840:
            # win_width = win_width + 630
            if win_height <= 500:
                win_width = win_width + 330
                win_height = win_height + 20
            elif win_height < 600:
                win_width = win_width + 400
                win_height = win_height + 30
            else:
                win_width = win_width + 630
                win_height = win_height + 20
        elif win_width <= 960:
            if win_height < 600:
                win_width = win_width + 300
                win_height = win_height + 60
            else:
                win_width = win_width + 400
                win_height = win_height + 60
        elif win_width <= 1024:
            if win_height < 600:
                win_width = win_width + 300
                win_height = win_height + 60
            else:
                win_width = win_width + 670
                win_height = win_height + 60
        elif win_width <= 1152:
            win_width = win_width + 540
            win_height = win_height + 60
        elif win_width <= 1176:
            win_width = win_width + 480
            win_height = win_height + 60
        elif win_width <= 1280:
            win_width = win_width + 400
        elif win_width <= 1366:
            win_width = win_width + 320
            win_height = win_height + 20
        elif win_width <= 1440:
            win_width = win_width + 250
        elif win_width <= 1600:
            win_width = win_width + 100
        elif win_width <= 1680:
            win_width = win_width + 100
        elif win_width < 1920:
            win_width = win_width + 100


        global protocol, domain_name, file_directory, file_name
        protocol = ''
        domain_name = ''
        file_directory = ''
        file_name = ''

        self.url_templates_label = QLabel('URL Templates :', self)
        self.url_templates_label.setFont(QFont("Times New Roman"))
        self.url_templates_label.setGeometry(35/1920*win_width, 14/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.url_templates_lineedit = QLineEdit(self)
        self.url_templates_lineedit.setGeometry(190/1920*win_width, 10/1080*win_height, 690/1920*win_width, 35/1080*win_height)
        # self.url_templates_lineedit.setPlaceholderText('<Protocol>://<Domain Name>/<File Directory>/<File Name>')
        self.url_templates_lineedit.setText('<Protocol>://<Domain Name>/<File Directory>/<File Name>')
        self.url_templates_lineedit.textChanged.connect(self.url_templates_lineedit_changed)

        self.setting_btn = QPushButton(self)
        self.setting_btn.setStyleSheet("QPushButton{border-image: url('./lib/logo/Setting.png')}")
        self.setting_btn.setGeometry(885 / 1920 * win_width, 15 / 1080 * win_height, 25 / 1920 * win_width, 25 / 1920 * win_width)
        self.setting_btn.clicked.connect(self.open_json_options_windows)

        #  setting protocol
        self.protocol_label = QLabel('Protocol :', self)
        self.protocol_label.setFont(QFont("Times New Roman"))
        self.protocol_label.setGeometry(35/1920*win_width, 65/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.choose_protocol_box = QComboBox(self)
        self.choose_protocol_box.setGeometry(190/1920*win_width, 63/1080*win_height, 360/1920*win_width, 35/1080*win_height)
        curdir = os.getcwd()
        json_text = json.load(open(str(curdir) + '/lib/json/custom_download_info.json', 'r'))
        self.choose_protocol_box.addItems(json_text[0][0][1:])
        self.choose_protocol_box.setCurrentIndex(-1)
        self.choose_protocol_box.currentTextChanged.connect(self.protocol_change)

        #  setting domain_name
        self.domain_name_label = QLabel('Domain Name :', self)
        self.domain_name_label.setFont(QFont("Times New Roman"))
        self.domain_name_label.setGeometry(35/1920*win_width, 117/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.choose_domain_name_box = QComboBox(self)
        self.choose_domain_name_box.setGeometry(190/1920*win_width, 115/1080*win_height, 720/1920*win_width, 35/1080*win_height)
        self.choose_domain_name_box.addItems(json_text[0][1][1:])
        self.choose_domain_name_box.addItem('Add')
        self.choose_domain_name_box.setCurrentIndex(-1)
        self.choose_domain_name_box.currentTextChanged.connect(self.domain_name_change)


        #  setting file_directory
        self.file_directory_label = QLabel('File Directory :', self)
        self.file_directory_label.setFont(QFont("Times New Roman"))
        self.file_directory_label.setGeometry(35/1920*win_width, 167/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.file_directory_lineedit = QLineEdit(self)
        self.file_directory_lineedit.setGeometry(190/1920*win_width, 165/1080*win_height, 720/1920*win_width, 35/1080*win_height)
        self.file_directory_lineedit.setPlaceholderText('Input File Directory Template')
        self.file_directory_lineedit.textChanged.connect(self.file_directory_lineedit_changed)

        self.file_directory_windows = QLabel(self)
        self.file_directory_windows.setGeometry(190/1920*win_width, 210/1080*win_height, 720/1920*win_width, 150/1080*win_height)
        self.file_directory_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.file_directory_windows.setFrameShape(QFrame.Box)
        self.file_directory_windows.setFrameShadow(QFrame.Raised)

        self.common_file_directory_title = QLabel('Common Template :', self)
        self.common_file_directory_title.setGeometry(212/1920*win_width, 215/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.common_file_directory_template_box = QComboBox(self)
        self.common_file_directory_template_box.setGeometry(380/1920*win_width, 214/1080*win_height, 500/1920*win_width, 35/1080*win_height)
        self.common_file_directory_template_box.addItems(json_text[0][2][1:])
        self.common_file_directory_template_box.addItem('Add')
        self.common_file_directory_template_box.setCurrentIndex(-1)
        self.common_file_directory_template_box.currentTextChanged.connect(self.common_file_directory_template_change)

        self.tag_explain_title = QLabel('Tag Explain :', self)
        self.tag_explain_title.setGeometry(223/1920*win_width, 280/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        layout = QHBoxLayout()
        self.tag_explain_table = QTableWidget(self)
        self.tag_explain_table.setColumnCount(3)
        self.tag_explain_table.setRowCount(6)
        self.tag_explain_table.setGeometry(380/1920*win_width, 255/1080*win_height, 500/1920*win_width, 100/1080*win_height)

        self.tag_explain_table.setHorizontalHeaderLabels(['Tag', 'Explanation', 'Example'])
        self.tag_explain_table.setColumnWidth(0, 105/1920*win_width)
        self.tag_explain_table.setColumnWidth(1, 240/1920*win_width)
        self.tag_explain_table.setColumnWidth(2, 102/1920*win_width)

        tag_explain_list = json_text[1][0][1:]
        for i in range(len(tag_explain_list)):
            for j in range(3):
                newItem = QTableWidgetItem(tag_explain_list[i][j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tag_explain_table.setItem(i, j, newItem)

        #  setting file_name
        self.file_name_label = QLabel('File Name :', self)
        self.file_name_label.setFont(QFont("Times New Roman"))
        self.file_name_label.setGeometry(35/1920*win_width, 372/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.file_name_lineedit = QLineEdit(self)
        self.file_name_lineedit.setGeometry(190/1920*win_width, 370/1080*win_height, 360/1920*win_width, 35/1080*win_height)
        self.file_name_lineedit.setPlaceholderText('Input File Name')
        self.file_name_lineedit.textChanged.connect(self.file_name_lineedit_changed)

        self.common_file_name_title = QLabel('Common Template :', self)
        self.common_file_name_title.setGeometry(560/1920*win_width, 372/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.common_file_name_template_box = QComboBox(self)
        self.common_file_name_template_box.setGeometry(750/1920*win_width, 370/1080*win_height, 160/1920*win_width, 35/1080*win_height)
        self.common_file_name_template_box.addItems(json_text[0][3]['file_name_type'].keys())
        self.common_file_name_template_box.setCurrentIndex(-1)
        self.common_file_name_template_box.currentTextChanged.connect(self.common_file_name_template_change)

        ###    Output Path
        self.choose_save_path_wuyong_label = QLabel('Output Path :', self)
        self.choose_save_path_wuyong_label.setFont(QFont("Times New Roman"))
        self.choose_save_path_wuyong_label.setGeometry(35/1920*win_width, 425/1080*win_height, 400/1920*win_width, 30/1080*win_height)

        self.show_outsave_files_path_button = QLineEdit(self)
        self.show_outsave_files_path_button.setGeometry(190/1920*win_width, 420/1080*win_height, 665/1920*win_width, 35/1080*win_height)
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        classial_desktop_path = desktop_path + '/' + 'Download'
        self.show_outsave_files_path_button.setText(classial_desktop_path)

        self.choose_outsave_files_path_button = QPushButton('<<<', self)
        self.choose_outsave_files_path_button.setGeometry(865/1920*win_width, 421/1080*win_height, 45/1920*win_width, 30/1080*win_height)
        self.choose_outsave_files_path_button.clicked.connect(self.save_download_files_path_function)

        ###   Time Span
        self.start_end_time_windows = QLabel(self)
        self.start_end_time_windows.setGeometry(50/1920*win_width, 475/1080*win_height, 700/1920*win_width, 132/1080*win_height)
        self.start_end_time_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.start_end_time_windows.setFrameShape(QFrame.Box)
        self.start_end_time_windows.setFrameShadow(QFrame.Raised)

        self.label_brdc_name = QLabel('  Time Span  ', self)
        self.label_brdc_name.move(110/1920*win_width, 465/1080*win_height)
        self.label_brdc_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.label_brdc_name.setFont(QFont('Times New Roman'))

        # year, month, day
        self.YearMonDay_label0101 = QLabel('Year-Month-Day :', self)
        self.YearMonDay_label0101.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0101.move(80/1920*win_width, 500/1080*win_height)
        # start time
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.start_time.setLocale(QLocale(QLocale.English))
        self.start_time.setGeometry(290/1920*win_width, 491/1080*win_height, 150/1920*win_width, 30/1080*win_height)
        self.start_time.setDisplayFormat('yyyy-MM-dd')
        self.start_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.start_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.start_time.setCalendarPopup(True)
        self.start_time.dateChanged.connect(self.onDateChanged01)
        # Year, Day of Year
        self.YearMonDay_label0102 = QLabel('Year, Day of Year :', self)
        self.YearMonDay_label0102.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0102.move(80/1920*win_width, 534/1080*win_height)
        # year
        self.changday0201 = QLineEdit(self)
        self.changday0201.setGeometry(290/1920*win_width, 528/1080*win_height, 95/1920*win_width, 30/1080*win_height)
        # doy
        self.changday0202 = QLineEdit(self)
        self.changday0202.setGeometry(390/1920*win_width, 528/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0201.textEdited.connect(self.YearAcumulateDay_to_all01)
        self.changday0202.textEdited.connect(self.YearAcumulateDay_to_all01)

        # GPS Week
        self.YearMonDay_label0103 = QLabel('GPS Week, Day of Week :', self)
        self.YearMonDay_label0103.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0103.move(80/1920*win_width, 569/1080*win_height)
        # GPS Week
        self.changday0301 = QLineEdit(self)
        self.changday0301.setGeometry(290/1920*win_width, 563/1080*win_height, 95/1920*win_width, 30/1080*win_height)
        # GPS Week
        self.changday0302 = QLineEdit(self)
        self.changday0302.setGeometry(390/1920*win_width, 563/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0301.textEdited.connect(self.GPSweeks_to_all01)
        self.changday0302.textEdited.connect(self.GPSweeks_to_all01)

        # start time
        time_yearmothday = self.start_time.text()
        year = int(time_yearmothday[0:4])
        mon = int(str(time_yearmothday[5:7]))
        day = int(str(time_yearmothday[8:10]))
        conbin_date = date(year, mon, day)
        year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
        self.changday0201.setText(str(year_accumulate_list[0]))
        self.changday0202.setText(str(year_accumulate_list[1]))
        GPS_weeks = gnsscal.date2gpswd(conbin_date)
        self.changday0301.setText(str(GPS_weeks[0]))
        self.changday0302.setText(str(GPS_weeks[1]))

        self.time_start_to_end = QLabel('>>>', self)
        self.time_start_to_end.move(485/1920*win_width, 534/1080*win_height)

        # end time
        self.end_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.end_time.setLocale(QLocale(QLocale.English))
        self.end_time.setGeometry(560/1920*win_width, 491/1080*win_height, 150/1920*win_width, 30/1080*win_height)
        self.end_time.setDisplayFormat('yyyy-MM-dd')
        self.end_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.end_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.end_time.setCalendarPopup(True)
        self.end_time.dateChanged.connect(self.onDateChanged02)

        # year
        self.changday0401 = QLineEdit(self)
        self.changday0401.setGeometry(560/1920*win_width, 528/1080*win_height, 95/1920*win_width, 30/1080*win_height)
        # doy
        self.changday0402 = QLineEdit(self)
        self.changday0402.setGeometry(660/1920*win_width, 528/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0401.textEdited.connect(self.YearAcumulateDay_to_all02)
        self.changday0402.textEdited.connect(self.YearAcumulateDay_to_all02)

        # GPS Week
        self.changday0501 = QLineEdit(self)
        self.changday0501.setGeometry(560/1920*win_width, 563/1080*win_height, 95/1920*win_width, 30/1080*win_height)
        # GPS Week
        self.changday0502 = QLineEdit(self)
        self.changday0502.setGeometry(660/1920*win_width, 563/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0501.textEdited.connect(self.GPSweeks_to_all02)
        self.changday0502.textEdited.connect(self.GPSweeks_to_all02)

        # End time Initialization
        time_yearmothday = self.end_time.text()
        year = int(time_yearmothday[0:4])
        mon = int(str(time_yearmothday[5:7]))
        day = int(str(time_yearmothday[8:10]))
        conbin_date = date(year, mon, day)
        year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
        self.changday0401.setText(str(year_accumulate_list[0]))
        self.changday0402.setText(str(year_accumulate_list[1]))
        GPS_weeks = gnsscal.date2gpswd(conbin_date)
        self.changday0501.setText(str(GPS_weeks[0]))
        self.changday0502.setText(str(GPS_weeks[1]))

        # Station
        self.GNSS_station_windows = QLabel(self)
        self.GNSS_station_windows.setGeometry(770/1920*win_width, 475/1080*win_height, 140/1920*win_width, 132/1080*win_height)
        self.GNSS_station_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.GNSS_station_windows.setFrameShape(QFrame.Box)
        self.GNSS_station_windows.setFrameShadow(QFrame.Raised)

        self.GNSS_station_windows_name = QLabel('  Site  ', self)
        self.GNSS_station_windows_name.move(810/1920*win_width, 465/1080*win_height)
        self.GNSS_station_windows_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.GNSS_station_windows_name.setFont(QFont('Times New Roman'))

        self.GNSS_station_qtextedit = QTextEdit(self)
        self.GNSS_station_qtextedit.setGeometry(790/1920*win_width, 491/1080*win_height, 100/1920*win_width, 97/1080*win_height)
        self.GNSS_station_qtextedit.setPlaceholderText("abmf\nshao\nURUM\nLHAZ")
        self.GNSS_station_qtextedit.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.GNSS_station_qtextedit.setVerticalScrollBarPolicy(2)

        # QPushButton
        self.URL_qtextedit = QTextEdit(self)
        self.URL_qtextedit.setGeometry(50/1920*win_width, 630/1080*win_height, 615/1920*win_width, 85/1080*win_height)
        self.URL_qtextedit.setPlaceholderText("All Download URL")
        self.URL_qtextedit.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.URL_qtextedit.setVerticalScrollBarPolicy(2)

        self.generate_url_but = QPushButton('Generate URL', self)
        self.generate_url_but.setFont(QFont("Times New Roman"))
        self.generate_url_but.setGeometry(680/1920*win_width, 630/1080*win_height, 120/1920*win_width, 35/1080*win_height)
        self.generate_url_but.clicked.connect(self.configue_url)

        self.igs_name_sure_but = QPushButton('Download', self)
        self.igs_name_sure_but.setFont(QFont("Times New Roman"))
        self.igs_name_sure_but.setGeometry(810/1920*win_width, 630/1080*win_height, 100/1920*win_width, 35/1080*win_height)
        self.igs_name_sure_but.clicked.connect(self.ready_to_download)

        self.open_have_download_file_path_but = QPushButton('Open Dir', self)
        self.open_have_download_file_path_but.setFont(QFont("Times New Roman"))
        self.open_have_download_file_path_but.setGeometry(680/1920*win_width, 680/1080*win_height, 120/1920*win_width, 35/1080*win_height)
        self.open_have_download_file_path_but.clicked.connect(self.open_have_download_path)

        self.download_details_report_but = QPushButton('Detail', self)
        self.download_details_report_but.setFont(QFont("Times New Roman"))
        self.download_details_report_but.setGeometry(810/1920*win_width, 680/1080*win_height, 100/1920*win_width, 35/1080*win_height)
        self.download_details_report_but.clicked.connect(self.download_details_report_view)

        # Download completion prompt
        self.show_download_information = QLabel(self)
        self.show_download_information.move(55/1920*win_width, 713/1080*win_height)
        self.show_download_information.setFixedSize(800/1920*win_width, 35/1080*win_height)
        self.show_download_process_state = QLabel(self)
        self.show_download_process_state.setGeometry(443/1920*win_width, 710/1080*win_height, 260/1920*win_width, 35/1080*win_height)

        # progress bar
        self.download_Progress_bar = QProgressBar(self)
        self.download_Progress_bar.setGeometry(50/1920*win_width, 745/1080*win_height, 880/1920*win_width, 40/1080*win_height)
        self_step = 0
        self.download_Progress_bar.setValue(self_step)
        QApplication.processEvents()

    def open_json_options_windows(self):
        print('Setting')
        self.options_windows = Custom_Options()
        self.options_windows.Options_Close_Signal.connect(self.options_windows_close)
        self.options_windows.show()

    def options_windows_close(self):
        print('Closed Options_Windows')
        curdir = os.getcwd()
        json_text = json.load(open(str(curdir) + '/lib/json/custom_download_info.json', 'r'))
        #  1
        self.choose_protocol_box.clear()
        self.choose_protocol_box.addItems(json_text[0][0][1:])
        self.choose_protocol_box.setCurrentIndex(-1)
        #  2
        self.choose_domain_name_box.clear()
        self.choose_domain_name_box.addItems(json_text[0][1][1:])
        self.choose_domain_name_box.addItem('Add')
        self.choose_domain_name_box.setCurrentIndex(-1)
        #  3
        self.common_file_directory_template_box.clear()
        self.common_file_directory_template_box.addItems(json_text[0][2][1:])
        self.common_file_directory_template_box.addItem('Add')
        self.common_file_directory_template_box.setCurrentIndex(-1)
        #  4
        self.common_file_name_template_box.clear()
        self.common_file_name_template_box.addItems(json_text[0][3]['file_name_type'].keys())
        self.common_file_name_template_box.setCurrentIndex(-1)
        self.file_name_lineedit.setText('')

    # 1   protocol
    def protocol_change(self):
        global protocol
        protocol = self.choose_protocol_box.currentText()
        self.url_templates_lineedit_changed()


    # 2   domain_name
    def domain_name_change(self):
        if self.choose_domain_name_box.currentText() == "Add":
            self.s = Domain_name_Customization_Windows()
            self.s.mySignal.connect(self.DomainName_Add_Signal)
            self.s.exec_()
        global domain_name
        domain_name = self.choose_domain_name_box.currentText()
        self.url_templates_lineedit_changed()

    def DomainName_Add_Signal(self, accepted_value):
        curdir = os.getcwd()
        json_text = json.load(open(str(curdir) + '/lib/json/custom_download_info.json', 'r'))
        json_text[0][1].insert(1, str(accepted_value))
        with open(str(curdir) + '/lib/json/custom_download_info.json', 'w', encoding='utf-8') as f:
            json.dump(json_text, f, ensure_ascii=False)
        self.choose_domain_name_box.clear()
        self.choose_domain_name_box.addItems(json_text[0][1][1:])
        self.choose_domain_name_box.addItem('Add')

    # 3   file_directory
    def file_directory_lineedit_changed(self):
        global file_directory
        file_directory = self.file_directory_lineedit.text()
        self.url_templates_lineedit_changed()

    def common_file_directory_template_change(self):
        if self.common_file_directory_template_box.currentText() == "Add":
            self.s = Domain_name_Customization_Windows()
            self.s.mySignal.connect(self.FileDirectory_Add_Signal)
            self.s.exec_()
        self.file_directory_lineedit.setText(self.common_file_directory_template_box.currentText())

    def FileDirectory_Add_Signal(self, accepted_value):
        curdir = os.getcwd()
        json_text = json.load(open(str(curdir) + '/lib/json/custom_download_info.json', 'r'))
        json_text[0][2].insert(1, str(accepted_value))
        with open(str(curdir) + '/lib/json/custom_download_info.json', 'w', encoding='utf-8') as f:
            json.dump(json_text, f, ensure_ascii=False)
        self.common_file_directory_template_box.clear()
        self.common_file_directory_template_box.addItems(json_text[0][2][1:])
        self.common_file_directory_template_box.addItem('Add')

    # 4   file_name
    def file_name_lineedit_changed(self):
        global file_name
        file_name = self.file_name_lineedit.text()
        self.url_templates_lineedit_changed()

    def common_file_name_template_change(self):
        try:
            curdir = os.getcwd()
            json_text = json.load(open(str(curdir) + '/lib/json/custom_download_info.json', 'r'))
            self.file_name_lineedit.setText(json_text[0][3]['file_name_type'][self.common_file_name_template_box.currentText()])
        except:
            pass

    # all
    def url_templates_lineedit_changed(self):
        # protocol, domain_name, file_directory, file_name
        url_part_list = []
        if protocol != '':
            url_part_list.append(protocol)
        else:
            url_part_list.append('<Protocol>')
        if domain_name != '':
            url_part_list.append(domain_name)
        else:
            url_part_list.append('<Domain Name>')
        if file_directory != '':
            url_part_list.append(file_directory)
        else:
            url_part_list.append('<File Directory>')
        if file_name != '':
            url_part_list.append(file_name)
        else:
            url_part_list.append('<File Name>')
        url_template_show_text = url_part_list[0]+'://'+url_part_list[1]+'/'+url_part_list[2]+'/'+url_part_list[3]
        self.url_templates_lineedit.setText(url_template_show_text)

    # output file path
    def save_download_files_path_function(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Select Output File', 'C:/')
        if save_path == '':
            # print('No Choose Output Path')
            pass
        else:
            self.show_outsave_files_path_button.setText(save_path)
        pass

    def configue_url(self):
        # print('Configure URL')
        #  1. get time
        start_time_T = str(self.start_time.dateTime().toString(Qt.ISODate))
        start_time = start_time_T[0:10] + ' ' + start_time_T[11:19]
        start_time_date = start_time_T[0:10]
        end_time_T = str(self.end_time.dateTime().toString(Qt.ISODate))
        end_time = end_time_T[0:10] + ' ' + end_time_T[11:19]
        end_time_date = end_time_T[0:10]
        dt1 = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        dt2 = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        difference_time = dt2 - dt1
        if difference_time.days >= 0:
            Judgement_time = 1
        else:
            Judgement_time = 0
        if Judgement_time == 0:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips', 'Please adjust time range !')
            return
        else:
            date_list = self.getEveryDay(start_time_date, end_time_date)
            all_YearAccuDay_GpsWeek = []
            for i in date_list:
                YearAccuDay_GpsWeek = self.GpsWeek_YearAccuDay(i)
                list = [YearAccuDay_GpsWeek[0], YearAccuDay_GpsWeek[1], YearAccuDay_GpsWeek[2], YearAccuDay_GpsWeek[3],
                        YearAccuDay_GpsWeek[4], YearAccuDay_GpsWeek[5]]
                all_YearAccuDay_GpsWeek = all_YearAccuDay_GpsWeek + [list]

        #  2. get site
        site_list = self.GNSS_station_qtextedit.toPlainText().split()
        for i in range(len(all_YearAccuDay_GpsWeek)):
            all_YearAccuDay_GpsWeek[i].append(site_list)
        # print(all_YearAccuDay_GpsWeek)

        #  3. whether protocol, domain_name, file_directory, and file_name are empty?
        if protocol == '' or domain_name == '' or file_directory == '' or file_name == '':
            QMessageBox.information(self, 'Tips', 'Please configure complete Protocol, Domain Name, File Directory, and File Name!')
            return

        #  4. protocol + domain_name
        website = protocol + '://' + domain_name

        #  5. file_directory_name_list
        file_directory_name = file_directory + '/' + file_name
        extract_tag_list = re.compile('\<(.*?)\>').findall(file_directory_name)
        for tag in extract_tag_list:
            file_directory_name = file_directory_name.replace(str(tag), '')
        remove_tag_file_directory_name_list = file_directory_name.split('<>')
        # print(extract_tag_list)  ## ['year4', 'doy', 'year2', 'site', 'doy', 'year2']
        # print(remove_tag_file_directory_name_list)  ## ['pub/gps/data/daily/', '/', '/', 'o', '', '0.', 'o.gz']
        tag_matching_dic = {'year4': 0, 'year2': 1, 'doy': 3, 'week': 4, 'dow': 5, 'site': 6}
        file_directory_name_list = []
        for time in all_YearAccuDay_GpsWeek:
            extract_tag_definite_list = []
            for one_extract_tag in extract_tag_list:
                temp_list = []
                if one_extract_tag.lower() == 'site':
                    extract_tag_definite_list.append(time[6])
                else:
                    temp_list.append(time[tag_matching_dic[one_extract_tag]])
                    extract_tag_definite_list.append(temp_list)
            ##  cross combine two list
            cppy_remove_tag_file_directory_name_list = remove_tag_file_directory_name_list[:]
            cppy_remove_tag_file_directory_name_list.reverse()
            extract_tag_definite_list.reverse()
            combin_list = [(lambda i: cppy_remove_tag_file_directory_name_list.pop() if (
                        cppy_remove_tag_file_directory_name_list != [] and (
                        i % 2 == 0 or extract_tag_definite_list == [])) else extract_tag_definite_list.pop())(i) for i
                           in
                           range(len(cppy_remove_tag_file_directory_name_list) + len(extract_tag_definite_list))]
            extract_tag_definite_list.reverse()
            # print(combin_list) # ['pub/gps/daily/', [2021], '/', [21], 'o/', ['ajf1', 'WHU1'], '', ['001'], '0.', [21], 'o.gz']
            ##  tree stitching
            tree_list_combine = []
            for i in combin_list:
                if type(i) == str:
                    if len(tree_list_combine) == 0:
                        tree_list_combine.append(str(i))
                    else:
                        for j in range(len(tree_list_combine)):
                            tree_list_combine[j] += str(i)
                else:
                    if len(tree_list_combine) == 0:
                        tree_list_combine = i[:]
                    else:
                        temp_list = []
                        for j in range(len(tree_list_combine)):
                            for k in i:
                                temp_list.append(tree_list_combine[j] + str(k))
                        tree_list_combine = temp_list[:]
            # print(tree_list_combine)
            file_directory_name_list.extend(tree_list_combine)
        # print(file_directory_name_list)

        #  6. all url list
        all_url_list = []
        for dir_name in file_directory_name_list:
            all_url_list.append(website + '/' + dir_name)
        print(all_url_list)
        for i in all_url_list:
            self.URL_qtextedit.append(i)


    def ready_to_download(self):
        qtextedit_content_list = self.URL_qtextedit.toPlainText().split()
        if len(qtextedit_content_list) == 0:
            QMessageBox.information(self, 'Tips', 'URL not be detected!')
            return
        # print(qtextedit_content_list)
        target_url_list = []
        for i in qtextedit_content_list:
            file_name = i.split('/')[-1]
            target_url_list.append([i, file_name])
        self.show_download_process_state.setText('downloading...')
        try:
            html = requests.get("https://www.baidu.com", timeout=4)
        except:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips', 'The network connection failed, please check the device network connection!')
            return

        function_start_time = datetime.now()
        self.show_download_information.setText('')
        global self_step
        self_step = 0
        self.download_Progress_bar.setValue(self_step)
        QApplication.processEvents()
        global successful_library
        global failed_library
        successful_library = []
        failed_library = []

        protocol_type = qtextedit_content_list[0][0:3]
        global session
        global ftp_max_thread
        if protocol_type == 'ftp':
            requests_ftp.monkeypatch_session()
        session = requests.Session()
        ftp_max_thread = threading.Semaphore(10)

        # Output folder exist
        if os.path.exists(self.show_outsave_files_path_button.text()):
            pass
        else:
            os.mkdir(self.show_outsave_files_path_button.text())

        thread_list = locals()
        thread_list_original_length = len(thread_list)
        for i, j in zip(target_url_list, range(len(target_url_list))):
            download_ftp_function = threading.Thread(target=self.download_function, args=(i[0], i[1]))
            thread_list['thread_' + str(j)] = []
            thread_list['thread_' + str(j)].append(download_ftp_function)
            pass
        ftp_list_length = len(thread_list) - thread_list_original_length
        self.download_Progress_bar.setRange(0, int(ftp_list_length))
        QApplication.processEvents()
        for j in range(ftp_list_length):
            thread_list['thread_' + str(j)][0].start()
        for j in range(ftp_list_length):
            thread_list['thread_' + str(j)][0].join()
        pass

        # Show download details
        function_end_time = datetime.now()
        used_time = (function_end_time - function_start_time).seconds
        used_time_miniter = used_time // 60
        used_time_seconds = used_time % 60
        if used_time_miniter == 0:
            used_time = str(used_time_seconds) + 's'
        else:
            used_time = str(used_time_miniter) + 'min' + str(used_time_seconds) + 's'
            pass
        self.show_download_information.setText('Total Tasks:%d  Succeeded:%d  Failed:%d （Time Consumed:%s）   Download completed!' % ((len(successful_library) + len(failed_library)), len(successful_library), len(failed_library), used_time))
        self.download_Progress_bar.setValue(int(len(target_url_list)))
        QApplication.processEvents()
        self.show_download_process_state.setText('')
        print('End Download')

    @retry(stop_max_attempt_number=21600, wait_random_min=1000, wait_random_max=5000)
    # @func_set_timeout(20)
    def download_function(self, url, file_name):
        global successful_library
        global failed_library
        global self_step
        global ftp_max_thread
        with ftp_max_thread:
            list = [url, file_name]
            self_file_path = self.show_outsave_files_path_button.text() + '/' + str(file_name)
            s = requests.Session()
            try:
                res = s.get(url, stream=True, timeout=10, auth=('anonymous', 'l_teamer@163.com'))
            except:
                print('failure：', url, 'Error: Server does not respond')
                self_step = self_step + 1
                self.download_Progress_bar.setValue(self_step)
                QApplication.processEvents()
                failed_library = failed_library + [list]
                return
            # print('Initial state：', res.status_code)
            if res.status_code == 200:
                file_size = int(res.headers['content-length'])
                # File exists and Contrast size
                if os.path.exists(self_file_path):
                    first_byte = os.path.getsize(self_file_path)
                    print()
                    header = {"Range": f"bytes={first_byte}-{file_size}"}
                    res = s.get(url, headers=header, stream=True)
                else:
                    first_byte = 0
                    pass
                if first_byte >= file_size:
                    print('file exist')
                    return
                with open(self_file_path, 'ab') as fp:
                    for line_content in res.iter_content(chunk_size=1024):
                        if line_content:
                            fp.write(line_content)
                print('success：', url, res.status_code)
                successful_library = successful_library + [list]
                self_step = self_step + 1
                self.download_Progress_bar.setValue(self_step)
                QApplication.processEvents()

            elif res.status_code == 503:
                try:
                    sleep(1)
                    retry_link_time = 0
                    res = s.get(url, stream=True, timeout=2)
                    while res.status_code != 200:
                        retry_link_time += 1
                        sleep(1)
                        res = s.get(url, stream=True, timeout=2)
                        print('load：', url, res.status_code)
                        if retry_link_time > 3:
                            break
                        elif res.status_code == 404:
                            break
                    if res.status_code == 200:
                        file_size = int(res.headers['content-length'])
                        # File exists and Contrast size
                        if os.path.exists(self_file_path):
                            first_byte = os.path.getsize(self_file_path)
                            header = {"Range": f"bytes={first_byte}-{file_size}"}
                            res = s.get(url, headers=header, stream=True)
                        else:
                            first_byte = 0
                            pass
                        if first_byte >= file_size:
                            print('file exist')
                            return
                        with open(self_file_path, 'ab') as fp:
                            for line_content in res.iter_content(chunk_size=1024):
                                if line_content:
                                    fp.write(line_content)
                        print('success：', url, res.status_code)
                        successful_library = successful_library + [list]
                        self_step = self_step + 1
                        self.download_Progress_bar.setValue(self_step)
                        QApplication.processEvents()
                    else:
                        print('failure：', url, res.status_code)
                        self_step = self_step + 1
                        self.download_Progress_bar.setValue(self_step)
                        QApplication.processEvents()
                        failed_library = failed_library + [list]
                except:
                    raise NameError
            else:
                print('failure：', url, res.status_code)
                self_step = self_step + 1
                self.download_Progress_bar.setValue(self_step)
                QApplication.processEvents()
                failed_library = failed_library + [list]
                pass
            pass

    # Open Dir
    def open_have_download_path(self):
        try:
            if self.show_outsave_files_path_button.text() == '':
                return
            else:
                if platform.system() == 'Windows':
                    os.startfile(self.show_outsave_files_path_button.text())
                elif platform.system() == 'Linux':
                    subprocess.Popen(['xdg-open', self.show_outsave_files_path_button.text()])
        except:
            return

    # -------------------------------------------------------------------------------------------------
    """ time convert """
    def onDateChanged01(self):
        try:
            time_yearmothday = self.start_time.text()
            year = int(time_yearmothday[0:4])
            mon = int(str(time_yearmothday[5:7]))
            day = int(str(time_yearmothday[8:10]))
            conbin_date = date(year, mon, day)
            year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
            self.changday0201.setText(str(year_accumulate_list[0]))
            self.changday0202.setText(str(year_accumulate_list[1]))
            GPS_weeks = gnsscal.date2gpswd(conbin_date)
            self.changday0301.setText(str(GPS_weeks[0]))
            self.changday0302.setText(str(GPS_weeks[1]))
        except:
            pass

    def YearAcumulateDay_to_all01(self):
        try:
            if self.changday0201.text() == '' or self.changday0202.text() == '':
                pass
            elif int(self.changday0201.text()) <= 1990 or int(self.changday0201.text()) >= 2050 or int(
                    self.changday0202.text()) <= 0 or int(self.changday0202.text()) > 366:
                pass
            else:
                year = int(self.changday0201.text())
                accumulate_day = int(self.changday0202.text())
                YearMonDay = gnsscal.yrdoy2date(year, accumulate_day)
                self.start_time.setDate(YearMonDay)
                pass
        except:
            pass

    def GPSweeks_to_all01(self):
        try:
            if self.changday0301.text() == '' or self.changday0302.text() == '':
                pass
            elif int(self.changday0301.text()) <= 500 or int(self.changday0301.text()) >= 3400 or int(
                    self.changday0302.text()) < 0 or int(self.changday0302.text()) >= 7:
                pass
            else:
                GPSweek = int(self.changday0301.text())
                GPSweekDay = int(self.changday0302.text())
                YearMonDay = gnsscal.gpswd2date(GPSweek, GPSweekDay)
                self.start_time.setDate(YearMonDay)
        except:
            pass

    def onDateChanged02(self):
        try:
            time_yearmothday = self.end_time.text()
            year = int(time_yearmothday[0:4])
            mon = int(str(time_yearmothday[5:7]))
            day = int(str(time_yearmothday[8:10]))
            conbin_date = date(year, mon, day)
            year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
            self.changday0401.setText(str(year_accumulate_list[0]))
            self.changday0402.setText(str(year_accumulate_list[1]))
            GPS_weeks = gnsscal.date2gpswd(conbin_date)
            self.changday0501.setText(str(GPS_weeks[0]))
            self.changday0502.setText(str(GPS_weeks[1]))
            pass
        except:
            pass

    def YearAcumulateDay_to_all02(self):
        try:
            if self.changday0401.text() == '' or self.changday0402.text() == '':
                pass
            elif int(self.changday0401.text()) <= 1990 or int(self.changday0401.text()) >= 2050 or int(self.changday0402.text()) <=0 or int(self.changday0402.text()) >= 366:
                pass
            else:
                year = int(self.changday0401.text())
                accumulate_day = int(self.changday0402.text())
                YearMonDay = gnsscal.yrdoy2date(year, accumulate_day)
                self.end_time.setDate(YearMonDay)
                pass
        except:
            pass

    def GPSweeks_to_all02(self):
        try:
            if self.changday0501.text() == '' or self.changday0502.text() == '':
                pass
            elif int(self.changday0501.text()) <= 500 or int(self.changday0501.text()) >= 3400 or int(self.changday0502.text()) < 0 or int(self.changday0502.text()) >= 7:
                pass
            else:
                GPSweek = int(self.changday0501.text())
                GPSweekDay = int(self.changday0502.text())
                YearMonDay = gnsscal.gpswd2date(GPSweek, GPSweekDay)
                self.end_time.setDate(YearMonDay)
        except:
            pass

    def getEveryDay(self, begin_date, end_date):
        date_list = []
        begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        while begin_date <= end_date:
            pass
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += timedelta(days=1)
        return date_list

    def day_run_year(self, year, mon, day):
        sum_day = day
        day_month = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for i in day_month[0:mon]:
            sum_day = sum_day + i
        return sum_day

    def day_ping_year(self, year, mon, day):
        sum_day = day
        day_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for i in day_month[0:mon]:
            sum_day = sum_day + i
        return sum_day

    def GpsWeek_YearAccuDay(self, time_yearmothday):
        GPS_week_year_list = []
        year = int(time_yearmothday[0:4])
        year_abbreviation = int(time_yearmothday[2:4])
        mon = int(str(time_yearmothday[5:7]))
        day = int(str(time_yearmothday[8:10]))
        if year % 4 == 0 and year % 400 != 0:
            year_accumulation_day = str(self.day_run_year(year, mon, day))
        else:
            year_accumulation_day = str(self.day_ping_year(year, mon, day))
        GPS_week_year_list.append(year)
        GPS_week_year_list.append(year_abbreviation)
        year_accumulation_day = int(year_accumulation_day)
        GPS_week_year_list.append(year_accumulation_day)
        if year_accumulation_day <= 9:
            year_accumulation_day = '00' + str(year_accumulation_day)
        elif year_accumulation_day >= 10 and year_accumulation_day <= 99:
            year_accumulation_day = '0' + str(year_accumulation_day)
        else:
            year_accumulation_day = str(year_accumulation_day)
        GPS_week_year_list.append(year_accumulation_day)
        conbin_date = date(year, mon, day)
        GPS_weeks = gnsscal.date2gpswd(conbin_date)
        GPS_week_year_list.append(GPS_weeks[0])
        GPS_week_year_list.append(GPS_weeks[1])
        return GPS_week_year_list

    # View download details
    def download_details_report_view(self):
        self.s = download_details_report_main01(successful_library,failed_library)
        self.s.show()
        pass

# -------------------------------------------------------------------------------------------------
""" download details gui """
class download_details_report_main01(QWidget):
    def __init__(self, success, fail):
        super().__init__()
        curdir = os.getcwd()
        self.setWindowTitle("Detail")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        self.move(200/1920*win_width, 60/1080*win_height)
        self.setFixedSize(1400/1920*win_width, 800/1080*win_height)
        self.setup_ui(success, fail)

    def setup_ui(self, success, fail):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        print(success)
        print(fail)
        self.show_text = QTextEdit(self)
        self.show_text.setGeometry(0, 0, 1400/1920*win_width, 800/1080*win_height)
        all = len(success)+len(fail)

        self.show_text.append('Download Details')
        self.show_text.append('Total Tasks:%d  Succeeded:%d  Failed:%d' %(all, len(success), len(fail)))
        self.show_text.append('Data Format : [’Download Link ‘,’File Name‘]')
        self.show_text.append('\n')
        self.show_text.append('Succeeded :')
        for i in success:
            self.show_text.append(str(i))
        self.show_text.append('\n')

        if len(fail) != 0:
            self.show_text.append('Failed :')
            for j in fail:
                self.show_text.append(str(j))
            self.show_text.append('\n')
            self.show_text.append('Failure reason analysis :')
            self.show_text.append('1. Reasons for the failure to download observation files: data lag (the observation file is delayed 12-24 hours), IGS station suspension of service (for some reason, the selected IGS station suspends the observation of this day, resulting in data loss); ')
            self.show_text.append('2. The reason for the failure to download the broadcast ephemeris: the lag of the data (the broadcast ephemeris of version 2.11 has a delay of 12-24 hours, and the broadcast ephemeris of version 3.04 has a delay of 1-2 days). Please select the appropriate broadcast ephemeris according to the time. File type to download; ')
            self.show_text.append('3. Reason for failure of downloading precision ephemeris: data lag (IGU delay 3-9 hours, IGR delay 17-41 hours, IGS delay 12-18 days), please select the appropriate precision ephemeris file type according to the time To download. ')
            self.show_text.append('\n')
        pass

# -------------------------------------------------------------------------------------------------
""" Domain_name_Customization gui """
class Domain_name_Customization_Windows(QDialog):
    mySignal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customization")
        curdir = os.getcwd()
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        self.setGeometry(780/1920*win_width, 470/1080*win_height, 400/1920*win_width, 100/1080*win_height)
        self.setup_ui()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        self.input_qlineedit = QLineEdit(self)
        self.input_qlineedit.move(30/1920*win_width, 30/1080*win_height)
        self.input_qlineedit.setFixedSize(210/1920*win_width, 30/1080*win_height)
        self.input_qlineedit.setPlaceholderText("Input")

        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.move(250/1920*win_width, 30/1080*win_height)
        self.ok_btn.setFixedSize(110/1920*win_width, 30/1080*win_height)
        self.ok_btn.clicked.connect(self.ok_function)

    def ok_function(self):
        transimittee_signal = self.input_qlineedit.text()
        self.mySignal.emit(transimittee_signal)
        self.hide()
        return transimittee_signal

# -------------------------------------------------------------------------------------------------
""" Custom_Options gui """
class Custom_Options(QWidget):
    TITLE1, TITLE2, CONTENT = range(3)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")
        curdir = os.getcwd()
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        self.setGeometry(620/1920*win_width, 290/1080*win_height, 700/1920*win_width, 440/1080*win_height)
        self.setup_ui()

    # emit windows close singal
    Options_Close_Signal = pyqtSignal(str)
    def sendEditContent(self):
        content = '1'
        self.Options_Close_Signal.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        self.dataView = QTreeView(self)
        self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)
        self.dataView.setGeometry(2/1920*win_width, 0, 696/1920*win_width, 400/1080*win_height)

        global model
        model = self.createMailModel(self)
        self.dataView.setModel(model)
        curdir = os.getcwd()
        json_text = json.load(open(str(curdir) + '/lib/json/custom_download_info.json', 'r'))
        show_json_text = json_text[0]
        for data in reversed(show_json_text):
            if isinstance(data, dict):
                for file_name_dict in data['file_name_type']:
                    self.addMail(model, list(data.keys())[0], file_name_dict, data['file_name_type'][file_name_dict])
            else:
                for i in data[1:]:
                    self.addMail(model, data[0], '', i)
        self.dataView.setColumnWidth(0, 150)
        self.dataView.setColumnWidth(1, 100)
        self.dataView.setColumnWidth(2, 400)

        self.plus_btn = QPushButton(self)
        self.plus_btn.setStyleSheet("QPushButton{border-image: url('./lib/logo/plus.png')}")
        self.plus_btn.setGeometry(20/1920*win_width, 410/1080*win_height, 20/1920*win_width, 20/1080*win_height)
        self.plus_btn.clicked.connect(self.plus_function)

        self.minus_btn = QPushButton(self)
        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./lib/logo/minus.png')}")
        self.minus_btn.setGeometry(60/1920*win_width, 410/1080*win_height, 20/1920*win_width, 20/1080*win_height)
        self.minus_btn.clicked.connect(self.minus_function)

        self.restore_btn = QPushButton(self)
        self.restore_btn.setStyleSheet("QPushButton{border-image: url('./lib/logo/recovery.png')}")
        self.restore_btn.setGeometry(97/1920*win_width, 407/1080*win_height, 24/1920*win_width, 24/1080*win_height)
        self.restore_btn.clicked.connect(self.restore_function)

        self.save_btn = QPushButton('Save', self)
        self.save_btn.setGeometry(140/1920*win_width, 403/1080*win_height, 560/1920*win_width, 35/1080*win_height)
        self.save_btn.clicked.connect(self.save_function)

    def createMailModel(self, parent):
        model = QStandardItemModel(0, 3, parent)# 表格的列数
        model.setHeaderData(self.TITLE1, Qt.Horizontal, "Title1")
        model.setHeaderData(self.TITLE2, Qt.Horizontal, "Title2")
        model.setHeaderData(self.CONTENT, Qt.Horizontal, "Content")
        return model

    def addMail(self, model, title1_text, title2_text, content_text):
        model.insertRow(0)
        model.setData(model.index(0, self.TITLE1), title1_text)
        model.setData(model.index(0, self.TITLE2), title2_text)
        model.setData(model.index(0, self.CONTENT), content_text)

    def save_function(self):
        all_tree_list = []
        all_rows = self.dataView.model().rowCount()
        all_columns = self.dataView.model().columnCount()
        for i in range(all_rows):
            temp_list = []
            try:
                for j in range(all_columns):
                    temp_list.append(self.dataView.model().item(i, j).text())
                all_tree_list.append(temp_list)
            except:
                pass
        # print(all_tree_list)
        # [[a, tg], [b, io], [a, aw], [b, iu]] --> [[[a, tg], [a, aw]], [[b, io], [b, iu]]]
        reorganize_list = []
        temp_record_heard_list = []
        for i in all_tree_list:
            if i[0] not in temp_record_heard_list:
                temp_record_heard_list.append(i[0])
        for i in temp_record_heard_list:
            temp_list = []
            for j in all_tree_list:
                if j[0] == i:
                    temp_list.append(j)
            reorganize_list.append(temp_list)
        # print(reorganize_list)
        record_list = []
        for sing_list in reorganize_list:
            if sing_list[0][0] == 'protocol' or sing_list[0][0] == 'domain_name' or sing_list[0][0] == 'file_directory':
                temp_list = [sing_list[0][0]]
                for i in sing_list:
                    temp_list.extend([i[2]])
                record_list.append(temp_list)
            elif sing_list[0][0] == 'file_name_type':
                temp_dict = {}
                for i in sing_list:
                    temp_dict[i[1]] = i[2]
                record_list.append({sing_list[0][0]: temp_dict})
                pass
        # print(record_list)
        sort_list = []
        for i in record_list:
            if i[0] == 'protocol':
                sort_list.append(i)
                break
        for i in record_list:
            if i[0] == 'domain_name':
                sort_list.append(i)
                break
        for i in record_list:
            if i[0] == 'file_directory':
                sort_list.append(i)
                break
        for i in record_list:
            if isinstance(i, dict):
                sort_list.append(i)
                break
        curdir = os.getcwd()  # str(curdir)
        json_text = json.load(open(str(curdir) + '/lib/json/custom_download_info.json', 'r'))
        json_text[0] = sort_list
        with open(str(curdir) + '/lib/json/custom_download_info.json', 'w', encoding='utf-8') as f:
            json.dump(json_text, f, ensure_ascii=False)
        QMessageBox.information(self, 'Tips', "Successful  ")

    def plus_function(self):
        choosed_row = self.dataView.selectionModel().currentIndex().row()
        # self.dataView.model().insertRow(int(choosed_row) + 1)
        model.insertRow(int(choosed_row) + 1)
        model.setData(model.index(int(choosed_row + 1), self.TITLE1), '')
        model.setData(model.index(int(choosed_row + 1), self.TITLE2), '')
        model.setData(model.index(int(choosed_row + 1), self.CONTENT), '')

    def minus_function(self):
        choosed_row = self.dataView.selectionModel().currentIndex().row()
        self.dataView.model().removeRow(choosed_row)

    def restore_function(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial options? ', QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            curdir = os.getcwd()  # str(curdir)
            shutil.copy(str(curdir) + '/lib/json/origin/custom_download_info.json', str(curdir) + r'/lib/json/custom_download_info.json')
            self.dataView.model().clear()
            global model
            model = self.createMailModel(self)
            self.dataView.setModel(model)
            json_text = json.load(open(str(curdir) + '/lib/json/custom_download_info.json', 'r'))
            show_json_text = json_text[0]
            for data in reversed(show_json_text):
                if isinstance(data, dict):
                    for file_name_dict in data['file_name_type']:
                        self.addMail(model, list(data.keys())[0], file_name_dict, data['file_name_type'][file_name_dict])
                else:
                    for i in data[1:]:
                        self.addMail(model, data[0], '', i)


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    screen = QDesktopWidget().screenGeometry()
    win_width = screen.width()
    win_height = screen.height()
    font = QFont()
    pointsize = font.pointSize()
    if win_width <= 1920:
        font.setPointSize(10)
    else:
        font.setPointSize(pointsize - 3)
    font.setFamily("Times New Roman")
    app.setFont(font)
    win = Custom_Download()
    win.show()
    sys.exit(app.exec_())