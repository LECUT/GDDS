from ftplib import FTP_TLS as FTP
import socket

import gnsscal
from datetime import *
from time import sleep
import requests
import requests_ftp
from bs4 import BeautifulSoup
import _thread as thread
import threading
import os
import subprocess
import platform
from retrying import retry
from PyQt5.QtCore import QUrl, QLocale, QDate, QDateTime
from PyQt5.QtWidgets import QMainWindow, QLabel, QComboBox, QTextEdit, QFrame, QCheckBox, QDateTimeEdit, QListWidget, QListWidgetItem, QProgressBar, QAction
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView
from flask import Flask, render_template, request
import resources_rc
from station_info_table import *
import global_var
JD = 3.21
MJD = 1.23

'''
-----------------------------------------------------------------------------------------------------------------------
Function: Download global IGS data 
Principle: 1. Preparation stage. Acquisition of time (year, day of year, GPS week, day of the week), acquisition of IGS station name (IGS station name of rinex2.11 - lowercase, IGS station name of rinex3.04 - uppercase)
2. Generate the target URL address. File type selection judgment - > time list cycle - > IGS station name list cycle - > splicing to generate target URL list
   (URL list format: [[url1, file_name1], [URL2, file_name2], ~])
3. Merge to generate a total URL list. Merge all the URL lists generated in step 2 into one total URL list
4. Crawler download phase. Execute in the same session: simulate login (after login, there is a jump of the interface. Only after the program execution completes the jump of the interface can valid cookie information be generated)
   ——>Loop total URL list - > execute URL web address - > write file (multithreading)
-----------------------------------------------------------------------------------------------------------------------
'''
global curdir
curdir = os.getcwd()
class IGS_data_Download(QWidget):
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
        self.setWindowTitle("Global IGS Data")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        if win_width <= 720:
            if win_height <= 450:
                self.setFixedSize(965/1280*win_width, 900/1080*win_height)
            elif win_height <= 480:
                self.setFixedSize(965/1150*win_width, 900/1080*win_height)
            elif win_height <= 500:
                self.setFixedSize(965/1450*win_width, 830/1080*win_height)
            elif win_height <= 512:
                self.setFixedSize(965/1150*win_width, 900/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(965/1150*win_width, 800/1080*win_height)
            else:
                self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        elif win_width <= 800 and win_width > 720:
            if win_height <= 500:
                self.setFixedSize(965/1320*win_width, 900/1080*win_height)
            elif win_height <= 515:
                self.setFixedSize(965/1460*win_width, 890/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(965/1080*win_width, 880/1080*win_height)
            self.move((screen.width() - 935/1040*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 840 and win_width > 800:
            self.setFixedSize(965/1300*win_width, 890/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 830/1080*win_height)/2)
        elif win_width <= 960 and win_width > 840:
            if win_height <= 550:
                self.setFixedSize(965/1460*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 600:
                self.setFixedSize(965/1460*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 720:
                self.setFixedSize(965/1140*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            else:
                self.setFixedSize(965/1740*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1024 and win_width > 960:
            self.setFixedSize(965/1150*win_width, 870/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1152 and win_width > 1024:
            self.setFixedSize(965/1300*win_width, 850/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1176 and win_width > 1152:
            self.setFixedSize(965/1350*win_width, 870/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1280 and win_width > 1176:
            self.setFixedSize(965/1435*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1320*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1366 and win_width > 1280:
            self.setFixedSize(965/1550*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1440 and win_width > 1366:
            self.setFixedSize(965/1620*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1600 and win_width > 1440:
            self.setFixedSize(965/1800*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1420*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1680 and win_width > 1600:
            self.setFixedSize(965/1800*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1792 and win_width > 1680:
            self.setFixedSize(965/1820*win_width, 810/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 2048 and win_width > 1920:
            self.setFixedSize(965/1920*win_width, 810/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)
        elif win_width <= 2560 and win_width > 2048:
            self.setFixedSize(965/1920*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)
        else:
            self.setFixedSize(940/1920*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)

        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))

        # self.move((screen.width() - 965/1920*win_width) / 2, (screen.height() - 800/1080*win_height) / 2)
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
                win_width = win_width + 420
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
                win_height = win_height + 60
            elif win_height < 600:
                win_width = win_width + 400
                win_height = win_height + 60
            elif win_height <= 680 and win_height > 600:
                win_width = win_width + 630
                win_height = win_height + 60
            else:
                win_width = win_width + 630
                win_height = win_height + 20
        elif win_width <= 960:
            if win_height < 600:
                win_width = win_width + 300
                win_height = win_height + 60
            else:
                win_width = win_width + 300
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

        self.choose_download_files_type_label = QLabel('File Type :', self)
        self.choose_download_files_type_label.setFont(QFont("Times New Roman"))
        self.choose_download_files_type_label.setGeometry(35/1920*win_width, 57/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.label_OBS_windows = QLabel(self)
        self.label_OBS_windows.setGeometry(190/1920*win_width, 20/1080*win_height, 330/1920*win_width, 100/1080*win_height)
        self.label_OBS_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.label_OBS_windows.setFrameShape(QFrame.Box)
        self.label_OBS_windows.setFrameShadow(QFrame.Raised)

        self.label_OBS_name = QComboBox(self)
        self.label_OBS_name.addItems(['Observation', 'Meteorology', 'Obs & Met'])
        self.label_OBS_name.setGeometry(230/1920*win_width, 7/1080*win_height, 150/1920*win_width, 32/1080*win_height)
        self.label_OBS_name.currentTextChanged.connect(self.obs_met_file_type_changed_link)

        self.igs_obs_intervel_label = QLabel('Intervel:', self)
        self.igs_obs_intervel_label.move(212 / 1920 * win_width, 47/1080*win_height)
        self.igs_obs_intervel_box = QComboBox(self)
        self.igs_obs_intervel_box.setGeometry(207/1920*win_width, 73/1080*win_height, 85/1920*win_width, 32/1080*win_height)
        self.igs_obs_intervel_box.addItems(['30s', '1s'])
        self.igs_obs_intervel_box.currentTextChanged.connect(self.igs_obs_interel_change)

        self.rinex211_o_check = QCheckBox(self)
        self.rinex211_o_check.move(310/1920*win_width, 45/1080*win_height)
        self.rinex211_o_check.setText('RINEX 2.11(.*o)                 ')
        self.rinex211_o_check.stateChanged.connect(self.obs_file_change_add_station_list)

        self.rinex304_o_check = QCheckBox('RINEX 3.xx(_MO.crx)                         ', self)
        self.rinex304_o_check.move(310/1920*win_width, 80/1080*win_height)
        self.rinex304_o_check.stateChanged.connect(self.obs_file_change_add_station_list)

        self.label_brdc_windows = QLabel(self)
        self.label_brdc_windows.setGeometry(570/1920*win_width, 20/1080*win_height, 335/1920*win_width, 100/1080*win_height)
        self.label_brdc_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.label_brdc_windows.setFrameShape(QFrame.Box)
        self.label_brdc_windows.setFrameShadow(QFrame.Raised)

        self.label_brdc_name = QLabel(self)
        self.label_brdc_name.move(640/1920*win_width, 10/1080*win_height)
        self.label_brdc_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.label_brdc_name.setText('  Navigation  ')
        self.label_brdc_name.setFont(QFont('Times New Roman'))

        self.rinex211_n_check = QCheckBox(self)
        self.rinex211_n_check.move(600/1920*win_width, 45/1080*win_height)

        self.rinex211_n_box = QComboBox(self)
        self.rinex211_n_box.setGeometry(622/1920*win_width, 42/1080*win_height, 110/1920*win_width, 32/1080*win_height)
        self.rinex211_n_box.addItems(['GPS', 'GLONASS'])
        self.rinex211_n_box.currentTextChanged.connect(self.brdc_n_g_change)

        self.rinex211_n_label = QLabel('RINEX 2.xx(.*n)', self)
        self.rinex211_n_label.setGeometry(738/1920*win_width, 41/1080*win_height, 170/1920*win_width, 25/1080*win_height)

        self.rinex304_n_check = QCheckBox('RINEX 3.xx(_MN.rnx)', self)
        self.rinex304_n_check.move(600/1920*win_width, 80/1080*win_height)

        self.choose_start_end_time_label = QLabel('Time Range :', self)
        self.choose_start_end_time_label.setFont(QFont("Times New Roman"))
        self.choose_start_end_time_label.setGeometry(35/1920*win_width, 160/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.YearMonDay_label0101 = QLabel('Year-Month-Day :', self)
        self.YearMonDay_label0101.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0101.move(190/1920*win_width, 140/1080*win_height)

        self.start_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.start_time.setLocale(QLocale(QLocale.English))
        self.start_time.setGeometry(400/1920*win_width, 131/1080*win_height, 150/1920*win_width, 30/1080*win_height)
        self.start_time.setDisplayFormat('yyyy-MM-dd')
        self.start_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.start_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.start_time.setCalendarPopup(True)
        self.start_time.dateChanged.connect(self.onDateChanged01)

        self.YearMonDay_label0102 = QLabel('Year, Day of Year :', self)
        self.YearMonDay_label0102.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0102.move(190/1920*win_width, 174/1080*win_height)

        self.changday0201 = QLineEdit(self)
        self.changday0201.setGeometry(400/1920*win_width, 168/1080*win_height, 95/1920*win_width, 30/1080*win_height)

        self.changday0202 = QLineEdit(self)
        self.changday0202.setGeometry(500/1920*win_width, 168/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0201.textEdited.connect(self.YearAcumulateDay_to_all01)
        self.changday0202.textEdited.connect(self.YearAcumulateDay_to_all01)

        self.YearMonDay_label0103 = QLabel('GPS Week, Day of Week :', self)
        self.YearMonDay_label0103.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0103.move(190/1920*win_width, 209/1080*win_height)

        self.changday0301 = QLineEdit(self)
        self.changday0301.setGeometry(400/1920*win_width, 203/1080*win_height, 95/1920*win_width, 30/1080*win_height)

        self.changday0302 = QLineEdit(self)
        self.changday0302.setGeometry(500/1920*win_width, 203/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0301.textEdited.connect(self.GPSweeks_to_all01)
        self.changday0302.textEdited.connect(self.GPSweeks_to_all01)

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
        self.time_start_to_end.move(585/1920*win_width, 174/1080*win_height)

        self.end_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.end_time.setLocale(QLocale(QLocale.English))
        self.end_time.setGeometry(650/1920*win_width, 131/1080*win_height, 150/1920*win_width, 30/1080*win_height)
        self.end_time.setDisplayFormat('yyyy-MM-dd')
        self.end_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.end_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.end_time.setCalendarPopup(True)
        self.end_time.dateChanged.connect(self.onDateChanged02)

        self.changday0401 = QLineEdit(self)
        self.changday0401.setGeometry(650/1920*win_width, 168/1080*win_height, 95/1920*win_width, 30/1080*win_height)

        self.changday0402 = QLineEdit(self)
        self.changday0402.setGeometry(750/1920*win_width, 168/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0401.textEdited.connect(self.YearAcumulateDay_to_all02)
        self.changday0402.textEdited.connect(self.YearAcumulateDay_to_all02)


        self.changday0501 = QLineEdit(self)
        self.changday0501.setGeometry(650/1920*win_width, 203/1080*win_height, 95/1920*win_width, 30/1080*win_height)

        self.changday0502 = QLineEdit(self)
        self.changday0502.setGeometry(750/1920*win_width, 203/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0501.textEdited.connect(self.GPSweeks_to_all02)
        self.changday0502.textEdited.connect(self.GPSweeks_to_all02)

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

        self.choose_IGS_station111w_label = QLabel('IGS Station :', self)
        self.choose_IGS_station111w_label.setFont(QFont("Times New Roman"))
        self.choose_IGS_station111w_label.setGeometry(35/1920*win_width, 350/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.choose_add_station_list_box = QComboBox(self)
        self.choose_add_station_list_box.setGeometry(190/1920*win_width, 257/1080*win_height, 227/1920*win_width, 31/1080*win_height)
        self.choose_add_station_list_box.addItems(['All Station', 'Obs RNX2 Station', 'Obs RNX3 Station', 'Obs RNX2-3 Station', 'Obs RNX2 Highrate Station', 'Obs RNX3 Highrate Station', 'Obs RNX2-3 Highrate Station', 'Met RNX2 Station', 'Met RNX3 Station', 'Met RNX2-3 Station', 'Obs-Met RNX2 Station', 'Obs-Met RNX3 Station', 'Obs-Met RNX2-3 Station'])
        self.choose_add_station_list_box.currentTextChanged.connect(self.choose_add_station_list)

        self.choose_all_station_label = QListWidget(self)
        self.choose_all_station_label.setGeometry(190/1920*win_width, 287/1080*win_height, 127/1920*win_width, 40/1080*win_height)

        self.choose_all_station_CheckBtn = QCheckBox('All', self)
        self.choose_all_station_CheckBtn.move(196/1920*win_width, 292/1080*win_height)
        # self.choose_all_station_CheckBtn.setMinimumHeight(20)
        self.choose_all_station_CheckBtn.stateChanged.connect(self.choose_all_station_function)

        self.search_igs_label = QLineEdit(self)
        self.search_igs_label.setPlaceholderText('Search')
        self.search_igs_label.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.search_igs_label.setGeometry(260/1920*win_width, 287/1080*win_height, 157/1920*win_width, 40/1080*win_height)
        self.search_igs_label.textChanged.connect(self.Search_text_changed)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(':/icon/magnifier.ico'))
        self.search_igs_label.addAction(station_search_icon, QLineEdit.LeadingPosition)

        self.main_list = QListWidget(self)
        self.main_list.setGeometry(190/1920*win_width, 320/1080*win_height, 227.8/1920*win_width, 180/1080*win_height)
        json_text = json.load(open(str(curdir) + r'/lib/json/IGS_Statios.json', 'r'))
        Files = json_text[0]
        global_var.set_value('IGS_current_view_station_list', Files)
        for item1 in Files:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.main_list.addItem(item)

        self.btnAddItems_map = QPushButton('Map Choose', self)
        self.btnAddItems_map.clicked.connect(self.add_map_Items)
        self.btnAddItems_map.setGeometry(430/1920*win_width, 257/1081*win_height, 210/1920*win_width, 35/1080*win_height)

        self.open_igs_station_table_btn = QPushButton('Info Inquire', self)
        self.open_igs_station_table_btn.clicked.connect(self.open_igs_station_table_view)
        self.open_igs_station_table_btn.setGeometry(430/1920*win_width, 306/1080*win_height, 210/1920*win_width, 35/1080*win_height)

        self.btnPrintItems = QPushButton('Add Station', self)
        self.btnPrintItems.setGeometry(430/1920*win_width, 358/1080*win_height, 210/1920*win_width, 35/1080*win_height)
        self.btnPrintItems.clicked.connect(self.add_igs_Items_function)

        self.stationDisplay = QPushButton('Map Display', self)
        self.stationDisplay.setGeometry(430/1920*win_width, 409/1080*win_height, 210/1920*win_width, 35/1080*win_height)
        self.stationDisplay.clicked.connect(self.station_map_display_function)

        self.btnClearStation = QPushButton('Clear Station', self)
        self.btnClearStation.setGeometry(430/1920*win_width, 460/1080*win_height, 210/1920*win_width, 35/1080*win_height)
        self.btnClearStation.clicked.connect(self.clear_added_station_function)

        self.igs_names_display_label = QLabel('Added 0 Station', self)
        self.igs_names_display_label.setGeometry(653/1920*win_width, 258/1080*win_height, 222/1920*win_width, 35/1080*win_height)
        self.igs_names_display_label.setFrameShape(QFrame.Box)
        self.igs_names_display_label.setFrameShadow(QFrame.Raised)

        self.igs_names_display = QTextEdit(self)
        self.igs_names_display.setPlaceholderText('abmf\nshao\nURUM\nLHAZ')
        self.igs_names_display.setGeometry(654/1920*win_width, 285/1080*win_height, 220/1920*win_width, 210/1080*win_height)
        self.igs_names_display.textChanged.connect(self.added_station_view_link)

        self.choose_dowunload_source_label = QLabel('Data Center :', self)
        self.choose_dowunload_source_label.setFont(QFont("Times New Roman"))
        self.choose_dowunload_source_label.setGeometry(39/1920*win_width, 525/1080*win_height, 400/1920*win_width, 35/1080*win_height)

        self.choose_local_area_box = QComboBox(self)
        self.choose_local_area_box.setGeometry(190/1920*win_width, 524/1080*win_height, 180/1920*win_width, 35/1080*win_height)
        self.choose_local_area_box.addItems(['WHU(China)', 'IGN(France)', 'ESA(Europe)', 'KASI(Korea)', 'SIO(USA)', 'CDDIS(USA)'])
        self.choose_local_area_box.currentTextChanged.connect(self.igs_obs_interel_change)

        self.choose_save_path_wuyong_label = QLabel('Output Path :', self)
        self.choose_save_path_wuyong_label.setFont(QFont("Times New Roman"))
        self.choose_save_path_wuyong_label.setGeometry(39/1920*win_width, 595/1080*win_height, 400/1920*win_width, 30/1080*win_height)

        self.show_outsave_files_path_button = QLineEdit(self)
        self.show_outsave_files_path_button.setGeometry(190/1920*win_width, 590/1080*win_height, 655/1920*win_width, 35/1080*win_height)
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        classial_desktop_path = desktop_path + '/' + 'Download'
        self.show_outsave_files_path_button.setText(classial_desktop_path)

        self.choose_outsave_files_path_button = QPushButton('<<<', self)
        self.choose_outsave_files_path_button.setGeometry(855/1920*win_width, 591/1080*win_height, 45/1920*win_width, 30/1080*win_height)
        self.choose_outsave_files_path_button.clicked.connect(self.save_download_files_path_function)

        self.igs_name_sure_but = QPushButton('Download', self)
        self.igs_name_sure_but.setFont(QFont("Times New Roman"))
        self.igs_name_sure_but.setGeometry(90/1920*win_width, 660/1080*win_height, 120/1920*win_width, 40/1080*win_height)
        self.igs_name_sure_but.clicked.connect(self.data_download_function02)

        self.download_details_report_but = QPushButton('Detail', self)
        self.download_details_report_but.setFont(QFont("Times New Roman"))
        self.download_details_report_but.setGeometry(313/1920*win_width, 660/1080*win_height, 120/1920*win_width, 40/1080*win_height)
        self.download_details_report_but.clicked.connect(self.download_details_report_view)

        self.open_have_download_file_path_but = QPushButton('Open', self)
        self.open_have_download_file_path_but.setFont(QFont("Times New Roman"))
        self.open_have_download_file_path_but.setGeometry(525/1920*win_width, 660/1080*win_height, 120/1920*win_width, 40/1080*win_height)
        self.open_have_download_file_path_but.clicked.connect(self.open_have_download_path)

        self.open_help_file_but = QPushButton('Help', self)
        self.open_help_file_but.setFont(QFont("Times New Roman"))
        self.open_help_file_but.setGeometry(740/1920*win_width, 660/1080*win_height, 120/1920*win_width, 40/1080*win_height)
        self.open_help_file_but.clicked.connect(self.open_download_help_file_but_line)

        self.show_download_information = QLabel(self)
        self.show_download_information.move(55/1920*win_width, 710/1080*win_height)
        self.show_download_information.setFixedSize(800/1920*win_width, 35/1080*win_height)
        self.show_download_process_state = QLabel(self)
        self.show_download_process_state.setGeometry(443/1920*win_width, 710/1080*win_height, 260/1920*win_width, 35/1080*win_height)

        self.download_Progress_bar = QProgressBar(self)
        self.download_Progress_bar.setGeometry(50/1920*win_width, 745/1080*win_height, 880/1920*win_width, 40/1080*win_height)
        self_step = 0
        self.download_Progress_bar.setValue(self_step)
        QApplication.processEvents()

    def obs_met_file_type_changed_link(self):
        self.rinex211_o_check.setCheckState(Qt.Unchecked)
        self.rinex304_o_check.setCheckState(Qt.Unchecked)
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
                win_width = win_width + 420
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
                win_height = win_height + 60
            elif win_height < 600:
                win_width = win_width + 400
                win_height = win_height + 60
            elif win_height <= 680 and win_height > 600:
                win_width = win_width + 630
                win_height = win_height + 60
            else:
                win_width = win_width + 630
                win_height = win_height + 20
        elif win_width <= 960:
            if win_height < 600:
                win_width = win_width + 300
                win_height = win_height + 60
            else:
                win_width = win_width + 300
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
        self.igs_obs_intervel_label.setVisible(False)
        self.igs_obs_intervel_box.setVisible(False)
        self.igs_obs_intervel_box.setCurrentText('30s')
        if self.label_OBS_name.currentText() == 'Observation':
            self.label_OBS_windows.setGeometry(190/1920*win_width, 20/1080*win_height, 320/1920*win_width, 100/1080*win_height)
            self.rinex211_o_check.setText('RINEX 2.11(.*o)')
            self.rinex304_o_check.setText('RINEX 3.xx(_MO.crx)')
            self.rinex211_o_check.move(310 / 1920 * win_width, 45 / 1080 * win_height)
            self.rinex304_o_check.move(310 / 1920 * win_width, 80 / 1080 * win_height)
            self.igs_obs_intervel_label.setVisible(True)
            self.igs_obs_intervel_box.setVisible(True)
        elif self.label_OBS_name.currentText() == 'Meteorology':
            self.label_OBS_windows.setGeometry(190 / 1920 * win_width, 20 / 1080 * win_height, 265 / 1920 * win_width, 100 / 1080 * win_height)
            self.rinex211_o_check.setText('RINEX 2.11(.*m)')
            self.rinex304_o_check.setText('RINEX 3.xx(_MM.rnx)')
            self.rinex211_o_check.move(220 / 1920 * win_width, 45 / 1080 * win_height)
            self.rinex304_o_check.move(220 / 1920 * win_width, 80 / 1080 * win_height)
        elif self.label_OBS_name.currentText() == 'Obs & Met':
            self.label_OBS_windows.setGeometry(190/1920*win_width, 20/1080*win_height, 335/1920*win_width, 100/1080*win_height)
            self.rinex211_o_check.setText('RINEX 2.11(.*o && .*m)')
            self.rinex304_o_check.setText('RINEX 3.xx(_MO.crx && _MM.rnx)')
            self.rinex211_o_check.move(220 / 1920 * win_width, 45 / 1080 * win_height)
            self.rinex304_o_check.move(220 / 1920 * win_width, 80 / 1080 * win_height)
        pass

    def igs_obs_interel_change(self):
        self.start_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.end_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
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
                win_width = win_width + 420
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
                win_height = win_height + 60
            elif win_height < 600:
                win_width = win_width + 400
                win_height = win_height + 60
            elif win_height <= 680 and win_height > 600:
                win_width = win_width + 630
                win_height = win_height + 60
            else:
                win_width = win_width + 630
                win_height = win_height + 20
        elif win_width <= 960:
            if win_height < 600:
                win_width = win_width + 300
                win_height = win_height + 60
            else:
                win_width = win_width + 300
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
        if self.igs_obs_intervel_box.currentText() == '30s':
            if self.rinex211_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs RNX2 Station')
            elif self.rinex304_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs RNX3 Station')
            elif self.rinex211_o_check.isChecked() and self.rinex304_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs RNX2-3 Station')
            else:
                self.choose_add_station_list_box.setCurrentText('All Station')
            self.rinex211_o_check.setText('RINEX 2.11(.*o)                 ')
            self.start_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
            self.end_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
            self.start_time.setDisplayFormat('yyyy-MM-dd')
            self.start_time.setGeometry(400 / 1920 * win_width, 131 / 1080 * win_height, 150 / 1920 * win_width, 30 / 1080 * win_height)
            self.end_time.setDisplayFormat('yyyy-MM-dd')
            self.end_time.setGeometry(650/1920*win_width, 131/1080*win_height, 150/1920*win_width, 30/1080*win_height)
            self.changday0201.setGeometry(400/1920*win_width, 168/1080*win_height, 95/1920*win_width, 30/1080*win_height)
            self.changday0202.setGeometry(500/1920*win_width, 168/1080*win_height, 50/1920*win_width, 30/1080*win_height)
            self.changday0301.setGeometry(400/1920*win_width, 203/1080*win_height, 95/1920*win_width, 30/1080*win_height)
            self.changday0302.setGeometry(500/1920*win_width, 203/1080*win_height, 50/1920*win_width, 30/1080*win_height)
            self.changday0401.setGeometry(650/1920*win_width, 168/1080*win_height, 95/1920*win_width, 30/1080*win_height)
            self.changday0402.setGeometry(750/1920*win_width, 168/1080*win_height, 50/1920*win_width, 30/1080*win_height)
            self.changday0501.setGeometry(650/1920*win_width, 203/1080*win_height, 95/1920*win_width, 30/1080*win_height)
            self.changday0502.setGeometry(750/1920*win_width, 203/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        else:
            if self.rinex211_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs RNX2 Highrate Sta')
            elif self.rinex304_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs RNX3 Highrate Sta')
            elif self.rinex211_o_check.isChecked() and self.rinex304_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs RNX2-3 Highrate Sta')
            else:
                self.choose_add_station_list_box.setCurrentText('All Station')
            # self.choose_local_area_box.addItems(['WHU(China)', 'IGN(France)', 'ESA(Europe)', 'KASI(Korea)', 'SIO(USA)', 'CDDIS(USA)'])
            self.rinex211_o_check.setText('RINEX 2.11(.*d)                 ')
            self.start_time.setDisplayFormat('yyyy-MM-dd HH:mm')
            self.start_time.setGeometry(385 / 1920 * win_width, 131 / 1080 * win_height, 180 / 1920 * win_width, 30 / 1080 * win_height)
            self.end_time.setDisplayFormat('yyyy-MM-dd HH:mm')
            self.end_time.setGeometry(635/1920*win_width, 131/1080*win_height, 180/1920*win_width, 30/1080*win_height)
            self.changday0201.setGeometry(385/1920*win_width, 168/1080*win_height, 110/1920*win_width, 30/1080*win_height)
            self.changday0202.setGeometry(500/1920*win_width, 168/1080*win_height, 65/1920*win_width, 30/1080*win_height)
            self.changday0301.setGeometry(385/1920*win_width, 203/1080*win_height, 110/1920*win_width, 30/1080*win_height)
            self.changday0302.setGeometry(500/1920*win_width, 203/1080*win_height, 65/1920*win_width, 30/1080*win_height)
            self.changday0401.setGeometry(635/1920*win_width, 168/1080*win_height, 110/1920*win_width, 30/1080*win_height)
            self.changday0402.setGeometry(750/1920*win_width, 168/1080*win_height, 65/1920*win_width, 30/1080*win_height)
            self.changday0501.setGeometry(635/1920*win_width, 203/1080*win_height, 110/1920*win_width, 30/1080*win_height)
            self.changday0502.setGeometry(750/1920*win_width, 203/1080*win_height, 65/1920*win_width, 30/1080*win_height)
            if self.choose_local_area_box.currentText() == 'WHU(China)':
                if self.rinex211_o_check.isChecked() or self.rinex304_o_check.isChecked():
                    self.start_time.setMinimumDate(QDate(2021, 9, 2))
                    self.end_time.setMinimumDate(QDate(2021, 9, 2))
            pass

    def obs_file_change_add_station_list(self):
        self.start_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.end_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        if self.label_OBS_name.currentText() == 'Observation':
            if self.igs_obs_intervel_box.currentText() == '30s':
                if self.rinex211_o_check.isChecked() and self.rinex304_o_check.isChecked():
                    self.choose_add_station_list_box.setCurrentText('Obs RNX2-3 Station')
                elif self.rinex211_o_check.isChecked():
                    self.choose_add_station_list_box.setCurrentText('Obs RNX2 Station')
                elif self.rinex304_o_check.isChecked():
                    self.choose_add_station_list_box.setCurrentText('Obs RNX3 Station')
                else:
                    self.choose_add_station_list_box.setCurrentText('All Station')
            elif self.igs_obs_intervel_box.currentText() == '1s':
                if self.rinex211_o_check.isChecked() and self.rinex304_o_check.isChecked():
                    self.choose_add_station_list_box.setCurrentText('Obs RNX2-3 Highrate Sta')
                elif self.rinex211_o_check.isChecked():
                    self.choose_add_station_list_box.setCurrentText('Obs RNX2 Highrate Sta')
                elif self.rinex304_o_check.isChecked():
                    self.choose_add_station_list_box.setCurrentText('Obs RNX3 Highrate Sta')
                else:
                    self.choose_add_station_list_box.setCurrentText('All Station')
                if self.choose_local_area_box.currentText() == 'WHU(China)':
                    if self.rinex211_o_check.isChecked() or self.rinex304_o_check.isChecked():
                        self.start_time.setMinimumDate(QDate(2021, 9, 2))
                        self.end_time.setMinimumDate(QDate(2021, 9, 2))
        elif self.label_OBS_name.currentText() == 'Meteorology':
            if self.rinex211_o_check.isChecked() and self.rinex304_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Met RNX2-3 Station')
            elif self.rinex211_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Met RNX2 Station')
            elif self.rinex304_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Met RNX3 Station')
            else:
                self.choose_add_station_list_box.setCurrentText('All Station')
        elif self.label_OBS_name.currentText() == 'Obs & Met':
            if self.rinex211_o_check.isChecked() and self.rinex304_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs-Met RNX2-3 Station')
            elif self.rinex211_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs-Met RNX2 Station')
            elif self.rinex304_o_check.isChecked():
                self.choose_add_station_list_box.setCurrentText('Obs-Met RNX3 Station')
            else:
                self.choose_add_station_list_box.setCurrentText('All Station')
        pass

    def choose_add_station_list(self):
        self.main_list.clear()
        json_text = json.load(open(str(curdir) + r'/lib/json/IGS_Statios.json', 'r'))
        all_station_list = json_text[1]
        rinex_211_station_list = json_text[2]
        rinex_3x_station_list = json_text[3]
        rinex_211and3x_station_list = json_text[4]
        met_rnx_211_station_list = json_text[5]
        met_rnx_3x_station_list = json_text[6]
        met_rnx_211and3x_station_list = json_text[7]
        obs_met_rnx_211_station_list = json_text[8]
        obs_met_rnx_3x_station_list = json_text[9]
        obs_met_rnx_211and3x_station_list = json_text[10]
        high_rate_rinex_211_station = json_text[11]
        high_rate_rinex_304_station = json_text[12]
        #['All Station', 'Obs RNX2 Station', 'Obs RNX3 Station', 'Obs RNX2-3 Station', 'Met RNX2 Station', 'Met RNX3 Station', 'Met RNX2-3 Station', 'Obs-Met RNX2 Station', 'Obs-Met RNX3 Station', 'Obs-Met RNX2-3 Station'])
        #  'Obs RNX2 Highrate Sta', 'Obs RNX3 Highrate Sta', 'Obs RNX2-3 Highrate Sta'
        if self.choose_add_station_list_box.currentText() == 'All Station':
            add_station_list = all_station_list
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX2 Station':
            add_station_list = rinex_211_station_list
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX3 Station':
            add_station_list = rinex_3x_station_list
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX2-3 Station':
            add_station_list = rinex_211and3x_station_list
        elif self.choose_add_station_list_box.currentText() == 'Met RNX2 Station':
            add_station_list = met_rnx_211_station_list
        elif self.choose_add_station_list_box.currentText() == 'Met RNX3 Station':
            add_station_list = met_rnx_3x_station_list
        elif self.choose_add_station_list_box.currentText() == 'Met RNX2-3 Station':
            add_station_list = met_rnx_211and3x_station_list
        elif self.choose_add_station_list_box.currentText() == 'Obs-Met RNX2 Station':
            add_station_list = obs_met_rnx_211_station_list
        elif self.choose_add_station_list_box.currentText() == 'Obs-Met RNX3 Station':
            add_station_list = obs_met_rnx_3x_station_list
        elif self.choose_add_station_list_box.currentText() == 'Obs-Met RNX2-3 Station':
            add_station_list = obs_met_rnx_211and3x_station_list
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX2 Highrate Sta':
            add_station_list = high_rate_rinex_211_station
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX3 Highrate Sta':
            add_station_list = high_rate_rinex_304_station
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX2-3 Highrate Sta':
            add_station_list = high_rate_rinex_211_station
        global_var.set_value('IGS_current_view_station_list', add_station_list)
        for item1 in add_station_list:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.main_list.addItem(item)
        self.left_added_station_to_right_checked()

    def Search_text_changed(self):
        self.main_list.clear()
        add_station_list = global_var.get_value('IGS_current_view_station_list')
        for item1 in add_station_list:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.main_list.addItem(item)

        goal_search_text = self.search_igs_label.text().lower()
        station_list_num = self.main_list.count()
        all_list_station_list = []
        for num in range(station_list_num):
            list_station = self.main_list.item(num).text()
            all_list_station_list.append(list_station)

        searched_station_num = 0
        choosed_station_row_list = []
        for list_station in all_list_station_list:
            if goal_search_text in list_station:
                choosed_station_row_list.append(searched_station_num)
            searched_station_num = searched_station_num + 1

        choosed_station_temp = all_list_station_list
        choosed_station_text_temp = []
        for i in reversed(choosed_station_row_list):
            choosed_station_text_temp.append(choosed_station_temp[i])
            del choosed_station_temp[i]
        for j in choosed_station_text_temp:
            choosed_station_temp.insert(0, j)

        self.main_list.clear()
        for item1 in choosed_station_temp:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.main_list.addItem(item)
        self.main_list.verticalScrollBar().setSliderPosition(0)
        self.left_added_station_to_right_checked()

    def brdc_n_g_change(self):
        if self.rinex211_n_box.currentText() == 'GPS':
            self.rinex211_n_label.setText('RINEX 2.xx(.*n)')
        else:
            self.rinex211_n_label.setText('RINEX 2.xx(.*g)')
        pass

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

    def save_download_files_path_function(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Select Output File', 'C:/')
        if save_path == '':
            print('Save path not selected')
            pass
        else:
            self.show_outsave_files_path_button.setText(save_path)
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

    # -------------------------------------------------------------------------------------------------
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
    # -------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------
    # Open download directory
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

    #  Map display
    def add_map_Items(self):
        # self.choose_add_station_list_box.addItems(['All Station', 'Obs RNX2 Station', 'Obs RNX3 Station', 'Obs RNX2-3 Station'])
        #  'Obs RNX2 Highrate Sta', 'Obs RNX3 Highrate Sta', 'Obs RNX2-3 Highrate Sta'
        if self.choose_add_station_list_box.currentText() == 'All Station':
            Download_Source = '/IGS_all'
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX2 Station':
            Download_Source = '/IGS_rinex2'
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX3 Station':
            Download_Source = '/IGS_rinex3'
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX2-3 Station':
            Download_Source = '/IGS_rinex23'
        elif self.choose_add_station_list_box.currentText() == 'Met RNX2 Station':
            Download_Source = '/IGS_met_rinex2'
        elif self.choose_add_station_list_box.currentText() == 'Met RNX3 Station':
            Download_Source = '/IGS_met_rinex3'
        elif self.choose_add_station_list_box.currentText() == 'Met RNX2-3 Station':
            Download_Source = '/IGS_met_rinex23'
        elif self.choose_add_station_list_box.currentText() == 'Obs-Met RNX2 Station':
            Download_Source = '/IGS_obs_met_rinex2'
        elif self.choose_add_station_list_box.currentText() == 'Obs-Met RNX3 Station':
            Download_Source = '/IGS_obs_met_rinex3'
        elif self.choose_add_station_list_box.currentText() == 'Obs-Met RNX2-3 Station':
            Download_Source = '/IGS_obs_met_rinex23'
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX2 Highrate Sta':
            Download_Source = '/IGS_higt_rate_rinex2'
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX3 Highrate Sta':
            Download_Source = '/IGS_higt_rate_rinex3'
        elif self.choose_add_station_list_box.currentText() == 'Obs RNX2-3 Highrate Sta':
            Download_Source = '/IGS_higt_rate_rinex23'
        self.h = Return_Map_Names(Download_Source)
        self.h.my_Signal.connect(self.close_sonView_trigger_event)
        self.h.show()
        pass

    # Close map
    def close_sonView_trigger_event(self):
        map_igs_names = []
        try:
            Map_IGS_name = global_var.get_value('IGS_station_list')
            if Map_IGS_name != {}:
                Map_IGS_name_list = Map_IGS_name['name']
                Map_IGS_name_list = list(Map_IGS_name_list)
                for i in Map_IGS_name_list:
                    map_igs_names.append(i)
                temp_station_text = ''
                for map_igs_name in map_igs_names:
                    temp_station_text = temp_station_text + str(map_igs_name) + '\n'
                self.igs_names_display.append(temp_station_text[:-1])
                pass
            self.left_added_station_deduplication()
            self.calculate_added_station_num()
        except:
            pass

    # Station information table
    def open_igs_station_table_view(self):
        self.exit_window = IGS_Station_Info_Table()
        self.exit_window.my_Signal_IGS.connect(self.IGS_Info_Table_exit)
        self.exit_window.show()
        pass
    def IGS_Info_Table_exit(self):
        IGS_Info_checked_station_list = global_var.get_value('Info_table_checked_IGS_stations')
        if IGS_Info_checked_station_list:
            temp_station_text = ''
            for i in IGS_Info_checked_station_list:
                temp_station_text = temp_station_text + str(i) + '\n'
                pass
            self.igs_names_display.append(temp_station_text[:-1])
        self.left_added_station_deduplication()
        self.calculate_added_station_num()
        self.choose_add_station_list()
        clear_station_list = []
        global_var.set_value('Info_table_checked_IGS_stations', clear_station_list)

    # Select station map display
    def station_map_display_function(self):
        json_text = json.load(open(str(curdir) + r'/lib/json/IGS_Statios_BaiDu_Coordinate.json', 'r'))
        all_source_Info = json_text[0]
        all_choosed_station_list = re.split('[,\n]', self.igs_names_display.toPlainText())
        print(all_choosed_station_list)
        if all_choosed_station_list == ['']:
            QMessageBox.warning(self, 'Tips', "No added station")
            return
        check_igs_names = []
        for k in all_choosed_station_list:
            if k not in check_igs_names and k != '':
                check_igs_names.append(k)
        added_station_coordinate = []
        for i in check_igs_names:
            for j in all_source_Info:
                if i.lower() in j:
                    added_station_coordinate = added_station_coordinate + [j]
        if added_station_coordinate == []:
            QMessageBox.information(self, 'Tips', 'The station coordinates are not matched !')
            return
        f_read = open(str(curdir) + r'/templates/TempDisplayMapTemplate.html', 'r', encoding='utf8')
        f_write = open(str(curdir) + r'/templates/TempDisplayMapTemplate02.html', 'w', encoding='utf8')
        number = 0
        for line in f_read:
            number += 1
            if number == 32:
                coordinat_x = added_station_coordinate[0][1]
                coordinat_y = added_station_coordinate[0][2]
                line = 'map.centerAndZoom(new BMapGL.Point(' + str(coordinat_x) + ', ' + str(coordinat_y) + '), 2);'
            if number == 40:
                line = 'data1' + ' = ' + str(added_station_coordinate) + ';'
            f_write.write(line)
        f_read.close()
        f_write.close()
        self.s = Station_Map_Display_View()
        self.s.show()
        pass

    # Select all station
    def choose_all_station_function(self):
        if self.choose_all_station_CheckBtn.checkState() == Qt.Checked:
            for num in range(self.main_list.count()):
                self.main_list.item(num).setCheckState(Qt.Checked)
        else:
            for num in range(self.main_list.count()):
                self.main_list.item(num).setCheckState(Qt.Unchecked)
        pass

    # add station
    def add_igs_Items_function(self):
        check_igs_names = []
        for num in range(self.main_list.count()):
            if self.main_list.item(num).checkState() == Qt.Checked:
                check_igs_names.append(self.main_list.item(num).text())
                self.main_list.item(num).setCheckState(False)
        temp_station_text = ''
        for check_igs_name in check_igs_names:
            temp_station_text = temp_station_text + str(check_igs_name) + '\n'
            # self.igs_names_display.append(str(check_igs_name))
            pass
        self.igs_names_display.append(temp_station_text[:-1])
        self.left_added_station_deduplication()

    def clear_added_station_function(self):
        self.igs_names_display.clear()
        self.choose_all_station_CheckBtn.setChecked(False)
        pass

    # Add station to Textbox
    def added_station_view_link(self):
        try:
            all_choosed_station_list = re.split('[,\n]', self.igs_names_display.toPlainText())
            added_station_num = 0
            for k in all_choosed_station_list:
                if len(k) == 4:
                    added_station_num = added_station_num + 1
            # print(added_station_num)
            self.igs_names_display_label.setText('Added %s Station' % (added_station_num))
            self.left_added_station_to_right_checked()
        except:
            pass

    # Displays the number of stations added
    def calculate_added_station_num(self):
        try:
            all_choosed_station_list = re.split('[,\n]', self.igs_names_display.toPlainText())
            added_station_num = 0
            for k in all_choosed_station_list:
                if len(k) == 4:
                    added_station_num = added_station_num + 1
            # print(added_station_num)
            self.igs_names_display_label.setText('Added %s Station' % (added_station_num))
            self.left_added_station_to_right_checked()
        except:
            pass

    # Delete duplicate stations
    def left_added_station_deduplication(self):
        all_choosed_station_list = re.split('[,\n]', self.igs_names_display.toPlainText())
        check_igs_names = []
        for k in all_choosed_station_list:
            if k not in check_igs_names and k != '':
                check_igs_names.append(k)
        temp_station_text = ''
        self.igs_names_display.clear()
        for check_igs_name in check_igs_names:
            temp_station_text = temp_station_text + str(check_igs_name) + '\n'
        self.igs_names_display.append(temp_station_text)

    # Add station, check the check box
    def left_added_station_to_right_checked(self):
        for k in range(self.main_list.count()):
            self.main_list.item(k).setCheckState(Qt.Unchecked)
        all_choosed_station_list = re.split('[,\n]', self.igs_names_display.toPlainText())
        goal_added_station_row = []
        for i in all_choosed_station_list:
            for num in range(self.main_list.count()):
                if i.lower() == self.main_list.item(num).text():
                    goal_added_station_row.append(num)
            pass
        # print(goal_added_station_row)
        for k in goal_added_station_row:
            self.main_list.item(k).setCheckState(Qt.Checked)

    # -------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------
    # @func_set_timeout(30)
    def CDDIS_Download_Function(self, url, file_name):
        global successful_library
        global failed_library
        global cddis_ftp_link
        local_file = self.show_outsave_files_path_button.text()+'/'+file_name
        remote_file = url.replace('gdc.cddis.eosdis.nasa.gov', '')
        buf_size = 1024
        list = [url, file_name]
        try:
            file_handler = open(local_file, 'wb')
            cddis_ftp_link.prot_p()
            res = cddis_ftp_link.retrbinary('RETR {}'.format(remote_file), file_handler.write, buf_size)
            file_handler.close()
            print('success：', url)
            successful_library = successful_library + [list]
        except:
            print('failure：', url)
            failed_library = failed_library + [list]


    @retry(stop_max_attempt_number=21600, wait_random_min=1000, wait_random_max=5000)
    # @func_set_timeout(20)
    def WUHAN_function(self, url, file_name):
        global successful_library
        global failed_library
        global self_step
        global ftp_max_thread
        with ftp_max_thread:
            list = [url, file_name]
            self_file_path = self.show_outsave_files_path_button.text()+'/'+str(file_name)
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


    # -------------------------------------------------------------------------------------------------
    # """ download main function """
    def data_download_function02(self):
        self.show_download_process_state.setText('downloading...')
        # Judgment networking
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

        # session initialization and Set the number of threads
        global session
        global ftp_max_thread
        if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
            session = requests.Session()
        else:
            requests_ftp.monkeypatch_session()
            session = requests.Session()
            if self.choose_local_area_box.currentText() == 'WHU(China)':
                ftp_max_thread = threading.Semaphore(15)
            elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                ftp_max_thread = threading.Semaphore(2)
            elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                ftp_max_thread = threading.Semaphore(3)
            elif self.choose_local_area_box.currentText() == 'IGN(France)':
                ftp_max_thread = threading.Semaphore(10)
            elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                ftp_max_thread = threading.Semaphore(10)
            pass
        if os.path.exists(self.show_outsave_files_path_button.text()):
            pass
        else:
            os.mkdir(self.show_outsave_files_path_button.text())

        # time list
        if self.igs_obs_intervel_box.currentText() == '30s':
            start_time_T = str(self.start_time.dateTime().toString(Qt.ISODate))
            start_time = start_time_T[0:10] + ' ' + start_time_T[11:19]
            start_time_date = start_time_T[0:10]
            end_time_T = str(self.end_time.dateTime().toString(Qt.ISODate))
            end_time = end_time_T[0:10] + ' ' + end_time_T[11:19]
            end_time_date = end_time_T[0:10]
            dt1 = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            dt2 = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            difference_time = dt2 - dt1
            print('Total data：', difference_time.days)
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
                    list = [YearAccuDay_GpsWeek[0], YearAccuDay_GpsWeek[1], YearAccuDay_GpsWeek[2],
                            YearAccuDay_GpsWeek[3], YearAccuDay_GpsWeek[4], YearAccuDay_GpsWeek[5]]
                    all_YearAccuDay_GpsWeek = all_YearAccuDay_GpsWeek + [list]
                    pass
                # print(all_YearAccuDay_GpsWeek)
        else:
            start_time_T = str(self.start_time.dateTime().toString(Qt.ISODate))
            start_time = start_time_T[0:10] + ' ' + start_time_T[11:19]
            start_time_date_1s = start_time_T[0:10]
            end_time_T = str(self.end_time.dateTime().toString(Qt.ISODate))
            end_time = end_time_T[0:10] + ' ' + end_time_T[11:19]
            end_time_date_1s = end_time_T[0:10]
            dt1 = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            dt2 = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            difference_time = dt2 - dt1
            print('Total data：', difference_time.days)
            if difference_time.days >= 0:
                Judgement_time = 1
            else:
                Judgement_time = 0
            if Judgement_time == 0:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Tips', 'Please adjust time range !')
                return
            else:
                start_time_T = str(self.start_time.dateTime().toString(Qt.ISODate))
                start_time = start_time_T[0:10] + ' ' + start_time_T[11:19]
                start_time_date = start_time_T[0:10]
                start_time_hhmmss = start_time_T[11:19]
                end_time_T = str(self.end_time.dateTime().toString(Qt.ISODate))
                end_time = end_time_T[0:10] + ' ' + end_time_T[11:19]
                end_time_date = end_time_T[0:10]
                end_time_hhmmss = end_time_T[11:19]
                start_time_hhmmss_list = [int(start_time_hhmmss[0:2]), int(start_time_hhmmss[3:5]), int(start_time_hhmmss[6:8])]
                end_time_hhmmss_list = [int(end_time_hhmmss[0:2]), int(end_time_hhmmss[3:5]), int(end_time_hhmmss[6:8])]
                print('Start time：', start_time_hhmmss_list)
                print('End time：', end_time_hhmmss_list)

                date_list_1s = self.getEveryDay(start_time_date_1s, end_time_date_1s)
                all_YearAccuDay_GpsWeek_1s = []
                for i in date_list_1s:
                    YearAccuDay_GpsWeek = self.GpsWeek_YearAccuDay(i)
                    list = [YearAccuDay_GpsWeek[0], YearAccuDay_GpsWeek[1], YearAccuDay_GpsWeek[2],
                            YearAccuDay_GpsWeek[3], YearAccuDay_GpsWeek[4], YearAccuDay_GpsWeek[5]]
                    all_YearAccuDay_GpsWeek_1s = all_YearAccuDay_GpsWeek_1s + [list]
                    pass
                print(all_YearAccuDay_GpsWeek_1s)
                all_YearAccuDay_GpsWeek = all_YearAccuDay_GpsWeek_1s[:]

                # Start time
                delete_minute_num1 = -1
                for i in [0, 15, 30, 45]:
                    if start_time_hhmmss_list[1] < i:
                        break
                    delete_minute_num1 = delete_minute_num1 + 1
                del_standard_minute_span = [0, 15, 30, 45]
                for i in range(delete_minute_num1):
                    del del_standard_minute_span[0]
                start_time_hhmmss = []
                for j in del_standard_minute_span:
                    i = start_time_hhmmss_list[0]
                    i = f"0{i}" if i < 10 else f"{i}"
                    j = f"0{j}" if j < 10 else f"{j}"
                    list1 = [i, j]
                    start_time_hhmmss = start_time_hhmmss + [list1]
                for i in range(start_time_hhmmss_list[0]+1, 24):
                    i = f"0{i}" if i < 10 else f"{i}"
                    for j in ['00', '15', '30', '45']:
                        list1 = [i, j]
                        start_time_hhmmss = start_time_hhmmss + [list1]

                # End time
                useful_minute_num2 = 0
                for i in [0, 15, 30, 45]:
                    if end_time_hhmmss_list[1] > i:
                        useful_minute_num2 = useful_minute_num2 + 1
                delete_minute_num2 = 4 - useful_minute_num2
                del_standard_minute_span = [0,15,30,45]
                for i in range(delete_minute_num2):
                    del del_standard_minute_span[-1]
                end_time_hhmmss = []
                for j in del_standard_minute_span:
                    i = end_time_hhmmss_list[0]
                    i = f"0{i}" if i < 10 else f"{i}"
                    j = f"0{j}" if j < 10 else f"{j}"
                    list1 = [i, j]
                    end_time_hhmmss = end_time_hhmmss + [list1]
                for i in range(0, end_time_hhmmss_list[0]):
                    i = f"0{i}" if i < 10 else f"{i}"
                    for j in ['00', '15', '30', '45']:
                        list1 = [i, j]
                        end_time_hhmmss = end_time_hhmmss + [list1]

                all_date_hhmmss = []
                if len(all_YearAccuDay_GpsWeek_1s) == 1:
                    temp_final_hhffmm_list = []
                    for i in start_time_hhmmss:
                        if i in end_time_hhmmss:
                            temp_final_hhffmm_list = temp_final_hhffmm_list + [i]
                    for i in temp_final_hhffmm_list:
                        temp_datetime1 = all_YearAccuDay_GpsWeek_1s[0] + i
                        all_date_hhmmss = all_date_hhmmss + [temp_datetime1]
                elif len(all_YearAccuDay_GpsWeek_1s) == 2:
                    for i in start_time_hhmmss:
                        all_date_hhmmss = all_date_hhmmss + [all_YearAccuDay_GpsWeek_1s[0] + i]
                    for j in end_time_hhmmss:
                        all_date_hhmmss = all_date_hhmmss + [all_YearAccuDay_GpsWeek_1s[1] + j]
                elif len(all_YearAccuDay_GpsWeek_1s) > 2:
                    for i in start_time_hhmmss:
                        all_date_hhmmss = all_date_hhmmss + [all_YearAccuDay_GpsWeek_1s[0] + i]
                    for j in end_time_hhmmss:
                        all_date_hhmmss = all_date_hhmmss + [all_YearAccuDay_GpsWeek_1s[-1] + j]
                    temp_all_YearAccuDay_GpsWeek_1s = all_YearAccuDay_GpsWeek_1s
                    del (temp_all_YearAccuDay_GpsWeek_1s[0], temp_all_YearAccuDay_GpsWeek_1s[-1])
                    for x in range(24):
                        x = f"0{x}" if x < 10 else f"{x}"
                        for y in ['00', '15', '30', '45']:
                            for z in temp_all_YearAccuDay_GpsWeek_1s:
                                all_date_hhmmss = all_date_hhmmss + [z + [x] + [y]]
                print(all_date_hhmmss)

        # Get station name
        igs_name_list = str(self.igs_names_display.toPlainText())
        igs_name_list = re.findall(r'\w+', igs_name_list)
        temp_igs_name_list = []
        for i in igs_name_list:
            if i not in temp_igs_name_list:
                temp_igs_name_list.append(i)
        igs_name_list = temp_igs_name_list
        print(igs_name_list)
        igs_uppercase = []
        igs_lowercase = []
        for igs_name in igs_name_list:
            igs_name = igs_name.lower()
            upper_igs_name = igs_name.upper()
            igs_uppercase.append(upper_igs_name)
            igs_lowercase.append(igs_name)

        # output path
        if self.show_outsave_files_path_button.text() == '':
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips', 'Please choose a output path!')
            return

        # Download file list
        rinex211o_url_list = []
        rinex304o_url_list = []
        rinex211n_url_list = []
        rinex304n_url_list = []

        #  Observation Files_URL
        if self.label_OBS_name.currentText() == 'Observation':
            # Rinex 2.11 url
            if self.rinex211_o_check.isChecked():
                if igs_lowercase == []:
                    self.show_download_process_state.setText('')
                    QMessageBox.information(self, 'Tips', 'No IGS stations added!')
                    return
                else:
                    #    self.igs_obs_intervel_box.addItems(['30s', '1s'])
                    if self.igs_obs_intervel_box.currentText() == '30s':
                        for time in all_YearAccuDay_GpsWeek:
                            for igs211_name in igs_lowercase:
                                if int(time[0]) <= 2020 and int(time[3]) <= 334:
                                    igs_0_weibu = 'o.Z'
                                else:
                                    igs_0_weibu = 'o.gz'
                                file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + igs_0_weibu
                                if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                    download_rinex211o_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'o/'+file_name
                                elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                    download_rinex211o_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'o/'+file_name
                                elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                    file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'd.Z'
                                    download_rinex211o_url = 'http://garner.ucsd.edu/pub/rinex/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                                elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                    download_rinex211o_url = 'ftp://gssc.esa.int/gnss/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                                elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                    download_rinex211o_url = 'ftp://igs.ign.fr/pub/igs/data/'+str(time[0])+'/'+str(time[3])+'/'+igs211_name+str(time[3])+str(0)+'.'+str(time[1])+'d.gz'
                                    file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'd.gz'
                                elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                    download_rinex211o_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'o/'+file_name
                                list = [download_rinex211o_url, file_name]
                                rinex211o_url_list = rinex211o_url_list + [list]
                                pass
                    elif self.igs_obs_intervel_box.currentText() == '1s':
                        rinex211o_url_list_temp = []
                        for time in all_date_hhmmss:
                            for igs211_name in igs_lowercase:
                                if int(time[0]) <= 2020 and int(time[3]) <= 334:
                                    igs_0_weibu = 'd.Z'
                                else:
                                    igs_0_weibu = 'd.gz'
                                #  nano351a15.21d.gz
                                file_name = igs211_name + str(time[3]) + chr(int(time[6])+97) + time[7] + '.' + str(time[1]) + igs_0_weibu
                                if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                    download_rinex211o_url = 'https://cddis.nasa.gov/archive/gnss/data/highrate/' + str(time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'd/' + time[6] + '/' + file_name
                                elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                    #  ftp://igs.gnsswhu.cn/pub/highrate/2021/351/21d/00/nano351a15.21d.gz
                                    download_rinex211o_url = 'ftp://igs.gnsswhu.cn/pub/highrate/' + str(time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'd/' + time[6] + '/' + file_name
                                elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                    #    http://garner.ucsd.edu/archive/garner/rinex_highrate/2021/002/alth0020.21d.Z
                                    file_name = file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'd.Z'
                                    download_rinex211o_url = 'http://garner.ucsd.edu/archive/garner/rinex_highrate/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                                elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                    download_rinex211o_url = 'ftp://gssc.esa.int/gnss/data/highrate/' + str(time[0]) + '/' + str(time[3]) + '/' + time[6] + '/' + file_name
                                elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                    download_rinex211o_url = 'ftp://igs.ign.fr/pub/igs/data/highrate/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                                elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                    download_rinex211o_url = 'ftp://nfs.kasi.re.kr/gnss/data/highrate/' + str(time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'd/' + time[6] + '/' + file_name
                                list = [download_rinex211o_url, file_name]
                                rinex211o_url_list_temp = rinex211o_url_list_temp + [list]

                                for i in rinex211o_url_list_temp:
                                    if i not in rinex211o_url_list:
                                        rinex211o_url_list.append(i)
                pass

            #  Rinex 3.xx url
            if self.rinex304_o_check.isChecked():
                if igs_uppercase == []:
                    self.show_download_process_state.setText('')
                    QMessageBox.information(self, 'warning', 'IGS station of rinex3.04 is not detected！')
                    return
                else:
                    #   self.igs_obs_intervel_box.addItems(['30s', '1s'])
                    if self.igs_obs_intervel_box.currentText() == '30s':
                        for time in all_YearAccuDay_GpsWeek:
                            for igs304_name in igs_uppercase:
                                with open(str(curdir) + r'/lib/rinex file name/rinex3.04 file name.txt', 'r') as f:
                                    file_name = re.findall(r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name), f.read())
                                    if file_name:
                                        file_name = file_name[0][0:12] + str(time[0])+str(time[3]) + file_name[0][19:41]
                                    else:
                                        file_name = igs304_name + '00XXX_R_' + str(time[0]) + str(time[3]) + '0000_01D_30S_MO.crx.gz'
                                if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                    download_rinex304o_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'d' + '/'+file_name
                                elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                    download_rinex304o_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/'+str(time[0])+'/' + str(time[3])+'/'+ str(time[1])+'d' + '/'+file_name
                                elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                    # http://garner.ucsd.edu/pub/rinex/2021/001/
                                    download_rinex304o_url = 'http://garner.ucsd.edu/pub/rinex/'+str(time[0])+ '/' + str(time[3])+'/' + file_name
                                elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                    download_rinex304o_url = 'ftp://gssc.esa.int/gnss/data/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                                elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                    download_rinex304o_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(time[0]) + '/' + str(time[3]) + '/'+ file_name
                                elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                    download_rinex304o_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'd' + '/' + file_name
                                list = [download_rinex304o_url, file_name]
                                rinex304o_url_list = rinex304o_url_list + [list]
                                pass
                    elif self.igs_obs_intervel_box.currentText() == '1s':
                        for time in all_date_hhmmss:
                            for igs304_name in igs_uppercase:
                                with open(str(curdir) + r'/lib/rinex file name/high rate rinex3.04 file name.txt', 'r') as f:
                                    file_name = re.findall(r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name), f.read())
                                    if file_name:
                                        file_name = file_name[0][0:12]+str(time[0])+str(time[3])+time[6]+time[7]+file_name[0][23:41]
                                    else:
                                        file_name = igs304_name+'00XXX_R_'+str(time[0])+str(time[3])+time[6]+time[7]+'_15M_01S_MO.crx.gz'
                                        pass
                                if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                    download_rinex304o_url = 'https://cddis.nasa.gov/archive/gnss/data/highrate/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'d/'+time[6]+'/'+file_name
                                elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                    ##  ftp://igs.gnsswhu.cn/pub/highrate/2021/351/21d/00/ABMF00GLP_S_20213510000_15M_01S_MO.crx.gz
                                    download_rinex304o_url = 'ftp://igs.gnsswhu.cn/pub/highrate/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'d/'+time[6]+'/'+file_name
                                elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                    download_rinex304o_url = 'http://garner.ucsd.edu/archive/garner/rinex_highrate/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'d/'+time[6]+'/'+file_name
                                elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                    download_rinex304o_url = 'ftp://gssc.esa.int/gnss/data/highrate/'+str(time[0])+'/'+str(time[3])+'/'+time[6]+'/'+file_name
                                elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                    download_rinex304o_url = 'ftp://igs.ign.fr/pub/igs/data/highrate/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                                elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                    download_rinex304o_url = 'ftp://nfs.kasi.re.kr/gnss/data/highrate/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'d/'+time[6]+'/'+file_name
                                list = [download_rinex304o_url, file_name]
                                rinex304o_url_list = rinex304o_url_list + [list]
                                pass
                pass

        # Meteorology Files_URL
        if self.label_OBS_name.currentText() == 'Meteorology':
            # Rinex2.11 url
            if self.rinex211_o_check.isChecked():
                if igs_lowercase == []:
                    self.show_download_process_state.setText('')
                    QMessageBox.information(self, 'Tips', 'No IGS stations added!')
                    return
                else:
                    for time in all_YearAccuDay_GpsWeek:
                        for igs211_name in igs_lowercase:
                            if int(time[0]) <= 2020 and int(time[3]) <= 334:
                                igs_0_weibu = 'm.Z'
                            else:
                                igs_0_weibu = 'm.gz'
                            file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + igs_0_weibu
                            if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                download_rinex211o_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm/' + file_name
                            elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                download_rinex211o_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm/' + file_name
                            elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'm.Z'
                                download_rinex211o_url = 'http://garner.ucsd.edu/pub/rinex/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                download_rinex211o_url = 'ftp://gssc.esa.int/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                download_rinex211o_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + igs211_name + str(time[3]) + str(
                                    0) + '.' + str(time[1]) + 'm.gz'
                                file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'm.gz'
                            elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                download_rinex211o_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm/' + file_name
                            list = [download_rinex211o_url, file_name]
                            rinex211o_url_list = rinex211o_url_list + [list]
                            pass
                pass

            # Rinex3.xx url
            if self.rinex304_o_check.isChecked():
                if igs_uppercase == []:
                    self.show_download_process_state.setText('')
                    QMessageBox.information(self, 'warning', 'IGS station of rinex3.04 is not detected！')
                    return
                    pass
                else:
                    for time in all_YearAccuDay_GpsWeek:
                        for igs304_name in igs_uppercase:
                            with open(str(curdir) + r'/lib/rinex file name/rinex3.04 file name.txt', 'r') as f:
                                file_name = re.findall(
                                    r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name),
                                    f.read())
                                if file_name:
                                    file_name = file_name[0][0:12] + str(time[0]) + str(time[3]) + '0000_01D_05M_MM.rnx.gz'
                                else:
                                    file_name = igs304_name + '00XXX_R_' + str(time[0]) + str(time[3]) + '0000_01D_05M_MM.rnx.gz'
                                    pass
                            if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                download_rinex304o_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm' + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                download_rinex304o_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm' + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                # http://garner.ucsd.edu/pub/rinex/2021/001/
                                download_rinex304o_url = 'http://garner.ucsd.edu/pub/rinex/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                download_rinex304o_url = 'ftp://gssc.esa.int/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                download_rinex304o_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                download_rinex304o_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm' + '/' + file_name
                            list = [download_rinex304o_url, file_name]
                            rinex304o_url_list = rinex304o_url_list + [list]
                        pass
                pass

        #  Obs & Met Files_URL
        if self.label_OBS_name.currentText() == 'Obs & Met':
            #  Obs_Met  Rinex2.11  url
            if self.rinex211_o_check.isChecked():
                if igs_lowercase == []:
                    self.show_download_process_state.setText('')
                    QMessageBox.information(self, 'Tips', 'No IGS stations added!')
                    return
                else:
                    for time in all_YearAccuDay_GpsWeek:
                        for igs211_name in igs_lowercase:
                            if int(time[0]) <= 2020 and int(time[3]) <= 334:
                                igs_0_weibu = 'm.Z'
                            else:
                                igs_0_weibu = 'm.gz'
                            file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + igs_0_weibu
                            if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                download_rinex211o_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm/' + file_name
                            elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                download_rinex211o_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm/' + file_name
                            elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'm.Z'
                                download_rinex211o_url = 'http://garner.ucsd.edu/pub/rinex/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                download_rinex211o_url = 'ftp://gssc.esa.int/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                download_rinex211o_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + igs211_name + str(time[3]) + str(
                                    0) + '.' + str(time[1]) + 'm.gz'
                                file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'm.gz'
                            elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                download_rinex211o_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm/' + file_name
                            list = [download_rinex211o_url, file_name]
                            rinex211o_url_list = rinex211o_url_list + [list]
                            pass

                        for igs211_name in igs_lowercase:
                            if int(time[0]) <= 2020 and int(time[3]) <= 334:
                                igs_0_weibu = 'o.Z'
                            else:
                                igs_0_weibu = 'o.gz'
                            file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + igs_0_weibu
                            if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                download_rinex211o_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'o/' + file_name
                            elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                download_rinex211o_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'o/' + file_name
                            elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'd.Z'
                                download_rinex211o_url = 'http://garner.ucsd.edu/pub/rinex/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                download_rinex211o_url = 'ftp://gssc.esa.int/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                download_rinex211o_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + igs211_name + str(time[3]) + str(
                                    0) + '.' + str(time[1]) + 'd.gz'
                                file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'd.gz'
                            elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                download_rinex211o_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'o/' + file_name
                            list = [download_rinex211o_url, file_name]
                            rinex211o_url_list = rinex211o_url_list + [list]
                            pass

                pass

            #  Obs_Met  Rinex3.xx url
            if self.rinex304_o_check.isChecked():
                if igs_uppercase == []:
                    self.show_download_process_state.setText('')
                    QMessageBox.information(self, 'warning', 'IGS station of rinex3.04 is not detected！')
                    return
                    pass
                else:
                    for time in all_YearAccuDay_GpsWeek:
                        for igs304_name in igs_uppercase:
                            with open(str(curdir) + r'/lib/rinex file name/rinex3.04 file name.txt', 'r') as f:
                                file_name = re.findall(
                                    r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name),
                                    f.read())
                                if file_name:
                                    file_name = file_name[0][0:12] + str(time[0]) + str(time[3]) + '0000_01D_05M_MM.rnx.gz'
                                else:
                                    file_name = igs304_name + '00XXX_R_' + str(time[0]) + str(time[3]) + '0000_01D_05M_MM.rnx.gz'
                                    pass
                            if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                download_rinex304o_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm' + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                download_rinex304o_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm' + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                # http://garner.ucsd.edu/pub/rinex/2021/001/
                                download_rinex304o_url = 'http://garner.ucsd.edu/pub/rinex/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                download_rinex304o_url = 'ftp://gssc.esa.int/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                download_rinex304o_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                download_rinex304o_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'm' + '/' + file_name
                            list = [download_rinex304o_url, file_name]
                            rinex304o_url_list = rinex304o_url_list + [list]
                        pass
                    # print(rinex304o_url_list)
                    for time in all_YearAccuDay_GpsWeek:
                        for igs304_name in igs_uppercase:
                            with open(str(curdir) + r'/lib/rinex file name/rinex3.04 file name.txt', 'r') as f:
                                file_name = re.findall(r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name), f.read())
                                if file_name:
                                    file_name = file_name[0][0:12] + str(time[0])+str(time[3]) + file_name[0][19:41]
                                else:
                                    file_name = igs304_name + '00XXX_R_' + str(time[0]) + str(time[3]) + '0000_01D_30S_MO.crx.gz'
                                    pass
                            if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                                download_rinex304o_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'d' + '/'+file_name
                            elif self.choose_local_area_box.currentText() == 'WHU(China)':
                                download_rinex304o_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/'+str(time[0])+'/' + str(time[3])+'/'+ str(time[1])+'d' + '/'+file_name
                            elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                                # http://garner.ucsd.edu/pub/rinex/2021/001/
                                download_rinex304o_url = 'http://garner.ucsd.edu/pub/rinex/'+str(time[0])+ '/' + str(time[3])+'/' + file_name
                            elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                                download_rinex304o_url = 'ftp://gssc.esa.int/gnss/data/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                            elif self.choose_local_area_box.currentText() == 'IGN(France)':
                                download_rinex304o_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(time[0]) + '/' + str(time[3]) + '/'+ file_name
                            elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                                download_rinex304o_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'd' + '/' + file_name
                            list = [download_rinex304o_url, file_name]
                            rinex304o_url_list = rinex304o_url_list + [list]
                        pass
                    # print(rinex304o_url_list)
                pass

        # Rinex2.11 Broadcast ephemeris url
        # self.rinex211_n_box.addItems(['GPS', 'GLONASS'])
        if self.rinex211_n_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.rinex211_n_box.currentText() == 'GPS':
                    if int(time[0]) <= 2020 and int(time[3]) <= 334:
                        n_weibu = 'n.Z'
                    else:
                        n_weibu = 'n.gz'
                    file_name = 'brdc' + str(time[3]) + '0.' + str(time[1]) + n_weibu
                    if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                        download_rinex211n_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'n/'+ file_name
                    elif self.choose_local_area_box.currentText() == 'WHU(China)':
                        download_rinex211n_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'n/'+file_name
                    elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                        # http://garner.ucsd.edu/pub/nav/2021/001/baie0010.21n.Z
                        download_rinex211n_url = 'http://garner.ucsd.edu/pub/nav/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                    elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                        download_rinex211n_url = 'ftp://gssc.esa.int/gnss/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                    elif self.choose_local_area_box.currentText() == 'IGN(France)':
                        download_rinex211n_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                        download_rinex211n_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'n/' + file_name
                elif self.rinex211_n_box.currentText() == 'GLONASS':
                    if int(time[0]) <= 2020 and int(time[3]) <= 334:
                        n_weibu = 'g.Z'
                    else:
                        n_weibu = 'g.gz'
                    file_name = 'brdc' + str(time[3]) + '0.' + str(time[1]) + n_weibu
                    if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                        download_rinex211n_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'g/'+ file_name
                    elif self.choose_local_area_box.currentText() == 'WHU(China)':
                        download_rinex211n_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'g/'+file_name
                    elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                        # http://garner.ucsd.edu/pub/nav/2021/001/baie0010.21n.Z
                        download_rinex211n_url = 'http://garner.ucsd.edu/pub/nav/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                    elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                        download_rinex211n_url = 'ftp://gssc.esa.int/gnss/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                    elif self.choose_local_area_box.currentText() == 'IGN(France)':
                        download_rinex211n_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                        download_rinex211n_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + str(time[1]) + 'g/' + file_name
                list = [download_rinex211n_url, file_name]
                rinex211n_url_list = rinex211n_url_list + [list]
            # print(rinex211n_url_list)

        # Rinex3.04 Broadcast ephemeris url
        if self.rinex304_n_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                file_name = 'BRDC00IGS_R_' + str(time[0]) + str(time[3]) + '0000_01D_MN.rnx.gz'
                if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
                    #   gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/2021/001/21p/BRDC00IGS_R_20210010000_01D_MN.rnx.gz
                    download_rinex304n_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'p/BRDC00IGS_R_'+str(time[0])+str(time[3])+'0000_01D_MN.rnx.gz'
                elif self.choose_local_area_box.currentText() == 'WHU(China)':
                    #   ftp://igs.gnsswhu.cn/pub/gps/data/daily/2021/001/21p/BRDC00IGS_R_20210010000_01D_MN.rnx.gz
                    download_rinex304n_url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'p/BRDC00IGS_R_'+str(time[0])+str(time[3])+'0000_01D_MN.rnx.gz'
                elif self.choose_local_area_box.currentText() == 'SIO(USA)':
                    # Not founding brdc 3.0x, thus the url is invailed.
                    download_rinex304n_url = 'http://garner.ucsd.edu/pub/nav/'+str(time[0])+'/'+str(time[3])+'/'+'BRDC00IGS_R_'+str(time[0])+str(time[3])+'0000_01D_MN.rnx.gz'
                elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
                    #   ftp://gssc.esa.int/gnss/data/daily/2021/001/BRDC00IGS_R_20210010000_01D_MN.rnx.gz
                    download_rinex304n_url = 'ftp://gssc.esa.int/gnss/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+'BRDC00IGS_R_'+str(time[0])+str(time[3])+'0000_01D_MN.rnx.gz'
                elif self.choose_local_area_box.currentText() == 'IGN(France)':
                    download_rinex304n_url = 'ftp://igs.ign.fr/pub/igs/data/' + str(time[0]) + '/' + str(time[3]) + '/' + 'BRDC00IGN_R_' + str(time[0]) + str(time[3]) + '0000_01D_MN.rnx.gz'
                    file_name = 'BRDC00IGN_R_' + str(time[0]) + str(time[3]) + '0000_01D_MN.rnx.gz'
                elif self.choose_local_area_box.currentText() == 'KASI(Korea)':
                    #   ftp://nfs.kasi.re.kr/gnss/data/daily/2021/001/21p/BRDC00IGS_R_20210010000_01D_MN.rnx.gz
                    download_rinex304n_url = 'ftp://nfs.kasi.re.kr/gnss/data/daily/'+str(time[0])+'/'+str(time[3])+'/'+str(time[1])+'p/BRDC00IGS_R_'+str(time[0])+str(time[3])+'0000_01D_MN.rnx.gz'
                list = [download_rinex304n_url, file_name]
                rinex304n_url_list = rinex304n_url_list + [list]
            # print(rinex304n_url_list)

        # Merge list
        combination_url_list = [rinex211o_url_list, rinex304o_url_list, rinex211n_url_list, rinex304n_url_list]
        target_url_list = []
        for i in combination_url_list:
            if i != []:
                target_url_list = target_url_list + i
        if target_url_list == []:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips', 'No file type selected !')
            return
        print(target_url_list)

        # Simulate login（NASA）
        if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
            try:
                header_url = 'https://cddis.nasa.gov/archive/gnss/data/daily'
                login_url = 'https://urs.earthdata.nasa.gov/login'
                target_url = 'gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/2021/001/21d'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52'
                }
                add_login_url_main_ui = session.get(url=header_url, headers=headers)
                soup = BeautifulSoup(add_login_url_main_ui.text, 'lxml')
                token = soup.select_one("input[name='authenticity_token']")['value']
                data = {
                    'utf8': '✓',
                    'authenticity_token': token,
                    'username': 'liangqiao',
                    'password': 'Lq060637',
                    'client_id': 'gDQnv1IO0j9O2xXdwS8KMQ',
                    'redirect_uri': 'https://cddis.nasa.gov/proxyauth',
                    'response_type': 'code',
                    'state': 'aHR0cDovL2NkZGlzLm5hc2EuZ292L2FyY2hpdmUvZ25zcy9kYXRhL2RhaWx5',
                    'stay_in': '1',
                    'commit': 'Log in'
                }
                add_self_informastion_url = session.post(url=login_url, headers=headers, data=data)
                soup = BeautifulSoup(add_self_informastion_url.text, 'lxml')
                url_code = soup.select_one("a[id='redir_link']")['href']
                gain_cookie_information_url = session.get(url=url_code, headers=headers)
                pass
            except:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Tips', 'CDDIS website is under maintenance, please change the download source and download again!')
                return

        # Download progress bar
        # * CDDIS
        if self.choose_local_area_box.currentText() == 'CDDIS(USA)':
            self.download_Progress_bar.setRange(0, len(target_url_list))
            QApplication.processEvents()
            global cddis_ftp_link
            cddis_ftp_link = FTP()
            cddis_ftp_link.encoding = 'gbk'
            try:
                cddis_ftp_link.set_pasv(True)
                cddis_ftp_link.connect("gdc.cddis.eosdis.nasa.gov", 21)
                cddis_ftp_link.login("anonymous", "l_teamer@163.com")
            except:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Tips', 'CDDIS website is under maintenance, please change the download source and download again!')
                return
            for i in target_url_list:
                self.CDDIS_Download_Function(i[0], i[1])
                self_step = self_step + 1
                self.download_Progress_bar.setValue(self_step)
                QApplication.processEvents()

        # * WHU/IGN/ESA/SOPAC...
        else:
            thread_list = locals()
            thread_list_original_length = len(thread_list)
            for i, j in zip(target_url_list, range(len(target_url_list))):
                download_ftp_function = threading.Thread(target=self.WUHAN_function, args=(i[0], i[1]))
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

        # Download task status
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

    # help document
    def open_download_help_file_but_line(self):
        self.s = open_download_help_file_windows01()
        self.s.show()
        pass

    # Download details
    def download_details_report_view(self):
        self.s = download_details_report_main01(successful_library,failed_library)
        self.s.show()
        pass

# -------------------------------------------------------------------------------------------------
""" download_details gui """
class download_details_report_main01(QWidget):
    def __init__(self, success, fail):
        super().__init__()
        self.setWindowTitle("Detail")
        curdir = os.getcwd()
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
""" map gui """
class Station_Map_Display_View(QMainWindow):
    def __init__(self):
        super(Station_Map_Display_View, self).__init__()
        self.setWindowTitle('Map Display')
        curdir = os.getcwd()
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        self.setGeometry(360/1920*win_width, 105/1080*win_height, 1250/1920*win_width, 870/1080*win_height)
        self.browser = QWebEngineView()
        curdir = os.getcwd()
        url = str(curdir) + r'/templates/TempDisplayMapTemplate02.html'
        self.browser.setUrl(QUrl.fromLocalFile(url))
        # self.browser.load(QUrl(QFileInfo("./templates/TempDisplayMapTemplate02.html").absoluteFilePath()))
        self.setCentralWidget(self.browser)

# -------------------------------------------------------------------------------------------------
""" explain gui """
class open_download_help_file_windows01(QMainWindow):
    def __init__(self):
        super().__init__()
        curdir = os.getcwd()
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        self.setGeometry(250/1920*win_width, 60/1080*win_height, 1420/1920*win_width, 900/1080*win_height)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setWindowTitle("Help")
        self.browser = QWebEngineView()
        url = str(curdir) + r'/tutorial/GDDS User Manual.html'
        self.browser.setUrl(QUrl.fromLocalFile(url))
        # self.browser.load(QUrl(QFileInfo("./GDDS User Manual.html").absoluteFilePath()))
        # self.browser.load(QUrl('https://docs.zohopublic.com.cn/file/41qmpeedee87ec45b40848137193890b5b5ad'))
        self.setCentralWidget(self.browser)

# -------------------------------------------------------------------------------------------------
""" Return to map gui """
class Return_Map_Names(QMainWindow):
    def __init__(self, route):
        super().__init__()
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("IGS-Station Map")
        curdir = os.getcwd()
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setup_ui(route)

    my_Signal = pyqtSignal(str)
    def sendEditContent(self):
        content = '1'
        self.my_Signal.emit(content)
    # def closeEvent(self, event):
    #     self.sendEditContent()

    def setup_ui(self, route):
        kwargs = {'host': '127.0.0.1', 'port': '5000', 'threaded': True, 'use_reloader': False, 'debug': False}
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        # self.setGeometry(360/1920*win_width, 105/1080*win_height, 1250/1920*win_width, 870/1080*win_height)
        self.resize(1250/1920*win_width, 870/1080*win_height)
        # gride = QGridLayout()
        # self.setGeometry(400, 80, 1250, 870)
        self.browser = QWebEngineView()
        host = kwargs['host']
        port = kwargs['port']
        url = 'http://' + host + ":" + port + route
        self.browser.load(QUrl(url))

        widget = QWidget()
        gride = QGridLayout()
        widget.setLayout(gride)
        self.setCentralWidget(widget)
        # self.setCentralWidget(gride)

        self.sure_submit_btn = QPushButton(self)
        self.sure_submit_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.sure_submit_btn.setStyleSheet("QPushButton{border-image: url(':/icon/OKsubmit.jpg')}")
        # self.sure_submit_btn.setFlat(True)
        # self.sure_submit_btn.setGeometry(298/1920*win_width, 751/1080*win_height, 105/1920*win_width, 47/1920*win_width)
        # self.sure_submit_btn.setGeometry(1030 / 1920 * win_width, 70 / 1080 * win_height, 105 / 1920 * win_width, 46 / 1920 * win_width)
        # self.sure_submit_btn.move(1030/1920*win_width, 70/1080*win_height)
        gride.addWidget(self.browser, 0, 0, 45, 45)
        gride.addWidget(self.sure_submit_btn, 5, 41, 2, 3)
        self.setLayout(gride)
        self.sure_submit_btn.clicked.connect(self.view_close_function)

    def view_close_function(self):
        self.sendEditContent()
        self.close()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    # kwargs = {'host': '127.0.0.1', 'port': '5000', 'threaded': True, 'use_reloader': False, 'debug': False}
    # threading.Thread(target=app1.run, daemon=True, kwargs=kwargs).start()
    win = IGS_data_Download()
    win.show()
    sys.exit(app.exec_())