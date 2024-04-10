import gnsscal
import paramiko
from datetime import *
from time import sleep
import requests
import requests_ftp
import threading
import os
import platform
from retrying import retry
import subprocess
from PyQt5.QtCore import QUrl, Qt, QLocale, QDate, QDateTime, QFileInfo
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDesktopWidget, QLabel, QComboBox, QLineEdit, QPushButton, QFileDialog, QMessageBox, QTextEdit, QTextEdit, QFrame, QCheckBox, QDateTimeEdit, QListWidget, QAction, QListWidgetItem, QProgressBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont
from station_info_table import *
import resources_rc
import global_var
JD = 3.21
MJD = 1.23

global curdir
curdir = os.getcwd()

'''
-----------------------------------------------------------------------------------------------------------------------
Function: Download regional CORS data
Principle: 1. Preparation stage. Acquisition of time (year, day of year, GPS week, day of the week), acquisition of CORS station name (CORS station name of rinex2.11 - lowercase, CORS station name of rinex3.04 - uppercase)
2. Generate the target URL address. File type selection judgment - > time list cycle - > CORS station name list cycle - > splicing to generate target URL list
   (URL list format: [[url1, file_name1], [URL2, file_name2], ~])
3. Merge to generate a total URL list. Merge all the URL lists generated in step 2 into one total URL list
4. Crawler download phase. Execute in the same session: simulate login (after login, there is a jump of the interface. Only after the program execution completes the jump of the interface can valid cookie information be generated)
   ——>Loop total URL list - > execute URL web address - > write file (multithreading)
-----------------------------------------------------------------------------------------------------------------------
'''

class CORS_data_Download(QWidget):
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
        self.setWindowTitle("Regional CORS Data")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.move(490, 100)
        # self.setFixedSize(1030, 800)
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        # self.setFixedSize(1030/1920*win_width, 800/1080*win_height)

        if win_width <= 720:
            if win_height <= 450:
                self.setFixedSize(1030/1280*win_width, 900/1080*win_height)
            elif win_height <= 480:
                self.setFixedSize(1030/1150*win_width, 900/1080*win_height)
            elif win_height <= 500:
                self.setFixedSize(1030/1450*win_width, 830/1080*win_height)
            elif win_height <= 512:
                self.setFixedSize(1030/1150*win_width, 900/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(1030/1150*win_width, 800/1080*win_height)
            else:
                self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        elif win_width <= 800 and win_width > 720:
            if win_height <= 500:
                self.setFixedSize(1030/1320*win_width, 900/1080*win_height)
            elif win_height <= 515:
                self.setFixedSize(1030/1460*win_width, 890/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(1030/1080*win_width, 880/1080*win_height)
            self.move((screen.width() - 935/1040*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 840 and win_width > 800:
            self.setFixedSize(1030/1300*win_width, 890/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 830/1080*win_height)/2)
        elif win_width <= 960 and win_width > 840:
            if win_height <= 550:
                self.setFixedSize(1030/1420*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 600:
                self.setFixedSize(1030/1460*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 720:
                self.setFixedSize(1030/1140*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            else:
                self.setFixedSize(1030/1740*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1024 and win_width > 960:
            self.setFixedSize(1030/1150*win_width, 870/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1152 and win_width > 1024:
            self.setFixedSize(1030/1300*win_width, 850/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1176 and win_width > 1152:
            self.setFixedSize(1030/1350*win_width, 870/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1280 and win_width > 1176:
            self.setFixedSize(1030/1435*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1320*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1366 and win_width > 1280:
            self.setFixedSize(1030/1550*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1440 and win_width > 1366:
            self.setFixedSize(1030/1620*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1600 and win_width > 1440:
            self.setFixedSize(1030/1800*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1420*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1680 and win_width > 1600:
            self.setFixedSize(1030/1800*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1792 and win_width > 1680:
            self.setFixedSize(1030/1820*win_width, 810/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 2048 and win_width > 1920:
            self.setFixedSize(1030/1920*win_width, 810/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)
        elif win_width <= 2560 and win_width > 1920:
            self.setFixedSize(1030/1920*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        else:
            self.setFixedSize(1030/1920*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 800/1080*win_height)/2)

        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))



        # self.move((screen.width() - 1030 / 1920 * win_width) / 2, (screen.height() - 840 / 1080 * win_height) / 2)

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


        self.choose_local_area_label = QLabel('CORS Source :', self)
        self.choose_local_area_label.setFont(QFont("Times New Roman"))
        self.choose_local_area_label.setGeometry(35 / 1920 * win_width, 30 / 1080 * win_height, 400 / 1920 * win_width,
                                                 30 / 1080 * win_height)

        self.choose_local_area_box = QComboBox(self)
        self.choose_local_area_box.setGeometry(190 / 1920 * win_width, 29 / 1080 * win_height, 265 / 1920 * win_width,
                                               35 / 1080 * win_height)

        self.choose_local_area_box.addItems(
            ['USA CORS', 'Europe EPN', 'Spain CORS', 'Japan JPN', 'Hong Kong CORS', 'Curtin University',
             'Australia APREF CORS'])
        self.choose_local_area_box.currentTextChanged.connect(self.local_area_changed)

        self.choose_download_files_type_label = QLabel('File Type :', self)
        self.choose_download_files_type_label.setFont(QFont("Times New Roman"))
        self.choose_download_files_type_label.setGeometry(35 / 1920 * win_width, 125 / 1080 * win_height,
                                                          400 / 1920 * win_width, 30 / 1080 * win_height)

        # -------------------------------------------------------------------------------------------------
        # HongKong starting
        # observation
        self.HK_label_OBS01_windows = QLabel(self)
        self.HK_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 85 / 1080 * win_height, 460 / 1920 * win_width,
                                                110 / 1080 * win_height)
        self.HK_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.HK_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.HK_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        #
        self.HK_label_OBS01_name = QLabel(self)
        self.HK_label_OBS01_name.move(260 / 1920 * win_width, 85 / 1080 * win_height)
        self.HK_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.HK_label_OBS01_name.setText('  Observation  ')
        self.HK_label_OBS01_name.setFont(QFont('Times New Roman'))

        # Observation duration
        self.HK_data_length_label = QLabel('Data Length:', self)
        self.HK_data_length_label.move(202 / 1920 * win_width, 117 / 1080 * win_height)

        self.HK_data_length_box = QComboBox(self)
        self.HK_data_length_box.setGeometry(202 / 1920 * win_width, 147 / 1080 * win_height, 100 / 1920 * win_width,
                                            32 / 1080 * win_height)
        self.HK_data_length_box.addItems(['1 hour', '1 day'])
        self.HK_data_length_box.currentTextChanged.connect(self.HK_data_length_change)

        #  .*d
        self.HK_rinex211_check = QCheckBox(self)
        self.HK_rinex211_check.move(350 / 1920 * win_width, 115 / 1080 * win_height)

        self.HK_rinex211_box = QComboBox(self)
        self.HK_rinex211_box.setGeometry(373 / 1920 * win_width, 112 / 1080 * win_height, 75 / 1920 * win_width,
                                         32 / 1080 * win_height)
        self.HK_rinex211_box.addItems(['1s', '5s'])

        self.HK_rinex211_label = QLabel('RINEX 2.11(.*d)', self)
        self.HK_rinex211_label.move(453 / 1920 * win_width, 115 / 1080 * win_height)

        #  _MO.crx
        self.HK_rinex304_check = QCheckBox(self)
        self.HK_rinex304_check.move(350 / 1920 * win_width, 155 / 1080 * win_height)

        self.HK_rinex304_box = QComboBox(self)
        self.HK_rinex304_box.setGeometry(373 / 1920 * win_width, 152 / 1080 * win_height, 75 / 1920 * win_width,
                                         32 / 1080 * win_height)
        self.HK_rinex304_box.addItems(['1s', '5s'])

        self.HK_rinex304_label = QLabel('RINEX 3.xx(_MO.crx)', self)
        self.HK_rinex304_label.move(453 / 1920 * win_width, 155 / 1080 * win_height)

        # Met
        self.HK_label_OBS02_windows = QLabel(self)
        self.HK_label_OBS02_windows.setGeometry(665 / 1920 * win_width, 85 / 1080 * win_height, 360 / 1920 * win_width,
                                                110 / 1080 * win_height)
        self.HK_label_OBS02_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.HK_label_OBS02_windows.setFrameShape(QFrame.Box)
        self.HK_label_OBS02_windows.setFrameShadow(QFrame.Raised)

        self.HK_label_OBS02_name = QComboBox(self)
        self.HK_label_OBS02_name.setGeometry(720 / 1920 * win_width, 73 / 1080 * win_height, 140 / 1920 * win_width,
                                             34 / 1080 * win_height)
        self.HK_label_OBS02_name.addItems(['Navigation', 'Meteorology'])
        self.HK_label_OBS02_name.currentTextChanged.connect(self.HK_met_nav_file_type_changed_link)

        self.HK_met_rnx211_check = QCheckBox('RINEX 2.11(.*m)', self)
        self.HK_met_rnx211_check.move(690 / 1920 * win_width, 115 / 1080 * win_height)
        self.HK_met_rnx211_check.stateChanged.connect(self.HK_met_file_checked_funcction)

        self.HK_met_rnx304_check = QCheckBox('RINEX 3.xx(_MM.rnx)', self)
        self.HK_met_rnx304_check.move(690 / 1920 * win_width, 153 / 1080 * win_height)
        self.HK_met_rnx304_check.stateChanged.connect(self.HK_met_file_checked_funcction)

        self.HK_rinex211_n_check = QCheckBox(self)
        self.HK_rinex211_n_check.move(690 / 1920 * win_width, 115 / 1080 * win_height)

        self.HK_rinex211_n_box = QComboBox(self)
        self.HK_rinex211_n_box.setGeometry(711 / 1920 * win_width, 112 / 1080 * win_height, 110 / 1920 * win_width,
                                           32 / 1080 * win_height)
        self.HK_rinex211_n_box.addItems(['GPS', 'GLONASS'])
        self.HK_rinex211_n_box.currentTextChanged.connect(self.curtin_brdc211_change)

        self.HK_rinex211_n_label = QLabel('RINEX 2.xx(.*n)', self)
        self.HK_rinex211_n_label.move(828 / 1920 * win_width, 115 / 1080 * win_height)

        self.HK_rinex304_n_check = QCheckBox('', self)
        self.HK_rinex304_n_check.move(690 / 1920 * win_width, 153 / 1080 * win_height)

        self.HK_rinex304_n_box = QComboBox(self)
        self.HK_rinex304_n_box.setGeometry(711 / 1920 * win_width, 150 / 1080 * win_height, 110 / 1920 * win_width,
                                           32 / 1080 * win_height)
        self.HK_rinex304_n_box.addItems(['GPS', 'BDS', 'GLONASS', 'GALILEO'])
        self.HK_rinex304_n_box.currentTextChanged.connect(self.curtin_brdc304_change)

        self.HK_rinex304_n_label = QLabel('RINEX 3.xx(_MN.rnx)', self)
        self.HK_rinex304_n_label.move(828 / 1920 * win_width, 153 / 1080 * win_height)

        self.HK_rinex211_n_check.setVisible(False)
        self.HK_rinex211_n_box.setVisible(False)
        self.HK_rinex211_n_label.setVisible(False)
        self.HK_rinex304_n_check.setVisible(False)
        self.HK_rinex304_n_box.setVisible(False)
        self.HK_rinex304_n_label.setVisible(False)

        self.HK_rinex211_check.setChecked(False)
        self.HK_rinex304_check.setChecked(False)
        self.HK_label_OBS01_windows.setVisible(False)
        self.HK_label_OBS01_name.setVisible(False)
        self.HK_rinex211_check.setVisible(False)
        self.HK_rinex211_box.setVisible(False)
        self.HK_rinex211_label.setVisible(False)
        self.HK_rinex304_check.setVisible(False)
        self.HK_rinex304_box.setVisible(False)
        self.HK_rinex304_label.setVisible(False)
        self.HK_data_length_label.setVisible(False)
        self.HK_data_length_box.setVisible(False)
        self.HK_label_OBS02_windows.setVisible(False)
        self.HK_label_OBS02_name.setVisible(False)
        self.HK_met_rnx211_check.setVisible(False)
        self.HK_met_rnx304_check.setVisible(False)

        # HongKong ending
        # -------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------
        # Curtin University starting
        # observation
        self.Curtin_label_OBS01_windows = QLabel(self)
        self.Curtin_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 95 / 1080 * win_height,
                                                    285 / 1920 * win_width, 100 / 1080 * win_height)
        self.Curtin_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.Curtin_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.Curtin_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        self.Curtin_label_OBS01_name = QLabel(self)
        self.Curtin_label_OBS01_name.move(240 / 1920 * win_width, 95 / 1080 * win_height)
        self.Curtin_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        # self.label_OBS_name.setFrameShape(QFrame.Box)
        # self.label_OBS_name.setFrameShadow(QFrame.Raised)
        self.Curtin_label_OBS01_name.setText('  Observation  ')
        self.Curtin_label_OBS01_name.setFont(QFont('Times New Roman'))
        #  *d
        self.Curtin_rinex211_check = QCheckBox('RINEX 2.11(.*d)', self)
        self.Curtin_rinex211_check.move(220 / 1920 * win_width, 120 / 1080 * win_height)
        #  _MO.crx
        self.Curtin_rinex304_check = QCheckBox('RINEX 3.xx(_MO.crx)', self)
        self.Curtin_rinex304_check.move(220 / 1920 * win_width, 155 / 1080 * win_height)

        # Broadcast ephemeris
        self.Curtin_label_OBS02_windows = QLabel(self)
        self.Curtin_label_OBS02_windows.setGeometry(550 / 1920 * win_width, 95 / 1080 * win_height,
                                                    395 / 1920 * win_width, 100 / 1080 * win_height)
        self.Curtin_label_OBS02_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.Curtin_label_OBS02_windows.setFrameShape(QFrame.Box)
        self.Curtin_label_OBS02_windows.setFrameShadow(QFrame.Raised)
        #  Curtin
        self.Curtin_label_OBS02_name = QLabel(self)
        self.Curtin_label_OBS02_name.move(600 / 1920 * win_width, 95 / 1080 * win_height)
        self.Curtin_label_OBS02_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        # self.label_OBS02_name.setFrameShape(QFrame.Box)
        # self.label_OBS02_name.setFrameShadow(QFrame.Raised)
        self.Curtin_label_OBS02_name.setText('  Navigation  ')
        self.Curtin_label_OBS02_name.setFont(QFont('Times New Roman'))
        #  APREF
        self.APREF_label_OBS02_name = QComboBox(self)
        self.APREF_label_OBS02_name.setGeometry(600 / 1920 * win_width, 81 / 1080 * win_height, 140 / 1920 * win_width,
                                                32 / 1080 * win_height)
        self.APREF_label_OBS02_name.addItems(['Navigation', 'Meteorology'])
        self.APREF_label_OBS02_name.currentTextChanged.connect(self.APREF_met_nav_file_type_changed_link)

        self.APREF_met_check = QCheckBox('RINEX 3.xx(_MM.rnx)', self)
        self.APREF_met_check.move(630 / 1920 * win_width, 140 / 1080 * win_height)
        self.APREF_met_check.stateChanged.connect(self.APREF_met_file_checked_funcction)

        self.Curtin_rinex211_n_check = QCheckBox(self)
        self.Curtin_rinex211_n_check.move(580 / 1920 * win_width, 120 / 1080 * win_height)

        self.Curtin_rinex211_n_box = QComboBox(self)
        self.Curtin_rinex211_n_box.setGeometry(601 / 1920 * win_width, 117 / 1080 * win_height, 110 / 1920 * win_width,
                                               32 / 1080 * win_height)
        self.Curtin_rinex211_n_box.addItems(['GPS', 'GLONASS'])
        self.Curtin_rinex211_n_box.currentTextChanged.connect(self.curtin_brdc211_change)

        self.Curtin_rinex211_n_label = QLabel('RINEX 2.xx(.*n)', self)
        self.Curtin_rinex211_n_label.move(718 / 1920 * win_width, 120 / 1080 * win_height)

        self.Curtin_rinex304_n_check = QCheckBox('', self)
        self.Curtin_rinex304_n_check.move(580 / 1920 * win_width, 155 / 1080 * win_height)
        self.Curtin_rinex304_n_check.stateChanged.connect(self.APREF_met_file_checked_funcction)

        self.Curtin_rinex304_n_box = QComboBox(self)
        self.Curtin_rinex304_n_box.setGeometry(601 / 1920 * win_width, 152 / 1080 * win_height, 110 / 1920 * win_width,
                                               32 / 1080 * win_height)
        self.Curtin_rinex304_n_box.addItems(['GPS', 'BDS', 'GLONASS', 'GALILEO', 'QZSS', 'IRNSS'])
        self.Curtin_rinex304_n_box.currentTextChanged.connect(self.curtin_brdc304_change)

        self.Curtin_rinex304_n_label = QLabel('RINEX 3.xx(_MN.rnx)', self)
        self.Curtin_rinex304_n_label.move(718 / 1920 * win_width, 155 / 1080 * win_height)

        self.Curtin_label_OBS01_windows.setVisible(False)
        self.Curtin_label_OBS01_name.setVisible(False)
        self.Curtin_rinex211_check.setVisible(False)
        self.Curtin_rinex304_check.setVisible(False)
        self.Curtin_label_OBS02_windows.setVisible(False)
        self.Curtin_label_OBS02_name.setVisible(False)
        self.Curtin_rinex211_n_check.setVisible(False)
        self.Curtin_rinex211_n_box.setVisible(False)
        self.Curtin_rinex211_n_label.setVisible(False)
        self.Curtin_rinex304_n_check.setVisible(False)
        self.Curtin_rinex304_n_box.setVisible(False)
        self.Curtin_rinex304_n_label.setVisible(False)
        self.APREF_label_OBS02_name.setVisible(False)
        self.APREF_met_check.setVisible(False)

        # Curtin University ending
        # -------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------
        # USA CORS starting
        # observation
        self.ngs_label_OBS01_windows = QLabel(self)
        self.ngs_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 95 / 1080 * win_height, 440 / 1920 * win_width,
                                                 85 / 1080 * win_height)
        self.ngs_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.ngs_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.ngs_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        self.ngs_label_OBS01_name = QLabel(self)
        self.ngs_label_OBS01_name.move(250 / 1920 * win_width, 95 / 1080 * win_height)
        self.ngs_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.ngs_label_OBS01_name.setText('  Observation  ')
        self.ngs_label_OBS01_name.setFont(QFont('Times New Roman'))
        #  *o
        self.ngs_rinex211_check = QCheckBox('RINEX 2.11(.*o)', self)
        self.ngs_rinex211_check.move(220 / 1920 * win_width, 130 / 1080 * win_height)
        #  *d
        self.ngs_rinex304_check = QCheckBox('RINEX 2.11(.*d)', self)
        self.ngs_rinex304_check.move(420 / 1920 * win_width, 130 / 1080 * win_height)

        # Broadcast ephemeris
        self.ngs_label_OBS02_windows = QLabel(self)
        self.ngs_label_OBS02_windows.setGeometry(635 / 1920 * win_width, 95 / 1080 * win_height, 355 / 1920 * win_width,
                                                 85 / 1080 * win_height)
        self.ngs_label_OBS02_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.ngs_label_OBS02_windows.setFrameShape(QFrame.Box)
        self.ngs_label_OBS02_windows.setFrameShadow(QFrame.Raised)
        self.ngs_label_OBS02_name = QLabel(self)
        self.ngs_label_OBS02_name.move(690 / 1920 * win_width, 95 / 1080 * win_height)
        self.ngs_label_OBS02_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.ngs_label_OBS02_name.setText('  Navigation  ')
        self.ngs_label_OBS02_name.setFont(QFont('Times New Roman'))

        self.ngs_rinex211_n_check = QCheckBox(self)
        self.ngs_rinex211_n_check.move(665 / 1920 * win_width, 130 / 1080 * win_height)

        self.ngs_rinex211_n_box = QComboBox(self)
        self.ngs_rinex211_n_box.setGeometry(688 / 1920 * win_width, 127 / 1080 * win_height, 110 / 1920 * win_width,
                                            32 / 1080 * win_height)
        self.ngs_rinex211_n_box.addItems(['GPS', 'GLONASS'])
        self.ngs_rinex211_n_box.currentTextChanged.connect(self.ngs_brdc211_change)

        self.ngs_rinex211_n_label = QLabel('RINEX 2.xx(.*n)', self)
        self.ngs_rinex211_n_label.move(805 / 1920 * win_width, 130 / 1080 * win_height)

        # USA CORS ending
        # -------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------
        # Enrope EPN starting
        # observation
        self.epn_label_OBS01_windows = QLabel(self)
        self.epn_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 105 / 1080 * win_height,
                                                 310 / 1920 * win_width, 70 / 1080 * win_height)
        self.epn_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.epn_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.epn_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        self.epn_label_OBS01_name = QLabel(self)
        self.epn_label_OBS01_name.move(240 / 1920 * win_width, 105 / 1080 * win_height)
        self.epn_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.epn_label_OBS01_name.setText('  Observation  ')
        self.epn_label_OBS01_name.setFont(QFont('Times New Roman'))
        #  _MO.crx
        self.epn_rinex304_check = QCheckBox('RINEX 3.xx(_MO.crx)', self)
        self.epn_rinex304_check.move(240 / 1920 * win_width, 130 / 1080 * win_height)

        # Broadcast ephemeris
        self.epn_label_OBS02_windows = QLabel(self)
        self.epn_label_OBS02_windows.setGeometry(545 / 1920 * win_width, 105 / 1080 * win_height,
                                                 295 / 1920 * win_width, 70 / 1080 * win_height)
        self.epn_label_OBS02_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.epn_label_OBS02_windows.setFrameShape(QFrame.Box)
        self.epn_label_OBS02_windows.setFrameShadow(QFrame.Raised)
        self.epn_label_OBS02_name = QLabel(self)
        self.epn_label_OBS02_name.move(590 / 1920 * win_width, 105 / 1080 * win_height)
        self.epn_label_OBS02_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        # self.label_OBS02_name.setFrameShape(QFrame.Box)
        # self.label_OBS02_name.setFrameShadow(QFrame.Raised)
        self.epn_label_OBS02_name.setText('  Navigation  ')
        self.epn_label_OBS02_name.setFont(QFont('Times New Roman'))

        #  _MN.rnx Broadcast ephemeris
        self.epn_rinex304_mn_check = QCheckBox('RINEX 3.xx(_MN.rnx)', self)
        self.epn_rinex304_mn_check.move(590 / 1920 * win_width, 130 / 1080 * win_height)

        self.epn_label_OBS01_windows.setVisible(False)
        self.epn_label_OBS01_name.setVisible(False)
        self.epn_label_OBS02_windows.setVisible(False)
        self.epn_label_OBS02_name.setVisible(False)
        self.epn_rinex304_check.setVisible(False)
        self.epn_rinex304_mn_check.setVisible(False)

        # Enrope EPN ending
        # -------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------
        # Spain CORS  starting
        # observation
        self.spain_label_OBS01_windows = QLabel(self)
        self.spain_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 105 / 1080 * win_height,
                                                   560 / 1920 * win_width, 80 / 1080 * win_height)
        self.spain_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.spain_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.spain_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        self.spain_label_OBS01_name = QLabel(self)
        self.spain_label_OBS01_name.move(235 / 1920 * win_width, 105 / 1080 * win_height)
        self.spain_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.spain_label_OBS01_name.setText('  Observation  ')
        self.spain_label_OBS01_name.setFont(QFont('Times New Roman'))
        #  .*d
        self.spain_rinex211_check = QCheckBox('RINEX 2.11(.*d)', self)
        self.spain_rinex211_check.move(240 / 1920 * win_width, 135 / 1080 * win_height)
        #  _MO.crx
        self.spain_rinex304_check = QCheckBox('RINEX 3.xx(_MO.crx)', self)
        self.spain_rinex304_check.move(475 / 1920 * win_width, 135 / 1080 * win_height)

        self.spain_label_OBS01_windows.setVisible(False)
        self.spain_label_OBS01_name.setVisible(False)
        self.spain_rinex211_check.setVisible(False)
        self.spain_rinex304_check.setVisible(False)

        # -------------------------------------------------------------------------------------------------
        # Japan JPN  ending
        # -------------------------------------------------------------------------------------------------
        # Japan JPN  starting
        # observation
        self.Japan_label_OBS01_windows = QLabel(self)
        self.Japan_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 85 / 1080 * win_height,
                                                   190 / 1920 * win_width, 60 / 1080 * win_height)
        self.Japan_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.Japan_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.Japan_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        self.Japan_label_OBS01_name = QLabel(self)
        self.Japan_label_OBS01_name.move(225 / 1920 * win_width, 85 / 1080 * win_height)
        self.Japan_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.Japan_label_OBS01_name.setText('  Observation  ')
        self.Japan_label_OBS01_name.setFont(QFont('Times New Roman'))
        # observation
        self.Japan_rinex211_check = QCheckBox('RINEX 2.11(.*o)', self)
        self.Japan_rinex211_check.move(210 / 1920 * win_width, 110 / 1080 * win_height)

        # Broadcast ephemeris
        self.Japan_label_OBS02_windows = QLabel(self)
        self.Japan_label_OBS02_windows.setGeometry(190 / 1920 * win_width, 155 / 1080 * win_height,
                                                   190 / 1920 * win_width, 60 / 1080 * win_height)
        self.Japan_label_OBS02_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.Japan_label_OBS02_windows.setFrameShape(QFrame.Box)
        self.Japan_label_OBS02_windows.setFrameShadow(QFrame.Raised)
        self.Japan_label_OBS02_name = QLabel(self)
        self.Japan_label_OBS02_name.move(225 / 1920 * win_width, 145 / 1080 * win_height)
        self.Japan_label_OBS02_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.Japan_label_OBS02_name.setText('  Navigation  ')
        self.Japan_label_OBS02_name.setFont(QFont('Times New Roman'))
        #  rinex 3.xx Broadcast ephemeris
        self.Japan_rinex211_glonassn_check = QCheckBox('RINEX 3.xx(.*p)', self)
        self.Japan_rinex211_glonassn_check.move(210 / 1920 * win_width, 180 / 1080 * win_height)

        # post-processing products
        self.Japan_label_OBS03_windows = QLabel(self)
        self.Japan_label_OBS03_windows.setGeometry(400 / 1920 * win_width, 85 / 1080 * win_height,
                                                   605 / 1920 * win_width, 130 / 1080 * win_height)
        self.Japan_label_OBS03_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.Japan_label_OBS03_windows.setFrameShape(QFrame.Box)
        self.Japan_label_OBS03_windows.setFrameShadow(QFrame.Raised)
        self.Japan_label_OBS03_name = QLabel(self)
        self.Japan_label_OBS03_name.move(450 / 1920 * win_width, 75 / 1080 * win_height)
        self.Japan_label_OBS03_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        # self.label_OBS02_name.setFrameShape(QFrame.Box)
        # self.label_OBS02_name.setFrameShadow(QFrame.Raised)
        self.Japan_label_OBS03_name.setText('  Products  ')
        self.Japan_label_OBS03_name.setFont(QFont('Times New Roman'))

        #  igu
        self.Japan_igu_check = QCheckBox('Ultra Precise Ephemeris(.sp3)', self)
        self.Japan_igu_check.move(425 / 1920 * win_width, 110 / 1080 * win_height)
        #  igr
        self.Japan_igr_check = QCheckBox('Rapid Precise Ephemeris(.sp3)', self)
        self.Japan_igr_check.move(425 / 1920 * win_width, 145 / 1080 * win_height)
        #  igs
        self.Japan_igs_check = QCheckBox('Final Precise Ephemeris(.sp3)', self)
        self.Japan_igs_check.move(425 / 1920 * win_width, 180 / 1080 * win_height)
        #  snx
        self.Japan_snx_check = QCheckBox('Weekly Solution(.snx)', self)
        self.Japan_snx_check.move(720 / 1920 * win_width, 110 / 1080 * win_height)
        #  .clk_30s
        self.Japan_clk_check = QCheckBox('30s Precise Clock(.clk)', self)
        self.Japan_clk_check.move(720 / 1920 * win_width, 145 / 1080 * win_height)
        #  fcb
        self.Japan_fcb_check = QCheckBox('Fractional Cycle Bias(.fcb)', self)
        self.Japan_fcb_check.move(720 / 1920 * win_width, 180 / 1080 * win_height)

        self.Japan_label_OBS01_windows.setVisible(False)
        self.Japan_label_OBS01_name.setVisible(False)
        self.Japan_label_OBS02_windows.setVisible(False)
        self.Japan_label_OBS02_name.setVisible(False)
        self.Japan_label_OBS03_windows.setVisible(False)
        self.Japan_label_OBS03_name.setVisible(False)
        self.Japan_rinex211_check.setVisible(False)
        self.Japan_rinex211_glonassn_check.setVisible(False)
        self.Japan_igu_check.setVisible(False)
        self.Japan_igr_check.setVisible(False)
        self.Japan_igs_check.setVisible(False)
        self.Japan_snx_check.setVisible(False)
        self.Japan_clk_check.setVisible(False)
        self.Japan_fcb_check.setVisible(False)

        # -------------------------------------------------------------------------------------------------
        # Japan JPN  ending
        self.choose_start_end_time_label = QLabel('Time Range :', self)
        self.choose_start_end_time_label.setFont(QFont("Times New Roman"))
        self.choose_start_end_time_label.setGeometry(35 / 1920 * win_width, 245 / 1080 * win_height,
                                                     400 / 1920 * win_width, 30 / 1080 * win_height)

        # year, month, day
        self.YearMonDay_label0101 = QLabel('Year-Month-Day :', self)
        self.YearMonDay_label0101.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0101.move(200 / 1920 * win_width, 225 / 1080 * win_height)
        # start time
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.start_time.setLocale(QLocale(QLocale.English))
        self.start_time.setGeometry(440 / 1920 * win_width, 218 / 1080 * win_height, 170 / 1920 * win_width,
                                    30 / 1080 * win_height)
        self.start_time.setDisplayFormat('yyyy-MM-dd')
        self.start_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.start_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.start_time.setCalendarPopup(True)  #
        self.start_time.dateChanged.connect(self.onDateChanged01)
        #  year, doy
        self.YearMonDay_label0102 = QLabel('Year, Day of Year :', self)
        self.YearMonDay_label0102.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0102.move(200 / 1920 * win_width, 259 / 1080 * win_height)
        #  year
        self.changday0201 = QLineEdit(self)
        self.changday0201.setGeometry(440 / 1920 * win_width, 253 / 1080 * win_height, 95 / 1920 * win_width,
                                      30 / 1080 * win_height)
        # doy
        self.changday0202 = QLineEdit(self)
        self.changday0202.setGeometry(545 / 1920 * win_width, 253 / 1080 * win_height, 65 / 1920 * win_width,
                                      30 / 1080 * win_height)
        self.changday0201.textEdited.connect(self.YearAcumulateDay_to_all01)
        self.changday0202.textEdited.connect(self.YearAcumulateDay_to_all01)

        #  GPS Week
        self.YearMonDay_label0103 = QLabel('GPS Week, Day of Week :', self)
        self.YearMonDay_label0103.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0103.move(200 / 1920 * win_width, 294 / 1080 * win_height)
        #  GPS Week
        self.changday0301 = QLineEdit(self)
        self.changday0301.setGeometry(440 / 1920 * win_width, 288 / 1080 * win_height, 95 / 1920 * win_width,
                                      30 / 1080 * win_height)
        # GPS Week day
        self.changday0302 = QLineEdit(self)
        self.changday0302.setGeometry(545 / 1920 * win_width, 288 / 1080 * win_height, 65 / 1920 * win_width,
                                      30 / 1080 * win_height)
        self.changday0301.textEdited.connect(self.GPSweeks_to_all01)
        self.changday0302.textEdited.connect(self.GPSweeks_to_all01)

        # -------------------------------------------------------------------------------------------------
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

        # -------------------------------------------------------------------------------------------------
        self.time_start_to_end = QLabel('>>>', self)
        self.time_start_to_end.move(626 / 1920 * win_width, 262 / 1080 * win_height)
        # -------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------
        # End time
        self.end_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.end_time.setLocale(QLocale(QLocale.English))
        self.end_time.setGeometry(680 / 1920 * win_width, 218 / 1080 * win_height, 170 / 1920 * win_width,
                                  30 / 1080 * win_height)
        self.end_time.setDisplayFormat('yyyy-MM-dd')
        self.end_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.end_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.end_time.setCalendarPopup(True)
        self.end_time.dateChanged.connect(self.onDateChanged02)

        # year
        self.changday0401 = QLineEdit(self)
        self.changday0401.setGeometry(680 / 1920 * win_width, 253 / 1080 * win_height, 95 / 1920 * win_width,
                                      30 / 1080 * win_height)
        # doy
        self.changday0402 = QLineEdit(self)
        self.changday0402.setGeometry(785 / 1920 * win_width, 253 / 1080 * win_height, 65 / 1920 * win_width,
                                      30 / 1080 * win_height)
        self.changday0401.textEdited.connect(self.YearAcumulateDay_to_all02)
        self.changday0402.textEdited.connect(self.YearAcumulateDay_to_all02)

        #  GPS Week
        self.changday0501 = QLineEdit(self)
        self.changday0501.setGeometry(680 / 1920 * win_width, 288 / 1080 * win_height, 95 / 1920 * win_width,
                                      30 / 1080 * win_height)
        self.changday0502 = QLineEdit(self)
        self.changday0502.setGeometry(785 / 1920 * win_width, 288 / 1080 * win_height, 65 / 1920 * win_width,
                                      30 / 1080 * win_height)
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

        # -------------------------------------------------------------------------------------------------
        # Station selection box
        self.choose_IGS_station111w_label = QLabel('CORS Station :', self)
        self.choose_IGS_station111w_label.setFont(QFont("Times New Roman"))
        self.choose_IGS_station111w_label.setGeometry(35 / 1920 * win_width, 450 / 1080 * win_height,
                                                      400 / 1920 * win_width, 30 / 1080 * win_height)

        self.choose_add_station_list_box = QComboBox(self)
        self.choose_add_station_list_box.setGeometry(210 / 1920 * win_width, 352 / 1080 * win_height,
                                                     210 / 1920 * win_width, 31 / 1080 * win_height)
        self.choose_add_station_list_box.addItems(['All Station', 'Met Station', 'Nav Station'])
        self.choose_add_station_list_box.currentTextChanged.connect(self.choose_add_station_list_change)

        self.choose_all_station_label = QListWidget(self)
        self.choose_all_station_label.setGeometry(210 / 1920 * win_width, 382 / 1080 * win_height,
                                                  127 / 1920 * win_width, 40 / 1080 * win_height)

        self.choose_all_station_CheckBtn = QCheckBox('All', self)
        self.choose_all_station_CheckBtn.move(216 / 1920 * win_width, 387 / 1080 * win_height)
        self.choose_all_station_CheckBtn.stateChanged.connect(self.choose_all_station_function)

        self.search_igs_label = QLineEdit(self)
        self.search_igs_label.setPlaceholderText('Search')
        self.search_igs_label.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.search_igs_label.setGeometry(280 / 1920 * win_width, 382 / 1080 * win_height, 140 / 1919 * win_width,
                                          40 / 1080 * win_height)
        self.search_igs_label.textChanged.connect(self.Search_text_changed)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(':/icon/magnifier.ico'))
        self.search_igs_label.addAction(station_search_icon, QLineEdit.LeadingPosition)

        self.choose_Option_display = QListWidget(self)
        self.choose_Option_display.setGeometry(210 / 1920 * win_width, 415 / 1080 * win_height, 210 / 1920 * win_width,
                                               180 / 1080 * win_height)

        # Initialize the contents of the information box (USA CORS stations)
        json_text = json.load(open(str(curdir) + r'/lib/json/CORS_Statios.json', 'r'))
        Files = json_text[0]
        global_var.set_value('CORS_current_view_station_list', Files)
        for item1 in Files:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.choose_Option_display.addItem(item)

        self.btnAddItems_map = QPushButton('Map Choose', self)
        self.btnAddItems_map.clicked.connect(self.add_map_Items)
        self.btnAddItems_map.setGeometry(442 / 1920 * win_width, 352 / 1080 * win_height, 210 / 1920 * win_width,
                                         35 / 1080 * win_height)

        self.open_station_info_table_btn = QPushButton('Info Inquire', self)
        self.open_station_info_table_btn.clicked.connect(self.open_station_info_table_link)
        self.open_station_info_table_btn.setGeometry(442 / 1920 * win_width, 403 / 1080 * win_height,
                                                     210 / 1920 * win_width, 35 / 1080 * win_height)

        self.btnPrintItems = QPushButton('Add Station', self)
        self.btnPrintItems.setGeometry(442 / 1920 * win_width, 453 / 1080 * win_height, 210 / 1920 * win_width,
                                       35 / 1080 * win_height)
        self.btnPrintItems.clicked.connect(self.add_igs_Items_function)

        self.stationDisplay = QPushButton('Map Display', self)
        self.stationDisplay.setGeometry(442 / 1920 * win_width, 504 / 1080 * win_height, 210 / 1920 * win_width,
                                        35 / 1080 * win_height)
        self.stationDisplay.clicked.connect(self.station_map_display_function)

        self.btnClearStation = QPushButton('Clear Station', self)
        self.btnClearStation.setGeometry(442 / 1920 * win_width, 555 / 1080 * win_height, 210 / 1920 * win_width,
                                         35 / 1080 * win_height)
        self.btnClearStation.clicked.connect(self.clear_added_station_function)

        self.igs_names_display_label = QLabel('Added 0 Station', self)
        self.igs_names_display_label.setGeometry(679 / 1920 * win_width, 352 / 1080 * win_height,
                                                 212 / 1920 * win_width, 35 / 1080 * win_height)
        self.igs_names_display_label.setFrameShape(QFrame.Box)
        self.igs_names_display_label.setFrameShadow(QFrame.Raised)

        self.igs_names_display = QTextEdit(self)
        self.igs_names_display.setPlaceholderText('1lsu\nab14\nALhc\nNDFA')
        self.igs_names_display.setGeometry(680 / 1920 * win_width, 380 / 1080 * win_height, 210 / 1920 * win_width,
                                           210 / 1080 * win_height)
        self.igs_names_display.textChanged.connect(self.added_station_view_link)

        # Station selection box
        # -------------------------------------------------------------------------------------------------

        self.choose_save_path_wuyong_label = QLabel('Output Path :', self)
        self.choose_save_path_wuyong_label.setFont(QFont("Times New Roman"))
        self.choose_save_path_wuyong_label.setGeometry(35 / 1920 * win_width, 620 / 1080 * win_height,
                                                       400 / 1920 * win_width, 30 / 1080 * win_height)

        self.show_outsave_files_path_button = QLineEdit(self)
        self.show_outsave_files_path_button.setGeometry(190 / 1920 * win_width, 620 / 1080 * win_height,
                                                        730 / 1920 * win_width, 35 / 1080 * win_height)
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        classial_desktop_path = desktop_path + '/' + 'Download'
        self.show_outsave_files_path_button.setText(classial_desktop_path)

        self.choose_outsave_files_path_button = QPushButton('<<<', self)
        # self.choose_outsave_files_path_button.setFont(QFont("Times New Roman"))
        self.choose_outsave_files_path_button.setGeometry(935 / 1920 * win_width, 621 / 1080 * win_height,
                                                          45 / 1920 * win_width, 30 / 1080 * win_height)
        self.choose_outsave_files_path_button.clicked.connect(self.save_download_files_path_function)

        # Start downloading
        self.igs_name_sure_but = QPushButton('Download', self)
        self.igs_name_sure_but.setFont(QFont("Times New Roman"))
        self.igs_name_sure_but.setGeometry(90 / 1920 * win_width, 670 / 1080 * win_height, 120 / 1920 * win_width,
                                           40 / 1080 * win_height)
        self.igs_name_sure_but.clicked.connect(self.data_download_function02)

        # View download Report
        self.download_details_report_but = QPushButton('Detail', self)
        self.download_details_report_but.setFont(QFont("Times New Roman"))
        self.download_details_report_but.setGeometry(337 / 1920 * win_width, 670 / 1080 * win_height,
                                                     120 / 1920 * win_width, 40 / 1080 * win_height)
        self.download_details_report_but.clicked.connect(self.download_details_report_view)

        # Open download directory
        self.open_have_download_file_path_but = QPushButton('Open', self)
        self.open_have_download_file_path_but.setFont(QFont("Times New Roman"))
        self.open_have_download_file_path_but.setGeometry(579 / 1920 * win_width, 670 / 1080 * win_height,
                                                          120 / 1920 * win_width, 40 / 1080 * win_height)
        self.open_have_download_file_path_but.clicked.connect(self.open_have_download_path)

        # Download completion report
        self.open_help_file_but = QPushButton('Help', self)
        self.open_help_file_but.setFont(QFont("Times New Roman"))
        self.open_help_file_but.setGeometry(810 / 1920 * win_width, 670 / 1080 * win_height, 120 / 1920 * win_width,
                                            40 / 1080 * win_height)
        self.open_help_file_but.clicked.connect(self.open_download_help_file_but_line)

        # Download completion prompt
        self.show_download_information = QLabel(self)
        self.show_download_information.move(55 / 1920 * win_width, 710 / 1080 * win_height)
        self.show_download_information.setFixedSize(800 / 1920 * win_width, 35 / 1080 * win_height)
        self.show_download_process_state = QLabel(self)
        self.show_download_process_state.setGeometry(465 / 1920 * win_width, 710 / 1080 * win_height,
                                                     260 / 1920 * win_width, 35 / 1080 * win_height)

        # Download progress bar
        self.download_Progress_bar = QProgressBar(self)
        self.download_Progress_bar.setGeometry(50 / 1920 * win_width, 745 / 1080 * win_height, 960 / 1920 * win_width,
                                               40 / 1080 * win_height)
        self_step = 0
        self.download_Progress_bar.setValue(self_step)
        QApplication.processEvents()

    #  Search station name
    def Search_text_changed(self):
        self.choose_Option_display.clear()
        add_station_list = global_var.get_value('CORS_current_view_station_list')
        for item1 in add_station_list:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.choose_Option_display.addItem(item)
        goal_search_text = self.search_igs_label.text().lower()
        station_list_num = self.choose_Option_display.count()
        all_list_station_list = []
        for num in range(station_list_num):
            list_station = self.choose_Option_display.item(num).text()
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
        self.choose_Option_display.clear()
        for item1 in choosed_station_temp:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.choose_Option_display.addItem(item)
        self.choose_Option_display.verticalScrollBar().setSliderPosition(0)
        self.left_added_station_to_right_checked()

    def APREF_met_nav_file_type_changed_link(self):
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
        if self.APREF_label_OBS02_name.currentText() == 'Navigation':
            self.APREF_met_check.setChecked(False)
            self.APREF_met_check.setVisible(False)
            self.Curtin_rinex304_n_check.move(580 / 1920 * win_width, 140 / 1080 * win_height)
            self.Curtin_rinex304_n_box.move(601 / 1920 * win_width, 138 / 1080 * win_height)
            self.Curtin_rinex304_n_label.move(718 / 1920 * win_width, 141 / 1080 * win_height)
            self.Curtin_rinex304_n_check.setVisible(True)
            self.Curtin_rinex304_n_box.setVisible(True)
            self.Curtin_rinex304_n_label.setVisible(True)
            pass
        elif self.APREF_label_OBS02_name.currentText() == 'Meteorology':
            self.Curtin_rinex304_n_check.setChecked(False)
            self.Curtin_rinex304_n_check.setVisible(False)
            self.Curtin_rinex304_n_box.setVisible(False)
            self.Curtin_rinex304_n_label.setVisible(False)
            self.APREF_met_check.setVisible(True)
            pass
        pass

    def HK_met_file_checked_funcction(self):
        if self.HK_met_rnx211_check.isChecked() or self.HK_met_rnx304_check.isChecked():
            self.choose_add_station_list_box.setCurrentText('Met Station')
        else:
            self.choose_add_station_list_box.setCurrentText('All Station')
        pass

    def APREF_met_file_checked_funcction(self):
        if self.APREF_met_check.isChecked():
            self.choose_add_station_list_box.setCurrentText('Met Station')
        elif self.Curtin_rinex304_n_check.isChecked():
            self.choose_add_station_list_box.setCurrentText('Nav Station')
        else:
            self.choose_add_station_list_box.setCurrentText('All Station')
        pass

    def choose_add_station_list_change(self):
        json_text = json.load(open(str(curdir) + r'/lib/json/CORS_Statios.json', 'r'))
        coord_json_text = json.load(open(str(curdir) + r'/lib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
        extra_station_list = []# 0usa 1epn 2spain 3japan 4HongKong 5curtin 6apref
        for i in coord_json_text:
            temp_list = []
            for j in i:
                temp_list.append(j[0])
            extra_station_list.append(temp_list)

        self.choose_Option_display.clear()
        try:
            # self.choose_local_area_box  ['USA CORS', 'Europe EPN', 'Spain CORS', 'Japan JPN', 'Hong Kong CORS', 'Curtin University','Australia APREF CORS'])
            if self.choose_local_area_box.currentText() == 'USA CORS':
                current_added_station_list = extra_station_list[0]
            elif self.choose_local_area_box.currentText() == 'Hong Kong CORS':
                if self.choose_add_station_list_box.currentText() == 'All Station':
                    current_added_station_list = extra_station_list[4]
                elif self.choose_add_station_list_box.currentText() == 'Met Station':
                    current_added_station_list = json_text[2]
            elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
                if self.choose_add_station_list_box.currentText() == 'All Station':
                    current_added_station_list = extra_station_list[6]
                elif self.choose_add_station_list_box.currentText() == 'Met Station':
                    current_added_station_list = json_text[4]
                elif self.choose_add_station_list_box.currentText() == 'Nav Station':
                    current_added_station_list = json_text[5]
            elif self.choose_local_area_box.currentText() == 'Curtin University':
                current_added_station_list = extra_station_list[5]
            elif self.choose_local_area_box.currentText() == 'Europe EPN':
                current_added_station_list = extra_station_list[1]
            elif self.choose_local_area_box.currentText() == 'Spain CORS':
                current_added_station_list = extra_station_list[2]
            elif self.choose_local_area_box.currentText() == 'Japan JPN':
                current_added_station_list = extra_station_list[3]
            for item1 in current_added_station_list:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
        except:
            pass

    def HK_met_nav_file_type_changed_link(self):
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
        if self.HK_label_OBS02_name.currentText() == 'Meteorology':
            self.HK_label_OBS02_windows.setGeometry(665 / 1920 * win_width, 85 / 1080 * win_height,
                                                    250 / 1920 * win_width, 110 / 1080 * win_height)
            self.HK_rinex211_n_check.setChecked(False)
            self.HK_rinex304_n_check.setChecked(False)
            self.HK_rinex211_n_check.setVisible(False)
            self.HK_rinex211_n_box.setVisible(False)
            self.HK_rinex211_n_label.setVisible(False)
            self.HK_rinex304_n_check.setVisible(False)
            self.HK_rinex304_n_box.setVisible(False)
            self.HK_rinex304_n_label.setVisible(False)
            self.HK_met_rnx211_check.setVisible(True)
            self.HK_met_rnx304_check.setVisible(True)
            pass
        elif self.HK_label_OBS02_name.currentText() == 'Navigation':
            self.HK_label_OBS02_windows.setGeometry(665 / 1920 * win_width, 85 / 1080 * win_height,
                                                    360 / 1920 * win_width, 110 / 1080 * win_height)
            self.HK_met_rnx211_check.setChecked(False)
            self.HK_met_rnx304_check.setChecked(False)
            self.HK_met_rnx211_check.setVisible(False)
            self.HK_met_rnx304_check.setVisible(False)
            self.HK_rinex211_n_check.setVisible(True)
            self.HK_rinex211_n_box.setVisible(True)
            self.HK_rinex211_n_label.setVisible(True)
            self.HK_rinex304_n_check.setVisible(True)
            self.HK_rinex304_n_box.setVisible(True)
            self.HK_rinex304_n_label.setVisible(True)
            pass

    def curtin_brdc211_change(self):
        if self.Curtin_rinex211_n_box.currentText() == 'GPS':
            self.Curtin_rinex211_n_label.setText('RINEX 2.xx(.*n)')
        else:
            self.Curtin_rinex211_n_label.setText('RINEX 2.xx(.*g)')
            pass

    def curtin_brdc304_change(self):
        if self.Curtin_rinex304_n_box.currentText() == 'GPS':
            self.Curtin_rinex304_n_label.setText('RINEX 3.xx(_GN.rnx)')
        elif self.Curtin_rinex304_n_box.currentText() == 'Mix':
            self.Curtin_rinex304_n_label.setText('RINEX 3.xx(_MN.rnx)')
        elif self.Curtin_rinex304_n_box.currentText() == 'GLONASS':
            self.Curtin_rinex304_n_label.setText('RINEX 3.xx(_RN.rnx)')
        elif self.Curtin_rinex304_n_box.currentText() == 'BDS':
            self.Curtin_rinex304_n_label.setText('RINEX 3.xx(_CN.rnx)')
        elif self.Curtin_rinex304_n_box.currentText() == 'QZSS':
            self.Curtin_rinex304_n_label.setText('RINEX 3.xx(_JN.rnx)')
        elif self.Curtin_rinex304_n_box.currentText() == 'IRNSS':
            self.Curtin_rinex304_n_label.setText('RINEX 3.xx(_IN.rnx)')
        elif self.Curtin_rinex304_n_box.currentText() == 'GALILEO':
            self.Curtin_rinex304_n_label.setText('RINEX 3.xx(_EN.rnx)')
        pass

    def ngs_brdc211_change(self):
        if self.ngs_rinex211_n_box.currentText() == 'GPS':
            self.ngs_rinex211_n_label.setText('RINEX 2.xx(.*n)')
        else:
            self.ngs_rinex211_n_label.setText('RINEX 2.xx(.*g)')
            pass

    def HK_data_length_change(self):
        self.HK_rinex211_box.clear()
        self.HK_rinex304_box.clear()
        if self.HK_data_length_box.currentText() == '1 hour':
            self.HK_rinex211_box.addItems(['1s', '5s'])
            self.HK_rinex304_box.addItems(['1s', '5s'])
            self.start_time.setDisplayFormat('yyyy-MM-dd HH')
            self.end_time.setDisplayFormat('yyyy-MM-dd HH')
        else:
            self.HK_rinex211_box.addItems(['5s', '30s'])
            self.HK_rinex304_box.addItems(['30s'])
            self.start_time.setDisplayFormat('yyyy-MM-dd')
            self.end_time.setDisplayFormat('yyyy-MM-dd')

    # Select download source
    def local_area_changed(self):
        coord_json_text = json.load(open(str(curdir) + r'/lib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
        extra_station_list = []# 0usa 1epn 2spain 3japan 4HongKong 5curtin 6apref
        for i in coord_json_text:
            temp_list = []
            for j in i:
                temp_list.append(j[0])
            extra_station_list.append(temp_list)

        json_text = json.load(open(str(curdir) + r'/lib/json/CORS_Statios.json', 'r'))
        self.start_time.setDisplayFormat('yyyy-MM-dd')
        self.end_time.setDisplayFormat('yyyy-MM-dd')
        self.igs_names_display.clear()
        #  HongKong
        print(self.choose_local_area_box.currentText())
        self.HK_rinex211_check.setChecked(False)
        self.HK_rinex304_check.setChecked(False)
        self.HK_met_rnx211_check.setChecked(False)
        self.HK_met_rnx304_check.setChecked(False)
        self.HK_rinex211_n_check.setChecked(False)
        self.HK_rinex304_n_check.setChecked(False)
        self.HK_label_OBS01_windows.setVisible(False)
        self.HK_label_OBS01_name.setVisible(False)
        self.HK_rinex211_check.setVisible(False)
        self.HK_rinex211_box.setVisible(False)
        self.HK_rinex211_label.setVisible(False)
        self.HK_rinex304_check.setVisible(False)
        self.HK_rinex304_box.setVisible(False)
        self.HK_rinex304_label.setVisible(False)
        self.HK_data_length_label.setVisible(False)
        self.HK_data_length_box.setVisible(False)
        self.HK_label_OBS02_windows.setVisible(False)
        self.HK_label_OBS02_name.setVisible(False)
        self.HK_met_rnx211_check.setVisible(False)
        self.HK_met_rnx304_check.setVisible(False)
        self.HK_rinex211_n_check.setVisible(False)
        self.HK_rinex211_n_box.setVisible(False)
        self.HK_rinex211_n_label.setVisible(False)
        self.HK_rinex304_n_check.setVisible(False)
        self.HK_rinex304_n_box.setVisible(False)
        self.HK_rinex304_n_label.setVisible(False)

        #  Curtin University
        self.Curtin_rinex211_check.setChecked(False)
        self.Curtin_rinex304_check.setChecked(False)
        self.Curtin_rinex211_n_check.setChecked(False)
        self.Curtin_rinex304_n_check.setChecked(False)
        self.APREF_met_check.setChecked(False)
        self.Curtin_label_OBS01_windows.setVisible(False)
        self.Curtin_label_OBS01_name.setVisible(False)
        self.Curtin_rinex211_check.setVisible(False)
        self.Curtin_rinex304_check.setVisible(False)
        self.Curtin_label_OBS02_windows.setVisible(False)
        self.Curtin_label_OBS02_name.setVisible(False)
        self.Curtin_rinex211_n_check.setVisible(False)
        self.Curtin_rinex211_n_box.setVisible(False)
        self.Curtin_rinex211_n_label.setVisible(False)
        self.Curtin_rinex304_n_check.setVisible(False)
        self.Curtin_rinex304_n_box.setVisible(False)
        self.Curtin_rinex304_n_label.setVisible(False)
        self.APREF_label_OBS02_name.setVisible(False)
        self.APREF_met_check.setVisible(False)

        #  USA CORS
        self.ngs_rinex211_check.setChecked(False)
        self.ngs_rinex304_check.setChecked(False)
        self.ngs_rinex211_n_check.setChecked(False)
        self.ngs_label_OBS01_windows.setVisible(False)
        self.ngs_label_OBS01_name.setVisible(False)
        self.ngs_label_OBS02_windows.setVisible(False)
        self.ngs_label_OBS02_name.setVisible(False)
        self.ngs_rinex211_check.setVisible(False)
        self.ngs_rinex304_check.setVisible(False)
        self.ngs_rinex211_n_check.setVisible(False)
        self.ngs_rinex211_n_box.setVisible(False)
        self.ngs_rinex211_n_label.setVisible(False)

        #  Enrope EPN
        self.epn_label_OBS01_windows.setVisible(False)
        self.epn_label_OBS01_name.setVisible(False)
        self.epn_label_OBS02_windows.setVisible(False)
        self.epn_label_OBS02_name.setVisible(False)
        self.epn_rinex304_check.setVisible(False)
        self.epn_rinex304_mn_check.setVisible(False)

        self.epn_rinex304_check.setChecked(False)
        self.epn_rinex304_mn_check.setChecked(False)

        #  Spain CORS
        self.spain_label_OBS01_windows.setVisible(False)
        self.spain_label_OBS01_name.setVisible(False)
        self.spain_rinex211_check.setVisible(False)
        self.spain_rinex304_check.setVisible(False)

        self.spain_rinex211_check.setChecked(False)
        self.spain_rinex304_check.setChecked(False)

        #  Japan JPN
        self.Japan_label_OBS01_windows.setVisible(False)
        self.Japan_label_OBS01_name.setVisible(False)
        self.Japan_label_OBS02_windows.setVisible(False)
        self.Japan_label_OBS02_name.setVisible(False)
        self.Japan_label_OBS03_windows.setVisible(False)
        self.Japan_label_OBS03_name.setVisible(False)
        self.Japan_rinex211_check.setVisible(False)
        self.Japan_rinex211_glonassn_check.setVisible(False)
        self.Japan_igu_check.setVisible(False)
        self.Japan_igr_check.setVisible(False)
        self.Japan_igs_check.setVisible(False)
        self.Japan_snx_check.setVisible(False)
        self.Japan_clk_check.setVisible(False)
        self.Japan_fcb_check.setVisible(False)

        self.Japan_rinex211_check.setChecked(False)
        self.Japan_rinex211_glonassn_check.setChecked(False)
        self.Japan_igu_check.setChecked(False)
        self.Japan_igr_check.setChecked(False)
        self.Japan_igs_check.setChecked(False)
        self.Japan_snx_check.setChecked(False)
        self.Japan_clk_check.setChecked(False)
        self.Japan_fcb_check.setChecked(False)


        if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
            self.start_time.setDisplayFormat('yyyy-MM-dd HH')
            self.end_time.setDisplayFormat('yyyy-MM-dd HH')
            self.HK_label_OBS01_windows.setVisible(True)
            self.HK_label_OBS01_name.setVisible(True)
            self.HK_rinex211_check.setVisible(True)
            self.HK_rinex211_box.setVisible(True)
            self.HK_rinex211_label.setVisible(True)
            self.HK_rinex304_check.setVisible(True)
            self.HK_rinex304_box.setVisible(True)
            self.HK_rinex304_label.setVisible(True)
            self.HK_data_length_label.setVisible(True)
            self.HK_data_length_box.setVisible(True)
            self.HK_label_OBS02_windows.setVisible(True)
            self.HK_label_OBS02_name.setVisible(True)
            # self.HK_met_rnx211_check.setVisible(True)
            # self.HK_met_rnx304_check.setVisible(True)
            self.HK_rinex211_n_check.setVisible(True)
            self.HK_rinex211_n_box.setVisible(True)
            self.HK_rinex211_n_label.setVisible(True)
            self.HK_rinex304_n_check.setVisible(True)
            self.HK_rinex304_n_box.setVisible(True)
            self.HK_rinex304_n_label.setVisible(True)
            self.choose_Option_display.clear()
            Files = extra_station_list[4]
            self.igs_names_display.setPlaceholderText('hkcl\nhkfn\nHKLM\nHKMW')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
                pass

        elif self.choose_local_area_box.currentText() == 'Curtin University' or self.choose_local_area_box.currentText() == 'Australia APREF CORS':
            self.Curtin_label_OBS01_windows.setVisible(True)
            self.Curtin_label_OBS01_name.setVisible(True)
            self.Curtin_rinex211_check.setVisible(True)
            self.Curtin_rinex304_check.setVisible(True)
            self.Curtin_label_OBS02_windows.setVisible(True)
            self.Curtin_label_OBS02_name.setVisible(True)
            self.Curtin_rinex304_n_check.setVisible(True)
            self.Curtin_rinex304_n_box.setVisible(True)
            self.Curtin_rinex304_n_label.setVisible(True)
            self.choose_Option_display.clear()
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
            if self.choose_local_area_box.currentText() == 'Curtin University':
                self.Curtin_rinex211_n_check.setVisible(True)
                self.Curtin_rinex211_n_box.setVisible(True)
                self.Curtin_rinex211_n_label.setVisible(True)
                self.Curtin_rinex304_n_check.move(580 / 1920 * win_width, 155 / 1080 * win_height)
                self.Curtin_rinex304_n_box.move(601 / 1920 * win_width, 153 / 1080 * win_height)
                self.Curtin_rinex304_n_label.move(718 / 1920 * win_width, 155 / 1080 * win_height)
                self.Curtin_rinex304_n_box.clear()
                self.Curtin_rinex304_n_box.addItems(['GPS', 'BDS', 'GLONASS', 'GALILEO', 'QZSS', 'IRNSS'])
                Files = extra_station_list[5]
                self.igs_names_display.setPlaceholderText('cuaa\ncut2\nCUTA\nSPA7')
            elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
                self.APREF_label_OBS02_name.setVisible(True)
                self.Curtin_rinex304_n_check.move(580 / 1920 * win_width, 140 / 1080 * win_height)
                self.Curtin_rinex304_n_box.move(601 / 1920 * win_width, 138 / 1080 * win_height)
                self.Curtin_rinex304_n_label.move(718 / 1920 * win_width, 141 / 1080 * win_height)
                self.Curtin_rinex304_n_box.clear()
                self.Curtin_rinex304_n_box.addItems(['GPS', 'BDS', 'GLONASS', 'GALILEO', 'QZSS'])
                Files = extra_station_list[6]
                self.igs_names_display.setPlaceholderText('abpo\nalbh\nALIC\nANTW')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)

        elif self.choose_local_area_box.currentText() == 'USA CORS':
            self.ngs_label_OBS01_windows.setVisible(True)
            self.ngs_label_OBS01_name.setVisible(True)
            self.ngs_label_OBS02_windows.setVisible(True)
            self.ngs_label_OBS02_name.setVisible(True)
            self.ngs_rinex211_check.setVisible(True)
            self.ngs_rinex304_check.setVisible(True)
            self.ngs_rinex211_n_check.setVisible(True)
            self.ngs_rinex211_n_box.setVisible(True)
            self.ngs_rinex211_n_label.setVisible(True)
            self.choose_Option_display.clear()
            Files = extra_station_list[0]
            self.igs_names_display.setPlaceholderText('1lsu\nab02\nAB17\nAB33')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)

        elif self.choose_local_area_box.currentText() == 'Europe EPN':
            self.epn_label_OBS01_windows.setVisible(True)
            self.epn_label_OBS01_name.setVisible(True)
            self.epn_label_OBS02_windows.setVisible(True)
            self.epn_label_OBS02_name.setVisible(True)
            self.epn_rinex304_check.setVisible(True)
            self.epn_rinex304_mn_check.setVisible(True)
            self.choose_Option_display.clear()
            Files = extra_station_list[1]
            self.igs_names_display.setPlaceholderText('acor\nalac\nAGUI\nBADH')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)

        elif self.choose_local_area_box.currentText() == 'Spain CORS':
            self.spain_label_OBS01_windows.setVisible(True)
            self.spain_label_OBS01_name.setVisible(True)
            self.spain_rinex211_check.setVisible(True)
            self.spain_rinex304_check.setVisible(True)
            self.choose_Option_display.clear()
            Files = extra_station_list[2]
            self.igs_names_display.setPlaceholderText('vblo\nsgva\nPEN1\nSORI')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
            pass
        elif self.choose_local_area_box.currentText() == 'Holland DPGA':
            self.Netherlands_label_OBS01_windows.setVisible(True)
            self.Netherlands_label_OBS01_name.setVisible(True)
            self.Netherlands_rinex211_check.setVisible(True)
            self.Netherlands_rinex304_check.setVisible(True)
            self.Netherlands_label_OBS02_windows.setVisible(True)
            self.Netherlands_label_OBS02_name.setVisible(True)
            self.Netherlands_broadcast_211_label.setVisible(True)
            self.Netherlands_rinex211_gpsn_check.setVisible(True)
            self.Netherlands_rinex211_glonassn_check.setVisible(True)
            self.Netherlands_broadcast_304_label.setVisible(True)
            self.Netherlands_rinex304_gpsn_check.setVisible(True)
            self.choose_Option_display.clear()
            Files = json_text[10]
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)

        elif self.choose_local_area_box.currentText() == 'Japan JPN':
            self.Japan_label_OBS01_windows.setVisible(True)
            self.Japan_label_OBS01_name.setVisible(True)
            self.Japan_label_OBS02_windows.setVisible(True)
            self.Japan_label_OBS02_name.setVisible(True)
            self.Japan_label_OBS03_windows.setVisible(True)
            self.Japan_label_OBS03_name.setVisible(True)
            self.Japan_rinex211_check.setVisible(True)
            self.Japan_rinex211_glonassn_check.setVisible(True)
            self.Japan_igu_check.setVisible(True)
            self.Japan_igr_check.setVisible(True)
            self.Japan_igs_check.setVisible(True)
            self.Japan_snx_check.setVisible(True)
            self.Japan_clk_check.setVisible(True)
            self.Japan_fcb_check.setVisible(True)
            self.choose_Option_display.clear()
            Files = extra_station_list[3]
            self.igs_names_display.setPlaceholderText('anmg\ncmum\nDAE2\nMSSA')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
        else:
            self.choose_Option_display.clear()
            pass
        global_var.set_value('CORS_current_view_station_list', Files)

    # -------------------------------------------------------------------------------------------------
    # start time convert
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
            pass
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

    # -------------------------------------------------------------------------------------------------
    # End time convert
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
            elif int(self.changday0401.text()) <= 1990 or int(self.changday0401.text()) >= 2050 or int(
                    self.changday0402.text()) <= 0 or int(self.changday0402.text()) >= 366:
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
            elif int(self.changday0501.text()) <= 500 or int(self.changday0501.text()) >= 3400 or int(
                    self.changday0502.text()) < 0 or int(self.changday0502.text()) >= 7:
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

    # Display CORS map
    def add_map_Items(self):
        if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
            Download_Source = '/HongKong'
        elif self.choose_local_area_box.currentText() == 'Curtin University':
            Download_Source = '/Curtin'
        elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
            Download_Source = '/Apref'
        elif self.choose_local_area_box.currentText() == 'USA CORS':
            Download_Source = '/USA'
        elif self.choose_local_area_box.currentText() == 'Europe EPN':
            Download_Source = '/Enrope'
        elif self.choose_local_area_box.currentText() == 'Spain CORS':
            Download_Source = '/Spain'
        elif self.choose_local_area_box.currentText() == 'Japan JPN':
            Download_Source = '/Japan'
        self.h = Return_Map_Names(Download_Source)
        self.h.my_Signal.connect(self.close_sonView_trigger_event)
        self.h.show()

    # Close sub interface
    def close_sonView_trigger_event(self):
        Map_HongKongCORS_name = global_var.get_value('HongKong_station_list')
        Map_CurtinCORS_name = global_var.get_value('Curtin_station_list')
        Map_AprefCORS_name = global_var.get_value('Apref_station_list')
        Map_EnropeCORS_name = global_var.get_value('ENP_station_list')
        Map_JapanCORS_name = global_var.get_value('JPN_station_list')
        Map_SpainCORS_name = global_var.get_value('Spain_station_list')
        Map_USACORS_name = global_var.get_value('USA_station_list')
        map_cors_names = []
        try:
            if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
                if Map_HongKongCORS_name != {}:
                    Map_HongKongCORS_name_list = Map_HongKongCORS_name['name']
                    Map_HongKongCORS_name_list = list(Map_HongKongCORS_name_list)
                    print(Map_HongKongCORS_name_list)
                    for i in Map_HongKongCORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'Curtin University':
                if Map_CurtinCORS_name != {}:
                    Map_CurtinCORS_name_list = Map_CurtinCORS_name['name']
                    Map_CurtinCORS_name_list = list(Map_CurtinCORS_name_list)
                    for i in Map_CurtinCORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
                if Map_AprefCORS_name != {}:
                    Map_AprefCORS_name_list = Map_AprefCORS_name['name']
                    Map_AprefCORS_name_list = list(Map_AprefCORS_name_list)
                    for i in Map_AprefCORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'USA CORS':
                if Map_USACORS_name != {}:
                    Map_USACORS_name_list = Map_USACORS_name['name']
                    Map_USACORS_name_list = list(Map_USACORS_name_list)
                    for i in Map_USACORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'Europe EPN':
                if Map_EnropeCORS_name != {}:
                    Map_EnropeCORS_name_list = Map_EnropeCORS_name['name']
                    Map_EnropeCORS_name_list = list(Map_EnropeCORS_name_list)
                    for i in Map_EnropeCORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'Spain CORS':
                if Map_SpainCORS_name != {}:
                    Map_SpainCORS_name_list = Map_SpainCORS_name['name']
                    Map_SpainCORS_name_list = list(Map_SpainCORS_name_list)
                    for i in Map_SpainCORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'Japan JPN':
                if Map_JapanCORS_name != {}:
                    Map_JapanCORS_name_list = Map_JapanCORS_name['name']
                    Map_JapanCORS_name_list = list(Map_JapanCORS_name_list)
                    for i in Map_JapanCORS_name_list:
                        map_cors_names.append(i)
                    pass
            temp_station_text = ''
            for map_cors_name in map_cors_names:
                temp_station_text = temp_station_text + str(map_cors_name) + '\n'
            self.igs_names_display.append(temp_station_text[:-1])
            self.left_added_station_deduplication()
        except:
            pass

    #  Map display
    def station_map_display_function(self):
        json_text = json.load(open(str(curdir) + r'/lib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
        #   self.choose_local_area_box  ['USA CORS', 'Europe EPN', 'Spain CORS', 'Japan JPN', 'Hong Kong CORS', 'Curtin University', 'Australia APREF CORS']
        if self.choose_local_area_box.currentText() == 'USA CORS':
            all_source_Info = json_text[0]
        elif self.choose_local_area_box.currentText() == 'Europe EPN':
            all_source_Info = json_text[1]
        elif self.choose_local_area_box.currentText() == 'Spain CORS':
            all_source_Info = json_text[2]
        elif self.choose_local_area_box.currentText() == 'Japan JPN':
            all_source_Info = json_text[3]
        elif self.choose_local_area_box.currentText() == 'Hong Kong CORS':
            all_source_Info = json_text[4]
        elif self.choose_local_area_box.currentText() == 'Curtin University':
            all_source_Info = json_text[5]
        elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
            all_source_Info = json_text[6]

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
        # print(added_station_coordinate)
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

    # Station information table
    #     ['Hong Kong CORS', 'USA CORS', 'Europe EPN', 'Spain CORS', 'Japan JPN', 'Australia APREF CORS', 'Curtin University']
    def open_station_info_table_link(self):
        if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
            self.exit_window = HongKong_Station_Info_Table()
        elif self.choose_local_area_box.currentText() == 'USA CORS':
            self.exit_window = NGS_Info_Table()
        elif self.choose_local_area_box.currentText() == 'Europe EPN':
            self.exit_window = EPN_Info_Table()
        elif self.choose_local_area_box.currentText() == 'Spain CORS':
            self.exit_window = Spain_CORS_Info_Table()
        elif self.choose_local_area_box.currentText() == 'Japan JPN':
            self.exit_window = JPN_Info_Table()
        elif self.choose_local_area_box.currentText() == 'Curtin University':
            self.exit_window = Curtin_Station_Info_Table()
        elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
            self.exit_window = APREF_CORS_Info_Table()
        self.exit_window.my_Signal_AreaCors.connect(self.AreaCors_Info_Table_exit)
        self.exit_window.show()
        pass

    def AreaCors_Info_Table_exit(self):
        AreaCORS_Info_checked_station_list = global_var.get_value('Info_table_checked_AreaCORS_stations')
        # print(IGS_Info_checked_station_list)
        temp_station_text = ''
        if AreaCORS_Info_checked_station_list:
            for i in AreaCORS_Info_checked_station_list:
                temp_station_text = temp_station_text + str(i) + '\n'
            self.igs_names_display.append(temp_station_text[:-1])
            self.left_added_station_deduplication()
        self.choose_add_station_list_change()
        clear_station_list = []
        global_var.set_value('Info_table_checked_AreaCORS_stations', clear_station_list)

    # Select all station
    def choose_all_station_function(self):
        if self.choose_all_station_CheckBtn.checkState() == Qt.Checked:
            for num in range(self.choose_Option_display.count()):
                self.choose_Option_display.item(num).setCheckState(Qt.Checked)
        else:
            for num in range(self.choose_Option_display.count()):
                self.choose_Option_display.item(num).setCheckState(Qt.Unchecked)
        pass

    # add station
    def add_igs_Items_function(self):
        check_igs_names = []
        for num in range(self.choose_Option_display.count()):
            if self.choose_Option_display.item(num).checkState() == Qt.Checked:
                check_igs_names.append(self.choose_Option_display.item(num).text())
                self.choose_Option_display.item(num).setCheckState(False)
        temp_station_text = ''
        for check_igs_name in check_igs_names:
            temp_station_text = temp_station_text + str(check_igs_name) + '\n'
            # self.igs_names_display.append(str(check_igs_name))
            pass
        self.igs_names_display.append(temp_station_text[:-1])
        self.left_added_station_deduplication()

    def clear_added_station_function(self):
        self.igs_names_display.clear()

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

    #  Displays the number of stations added
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

    #  Delete duplicate stations
    def left_added_station_deduplication(self):
        all_choosed_station_list = re.split('[,\n]', self.igs_names_display.toPlainText())
        check_igs_names = []
        for k in all_choosed_station_list:
            if k not in check_igs_names and k != '':
                check_igs_names.append(k)
        # print(check_igs_names)
        temp_station_text = ''
        self.igs_names_display.clear()
        for check_igs_name in check_igs_names:
            temp_station_text = temp_station_text + str(check_igs_name) + '\n'
        self.igs_names_display.append(temp_station_text)

    # Add station, check the check box
    def left_added_station_to_right_checked(self):
        for k in range(self.choose_Option_display.count()):
            self.choose_Option_display.item(k).setCheckState(Qt.Unchecked)
        all_choosed_station_list = re.split('[,\n]', self.igs_names_display.toPlainText())
        goal_added_station_row = []
        for i in all_choosed_station_list:
            for num in range(self.choose_Option_display.count()):
                if i.lower() == self.choose_Option_display.item(num).text():
                    goal_added_station_row.append(num)
                pass
        for k in goal_added_station_row:
            self.choose_Option_display.item(k).setCheckState(Qt.Checked)

    @retry(stop_max_attempt_number=21600, wait_random_min=1000, wait_random_max=5000)
    def sftp_download_function(self, url, file_name):
        global successful_library
        global failed_library
        global self_step
        global ftp_max_thread
        import time
        time.sleep(0.1)
        with ftp_max_thread:
            download_location = 'sftp.data.gnss.ga.gov.au' + url
            list = [download_location, file_name]
            self_file_path = self.show_outsave_files_path_button.text() + '/' + str(file_name)
            try:
                sftp.get(url, self_file_path)
                print('success：', 'sftp.data.gnss.ga.gov.au' + url)
                successful_library = successful_library + [list]
                self_step = self_step + 1
                self.download_Progress_bar.setValue(self_step)
                QApplication.processEvents()
            except:
                print('failure：', 'sftp.data.gnss.ga.gov.au' + url)
                self_step = self_step + 1
                self.download_Progress_bar.setValue(self_step)
                QApplication.processEvents()
                failed_library = failed_library + [list]

    @retry(stop_max_attempt_number=21600, wait_random_min=1000, wait_random_max=5000)
    # @func_set_timeout(20)
    def ftp_download_function(self, url, file_name, s):
        global successful_library
        global failed_library
        global self_step
        global ftp_max_thread
        import time
        time.sleep(0.1)
        with ftp_max_thread:
            list = [url, file_name]
            self_file_path = self.show_outsave_files_path_button.text() + '/' + str(file_name)

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
        try:
            html = requests.get("http://www.baidu.com", timeout=2)
        except:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips',
                                    'The network connection failed, please check the device network connection!')
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
        if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
            requests_ftp.monkeypatch_session()
            session = requests.Session()
            ftp_max_thread = threading.Semaphore(10)
            pass
        elif self.choose_local_area_box.currentText() == 'Curtin University':
            session = requests.Session()
            ftp_max_thread = threading.Semaphore(10)
            pass
        elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
            requests_ftp.monkeypatch_session()
            session = requests.Session()
            ftp_max_thread = threading.Semaphore(1)
        elif self.choose_local_area_box.currentText() == 'USA CORS':
            session = requests.Session()
            ftp_max_thread = threading.Semaphore(10)
            pass
        elif self.choose_local_area_box.currentText() == 'Europe EPN':
            requests_ftp.monkeypatch_session()
            session = requests.Session()
            ftp_max_thread = threading.Semaphore(1)
            pass
        elif self.choose_local_area_box.currentText() == 'Spain CORS':
            session = requests.Session()
            ftp_max_thread = threading.Semaphore(10)
            pass
        elif self.choose_local_area_box.currentText() == 'Holland DPGA':
            requests_ftp.monkeypatch_session()
            session = requests.Session()
            ftp_max_thread = threading.Semaphore(5)
            pass
        elif self.choose_local_area_box.currentText() == 'Japan JPN':
            requests_ftp.monkeypatch_session()
            session = requests.Session()
            ftp_max_thread = threading.Semaphore(1)
        else:
            pass
        if os.path.exists(self.show_outsave_files_path_button.text()):
            pass
        else:
            os.mkdir(self.show_outsave_files_path_button.text())

        # time list
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
                list = [YearAccuDay_GpsWeek[0], YearAccuDay_GpsWeek[1], YearAccuDay_GpsWeek[2], YearAccuDay_GpsWeek[3],
                        YearAccuDay_GpsWeek[4], YearAccuDay_GpsWeek[5]]
                all_YearAccuDay_GpsWeek = all_YearAccuDay_GpsWeek + [list]
                pass
            print(all_YearAccuDay_GpsWeek)

            # new time list
            all_YearAccuDay_Hour = []
            if self.choose_local_area_box.currentText() == 'Hong Kong CORS' and self.HK_data_length_box.currentText()  == '1 hour':
                start_time_T = str(self.start_time.dateTime().toString(Qt.ISODate))
                start_time = start_time_T[0:10] + ' ' + start_time_T[11:13]  # 2021-12-22 01
                start_time_date = start_time_T[0:10]
                start_time_hhmmss = start_time_T[11:13]
                end_time_T = str(self.end_time.dateTime().toString(Qt.ISODate))
                end_time = end_time_T[0:10] + ' ' + end_time_T[11:13]
                end_time_date = end_time_T[0:10]
                end_time_hhmmss = end_time_T[11:13]
                start_time_hhmmss_list = [int(start_time_hhmmss[0:2])]
                end_time_hhmmss_list = [int(end_time_hhmmss[0:2])]

                # Start time
                delete_minute_num1 = -1
                for i in range(24):
                    if start_time_hhmmss_list[0] < i:
                        break
                    delete_minute_num1 = delete_minute_num1 + 1
                del_standard_minute_span = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                for i in range(delete_minute_num1):
                    del del_standard_minute_span[0]
                start_time_hh = []
                for j in del_standard_minute_span:
                    j = f"0{j}" if j < 10 else f"{j}"
                    start_time_hh = start_time_hh + [j]

                # End time
                delete_minute_num2 = -1
                for i in range(24):
                    if end_time_hhmmss_list[0] < i:
                        break
                    delete_minute_num2 = delete_minute_num2 + 1
                    delete_minute_num22 = 24 - delete_minute_num2
                del_standard_minute_span2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                for i in range(delete_minute_num22):
                    del del_standard_minute_span2[-1]
                end_time_hh = []
                for j in del_standard_minute_span2:
                    j = f"0{j}" if j < 10 else f"{j}"
                    end_time_hh = end_time_hh + [j]

                if len(all_YearAccuDay_GpsWeek) == 1:
                    temp_final_hh_list = []
                    for i in start_time_hh:
                        if i in end_time_hh:
                            temp_final_hh_list = temp_final_hh_list + [i]
                    for i in temp_final_hh_list:
                        temp_datetime1 = all_YearAccuDay_GpsWeek[0] + [i]
                        all_YearAccuDay_Hour = all_YearAccuDay_Hour + [temp_datetime1]
                elif len(all_YearAccuDay_GpsWeek) == 2:
                    for i in start_time_hh:
                        all_YearAccuDay_Hour = all_YearAccuDay_Hour + [all_YearAccuDay_GpsWeek[0] + [i]]
                    for j in end_time_hh:
                        all_YearAccuDay_Hour = all_YearAccuDay_Hour + [all_YearAccuDay_GpsWeek[1] + [j]]
                elif len(all_YearAccuDay_GpsWeek) > 2:
                    for i in start_time_hh:
                        all_YearAccuDay_Hour = all_YearAccuDay_Hour + [all_YearAccuDay_GpsWeek[0] + [i]]
                    for j in end_time_hh:
                        all_YearAccuDay_Hour = all_YearAccuDay_Hour + [all_YearAccuDay_GpsWeek[-1] + [j]]
                    temp_all_YearAccuDay_GpsWeek_1s = all_YearAccuDay_GpsWeek[:]
                    del (temp_all_YearAccuDay_GpsWeek_1s[0], temp_all_YearAccuDay_GpsWeek_1s[-1])
                    for x in range(24):
                        x = f"0{x}" if x < 10 else f"{x}"
                        for z in temp_all_YearAccuDay_GpsWeek_1s:
                            all_YearAccuDay_Hour = all_YearAccuDay_Hour + [z + [x]]
                print(all_YearAccuDay_Hour)

        # Get station name
        igs_name_list = str(self.igs_names_display.toPlainText())
        igs_name_list = re.findall(r'\w+', igs_name_list)
        temp_igs_name_list = []
        for i in igs_name_list:
            if i not in temp_igs_name_list:
                temp_igs_name_list.append(i)
        igs_name_list = temp_igs_name_list
        igs_uppercase = []
        igs_lowercase = []
        for igs_name in igs_name_list:
            upper_latter = igs_name.upper()
            low_latter = igs_name.lower()
            igs_uppercase.append(upper_latter)
            igs_lowercase.append(low_latter)

        # output path
        if self.show_outsave_files_path_button.text() == '':
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips', 'Please choose a output path!')
            return

        # Generate download list
        rinex211o_1s_url_list = []
        rinex211o_5s_url_list = []
        rinex211o_30s_url_list = []
        rinex304o_1s_url_list = []
        rinex304o_5s_url_list = []
        rinex304o_30s_url_list = []
        rinex211n_url_list = []
        rinex304n_url_list = []
        igs_url_list = []
        igu_url_list = []
        igr_url_list = []
        tro_url_list = []
        ion_url_list = []
        dcb_url_list = []
        erp_url_list = []
        clk_30s_url_list = []
        clk_5s_url_list = []
        snx_url_list = []
        obx_url_list = []

        # -------------------------------------------------------------------------------------------------
        #  HongKong CORS
        #  2. HongKong Rinex2.11  observation ；Curtin University Rinex2.11 observation ;  APREF CORS Rinex2.11 observation ; USA NGS CORS Rinex  .*o filee ； Spain CORS .*d OBS ；Netherlands DPGA .*d OBS ；Japan JPN .*o OBS url
        if self.HK_rinex211_check.isChecked() or self.Curtin_rinex211_check.isChecked() or self.ngs_rinex211_check.isChecked() or self.spain_rinex211_check.isChecked() or self.Japan_rinex211_check.isChecked():
            if igs_lowercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                return
            else:
                rinex211o_1s_url_list_temp = []
                if all_YearAccuDay_Hour:
                    url_time = all_YearAccuDay_Hour
                else:
                    url_time = all_YearAccuDay_GpsWeek
                for time in url_time:
                    for igs211_name in igs_lowercase:
                        if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
                            if self.HK_rinex211_box.currentText() == '1s':
                                single_letter = chr(int(time[6])+97)
                                file_name = igs211_name + str(time[3]) + single_letter + '.' + str(time[1]) + 'd.gz'
                                #  https://rinex.geodetic.gov.hk/rinex2/2021/001/hkmw/1s/hkmw001k.21d.gz
                                download_rinex211o_1s_url = 'https://rinex.geodetic.gov.hk/rinex2/' + str(time[0]) + '/' + str(time[3]) + '/' + igs211_name + '/1s/' + file_name
                                list = [download_rinex211o_1s_url, file_name]
                                rinex211o_1s_url_list_temp = rinex211o_1s_url_list_temp + [list]
                                pass
                            elif self.HK_rinex211_box.currentText() == '5s':
                                if self.HK_data_length_box.currentText() == '1 hour':
                                    single_letter = chr(int(time[6])+97)
                                    file_name = igs211_name + str(time[3]) + single_letter + '.' + str(time[1]) + 'd.gz'
                                    #  https://rinex.geodetic.gov.hk/rinex2/2021/001/hkmw/5s/hkmw001k.21d.gz
                                    download_rinex211o_1s_url = 'https://rinex.geodetic.gov.hk/rinex2/' + str(time[0]) + '/' + str(time[3]) + '/' + igs211_name + '/5s/' + file_name
                                    list = [download_rinex211o_1s_url, file_name]
                                    rinex211o_1s_url_list_temp = rinex211o_1s_url_list_temp + [list]
                                    pass
                                elif self.HK_data_length_box.currentText() == '1 day':
                                    file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'd.gz'
                                    #  https://rinex.geodetic.gov.hk/rinex2/2021/001/hkkt/5s/hkkt0010.21d.gz
                                    download_rinex211o_1s_url = 'https://rinex.geodetic.gov.hk/rinex2/' + str(time[0]) + '/' + str(time[3]) + '/' + igs211_name + '/5s/' + file_name
                                    list = [download_rinex211o_1s_url, file_name]
                                    rinex211o_1s_url_list = rinex211o_1s_url_list + [list]
                            elif self.HK_rinex211_box.currentText() == '30s':
                                file_name = igs211_name + str(time[3]) + str(0) + '.' + str(time[1]) + 'd.gz'
                                #  https://rinex.geodetic.gov.hk/rinex2/2021/001/hkcl/30s/hkcl0010.21d.gz
                                download_rinex211o_1s_url = 'https://rinex.geodetic.gov.hk/rinex2/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + igs211_name + '/30s/' + file_name
                                list = [download_rinex211o_1s_url, file_name]
                                rinex211o_1s_url_list = rinex211o_1s_url_list + [list]
                                pass
                        elif self.choose_local_area_box.currentText() == 'Curtin University':
                            file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'd.Z'
                            #   http://saegnss2.curtin.edu/ldc/rinex/daily/2021/001/cuaa0010.21d.Z
                            download_rinex211o_1s_url = 'http://saegnss2.curtin.edu/ldc/rinex/daily/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + file_name
                            list = [download_rinex211o_1s_url, file_name]
                            rinex211o_1s_url_list = rinex211o_1s_url_list + [list]
                            pass
                        elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
                            file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'd.gz'
                            #   sftp.data.gnss.ga.gov.au   /rinex/daily/2022/001/hksl0010.21d.gz
                            download_rinex211o_1s_url = '/rinex/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                            list = [download_rinex211o_1s_url, file_name]
                            rinex211o_1s_url_list = rinex211o_1s_url_list + [list]
                            pass
                        elif self.choose_local_area_box.currentText() == 'USA CORS':
                            file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'o.gz'
                            #   https://geodesy.noaa.gov/corsdata/rinex/2021/001/ab13/ab130010.21o.gz
                            download_rinex211o_1s_url = 'https://geodesy.noaa.gov/corsdata/rinex/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + igs211_name + '/' + igs211_name + str(
                                time[3]) + '0.' + str(time[1]) + 'o.gz'
                            list = [download_rinex211o_1s_url, file_name]
                            rinex211o_1s_url_list = rinex211o_1s_url_list + [list]
                            pass
                        elif self.choose_local_area_box.currentText() == 'Spain CORS':
                            file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'd.Z'
                            #   http://ftp.itacyl.es/RINEX/diario_30s/2021/003/vala0030.21d.Z
                            download_rinex211o_1s_url = 'http://ftp.itacyl.es/RINEX/diario_30s/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + igs211_name + str(time[3]) + '0.' + str(
                                time[1]) + 'd.Z'
                            list = [download_rinex211o_1s_url, file_name]
                            rinex211o_1s_url_list = rinex211o_1s_url_list + [list]
                            pass
                        elif self.choose_local_area_box.currentText() == 'Japan JPN':
                            igs304_name = igs211_name.upper()
                            file_name = igs304_name + str(time[3]) + '0.' + str(time[1]) + 'o.Z'
                            #   ftp://mgmds01.tksc.jaxa.jp/data/daily/2021/001/ANMG0010.21o.Z
                            download_rinex211o_1s_url = 'ftp://mgmds01.tksc.jaxa.jp/data/daily/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + igs304_name + str(time[3]) + '0.' + str(
                                time[1]) + 'o.Z'
                            list = [download_rinex211o_1s_url, file_name]
                            rinex211o_1s_url_list = rinex211o_1s_url_list + [list]
                            pass
                for i in rinex211o_1s_url_list_temp:
                    if i not in rinex211o_1s_url_list:
                        rinex211o_1s_url_list.append(i)

        #  3. Curtin University  Rinex2.11 GPS Broadcast ephemeris ; APREF CORS Rinex2.11 GPS Broadcast ephemeris USA NGS Rinex  .*d filee ；Japan JPN .*p url
        if self.Curtin_rinex211_n_check.isChecked() or self.ngs_rinex304_check.isChecked() or self.Japan_rinex211_glonassn_check.isChecked():
            if igs_lowercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                return
            else:
                for time in all_YearAccuDay_GpsWeek:
                    for igs211_name in igs_lowercase:
                        if self.choose_local_area_box.currentText() == 'Curtin University':
                            if self.Curtin_rinex211_n_box.currentText() == 'GPS':
                                file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'n.Z'
                                #  http://saegnss2.curtin.edu/ldc/rinex/daily/2021/001/cuaa0010.21n.Z
                                download_rinex211o_5s_url = 'http://saegnss2.curtin.edu/ldc/rinex/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            else:
                                file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'g.Z'
                                download_rinex211o_5s_url = 'http://saegnss2.curtin.edu/ldc/rinex/daily/' + str(
                                    time[0]) + '/' + str(time[3]) + '/' + file_name
                            list = [download_rinex211o_5s_url, file_name]
                            rinex211o_5s_url_list = rinex211o_5s_url_list + [list]
                            pass
                        elif self.choose_local_area_box.currentText() == 'USA CORS':
                            file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'd.gz'
                            #   https://geodesy.noaa.gov/corsdata/rinex/2021/001/ab13/ab130010.21d.gz
                            download_rinex211o_5s_url = 'https://geodesy.noaa.gov/corsdata/rinex/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + igs211_name + '/' + igs211_name + str(
                                time[3]) + '0.' + str(time[1]) + 'd.gz'
                            list = [download_rinex211o_5s_url, file_name]
                            rinex211o_5s_url_list = rinex211o_5s_url_list + [list]
                            pass
                        elif self.choose_local_area_box.currentText() == 'Japan JPN':
                            igs304_name = igs211_name.upper()
                            file_name = igs304_name + str(time[3]) + '0.' + str(time[1]) + 'p.Z'
                            #   ftp://mgmds01.tksc.jaxa.jp/data/daily/2021/001/ANMG0010.21p.Z
                            download_rinex211o_5s_url = 'ftp://mgmds01.tksc.jaxa.jp/data/daily/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + igs304_name + str(time[3]) + '0.' + str(
                                time[1]) + 'p.Z'
                            list = [download_rinex211o_5s_url, file_name]
                            rinex211o_5s_url_list = rinex211o_5s_url_list + [list]
                            pass

        #  5. HongKong Rinex3.04 1s ； Curtin University  Rinex3.04 OBS ；APREF CORS  Rinex3.04 OBS ;  Enrope EPN _MO.crx ；Spain CORS _MO.crx url
        if self.HK_rinex304_check.isChecked() or self.Curtin_rinex304_check.isChecked() or self.epn_rinex304_check.isChecked() or self.spain_rinex304_check.isChecked():
            if igs_uppercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                return
            else:
                if all_YearAccuDay_Hour:
                    url_time = all_YearAccuDay_Hour
                else:
                    url_time = all_YearAccuDay_GpsWeek
                rinex304o_1s_url_list_temp = []
                for time in url_time:
                    for igs304_name in igs_uppercase:
                        igs_lower_name = igs304_name.lower()
                        if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
                            if self.HK_rinex304_box.currentText() == '1s':
                                file_name = igs304_name + '00HKG_R_' + str(time[0]) + str(time[3]) + time[6] + '00_01H_01S_MO.crx.gz'
                                #  https://rinex.geodetic.gov.hk/rinex3/2021/001/hkoh/1s/HKOH00HKG_R_20210011600_01H_01S_MO.crx.gz
                                url = 'https://rinex.geodetic.gov.hk/rinex3/' + str(time[0]) + '/' + str(time[3]) + '/' + igs_lower_name + '/1s/' + file_name
                                list = [url, file_name]
                                rinex304o_1s_url_list_temp = rinex304o_1s_url_list_temp + [list]
                                pass
                            elif self.HK_rinex304_box.currentText() == '5s':
                                file_name = igs304_name + '00HKG_R_' + str(time[0]) + str(time[3]) + time[6] + '00_01H_05S_MO.crx.gz'
                                #  https://rinex.geodetic.gov.hk/rinex3/2021/001/hkoh/5s/HKOH00HKG_R_20210012100_01H_05S_MO.crx.gz
                                url = 'https://rinex.geodetic.gov.hk/rinex3/' + str(time[0]) + '/' + str(time[3]) + '/' + igs_lower_name + '/5s/' + file_name
                                list = [url, file_name]
                                rinex304o_1s_url_list_temp = rinex304o_1s_url_list_temp + [list]
                                pass
                            elif self.HK_rinex304_box.currentText() == '30s':
                                file_name = igs304_name + '00HKG_R_' + str(time[0]) + str(
                                    time[3]) + '0000_01D_30S_MO.crx.gz'
                                #  https://rinex.geodetic.gov.hk/rinex3/2021/001/hklm/30s/HKLM00HKG_R_20210010000_01D_30S_MO.crx.gz
                                url = 'https://rinex.geodetic.gov.hk/rinex3/' + str(time[0]) + '/' + str(
                                    time[3]) + '/' + igs_lower_name + '/30s/' + file_name
                                list = [url, file_name]
                                rinex304o_30s_url_list = rinex304o_30s_url_list + [list]
                                pass
                        elif self.choose_local_area_box.currentText() == 'Curtin University':
                            file_name = igs304_name + '00AUS_R_' + str(time[0]) + str(
                                time[3]) + '0000_01D_30S_MO.crx.gz'
                            #  http://saegnss2.curtin.edu/ldc/rinex3/daily/2021/001/CUAA00AUS_R_20210010000_01D_30S_MO.crx.gz
                            download_rinex304o_1s_url = 'http://saegnss2.curtin.edu/ldc/rinex3/daily/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + file_name
                            list = [download_rinex304o_1s_url, file_name]
                            rinex304o_1s_url_list = rinex304o_1s_url_list + [list]
                        elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
                            with open(str(curdir) + r'/lib/rinex file name/rinex3.04 file name.txt', 'r') as f:
                                file_name = re.findall(
                                    r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name), f.read())
                                if file_name:
                                    file_name = file_name[0][0:12] + str(time[0]) + str(time[3]) + file_name[0][19:41]
                                    #   sftp.data.gnss.ga.gov.au   /rinex/daily/2022/001/ACOR00ESP_R_20210010000_01D_30S_MO.crx.gz
                                    download_rinex304o_1s_url = '/rinex/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                                    list = [download_rinex304o_1s_url, file_name]
                                    rinex304o_1s_url_list = rinex304o_1s_url_list + [list]
                                else:
                                    print('Not Founding IGS Name !')
                        elif self.choose_local_area_box.currentText() == 'Europe EPN':
                            with open(str(curdir) + r'/lib/rinex file name/rinex3.04 file name.txt', 'r') as f:
                                file_name = re.findall(
                                    r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name), f.read())
                                if file_name:
                                    file_name = file_name[0][0:12] + str(time[0]) + str(time[3]) + file_name[0][19:41]
                                    #  ftp://ftp.epncb.oma.be/pub/obs/2021/001/ACOR00ESP_R_20210010000_01D_30S_MO.crx.gz
                                    download_rinex304o_1s_url = 'ftp://ftp.epncb.oma.be/pub/obs/' + str(
                                        time[0]) + '/' + str(time[3]) + '/' + file_name
                                    list = [download_rinex304o_1s_url, file_name]
                                    rinex304o_1s_url_list = rinex304o_1s_url_list + [list]
                                else:
                                    print('Not Founding IGS Name !')
                        elif self.choose_local_area_box.currentText() == 'Spain CORS':
                            with open(str(curdir) + r'/lib/rinex file name/rinex3.04 file name.txt', 'r') as f:
                                file_name = re.findall(
                                    r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name), f.read())
                                if file_name:
                                    file_name = file_name[0][0:12] + str(time[0]) + str(time[3]) + file_name[0][19:41]
                                    #  http://ftp.itacyl.es/RINEX/diario_30s/2021/003/PEN100ESP_R_20210030000_01D_30S_MO.crx.gz
                                    download_rinex304o_1s_url = 'http://ftp.itacyl.es/RINEX/diario_30s/' + str(
                                        time[0]) + '/' + str(time[3]) + '/' + file_name
                                    list = [download_rinex304o_1s_url, file_name]
                                    rinex304o_1s_url_list = rinex304o_1s_url_list + [list]
                                else:
                                    print('Not Founding IGS Name !')
                for i in rinex304o_1s_url_list_temp:
                    if i not in rinex304o_1s_url_list:
                        rinex304o_1s_url_list.append(i)

        #  6. Curtin University  Rinex3.04 GPS brdc ; APREF CORS Rinex3.04 GPS brdc  url
        if self.Curtin_rinex304_n_check.isChecked():
            if igs_uppercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                return
            else:
                for time in all_YearAccuDay_GpsWeek:
                    for igs304_name in igs_uppercase:
                        with open(str(curdir) + r'/lib/rinex file name/rinex3.04 file name.txt', 'r') as f:
                            file_name = re.findall(
                                r'%s\d{2}\w{3}_\w_\d+_\d{2}\w_\d{2}\w_\w{2}\.\w{3}\.\w+' % (igs304_name), f.read())
                            if file_name:
                                file_name_head = file_name[0][0:12]
                            else:
                                file_name_head = igs304_name + '00AUS_R_'
                        Curtin_n_file_name_suffix = ''
                        if self.Curtin_rinex304_n_box.currentText() == 'Mix':
                            Curtin_n_file_name_suffix = 'MN.rnx.gz'
                        elif self.Curtin_rinex304_n_box.currentText() == 'GPS':
                            Curtin_n_file_name_suffix = 'GN.rnx.gz'
                        elif self.Curtin_rinex304_n_box.currentText() == 'BDS':
                            Curtin_n_file_name_suffix = 'CN.rnx.gz'
                        elif self.Curtin_rinex304_n_box.currentText() == 'GLONASS':
                            Curtin_n_file_name_suffix = 'RN.rnx.gz'
                        elif self.Curtin_rinex304_n_box.currentText() == 'GALILEO':
                            Curtin_n_file_name_suffix = 'EN.rnx.gz'
                        elif self.Curtin_rinex304_n_box.currentText() == 'QZSS':
                            Curtin_n_file_name_suffix = 'JN.rnx.gz'
                        elif self.Curtin_rinex304_n_box.currentText() == 'IRNSS':
                            Curtin_n_file_name_suffix = 'IN.rnx.gz'

                        if self.choose_local_area_box.currentText() == 'Curtin University':
                            file_name = file_name_head + str(time[0]) + str(
                                time[3]) + '0000_01D_' + Curtin_n_file_name_suffix
                            #  http://saegnss2.curtin.edu/ldc/rinex3/daily/2021/001/CUAA00AUS_R_20210010000_01D_GN.rnx.gz
                            download_rinex304o_5s_url = 'http://saegnss2.curtin.edu/ldc/rinex3/daily/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + file_name
                            list = [download_rinex304o_5s_url, file_name]
                            rinex304o_5s_url_list = rinex304o_5s_url_list + [list]
                        elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
                            file_name = file_name_head + str(time[0]) + str(
                                time[3]) + '0000_01D_' + Curtin_n_file_name_suffix
                            #   sftp.data.gnss.ga.gov.au   /rinex/daily/2022/001/ACOR00ESP_R_20210010000_01D_30S_MO.crx.gz
                            download_rinex304o_5s_url = '/rinex/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                            list = [download_rinex304o_5s_url, file_name]
                            rinex304o_5s_url_list = rinex304o_5s_url_list + [list]
            pass

        #  11. USA NGS  brdc(.*n)  ； Enrope EPS _MN.rnx  ； Japan JPN igu(.sp3) url
        if self.ngs_rinex211_n_check.isChecked() or self.epn_rinex304_mn_check.isChecked() or self.Japan_igu_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.choose_local_area_box.currentText() == 'USA CORS':
                    # self.ngs_rinex211_n_check.move(540, 110)
                    # self.ngs_rinex211_n_box.addItems(['GPS', 'GLONASS'])
                    if self.ngs_rinex211_n_box.currentText() == 'GPS':
                        file_name = 'brdc' + str(time[3]) + '0.' + str(time[1]) + 'n.gz'
                    else:
                        file_name = 'brdc' + str(time[3]) + '0.' + str(time[1]) + 'g.gz'
                    #  https://geodesy.noaa.gov/corsdata/rinex/2021/001/brdc0010.21n.gz
                    download_ngs_brdc_gps_url = 'https://geodesy.noaa.gov/corsdata/rinex/' + str(time[0]) + '/' + str(
                        time[3]) + '/' + file_name
                    list = [download_ngs_brdc_gps_url, file_name]
                    tro_url_list = tro_url_list + [list]
                    pass
                elif self.choose_local_area_box.currentText() == 'Europe EPN':
                    file_name = 'BRDC00GOP_R_' + str(time[0]) + str(time[3]) + '0000_01D_MN.rnx.gz'
                    #  ftp://ftp.epncb.oma.be/pub/obs/BRDC/2021/BRDC00GOP_R_20210010000_01D_MN.rnx.gz
                    download_ngs_brdc_gps_url = 'ftp://ftp.epncb.oma.be/pub/obs/BRDC/' + str(
                        time[0]) + '/' + 'BRDC00GOP_R_' + str(time[0]) + str(time[3]) + '0000_01D_MN.rnx.gz'
                    list = [download_ngs_brdc_gps_url, file_name]
                    tro_url_list = tro_url_list + [list]
                    pass
                elif self.choose_local_area_box.currentText() == 'Japan JPN':
                    for i in ['00', '06', '12', '18']:
                        file_name = 'jxu' + str(time[4]) + str(time[5]) + '_' + i + '.sp3.Z'
                        #  ftp://mgmds01.tksc.jaxa.jp/products/2160/jxu21601_00.sp3.Z
                        download_ngs_brdc_gps_url = 'ftp://mgmds01.tksc.jaxa.jp/products/' + str(
                            time[4]) + '/' + file_name
                        list = [download_ngs_brdc_gps_url, file_name]
                        tro_url_list = tro_url_list + [list]
            pass

        #  12. Japan JPN igr(.sp3) ;  HongKong Met Rinex2.11  url
        if self.Japan_igr_check.isChecked() or self.HK_met_rnx211_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.choose_local_area_box.currentText() == 'Japan JPN':
                    file_name = 'jxr' + str(time[4]) + str(time[5]) + '.sp3.Z'
                    #  ftp://mgmds01.tksc.jaxa.jp/products/2160/jxr21603.sp3.Z
                    download_ngs_brdc_glonass_url = 'ftp://mgmds01.tksc.jaxa.jp/products/' + str(
                        time[4]) + '/' + file_name
                    list = [download_ngs_brdc_glonass_url, file_name]
                    ion_url_list = ion_url_list + [list]
                    pass
                #  HongKong  Met Rinex2.11  file
                if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
                    if igs_lowercase == []:
                        self.show_download_process_state.setText('')
                        QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                        return
                    else:
                        for igs211_name in igs_lowercase:
                            file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'm.gz'
                            #  https://rinex.geodetic.gov.hk/rinex2/2021/001/hkws/hkws0010.21m.gz
                            download_ngs_brdc_glonass_url = 'https://rinex.geodetic.gov.hk/rinex2/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + igs211_name + '/' + file_name
                            list = [download_ngs_brdc_glonass_url, file_name]
                            ion_url_list = ion_url_list + [list]

        #  13. Japan JPN igs(.sp3)   ;  HongKong Met Rinex3.xx   ;   APREF Met Rinex3.xx   url
        if self.Japan_igs_check.isChecked() or self.HK_met_rnx304_check.isChecked() or self.APREF_met_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.choose_local_area_box.currentText() == 'Japan JPN':
                    file_name = 'jxf' + str(time[4]) + str(time[5]) + '.sp3.Z'
                    #  ftp://mgmds01.tksc.jaxa.jp/products/2160/jxf21600.sp3.Z
                    download_igu_url = 'ftp://mgmds01.tksc.jaxa.jp/products/' + str(time[4]) + '/' + file_name
                    list = [download_igu_url, file_name]
                    dcb_url_list = dcb_url_list + [list]
                    pass
                #  HongKong  Met Rinex3.xx  file
                elif self.choose_local_area_box.currentText() == 'Hong Kong CORS':
                    if igs_uppercase == []:
                        self.show_download_process_state.setText('')
                        QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                        return
                    else:
                        for igs304_name in igs_uppercase:
                            file_name = igs304_name + '00HKG_R_' + str(time[0]) + str(time[3]) + '0000_01D_MM.rnx.gz'
                            #  https://rinex.geodetic.gov.hk/rinex3/2021/001/hkws/HKWS00HKG_R_20210010000_01D_MM.rnx.gz
                            download_igu_url = 'https://rinex.geodetic.gov.hk/rinex3/' + str(time[0]) + '/' + str(
                                time[3]) + '/' + igs304_name.lower() + '/' + file_name
                            list = [download_igu_url, file_name]
                            dcb_url_list = dcb_url_list + [list]
                #  APREF  Met Rinex3.xx  file
                elif self.choose_local_area_box.currentText() == 'Australia APREF CORS':
                    if igs_uppercase == []:
                        self.show_download_process_state.setText('')
                        QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                        return
                    else:
                        for time in all_YearAccuDay_GpsWeek:
                            for igs304_name in igs_uppercase:
                                igs_lower_name = igs304_name.lower()
                                file_name = igs304_name + '00AUS_R_' + str(time[0]) + str(
                                    time[3]) + '0000_01D_MM.rnx.gz'
                                #   sftp.data.gnss.ga.gov.au   /rinex/daily/2022/001/ACOR00ESP_R_20210010000_01D_30S_MO.crx.gz
                                download_rinex304o_5s_url = '/rinex/daily/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                                list = [download_rinex304o_5s_url, file_name]
                                dcb_url_list = dcb_url_list + [list]
                    pass

        #  14. Japan JPN snx   ;  HongKong Nav Rinex2.11 url
        if self.Japan_snx_check.isChecked() or self.HK_rinex211_n_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.choose_local_area_box.currentText() == 'Japan JPN':
                    file_name = 'jxf' + str(time[4]) + str(time[5]) + '.snx.Z'
                    #  ftp://mgmds01.tksc.jaxa.jp/products/2160/jxf21600.snx.Z
                    download_igr_url = 'ftp://mgmds01.tksc.jaxa.jp/products/' + str(time[4]) + '/' + file_name
                    list = [download_igr_url, file_name]
                    erp_url_list = erp_url_list + [list]
                    pass
                #  HongKong  Nav Rinex2.11
                if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
                    if igs_lowercase == []:
                        self.show_download_process_state.setText('')
                        QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                        return
                    else:
                        for igs211_name in igs_lowercase:
                            if self.HK_rinex211_n_box.currentText() == 'GPS':
                                file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'n.gz'
                            elif self.HK_rinex211_n_box.currentText() == 'GLONASS':
                                file_name = igs211_name + str(time[3]) + '0.' + str(time[1]) + 'g.gz'
                            #  https://rinex.geodetic.gov.hk/rinex2/2021/001/hkws/hkws0010.21n.gz
                            download_ngs_brdc_glonass_url = 'https://rinex.geodetic.gov.hk/rinex2/' + str(
                                time[0]) + '/' + str(time[3]) + '/' + igs211_name + '/' + file_name
                            list = [download_ngs_brdc_glonass_url, file_name]
                            erp_url_list = erp_url_list + [list]

        #  15.  Japan JPN clk,  HongKong Nav Rinex3.xx  url
        if self.Japan_clk_check.isChecked() or self.HK_rinex304_n_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.choose_local_area_box.currentText() == 'Japan JPN':
                    file_name = 'jxf' + str(time[4]) + str(time[5]) + '.clk_30s.Z'
                    #  ftp://mgmds01.tksc.jaxa.jp/products/2160/jxf21601.clk_30s.Z
                    download_igs_url = 'ftp://mgmds01.tksc.jaxa.jp/products/' + str(time[4]) + '/' + file_name
                    list = [download_igs_url, file_name]
                    clk_30s_url_list = clk_30s_url_list + [list]
                    pass
                #  HongKong  Nav Rinex3.xx
                if self.choose_local_area_box.currentText() == 'Hong Kong CORS':
                    if igs_uppercase == []:
                        self.show_download_process_state.setText('')
                        QMessageBox.information(self, 'Tips', 'No CORS stations added!')
                        return
                    else:
                        for igs304_name in igs_uppercase:
                            if self.HK_rinex304_n_box.currentText() == 'GPS':
                                file_name = igs304_name + '00HKG_R_' + str(time[0]) + str(
                                    time[3]) + '0000_01D_GN.rnx.gz'
                            elif self.HK_rinex304_n_box.currentText() == 'BDS':
                                file_name = igs304_name + '00HKG_R_' + str(time[0]) + str(
                                    time[3]) + '0000_01D_CN.rnx.gz'
                            elif self.HK_rinex304_n_box.currentText() == 'GLONASS':
                                file_name = igs304_name + '00HKG_R_' + str(time[0]) + str(
                                    time[3]) + '0000_01D_RN.rnx.gz'
                            elif self.HK_rinex304_n_box.currentText() == 'GALILEO':
                                file_name = igs304_name + '00HKG_R_' + str(time[0]) + str(
                                    time[3]) + '0000_01D_EN.rnx.gz'
                            #  https://rinex.geodetic.gov.hk/rinex3/2021/001/hkws/HKWS00HKG_R_20210010000_01D_GN.rnx.gz
                            download_igu_url = 'https://rinex.geodetic.gov.hk/rinex3/' + str(time[0]) + '/' + str(
                                time[3]) + '/' + igs304_name.lower() + '/' + file_name
                            list = [download_igu_url, file_name]
                            clk_30s_url_list = clk_30s_url_list + [list]

        #  16. Japan JPN fcb url
        if self.Japan_fcb_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.choose_local_area_box.currentText() == 'Japan JPN':
                    file_name = 'jxf' + str(time[4]) + str(time[5]) + '.fcb.Z'
                    #  ftp://mgmds01.tksc.jaxa.jp/products/2160/jxf21601.fcb.Z
                    download_fcb_url = 'ftp://mgmds01.tksc.jaxa.jp/products/' + str(time[4]) + '/' + file_name
                    list = [download_fcb_url, file_name]
                    clk_5s_url_list = clk_5s_url_list + [list]
                    pass

        # Merge list
        combination_url_list = [rinex211o_1s_url_list, rinex211o_5s_url_list, rinex211o_30s_url_list,
                                rinex304o_1s_url_list, rinex304o_5s_url_list, rinex304o_30s_url_list,
                                rinex211n_url_list, rinex304n_url_list, igs_url_list, igu_url_list, igr_url_list,
                                tro_url_list, ion_url_list, dcb_url_list, erp_url_list, clk_30s_url_list,
                                clk_5s_url_list, snx_url_list, obx_url_list]
        target_url_list = []
        for i in combination_url_list:
            if i != []:
                target_url_list = target_url_list + i
        if target_url_list == []:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips', 'No file type selected !')
            return
        print(target_url_list)

        #  Call to download function
        self.data_download(target_url_list)

        # add R/S url download
        failed_url = failed_library
        failed_list = []
        for x in failed_url:
            failed_list.append([x[0].replace('_R_', '_S_'), x[1].replace('_R_', '_S_')])
        if len(failed_list)>0:
            self.data_download(failed_list)

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

        self.show_download_information.setText(
            'Total Tasks:%d  Succeeded:%d  Failed:%d （Time Consumed:%s）   Download completed!' % (
            (len(successful_library) + len(failed_library)), len(successful_library), len(failed_library), used_time))
        self.download_Progress_bar.setValue(int(len(target_url_list)))
        QApplication.processEvents()
        self.show_download_process_state.setText('')
        print('End Download')

    def data_download(self, target_url_list):
        if self.choose_local_area_box.currentText() == 'Australia APREF CORS':
            #  sftp_download_function
            global client,sftp
            client = None
            sftp = None
            try:
                client = paramiko.Transport(('sftp.data.gnss.ga.gov.au', 22))
            except Exception as error:
                print('Sftp connection failed')
            else:
                try:
                    client.connect(username='anonymous', password='l_teamer@163.com')
                except Exception as error:
                    print('Login failed')
                else:
                    sftp = paramiko.SFTPClient.from_transport(client)
            thread_list = locals()
            thread_list_original_length = len(thread_list)
            for i, j in zip(target_url_list, range(len(target_url_list))):
                download_ftp_function = threading.Thread(target=self.sftp_download_function, args=(i[0], i[1]))
                thread_list['thread_' + str(j)] = []
                thread_list['thread_' + str(j)].append(download_ftp_function)
                pass
            ftp_list_length = len(thread_list) - thread_list_original_length
            # self.download_Progress_bar.setValue(0)
            self.download_Progress_bar.setRange(0, int(ftp_list_length))
            QApplication.processEvents()
            for j in range(ftp_list_length):
                thread_list['thread_' + str(j)][0].start()
            for j in range(ftp_list_length):
                thread_list['thread_' + str(j)][0].join()
            client.close()
            self.download_Progress_bar.setValue(int(ftp_list_length))
        else:
            #  ftp_download_function
            thread_list = locals()
            thread_list_original_length = len(thread_list)
            s = requests.Session()
            for i, j in zip(target_url_list, range(len(target_url_list))):
                download_ftp_function = threading.Thread(target=self.ftp_download_function, args=(i[0], i[1], s))
                download_ftp_function.setDaemon(True)
                thread_list['thread_' + str(j)] = []
                thread_list['thread_' + str(j)].append(download_ftp_function)
                pass
            ftp_list_length = len(thread_list) - thread_list_original_length
            # self.download_Progress_bar.setValue(0)
            self.download_Progress_bar.setRange(0, int(ftp_list_length))
            QApplication.processEvents()
            for j in range(ftp_list_length):
                thread_list['thread_' + str(j)][0].start()
            for j in range(ftp_list_length):
                thread_list['thread_' + str(j)][0].join()
            self.download_Progress_bar.setValue(int(ftp_list_length))



    def wgetm(self, x):
        if self.choose_local_area_box.currentText() == 'Australia APREF CORS':
            x1 = x.split('/')[-1]
            dirname = os.path.dirname(os.path.abspath(__file__))
            wget = os.path.join(dirname, 'lib/download', 'curl.exe')
            wget += " -u anonymous:l_teamer@163.com "
            url = 'sftp://sftp.data.gnss.ga.gov.au/' + x
            cmd = wget + ' -o ' + 'C:/Users/Admin/Desktop/Download/data/o/' + x1 + ' ' + url
            os.system(cmd)
        else:
            pass

    def data_download_h(self, target_url_list):
        from multiprocessing.pool import ThreadPool
        for typeurl in target_url_list:
            pool = ThreadPool(5)
            pool.map(self.wgetm, typeurl)
            pool.close()
            pool.join()




    # help document
    def open_download_help_file_but_line(self):
        self.s = open_download_help_file_windows01()
        self.s.show()
        pass

    # Download details
    def download_details_report_view(self):
        self.s = download_details_report_main01(successful_library, failed_library)
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
        self.move(200 / 1920 * win_width, 60 / 1080 * win_height)
        self.setFixedSize(1400 / 1920 * win_width, 800 / 1080 * win_height)
        self.setup_ui(success, fail)

    def setup_ui(self, success, fail):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        print(success)
        print(fail)
        self.show_text = QTextEdit(self)
        self.show_text.setGeometry(0, 0, 1400 / 1920 * win_width, 800 / 1080 * win_height)
        all = len(success) + len(fail)

        self.show_text.append('Download Details')
        self.show_text.append('Total Tasks:%d  Succeeded:%d  Failed:%d' % (all, len(success), len(fail)))
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
            self.show_text.append(
                '1. Reasons for the failure to download observation files: data lag (the observation file is delayed 12-24 hours), IGS station suspension of service (for some reason, the selected IGS station suspends the observation of this day, resulting in data loss); ')
            self.show_text.append(
                '2. The reason for the failure to download the Navigation: the lag of the data (the Navigation of version 2.11 has a delay of 12-24 hours, and the Navigation of version 3.04 has a delay of 1-2 days). Please select the appropriate Navigation according to the time. File type to download; ')
            self.show_text.append(
                '3. Reason for failure of downloading precision ephemeris: data lag (IGU delay 3-9 hours, IGR delay 17-41 hours, IGS delay 12-18 days), please select the appropriate precision ephemeris file type according to the time To download. ')
            self.show_text.append('\n')
        pass

# -------------------------------------------------------------------------------------------------
""" explain gui """
class open_download_help_file_windows01(QMainWindow):
    def __init__(self):
        super().__init__()
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        self.setGeometry(250/1920*win_width, 60/1080*win_height, 1420/1920*win_width, 900/1080*win_height)
        curdir = os.getcwd()
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setWindowTitle("Help")
        self.browser = QWebEngineView()
        url = str(curdir) + r'/tutorial/GDDS User Manual.html'
        self.browser.setUrl(QUrl.fromLocalFile(url))
        # self.browser.load(QUrl(QFileInfo("./tutorial/GDDS User Manual.html").absoluteFilePath()))
        # self.browser.load(QUrl('https://docs.zohopublic.com.cn/file/41qmpeedee87ec45b40848137193890b5b5ad'))
        self.setCentralWidget(self.browser)

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
        self.setGeometry(360 / 1920 * win_width, 105 / 1080 * win_height, 1250 / 1920 * win_width,
                         870 / 1080 * win_height)
        self.browser = QWebEngineView()
        url = str(curdir) + r'/templates/TempDisplayMapTemplate02.html'
        self.browser.setUrl(QUrl.fromLocalFile(url))
        # self.browser.load(QUrl(QFileInfo("./templates/TempDisplayMapTemplate02.html").absoluteFilePath()))
        self.setCentralWidget(self.browser)

# -------------------------------------------------------------------------------------------------
""" Return to map gui """
class Return_Map_Names(QMainWindow):
    def __init__(self, route):
        super().__init__()
        self.setWindowTitle("CORS-Stations Map")
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
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
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        self.resize(1250/1920*win_width, 870/1080*win_height)
        # gride = QGridLayout(self)

        # self.setGeometry(360 / 1920 * win_width, 105 / 1080 * win_height, 1250 / 1920 * win_width, 870 / 1080 * win_height)
        # self.setGeometry(400, 80, 1250, 870)
        self.browser = QWebEngineView()
        kwargs = {'host': '127.0.0.1', 'port': '5000', 'threaded': True, 'use_reloader': False, 'debug': False}
        host = kwargs['host']
        port = kwargs['port']
        url = 'http://' + host + ":" + port + route
        self.browser.load(QUrl(url))
        # self.setCentralWidget(self.browser)

        widget = QWidget()
        gride = QGridLayout()
        widget.setLayout(gride)
        self.setCentralWidget(widget)

        self.sure_submit_btn = QPushButton(self)
        self.sure_submit_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.sure_submit_btn.setStyleSheet("QPushButton{border-image: url(':/icon/OKsubmit.jpg')}")
        # self.sure_submit_btn.setFlat(True)
        # self.sure_submit_btn.setGeometry(298/1920*win_width, 751/1080*win_height, 105/1920*win_width, 47/1920*win_width)
        # self.sure_submit_btn.setGeometry(1030 / 1920 * win_width, 70 / 1080 * win_height, 105/1080*win_height, 46/1080*win_height)
        # self.sure_submit_btn.move(1030/1920*win_width, 70/1080*win_height)

        gride.addWidget(self.browser, 0, 0, 45, 45)
        gride.addWidget(self.sure_submit_btn, 5, 41, 2, 3)
        self.setLayout(gride)
        self.sure_submit_btn.clicked.connect(self.view_close_function)

    def view_close_function(self):
        self.sendEditContent()
        self.close()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    # kwargs = {'host': '127.0.0.1', 'port': '5000', 'threaded': True, 'use_reloader': False, 'debug': False}
    # threading.Thread(target=app1.run, daemon=True, kwargs=kwargs).start()
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
    win = CORS_data_Download()
    win.show()
    sys.exit(app.exec_())