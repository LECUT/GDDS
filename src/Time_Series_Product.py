from PyQt5.Qt import *
from PyQt5 import QtGui
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QIcon
import gnsscal
from datetime import *
from time import sleep
import re
import requests
import requests_ftp
from bs4 import BeautifulSoup
import _thread as thread
import threading
import os
import json
from func_timeout import func_set_timeout
from retrying import retry
import gzip
import unlzw3
import shutil
from pathlib import Path
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QLocale
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from flask import Flask, render_template, request
import resources_rc
from station_info_table import *
# import global_var

JD = 3.21
MJD = 1.23


################### UI  ####################
global curdir
curdir = os.getcwd()
class Time_Serise_Download(QWidget):
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
        global_var._init()
        self.setWindowTitle('Time Series Product')
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        if win_width <= 720:
            if win_height <= 450:
                self.setFixedSize(1045/1280*win_width, 900/1080*win_height)
            elif win_height <= 480:
                self.setFixedSize(1045/1150*win_width, 900/1080*win_height)
            elif win_height <= 500:
                self.setFixedSize(1045/1450*win_width, 835/1080*win_height)
            elif win_height <= 512:
                self.setFixedSize(1045/1150*win_width, 900/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(1045/1150*win_width, 805/1080*win_height)
            else:
                self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        elif win_width <= 800 and win_width > 720:
            if win_height <= 500:
                self.setFixedSize(1045/1320*win_width, 905/1080*win_height)
            elif win_height <= 515:
                self.setFixedSize(1045/1460*win_width, 890/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(1045/1080*win_width, 880/1080*win_height)
            self.move((screen.width() - 935/1040*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 840 and win_width > 800:
            self.setFixedSize(1045/1300*win_width, 890/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 830/1080*win_height)/2)
        elif win_width <= 960 and win_width > 840:
            if win_height <= 550:
                self.setFixedSize(1045/1460*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 600:
                self.setFixedSize(1045/1460*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 720:
                self.setFixedSize(1045/1140*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            else:
                self.setFixedSize(1045/1740*win_width, 880/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1024 and win_width > 960:
            self.setFixedSize(1045/1150*win_width, 870/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1152 and win_width > 1024:
            self.setFixedSize(1045/1300*win_width, 850/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1176 and win_width > 1152:
            self.setFixedSize(1045/1350*win_width, 870/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1280 and win_width > 1176:
            self.setFixedSize(1045/1435*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1320*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1366 and win_width > 1280:
            self.setFixedSize(1045/1550*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1440 and win_width > 1366:
            self.setFixedSize(1045/1620*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1600 and win_width > 1440:
            self.setFixedSize(1045/1800*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1420*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1680 and win_width > 1600:
            self.setFixedSize(1045/1800*win_width, 800/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 1792 and win_width > 1680:
            self.setFixedSize(1045/1820*win_width, 810/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 2048 and win_width > 1920:
            self.setFixedSize(1045/1920*win_width, 810/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)
        elif win_width <= 2560 and win_width > 2048:
            self.setFixedSize(1045/1920*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)
        else:
            self.setFixedSize(1025/1920*win_width, 820/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)

        size = self.geometry()
        self.move((screen.width() - 1030 / 1920 * win_width) / 2, (screen.height() - 880 / 1080 * win_height) / 2)

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

        self.choose_local_area_label = QLabel('Data Source  :', self)
        self.choose_local_area_label.setFont(QFont("Times New Roman"))
        self.choose_local_area_label.setGeometry(35 / 1920 * win_width, 30 / 1080 * win_height, 400 / 1920 * win_width,
                                                 30 / 1080 * win_height)

        self.choose_local_area_box = QComboBox(self)
        self.choose_local_area_box.setGeometry(190 / 1920 * win_width, 29 / 1080 * win_height, 265 / 1920 * win_width,
                                               35 / 1080 * win_height)
        self.choose_local_area_box.addItems(['EQDSC(China)', 'NGL(USA)', 'SOPAC(USA)', 'UNAVCO(USA)', 'IERS'])
        self.choose_local_area_box.currentTextChanged.connect(self.local_area_changed)

        self.tips_btn = QPushButton(self)
        self.tips_btn.setGeometry(510 / 1920 * win_width, 32 / 1080 * win_height, 54 / 1920 * win_width,
                                   27 / 1080 * win_height)
        self.tips_btn.setStyleSheet("QPushButton{border-image: url(':/icon/tips.png')}")
        self.tips_btn.clicked.connect(self.tips_info_links)

        self.choose_download_files_type_label = QLabel('File Type :', self)
        self.choose_download_files_type_label.setFont(QFont("Times New Roman"))
        self.choose_download_files_type_label.setGeometry(35 / 1920 * win_width, 125 / 1080 * win_height,
                                                          400 / 1920 * win_width, 30 / 1080 * win_height)

        ##                   *              EQDSC          starting            *              ##
        ##                   *              EQDSC          starting            *              ##
        # 大框
        self.ced_label_OBS02_windows = QLabel(self)
        self.ced_label_OBS02_windows.setGeometry(190 / 1920 * win_width, 95 / 1080 * win_height, 740 / 1920 * win_width,
                                                 75 / 1080 * win_height)
        self.ced_label_OBS02_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.ced_label_OBS02_windows.setFrameShape(QFrame.Box)
        self.ced_label_OBS02_windows.setFrameShadow(QFrame.Raised)
        # 小框
        self.ced_label_OBS02_name = QLabel(self)
        self.ced_label_OBS02_name.move(500 / 1920 * win_width, 89 / 1080 * win_height)
        self.ced_label_OBS02_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.ced_label_OBS02_name.setText('  Time Series  ')
        self.ced_label_OBS02_name.setFont(QFont('Times New Roman'))

        self.ced_raw_data_check = QCheckBox(self)
        self.ced_raw_data_check.move(225 / 1920 * win_width, 130 / 1080 * win_height)

        self.ced_raw_data_box = QComboBox(self)
        self.ced_raw_data_box.setGeometry(248 / 1920 * win_width, 127 / 1080 * win_height, 90 / 1920 * win_width,
                                            25 / 1080 * win_height)
        self.ced_raw_data_box.addItems(['Rapid', 'Precision'])

        self.ced_raw_data_label = QLabel('Origin_Time Series(.txt)', self)
        self.ced_raw_data_label.move(345 / 1920 * win_width, 130 / 1080 * win_height)

        
        self.ced_deal_data_check = QCheckBox(self)
        self.ced_deal_data_check.move(580 / 1920 * win_width, 130 / 1080 * win_height)

        self.ced_deal_data_box = QComboBox(self)
        self.ced_deal_data_box.setGeometry(603 / 1920 * win_width, 127 / 1080 * win_height, 90 / 1920 * win_width,
                                            25 / 1080 * win_height)
        self.ced_deal_data_box.addItems(['Rapid', 'Precision'])

        self.ced_deal_data_label = QLabel('Removal of Linear_Time Series(.txt)', self)
        self.ced_deal_data_label.move(700 / 1920 * win_width, 130 / 1080 * win_height)

        # self.ced_label_OBS02_windows.setVisible(False)
        # self.ced_label_OBS02_name.setVisible(False)
        # self.ced_raw_data_check.setVisible(False)
        # self.ced_raw_data_box.setVisible(False)
        # self.ced_raw_data_label.setVisible(False)
        # self.ced_deal_data_check.setVisible(False)
        # self.ced_deal_data_box.setVisible(False)
        # self.ced_deal_data_label.setVisible(False)

        ##                   *              NGL          starting            *              ##
        ##                   *              NGL          starting            *              ##
        #
        self.nevada_label_OBS01_windows = QLabel(self)
        self.nevada_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 95 / 1080 * win_height, 800 / 1920 * win_width,
                                                 75 / 1080 * win_height)
        self.nevada_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.nevada_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.nevada_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        #
        self.nevada_label_OBS01_name = QLabel(self)
        self.nevada_label_OBS01_name.move(520 / 1920 * win_width, 89 / 1080 * win_height)
        self.nevada_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.nevada_label_OBS01_name.setText('  Time Series  ')
        self.nevada_label_OBS01_name.setFont(QFont('Times New Roman'))
        #  enu
        self.nevada_enu_check = QCheckBox('IGS14_ENU(.tenv3)', self)
        self.nevada_enu_check.move(220 / 1920 * win_width, 130 / 1080 * win_height)
        #  xyz
        self.nevada_xyz_check = QCheckBox('IGS14_XYZ(.txyz2)', self)
        self.nevada_xyz_check.move(469 / 1920 * win_width, 130 / 1080 * win_height)
        #  plot
        self.nevada_plot_check = QCheckBox('IGS14_Time Series Analysis(.png)', self)
        self.nevada_plot_check.move(720 / 1920 * win_width, 130 / 1080 * win_height)

        self.nevada_label_OBS01_windows.setVisible(False)
        self.nevada_label_OBS01_name.setVisible(False)
        self.nevada_enu_check.setVisible(False)
        self.nevada_xyz_check.setVisible(False)
        self.nevada_plot_check.setVisible(False)

        ##                   *              SOPAC          starting            *              ##
        ##                   *              SOPAC          starting            *              ##
        #
        self.sopac_label_OBS01_windows = QLabel(self)
        self.sopac_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 105 / 1080 * win_height,
                                                 380 / 1920 * win_width, 60 / 1080 * win_height)
        self.sopac_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.sopac_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.sopac_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        #
        self.sopac_label_OBS01_name = QLabel(self)
        self.sopac_label_OBS01_name.move(320 / 1920 * win_width, 99 / 1080 * win_height)
        self.sopac_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.sopac_label_OBS01_name.setText('  Time Series  ')
        self.sopac_label_OBS01_name.setFont(QFont('Times New Roman'))

        self.sopac_comb_input_check = QCheckBox(self)
        self.sopac_comb_input_check.move(240 / 1920 * win_width, 130 / 1080 * win_height)

        self.sopac_comb_input_box = QComboBox(self)
        self.sopac_comb_input_box.setGeometry(263 / 1920 * win_width, 127 / 1080 * win_height, 90 / 1920 * win_width,
                                            25 / 1080 * win_height)
        self.sopac_comb_input_box.addItems(['sopac', 'comb', 'jpl'])

        self.sopac_comb_input_label = QLabel('Combine_Time Series(.tar)', self)
        self.sopac_comb_input_label.move(360 / 1920 * win_width, 130 / 1080 * win_height)

        self.sopac_label_OBS01_windows.setVisible(False)
        self.sopac_label_OBS01_name.setVisible(False)
        self.sopac_comb_input_check.setVisible(False)
        self.sopac_comb_input_box.setVisible(False)
        self.sopac_comb_input_label.setVisible(False)

        ##                   *              UNAVCO          starting            *              ##
        ##                   *              UNAVCO          starting            *              ##
        #
        self.unavco_label_OBS01_windows = QLabel(self)
        self.unavco_label_OBS01_windows.setGeometry(190 / 1920 * win_width, 105 / 1080 * win_height,
                                                   560 / 1920 * win_width, 70 / 1080 * win_height)
        self.unavco_label_OBS01_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.unavco_label_OBS01_windows.setFrameShape(QFrame.Box)
        self.unavco_label_OBS01_windows.setFrameShadow(QFrame.Raised)
        #
        self.unavco_label_OBS01_name = QLabel(self)
        self.unavco_label_OBS01_name.move(400 / 1920 * win_width, 99 / 1080 * win_height)
        self.unavco_label_OBS01_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.unavco_label_OBS01_name.setText('  Time Series  ')
        self.unavco_label_OBS01_name.setFont(QFont('Times New Roman'))
        #  ITRF 2008
        self.unavco_itrf08_check = QCheckBox('ITRF_2008(.txt)', self)
        self.unavco_itrf08_check.move(240 / 1920 * win_width, 135 / 1080 * win_height)
        #  ITRF 2014
        self.unavco_itrf14_check = QCheckBox('ITRF_2014(.txt)', self)
        self.unavco_itrf14_check.move(490 / 1920 * win_width, 135 / 1080 * win_height)

        self.unavco_label_OBS01_windows.setVisible(False)
        self.unavco_label_OBS01_name.setVisible(False)
        self.unavco_itrf08_check.setVisible(False)
        self.unavco_itrf14_check.setVisible(False)

        ##                   *              IERS          starting            *              ##
        ##                   *              IERS          starting            *              ##
        #
        self.iers_label_OBS02_windows = QLabel(self)
        self.iers_label_OBS02_windows.setGeometry(190 / 1920 * win_width, 95 / 1080 * win_height, 500 / 1920 * win_width,
                                                 75 / 1080 * win_height)
        self.iers_label_OBS02_windows.setStyleSheet('''QWidget{border:1px solid #5F92B2;border-radius:5px;}''')
        self.iers_label_OBS02_windows.setFrameShape(QFrame.Box)
        self.iers_label_OBS02_windows.setFrameShadow(QFrame.Raised)
        #
        self.iers_label_OBS02_name = QLabel(self)
        self.iers_label_OBS02_name.move(390 / 1920 * win_width, 89 / 1080 * win_height)
        self.iers_label_OBS02_name.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);color:navy;}''')
        self.iers_label_OBS02_name.setText('  Time Series  ')
        self.iers_label_OBS02_name.setFont(QFont('Times New Roman'))

        self.iers_data_check = QCheckBox(self)
        self.iers_data_check.move(225 / 1920 * win_width, 130 / 1080 * win_height)

        self.iers_itrf_box = QComboBox(self)
        self.iers_itrf_box.setGeometry(248 / 1920 * win_width, 127 / 1080 * win_height, 120 / 1920 * win_width,
                                          25 / 1080 * win_height)
        self.iers_itrf_box.addItems(['ITRF 2020', 'ITRF 2014', 'ITRF 2008'])
        self.iers_itrf_box.currentTextChanged.connect(self.iers_map_show_change)

        self.iers_technique_box = QComboBox(self)
        self.iers_technique_box.setGeometry(372 / 1920 * win_width, 127 / 1080 * win_height, 90 / 1920 * win_width,
                                          25 / 1080 * win_height)
        self.iers_technique_box.addItems(['GNSS', 'SLR', 'VLBI', 'DORIS'])
        self.iers_technique_box.currentTextChanged.connect(self.iers_map_show_change)

        self.iers_raw_data_label = QLabel('ENU residue_Time Series(.dat)', self)
        self.iers_raw_data_label.move(466 / 1920 * win_width, 130 / 1080 * win_height)

        self.iers_label_OBS02_windows.setVisible(False)
        self.iers_label_OBS02_name.setVisible(False)
        self.iers_data_check.setVisible(False)
        self.iers_itrf_box.setVisible(False)
        self.iers_technique_box.setVisible(False)
        self.iers_raw_data_label.setVisible(False)


        self.choose_start_end_time_label = QLabel('Time Range :', self)
        self.choose_start_end_time_label.setFont(QFont("Times New Roman"))
        self.choose_start_end_time_label.setGeometry(35 / 1920 * win_width, 245 / 1080 * win_height,
                                                     400 / 1920 * win_width, 30 / 1080 * win_height)

        #  YearMonDay 01
        self.YearMonDay_label0101 = QLabel('Year-Month-Day :', self)
        self.YearMonDay_label0101.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0101.move(200 / 1920 * win_width, 225 / 1080 * win_height)
        ## start_time
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        # self.start_time.setLocale(QLocale(QLocale.English))
        self.start_time.setGeometry(360 / 1920 * win_width, 218 / 1080 * win_height, 170 / 1920 * win_width,
                                    30 / 1080 * win_height)
        self.start_time.setDisplayFormat('yyyy-MM-dd HH')
        self.start_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.start_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.start_time.setCalendarPopup(True)
        self.start_time.dateChanged.connect(self.onDateChanged01)
        #  YearMonDay01
        self.YearMonDay_label0102 = QLabel('Year, Day of Year :', self)
        self.YearMonDay_label0102.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0102.move(200 / 1920 * win_width, 260 / 1080 * win_height)
        #  year
        self.changday0201 = QLineEdit(self)
        self.changday0201.setGeometry(360 / 1920 * win_width, 253 / 1080 * win_height, 95 / 1920 * win_width,
                                      30 / 1080 * win_height)
        #  doy
        self.changday0202 = QLineEdit(self)
        self.changday0202.setGeometry(465 / 1920 * win_width, 253 / 1080 * win_height, 65 / 1920 * win_width,
                                      30 / 1080 * win_height)
        self.changday0201.textEdited.connect(self.YearAcumulateDay_to_all01)
        self.changday0202.textEdited.connect(self.YearAcumulateDay_to_all01)

        #  GPS week
        self.YearMonDay_label0103 = QLabel('GPS Week, Day of Week :', self)
        self.YearMonDay_label0103.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0103.move(200 / 1920 * win_width, 296 / 1080 * win_height)
        #  week
        self.changday0301 = QLineEdit(self)
        self.changday0301.setGeometry(360 / 1920 * win_width, 288 / 1080 * win_height, 95 / 1920 * win_width,
                                      30 / 1080 * win_height)
        #  day of week
        self.changday0302 = QLineEdit(self)
        self.changday0302.setGeometry(465 / 1920 * win_width, 288 / 1080 * win_height, 65 / 1920 * win_width,
                                      30 / 1080 * win_height)
        self.changday0301.textEdited.connect(self.GPSweeks_to_all01)
        self.changday0302.textEdited.connect(self.GPSweeks_to_all01)

        #  start time
        time_yearmothday = self.start_time.text()
        year = int(time_yearmothday[0:4])
        mon = int(str(time_yearmothday[5:7]))
        day = int(str(time_yearmothday[8:10]))
        conbin_date = date(year, mon, day)
        #  julian to year and doy
        year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
        self.changday0201.setText(str(year_accumulate_list[0]))
        self.changday0202.setText(str(year_accumulate_list[1]))
        #  julian to week and day of week
        GPS_weeks = gnsscal.date2gpswd(conbin_date)
        self.changday0301.setText(str(GPS_weeks[0]))
        self.changday0302.setText(str(GPS_weeks[1]))

        self.time_start_to_end = QLabel('>>>', self)
        self.time_start_to_end.move(588 / 1920 * win_width, 262 / 1080 * win_height)

        # end time
        self.end_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        # self.end_time.setLocale(QLocale(QLocale.English))
        self.end_time.setGeometry(680 / 1920 * win_width, 218 / 1080 * win_height, 170 / 1920 * win_width,
                                  30 / 1080 * win_height)
        self.end_time.setDisplayFormat('yyyy-MM-dd HH')
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
        # GPS week
        self.changday0501 = QLineEdit(self)
        self.changday0501.setGeometry(680 / 1920 * win_width, 288 / 1080 * win_height, 95 / 1920 * win_width,
                                      30 / 1080 * win_height)
        # day of week
        self.changday0502 = QLineEdit(self)
        self.changday0502.setGeometry(785 / 1920 * win_width, 288 / 1080 * win_height, 65 / 1920 * win_width,
                                      30 / 1080 * win_height)
        self.changday0501.textEdited.connect(self.GPSweeks_to_all02)
        self.changday0502.textEdited.connect(self.GPSweeks_to_all02)

        # initial end time
        time_yearmothday = self.end_time.text()
        year = int(time_yearmothday[0:4])
        mon = int(str(time_yearmothday[5:7]))
        day = int(str(time_yearmothday[8:10]))
        conbin_date = date(year, mon, day)
        # julian to year and doy
        year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
        self.changday0401.setText(str(year_accumulate_list[0]))
        self.changday0402.setText(str(year_accumulate_list[1]))
        # julian to week and day of week
        GPS_weeks = gnsscal.date2gpswd(conbin_date)
        self.changday0501.setText(str(GPS_weeks[0]))
        self.changday0502.setText(str(GPS_weeks[1]))

        self.start_time.setEnabled(False)
        self.changday0201.setEnabled(False)
        self.changday0202.setEnabled(False)
        self.changday0301.setEnabled(False)
        self.changday0302.setEnabled(False)
        self.end_time.setEnabled(False)
        self.changday0401.setEnabled(False)
        self.changday0402.setEnabled(False)
        self.changday0501.setEnabled(False)
        self.changday0502.setEnabled(False)

        ########        ****        sation select    starting         ****         ##########
        self.choose_IGS_station111w_label = QLabel('GNSS Station :', self)
        self.choose_IGS_station111w_label.setFont(QFont("Times New Roman"))
        self.choose_IGS_station111w_label.setGeometry(35 / 1920 * win_width, 450 / 1080 * win_height,
                                                      400 / 1920 * win_width, 30 / 1080 * win_height)

        self.choose_add_station_list_box = QComboBox(self)
        self.choose_add_station_list_box.setGeometry(210 / 1920 * win_width, 352 / 1080 * win_height,
                                                     210 / 1920 * win_width, 31 / 1080 * win_height)
        self.choose_add_station_list_box.addItems(['All Station'])

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
                                          30 / 1080 * win_height)
        self.search_igs_label.textChanged.connect(self.Search_text_changed)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(':/icon/magnifier.ico'))
        self.search_igs_label.addAction(station_search_icon, QLineEdit.LeadingPosition)

        self.choose_Option_display = QListWidget(self)
        self.choose_Option_display.setGeometry(210 / 1920 * win_width, 410 / 1080 * win_height, 210 / 1920 * win_width,
                                               180 / 1080 * win_height)
        # initial info
        self.stations_json_text = json.load(open(str(curdir) + r'/lib/json/TimeSerise_Stations.json', encoding='utf-8'))
        Files = self.stations_json_text[0]
        self.stations_coordinate_json_text = json.load(open(str(curdir) + r'/lib/json/TimeSerise_Stations_Coordinate.json', encoding='utf-8'))

        global_var.set_value('CORS_current_view_station_list', Files)
        for item1 in Files:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.choose_Option_display.addItem(item)

        self.btnAddItems_map = QPushButton('Map Choose', self)
        self.btnAddItems_map.clicked.connect(self.add_map_Items)
        self.btnAddItems_map.setGeometry(442 / 1920 * win_width, 352 / 1080 * win_height, 210 / 1920 * win_width,
                                         35 / 1080 * win_height)

        self.btnPrintItems = QPushButton('Add Station', self)
        self.btnPrintItems.setGeometry(442 / 1920 * win_width, 420 / 1080 * win_height, 210 / 1920 * win_width,
                                       35 / 1080 * win_height)
        self.btnPrintItems.clicked.connect(self.add_igs_Items_function)

        self.stationDisplay = QPushButton('Map Display', self)
        self.stationDisplay.setGeometry(442 / 1920 * win_width, 489 / 1080 * win_height, 210 / 1920 * win_width,
                                        35 / 1080 * win_height)
        self.stationDisplay.clicked.connect(self.station_map_display_function)

        self.btnClearStation = QPushButton('Clear Station', self)
        self.btnClearStation.setGeometry(442 / 1920 * win_width, 555 / 1080 * win_height, 210 / 1920 * win_width,
                                         35 / 1080 * win_height)
        self.btnClearStation.clicked.connect(self.clear_added_station_function)

        self.igs_names_display_label = QLabel('Added 0 Station', self)
        self.igs_names_display_label.setGeometry(679 / 1920 * win_width, 352 / 1080 * win_height,
                                                 212 / 1920 * win_width, 30 / 1080 * win_height)
        self.igs_names_display_label.setFrameShape(QFrame.Box)
        self.igs_names_display_label.setFrameShadow(QFrame.Raised)

        self.igs_names_display = QTextEdit(self)
        self.igs_names_display.setPlaceholderText('1lsu\nab14\nALhc\nNDFA')
        self.igs_names_display.setGeometry(680 / 1920 * win_width, 380 / 1080 * win_height, 210 / 1920 * win_width,
                                           210 / 1080 * win_height)
        self.igs_names_display.textChanged.connect(self.added_station_view_link)


        self.show_map_label = QLabel(self)
        self.show_map_label.setGeometry(186 / 1920 * win_width, 348 / 1080 * win_height, 738 / 1920 * win_width, 246 / 1080 * win_height)
        self.show_map_label.setFrameShape(QFrame.Box)
        self.show_map_label.setFrameShadow(QFrame.Raised)

        self.show_map_view = QWebEngineView(self)
        # self.show_map_view.load(QUrl(QFileInfo("./templates/Time_Serises/IERS_itrf2008.html").absoluteFilePath()))
        self.show_map_view.setGeometry(190 / 1920 * win_width, 352 / 1080 * win_height, 730 / 1920 * win_width, 238 / 1080 * win_height)

        self.show_map_label.setVisible(False)
        self.show_map_view.setVisible(False)
        ########        ****        sation select    Ending          ****         ##########

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
        self.choose_outsave_files_path_button.setGeometry(935 / 1920 * win_width, 621 / 1080 * win_height,
                                                          45 / 1920 * win_width, 30 / 1080 * win_height)
        self.choose_outsave_files_path_button.clicked.connect(self.save_download_files_path_function)

        #  Download
        self.igs_name_sure_but = QPushButton('Download', self)
        self.igs_name_sure_but.setFont(QFont("Times New Roman"))
        self.igs_name_sure_but.setGeometry(90 / 1920 * win_width, 670 / 1080 * win_height, 120 / 1920 * win_width,
                                           40 / 1080 * win_height)
        self.igs_name_sure_but.clicked.connect(self.data_download_function02)

        #  detail
        self.download_details_report_but = QPushButton('Detail', self)
        self.download_details_report_but.setFont(QFont("Times New Roman"))
        self.download_details_report_but.setGeometry(337 / 1920 * win_width, 670 / 1080 * win_height,
                                                     120 / 1920 * win_width, 40 / 1080 * win_height)
        self.download_details_report_but.clicked.connect(self.download_details_report_view)

        #  content
        self.open_have_download_file_path_but = QPushButton('Open', self)
        self.open_have_download_file_path_but.setFont(QFont("Times New Roman"))
        self.open_have_download_file_path_but.setGeometry(579 / 1920 * win_width, 670 / 1080 * win_height,
                                                          120 / 1920 * win_width, 40 / 1080 * win_height)
        self.open_have_download_file_path_but.clicked.connect(self.open_have_download_path)

        #  detail
        self.open_help_file_but = QPushButton('Help', self)
        self.open_help_file_but.setFont(QFont("Times New Roman"))
        self.open_help_file_but.setGeometry(810 / 1920 * win_width, 670 / 1080 * win_height, 120 / 1920 * win_width,
                                            40 / 1080 * win_height)
        self.open_help_file_but.clicked.connect(self.open_download_help_file_but_line)

        #  tips
        self.show_download_information = QLabel(self)
        self.show_download_information.move(55 / 1920 * win_width, 710 / 1080 * win_height)
        self.show_download_information.setFixedSize(800 / 1920 * win_width, 35 / 1080 * win_height)
        # self.show_download_information.setText('总Download任务:32  成功:22  失败:10 （耗时:10分32秒）')
        self.show_download_process_state = QLabel(self)
        self.show_download_process_state.setGeometry(493 / 1920 * win_width, 710 / 1080 * win_height,
                                                     260 / 1920 * win_width, 35 / 1080 * win_height)

        # progress bar
        self.download_Progress_bar = QProgressBar(self)
        self.download_Progress_bar.setGeometry(50 / 1920 * win_width, 745 / 1080 * win_height, 960 / 1920 * win_width,
                                               40 / 1080 * win_height)
        self_step = 0
        self.download_Progress_bar.setValue(self_step)


    def tips_info_links(self):
        if self.choose_local_area_box.currentText() == 'SOPAC(USA)':
            QMessageBox.information(self, 'Prompt', 'The data source provides time series data of multiple stations at a particular time, and the specific station can see the distribution of the GNSS station map!')
        elif self.choose_local_area_box.currentText() == 'IERS':
            QMessageBox.information(self, 'prompt', 'The data source provides ENU residual time series data of multiple stations. The specific station can see the distribution of the GNSS station map, and there is no need to set the time range!')
        else:
            QMessageBox.information(self, 'prompt', 'The data source provides time series data of a single station in a long time range without setting the time range!')
        pass


    def iers_map_show_change(self):
        if self.iers_itrf_box.currentText() == 'ITRF 2008':
            map_show_name = 'IERS_itrf2008.html'
        elif self.iers_itrf_box.currentText() == 'ITRF 2014':
            if self.iers_technique_box.currentText() == 'GNSS':
                map_show_name = 'IERS_itrf2014_gnss.html'
            elif self.iers_technique_box.currentText() == 'SLR':
                map_show_name = 'IERS_itrf2014_slr.html'
            elif self.iers_technique_box.currentText() == 'VLBI':
                map_show_name = 'IERS_itrf2014_vlbi.html'
            elif self.iers_technique_box.currentText() == 'DORIS':
                map_show_name = 'IERS_itrf2014_doris.html'
        elif self.iers_itrf_box.currentText() == 'ITRF 2020':
            if self.iers_technique_box.currentText() == 'GNSS':
                map_show_name = 'IERS_itrf2020_gnss.html'
            elif self.iers_technique_box.currentText() == 'SLR':
                map_show_name = 'IERS_itrf2020_slr.html'
            elif self.iers_technique_box.currentText() == 'VLBI':
                map_show_name = 'IERS_itrf2020_vlbi.html'
            elif self.iers_technique_box.currentText() == 'DORIS':
                map_show_name = 'IERS_itrf2020_doris.html'
        map_show_url = './templates/Time_Serises/' + map_show_name
        self.show_map_view.load(QUrl(QFileInfo(map_show_url).absoluteFilePath()))
        pass


    #  search search
    def Search_text_changed(self):
        #
        self.choose_Option_display.clear()
        add_station_list = global_var.get_value('CORS_current_view_station_list')
        for item1 in add_station_list:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.choose_Option_display.addItem(item)

        #
        goal_search_text = self.search_igs_label.text().lower()
        station_list_num = self.choose_Option_display.count()
        all_list_station_list = []
        for num in range(station_list_num):
            list_station = self.choose_Option_display.item(num).text()
            all_list_station_list.append(list_station)
        # print(all_list_station_list)

        #
        searched_station_num = 0
        choosed_station_row_list = []
        for list_station in all_list_station_list:
            if goal_search_text in list_station:
                choosed_station_row_list.append(searched_station_num)
            searched_station_num = searched_station_num + 1
        # print(choosed_station_row_list)

        #
        # choosed_station_temp = []
        choosed_station_temp = all_list_station_list
        choosed_station_text_temp = []
        for i in reversed(choosed_station_row_list):
            choosed_station_text_temp.append(choosed_station_temp[i])
            del choosed_station_temp[i]
        # print(choosed_station_text_temp)
        # print(choosed_station_temp)
        for j in choosed_station_text_temp:
            choosed_station_temp.insert(0, j)
        # print(choosed_station_temp)

        #
        self.choose_Option_display.clear()
        for item1 in choosed_station_temp:
            item = QListWidgetItem(item1)
            item.setCheckState(Qt.Unchecked)
            self.choose_Option_display.addItem(item)
        self.choose_Option_display.verticalScrollBar().setSliderPosition(0)
        self.left_added_station_to_right_checked()

    # visible
    def choose_station_visible_Ture(self):
        self.choose_add_station_list_box.setVisible(True)
        self.choose_all_station_label.setVisible(True)
        self.choose_all_station_CheckBtn.setVisible(True)
        self.search_igs_label.setVisible(True)
        self.search_igs_label.setVisible(True)
        self.choose_Option_display.setVisible(True)
        self.btnAddItems_map.setVisible(True)
        self.btnPrintItems.setVisible(True)
        self.stationDisplay.setVisible(True)
        self.btnClearStation.setVisible(True)
        self.igs_names_display_label.setVisible(True)
        self.igs_names_display.setVisible(True)
        pass

    # invisible
    def choose_station_visible_False(self):
        self.choose_add_station_list_box.setVisible(False)
        self.choose_all_station_label.setVisible(False)
        self.choose_all_station_CheckBtn.setVisible(False)
        self.search_igs_label.setVisible(False)
        self.search_igs_label.setVisible(False)
        self.choose_Option_display.setVisible(False)
        self.btnAddItems_map.setVisible(False)
        self.btnPrintItems.setVisible(False)
        self.stationDisplay.setVisible(False)
        self.btnClearStation.setVisible(False)
        self.igs_names_display_label.setVisible(False)
        self.igs_names_display.setVisible(False)
        pass


    #
    def local_area_changed(self):
        self.choose_station_visible_False()
        self.show_map_label.setVisible(False)
        self.show_map_view.setVisible(False)
        #
        self.start_time.setEnabled(True)
        self.changday0201.setEnabled(True)
        self.changday0202.setEnabled(True)
        self.changday0301.setEnabled(True)
        self.changday0302.setEnabled(True)
        self.end_time.setEnabled(True)
        self.changday0401.setEnabled(True)
        self.changday0402.setEnabled(True)
        self.changday0501.setEnabled(True)
        self.changday0502.setEnabled(True)
        self.start_time.setDisplayFormat('yyyy-MM-dd')
        self.end_time.setDisplayFormat('yyyy-MM-dd')
        self.igs_names_display.clear()
        print(self.choose_local_area_box.currentText())
        #  Nevada
        self.nevada_label_OBS01_windows.setVisible(False)
        self.nevada_label_OBS01_name.setVisible(False)
        self.nevada_enu_check.setVisible(False)
        self.nevada_xyz_check.setVisible(False)
        self.nevada_plot_check.setVisible(False)
        self.nevada_enu_check.setChecked(False)
        self.nevada_xyz_check.setChecked(False)
        self.nevada_plot_check.setChecked(False)
        #  EQDSC
        self.ced_raw_data_check.setChecked(False)
        self.ced_deal_data_check.setChecked(False)
        self.ced_label_OBS02_windows.setVisible(False)
        self.ced_label_OBS02_name.setVisible(False)
        self.ced_raw_data_check.setVisible(False)
        self.ced_raw_data_box.setVisible(False)
        self.ced_raw_data_label.setVisible(False)
        self.ced_deal_data_check.setVisible(False)
        self.ced_deal_data_box.setVisible(False)
        self.ced_deal_data_label.setVisible(False)
        #  SOPAC
        self.sopac_label_OBS01_windows.setVisible(False)
        self.sopac_label_OBS01_name.setVisible(False)
        self.sopac_comb_input_check.setVisible(False)
        self.sopac_comb_input_check.setChecked(False)
        self.sopac_comb_input_box.setVisible(False)
        self.sopac_comb_input_label.setVisible(False)
        #  UNAVCO
        self.unavco_label_OBS01_windows.setVisible(False)
        self.unavco_label_OBS01_name.setVisible(False)
        self.unavco_itrf08_check.setVisible(False)
        self.unavco_itrf14_check.setVisible(False)
        self.unavco_itrf08_check.setChecked(False)
        self.unavco_itrf14_check.setChecked(False)
        #  IERS
        self.iers_label_OBS02_windows.setVisible(False)
        self.iers_label_OBS02_name.setVisible(False)
        self.iers_data_check.setVisible(False)
        self.iers_itrf_box.setVisible(False)
        self.iers_technique_box.setVisible(False)
        self.iers_raw_data_label.setVisible(False)
        self.iers_data_check.setChecked(False)

        if self.choose_local_area_box.currentText() == 'EQDSC(China)':
            self.choose_station_visible_Ture()
            self.ced_label_OBS02_windows.setVisible(True)
            self.ced_label_OBS02_name.setVisible(True)
            self.ced_raw_data_check.setVisible(True)
            self.ced_raw_data_box.setVisible(True)
            self.ced_raw_data_label.setVisible(True)
            self.ced_deal_data_check.setVisible(True)
            self.ced_deal_data_box.setVisible(True)
            self.ced_deal_data_label.setVisible(True)
            self.choose_Option_display.clear()
            Files = self.stations_json_text[0]
            self.start_time.setEnabled(False)
            self.changday0201.setEnabled(False)
            self.changday0202.setEnabled(False)
            self.changday0301.setEnabled(False)
            self.changday0302.setEnabled(False)
            self.end_time.setEnabled(False)
            self.changday0401.setEnabled(False)
            self.changday0402.setEnabled(False)
            self.changday0501.setEnabled(False)
            self.changday0502.setEnabled(False)
            self.igs_names_display.setPlaceholderText('ahaq\nahbb\nbjsh\nbjgb')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
            pass

        elif self.choose_local_area_box.currentText() == 'NGL(USA)':
            self.choose_station_visible_Ture()
            self.nevada_label_OBS01_windows.setVisible(True)
            self.nevada_label_OBS01_name.setVisible(True)
            self.nevada_enu_check.setVisible(True)
            self.nevada_xyz_check.setVisible(True)
            self.nevada_plot_check.setVisible(True)
            self.choose_Option_display.clear()
            Files = self.stations_json_text[1]
            self.start_time.setEnabled(False)
            self.changday0201.setEnabled(False)
            self.changday0202.setEnabled(False)
            self.changday0301.setEnabled(False)
            self.changday0302.setEnabled(False)
            self.end_time.setEnabled(False)
            self.changday0401.setEnabled(False)
            self.changday0402.setEnabled(False)
            self.changday0501.setEnabled(False)
            self.changday0502.setEnabled(False)
            self.igs_names_display.setPlaceholderText('0abi\nmtwo\nuzhd\nzzon')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
            pass

        elif self.choose_local_area_box.currentText() == 'SOPAC(USA)':
            self.show_map_view.load(QUrl(QFileInfo('./templates/Time_Serises/IERS_itrf2008.html').absoluteFilePath()))
            self.show_map_label.setVisible(True)
            self.show_map_view.setVisible(True)
            self.sopac_label_OBS01_windows.setVisible(True)
            self.sopac_label_OBS01_name.setVisible(True)
            self.sopac_comb_input_check.setVisible(True)
            self.sopac_comb_input_box.setVisible(True)
            self.sopac_comb_input_label.setVisible(True)
            self.choose_Option_display.clear()
            Files = []
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
            pass

        elif self.choose_local_area_box.currentText() == 'UNAVCO(USA)':
            self.choose_station_visible_Ture()
            self.unavco_label_OBS01_windows.setVisible(True)
            self.unavco_label_OBS01_name.setVisible(True)
            self.unavco_itrf08_check.setVisible(True)
            self.unavco_itrf14_check.setVisible(True)
            self.choose_Option_display.clear()
            Files = self.stations_json_text[2]
            self.start_time.setEnabled(False)
            self.changday0201.setEnabled(False)
            self.changday0202.setEnabled(False)
            self.changday0301.setEnabled(False)
            self.changday0302.setEnabled(False)
            self.end_time.setEnabled(False)
            self.changday0401.setEnabled(False)
            self.changday0402.setEnabled(False)
            self.changday0501.setEnabled(False)
            self.changday0502.setEnabled(False)
            self.igs_names_display.setPlaceholderText('1lsu\n1nsu\n1ulm\nab02')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
            pass

        elif self.choose_local_area_box.currentText() == 'IERS':
            self.show_map_view.load(QUrl(QFileInfo('./templates/Time_Serises/IERS_itrf2020_gnss.html').absoluteFilePath()))
            self.show_map_label.setVisible(True)
            self.show_map_view.setVisible(True)
            self.iers_label_OBS02_windows.setVisible(True)
            self.iers_label_OBS02_name.setVisible(True)
            self.iers_data_check.setVisible(True)
            self.iers_itrf_box.setVisible(True)
            self.iers_technique_box.setVisible(True)
            self.iers_raw_data_label.setVisible(True)
            self.choose_Option_display.clear()
            Files = []
            self.start_time.setEnabled(False)
            self.changday0201.setEnabled(False)
            self.changday0202.setEnabled(False)
            self.changday0301.setEnabled(False)
            self.changday0302.setEnabled(False)
            self.end_time.setEnabled(False)
            self.changday0401.setEnabled(False)
            self.changday0402.setEnabled(False)
            self.changday0501.setEnabled(False)
            self.changday0502.setEnabled(False)
            self.igs_names_display.setPlaceholderText('No need to add the station!')
            for item1 in Files:
                item = QListWidgetItem(item1)
                item.setCheckState(Qt.Unchecked)
                self.choose_Option_display.addItem(item)
            pass

        else:
            self.choose_Option_display.clear()
            pass
        global_var.set_value('CORS_current_view_station_list', Files)

    ##                time format transformation                                  ##
    ###
    def onDateChanged01(self):
        try:
            time_yearmothday = self.start_time.text()
            year = int(time_yearmothday[0:4])
            mon = int(str(time_yearmothday[5:7]))
            day = int(str(time_yearmothday[8:10]))

            conbin_date = date(year, mon, day)

            #  julian to year and doy
            year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
            self.changday0201.setText(str(year_accumulate_list[0]))
            self.changday0202.setText(str(year_accumulate_list[1]))

            #  julian to week and day of week
            GPS_weeks = gnsscal.date2gpswd(conbin_date)
            self.changday0301.setText(str(GPS_weeks[0]))
            self.changday0302.setText(str(GPS_weeks[1]))
            pass
        except:
            pass

    # year and doy to julian
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

                #
                YearMonDay = gnsscal.yrdoy2date(year, accumulate_day)
                self.start_time.setDate(YearMonDay)
                pass
        except:
            pass

    ## week and day of week to julian
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

            # julian to year and doy
            year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
            self.changday0401.setText(str(year_accumulate_list[0]))
            self.changday0402.setText(str(year_accumulate_list[1]))

            # julian to week and day of week
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

    # output
    def save_download_files_path_function(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Select Output Path', 'C:/')
        if save_path == '':
            pass
        else:
            self.show_outsave_files_path_button.setText(save_path)
        pass

    # data spans
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

    # start
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

        if year%4 == 0 and year%400 != 0:
            year_accumulation_day = str(self.day_run_year(year, mon, day))
        else:
            year_accumulation_day = str(self.day_ping_year(year, mon, day))
        GPS_week_year_list.append(year)
        GPS_week_year_list.append(year_abbreviation)
        GPS_week_year_list.append(str(mon))
        GPS_week_year_list.append(str(day))
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

    # output content
    def open_have_download_path(self):
        try:
            if self.show_outsave_files_path_button.text() == '':
                return
            else:
                os.startfile(self.show_outsave_files_path_button.text())
        except:
            return

    # map
    def add_map_Items(self):
        if self.choose_local_area_box.currentText() == 'NGL(USA)':
            Download_Source = '/Nevada'
        elif self.choose_local_area_box.currentText() == 'EQDSC(China)':
            Download_Source = '/Ced'
        elif self.choose_local_area_box.currentText() == 'SOPAC(USA)':
            Download_Source = '/Sopac'
        elif self.choose_local_area_box.currentText() == 'UNAVCO(USA)':
            Download_Source = '/Unavco'
        self.h = Return_Map_Names(Download_Source)
        self.h.my_Signal.connect(self.close_sonView_trigger_event)
        self.h.show()

    #  close
    def close_sonView_trigger_event(self):
        print('子窗口被关闭')
        Map_NevadaCORS_name = global_var.get_value('Nevada_station_list')
        Map_CedCORS_name = global_var.get_value('Ced_station_list')
        Map_SopacCORS_name = global_var.get_value('Sopac_station_list')
        Map_UnavcoCORS_name = global_var.get_value('Unavco_station_list')
        map_cors_names = []

        try:
            if self.choose_local_area_box.currentText() == 'NGL(USA)':
                if Map_NevadaCORS_name != {}:
                    Map_NevadaCORS_name_list = Map_NevadaCORS_name['name']
                    Map_NevadaCORS_name_list = list(Map_NevadaCORS_name_list)
                    print(Map_NevadaCORS_name_list)
                    for i in Map_NevadaCORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'EQDSC(China)':
                if Map_CedCORS_name != {}:
                    Map_CedCORS_name_list = Map_CedCORS_name['name']
                    Map_CedCORS_name_list = list(Map_CedCORS_name_list)
                    for i in Map_CedCORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'SOPAC(USA)':
                if Map_SopacCORS_name != {}:
                    Map_SopacCORS_name_list = Map_SopacCORS_name['name']
                    Map_SopacCORS_name_list = list(Map_SopacCORS_name_list)
                    for i in Map_SopacCORS_name_list:
                        map_cors_names.append(i)
                    pass
            elif self.choose_local_area_box.currentText() == 'UNAVCO(USA)':
                if Map_UnavcoCORS_name != {}:
                    Map_UnavcoCORS_name_list = Map_UnavcoCORS_name['name']
                    Map_UnavcoCORS_name_list = list(Map_UnavcoCORS_name_list)
                    for i in Map_UnavcoCORS_name_list:
                        map_cors_names.append(i)
                    pass
            temp_station_text = ''
            for map_cors_name in map_cors_names:
                temp_station_text = temp_station_text + str(map_cors_name) + '\n'
            self.igs_names_display.append(temp_station_text[:-1])
            self.left_added_station_deduplication()
        except:
            pass

    # display map
    def station_map_display_function(self):
        if self.choose_local_area_box.currentText() == 'EQDSC(China)':
            all_source_Info = self.stations_coordinate_json_text[0]
        elif self.choose_local_area_box.currentText() == 'NGL(USA)':
            all_source_Info = self.stations_coordinate_json_text[1]
        elif self.choose_local_area_box.currentText() == 'SOPAC(USA)':
            all_source_Info = []
        elif self.choose_local_area_box.currentText() == 'UNAVCO(USA)':
            all_source_Info = self.stations_coordinate_json_text[2]

        all_choosed_station_list = re.split('[,\n]', self.igs_names_display.toPlainText())
        print(all_choosed_station_list)
        if all_choosed_station_list == ['']:
            QMessageBox.warning(self, 'prompt', "Not matched to the station！")
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
            QMessageBox.information(self, 'prompt', 'Not matched to the station coordinate!')
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


    # all selelct
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
        self.choose_all_station_CheckBtn.setChecked(False)

    #  station number
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
        # print(goal_added_station_row)
        for k in goal_added_station_row:
            self.choose_Option_display.item(k).setCheckState(Qt.Checked)


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
                if url[:20] == 'ftp://sopac-ftp.ucsd' or url[:20] == 'https://itrf.ign.fr/':
                    pass
                else:
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
                if url[:20] == 'ftp://sopac-ftp.ucsd' or url[:20] == 'https://itrf.ign.fr/':
                    pass
                else:
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
                        if url[:20] == 'ftp://sopac-ftp.ucsd' or url[:20] == 'https://itrf.ign.fr/':
                            pass
                        else:
                            self.download_Progress_bar.setValue(self_step)
                        QApplication.processEvents()
                    else:
                        print('failure：', url, res.status_code)
                        self_step = self_step + 1
                        if url[:20] == 'ftp://sopac-ftp.ucsd' or url[:20] == 'https://itrf.ign.fr/':
                            pass
                        else:
                            self.download_Progress_bar.setValue(self_step)
                        QApplication.processEvents()
                        failed_library = failed_library + [list]
                except:
                    raise NameError
            else:
                print('failure：', url, res.status_code)
                self_step = self_step + 1
                if url[:20] == 'ftp://sopac-ftp.ucsd' or url[:20] == 'https://itrf.ign.fr/':
                    pass
                else:
                    self.download_Progress_bar.setValue(self_step)
                QApplication.processEvents()
                failed_library = failed_library + [list]
                pass
            pass


    # -------------------------------------------------------------------------------------------------
    # """ download main function """
    def data_download_function02(self):
        self.show_download_process_state.setText('Download...')
        # Judgment networking
        try:
            html = requests.get("https://www.baidu.com", timeout=4)
        except:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'prompt', 'Failed, please check the network connection')
            return

        function_start_time = datetime.now()
        self.show_download_information.setText('')
        global self_step
        self_step = 0
        self.download_Progress_bar.setValue(self_step)
        #
        global successful_library
        global failed_library
        successful_library = []
        failed_library = []

        #
        global session
        requests_ftp.monkeypatch_session()
        session = requests.Session()
        global ftp_max_thread
        if self.choose_local_area_box.currentText() == 'NGL(USA)':
            ftp_max_thread = threading.Semaphore(10)
        elif self.choose_local_area_box.currentText() == 'EQDSC(China)':
            ftp_max_thread = threading.Semaphore(5)
        elif self.choose_local_area_box.currentText() == 'SOPAC(USA)':
            ftp_max_thread = threading.Semaphore(1)
        elif self.choose_local_area_box.currentText() == 'UNAVCO(USA)':
            ftp_max_thread = threading.Semaphore(10)
        elif self.choose_local_area_box.currentText() == 'IERS':
            ftp_max_thread = threading.Semaphore(2)
        else:
            pass

        if os.path.exists(self.show_outsave_files_path_button.text()):
            pass
        else:
            os.mkdir(self.show_outsave_files_path_button.text())

        #  1. obtain time list
        start_time_T = str(self.start_time.dateTime().toString(Qt.ISODate))
        start_time = start_time_T[0:10] + ' ' + start_time_T[11:19]
        start_time_date = start_time_T[0:10]
        end_time_T = str(self.end_time.dateTime().toString(Qt.ISODate))
        end_time = end_time_T[0:10] + ' ' + end_time_T[11:19]
        end_time_date = end_time_T[0:10]
        #
        dt1 = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        dt2 = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        difference_time = dt2 - dt1

        if difference_time.days >= 0:
            Judgement_time = 1
        else:
            Judgement_time = 0

        if Judgement_time == 0:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Prompt', 'Error Time Order')
            return
        else:
            #
            date_list = self.getEveryDay(start_time_date, end_time_date)
            print('所有时间', date_list)
            #
            all_YearAccuDay_GpsWeek = []
            for i in date_list:
                YearAccuDay_GpsWeek = self.GpsWeek_YearAccuDay(i)
                list = [YearAccuDay_GpsWeek[0], YearAccuDay_GpsWeek[1], YearAccuDay_GpsWeek[2], YearAccuDay_GpsWeek[3],
                        YearAccuDay_GpsWeek[4], YearAccuDay_GpsWeek[5], YearAccuDay_GpsWeek[6], YearAccuDay_GpsWeek[7]]
                all_YearAccuDay_GpsWeek = all_YearAccuDay_GpsWeek + [list]
                pass
            #
            print(all_YearAccuDay_GpsWeek)

        #  2. obtain station list
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

        if self.show_outsave_files_path_button.text() == '':
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Prompt', 'Please select the output path！')
            return

        Ced_raw_url_list = []
        Ced_deal_url_list = []
        Nevada_enu_url_list = []
        Nevada_xyz_url_list = []
        Nevada_plot_url_list = []
        Sopac_input_file_url_list = []
        UNAVCO_itrf08_url_list = []
        UNAVCO_itrf14_url_list = []
        Iers_itrf_url_list = []

        ###                    ***         EQDSC(China) TimeSeries          ***                        ###
        # self.ced_raw_data_check          self.ced_deal_data_check
        # self.ced_raw_data_box.addItems(['Rapid', 'Precision'])       self.ced_deal_data_box.addItems(['Rapid', 'Precision'])
        # Ced_raw_url_list    Ced_deal_url_list
        #   Cad raw file
        if self.ced_raw_data_check.isChecked():
            if igs_uppercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Prompt', 'No added to the station！')
                return
            else:
                Ced_raw_url_list = []
                for station_name in igs_uppercase:
                    file_name = station_name + '.txt'
                    if self.ced_raw_data_box.currentText() == 'Rapid':
                        #  https://www.eqdsc.com/eastern/upload/gnss/kssjxl/ys/AHAQ.txt
                        download_url = 'https://www.eqdsc.com/eastern/upload/gnss/kssjxl/ys/' + file_name
                    elif self.ced_raw_data_box.currentText() == 'Precision':
                        #  https://www.eqdsc.com/eastern/upload/gnss/jmsjxl/ys/AHAQ.txt
                        download_url = 'https://www.eqdsc.com/eastern/upload/gnss/kssjxl/ys/' + file_name
                    list = [download_url, file_name]
                    Ced_raw_url_list = Ced_raw_url_list + [list]
                    pass

        #   Cad deal file
        if self.ced_deal_data_check.isChecked():
            if igs_uppercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Prompt', 'No added to the station！')
                return
            else:
                Ced_deal_url_list = []
                for station_name in igs_uppercase:
                    file_name = station_name + '.txt'
                    if self.ced_raw_data_box.currentText() == 'Rapid':
                        #  https://www.eqdsc.com/eastern/upload/gnss/kssjxl/qxx/AHAQ.txt
                        download_url = 'https://www.eqdsc.com/eastern/upload/gnss/kssjxl/qxx/' + file_name
                    elif self.ced_raw_data_box.currentText() == 'Precision':
                        #  https://www.eqdsc.com/eastern/upload/gnss/jmsjxl/qxx/AHAQ.txt
                        download_url = 'https://www.eqdsc.com/eastern/upload/gnss/jmsjxl/qxx/' + file_name
                    list = [download_url, file_name]
                    Ced_deal_url_list = Ced_deal_url_list + [list]
                    pass

        ###                    ***          TimeSeries          ***                        ###
        # self.nevada_enu_check          self.nevada_xyz_check        self.nevada_plot_check
        # Nevada_enu_url_list    Nevada_xyz_url_list    Nevada_plot_url_list
        #   Nevada enu file
        if self.nevada_enu_check.isChecked():
            if igs_uppercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Prompt', 'No added to the station！')
                return
            else:
                Nevada_enu_url_list = []
                for station_name in igs_uppercase:
                    #  http://geodesy.unr.edu/gps_timeseries/tenv3/IGS14/BJFS.tenv3
                    file_name = station_name + '.tenv3'
                    download_url = 'http://geodesy.unr.edu/gps_timeseries/tenv3/IGS14/' + file_name
                    list = [download_url, file_name]
                    Nevada_enu_url_list = Nevada_enu_url_list + [list]
                    pass

        #   Nevada xyz file
        if self.nevada_xyz_check.isChecked():
            if igs_uppercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Prompt', 'No added to the station！')
                return
            else:
                Nevada_xyz_url_list = []
                for station_name in igs_uppercase:
                    #  http://geodesy.unr.edu/gps_timeseries/txyz/IGS14/BJFS.tenv3
                    file_name = station_name + '.txyz2'
                    download_url = 'http://geodesy.unr.edu/gps_timeseries/txyz/IGS14/' + file_name
                    list = [download_url, file_name]
                    Nevada_xyz_url_list = Nevada_xyz_url_list + [list]
                    pass

        #   Nevada plot file
        if self.nevada_plot_check.isChecked():
            if igs_uppercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Prompt', 'No added to the station！')
                return
            else:
                Nevada_plot_url_list = []
                for station_name in igs_uppercase:
                    #  http://geodesy.unr.edu/tsplots/IGS14/IGS14/TimeSeries/BJFS.png
                    file_name = station_name + '.png'
                    download_url = 'http://geodesy.unr.edu/tsplots/IGS14/IGS14/TimeSeries/' + file_name
                    list = [download_url, file_name]
                    Nevada_plot_url_list = Nevada_plot_url_list + [list]
                    pass

        ###                    ***        SOPAC  TimeSeries          ***                        ###
        # self.sopac_comb_input_check
        # self.sopac_comb_input_box.addItems(['sopac', 'comb', 'jpl'])
        # Sopac_input_file_url_list
        #   SOPAC input_file
        comb_useful_time_list = [['2016', '06', '01'], ['2016', '06', '08'], ['2016', '06', '23'], ['2016', '07', '01'], ['2016', '07', '09'], ['2016', '07', '14'], ['2016', '07', '21'], ['2016', '07', '27'], ['2016', '08', '02'], ['2016', '08', '11'], ['2016', '08', '18'], ['2016', '08', '24'], ['2016', '09', '02'], ['2016', '09', '06'], ['2016', '09', '14'], ['2016', '09', '21'], ['2016', '09', '28'], ['2016', '10', '06'], ['2016', '10', '13'], ['2016', '10', '20'], ['2016', '10', '28'], ['2016', '11', '03'], ['2016', '11', '09'], ['2016', '11', '17'], ['2016', '11', '22'], ['2016', '12', '04'], ['2016', '12', '09'], ['2016', '12', '14'], ['2016', '12', '24'], ['2016', '12', '30'], ['2017', '01', '08'], ['2017', '01', '14'], ['2017', '01', '23'], ['2017', '01', '29'], ['2017', '02', '08'], ['2017', '02', '18'], ['2017', '02', '19'], ['2017', '02', '20'], ['2017', '02', '21'], ['2017', '02', '22'], ['2017', '02', '23'], ['2017', '03', '01'], ['2017', '03', '20'], ['2017', '03', '26'], ['2017', '04', '01'], ['2017', '04', '07'], ['2017', '04', '20'], ['2017', '04', '27'], ['2017', '05', '05'], ['2017', '05', '25'], ['2017', '06', '03'], ['2017', '06', '08'], ['2017', '06', '16'], ['2017', '06', '25'], ['2017', '07', '01'], ['2017', '07', '07'], ['2017', '07', '15'], ['2017', '07', '20'], ['2017', '07', '28'], ['2017', '08', '12'], ['2017', '08', '22'], ['2017', '09', '03'], ['2017', '09', '10'], ['2017', '10', '04'], ['2017', '11', '08'], ['2017', '11', '22'], ['2017', '12', '05'], ['2017', '12', '16'], ['2018', '06', '21'], ['2018', '06', '28'], ['2018', '07', '16'], ['2018', '08', '10'], ['2018', '08', '27'], ['2018', '09', '10'], ['2018', '09', '30'], ['2018', '10', '03'], ['2018', '10', '29'], ['2018', '12', '19'], ['2018', '12', '20'], ['2018', '12', '21'], ['2018', '12', '22'], ['2019', '01', '02'], ['2019', '01', '05'], ['2019', '01', '14'], ['2019', '01', '16'], ['2019', '02', '06'], ['2019', '03', '07'], ['2019', '03', '20'], ['2019', '04', '20'], ['2019', '05', '08'], ['2019', '05', '18'], ['2019', '05', '29'], ['2019', '06', '26'], ['2019', '07', '08'], ['2019', '07', '28'], ['2019', '08', '04'], ['2019', '08', '12'], ['2019', '08', '13'], ['2019', '09', '12'], ['2019', '10', '03'], ['2019', '10', '16'], ['2019', '10', '21'], ['2019', '11', '20'], ['2019', '11', '26'], ['2019', '11', '27'], ['2020', '05', '05'], ['2020', '05', '27'], ['2020', '06', '03'], ['2020', '06', '09'], ['2020', '07', '24'], ['2020', '07', '29'], ['2020', '08', '15'], ['2020', '08', '20'], ['2020', '09', '04'], ['2020', '09', '09'], ['2020', '09', '11'], ['2020', '09', '30'], ['2020', '11', '05'], ['2020', '11', '23'], ['2020', '12', '18'], ['2021', '01', '11'], ['2021', '01', '28'], ['2021', '02', '10'], ['2021', '02', '21'], ['2021', '03', '10'], ['2021', '04', '04'], ['2021', '05', '12'], ['2021', '06', '22'], ['2021', '07', '01'], ['2021', '07', '02'], ['2021', '07', '08'], ['2021', '07', '12'], ['2021', '07', '14'], ['2021', '07', '19'], ['2021', '07', '26'], ['2021', '08', '06'], ['2021', '08', '10'], ['2021', '08', '15'], ['2021', '08', '19'], ['2021', '08', '22'], ['2021', '08', '23'], ['2021', '08', '29'], ['2021', '08', '30'], ['2021', '09', '05'], ['2021', '09', '16'], ['2021', '09', '26'], ['2021', '10', '05'], ['2021', '10', '12'], ['2021', '10', '24'], ['2021', '11', '01'], ['2021', '11', '11'], ['2021', '11', '15'], ['2021', '11', '21'], ['2021', '11', '28'], ['2021', '12', '24'], ['2022', '01', '08'], ['2022', '01', '17'], ['2022', '01', '25'], ['2022', '02', '07'], ['2022', '02', '17'], ['2022', '02', '20'], ['2022', '02', '27'], ['2022', '03', '08'], ['2022', '03', '13'], ['2022', '03', '20'], ['2022', '03', '28'], ['2022', '04', '07'], ['2022', '04', '11'], ['2022', '04', '18'], ['2022', '04', '24'], ['2022', '05', '02'], ['2022', '05', '10'], ['2022', '05', '16'], ['2022', '05', '23'], ['2022', '05', '30'], ['2022', '06', '08'], ['2022', '06', '14'], ['2022', '06', '20'], ['2022', '06', '28'], ['2022', '07', '04'], ['2022', '07', '12'], ['2022', '07', '18'], ['2022', '07', '25'], ['2022', '08', '01'], ['2022', '08', '08'], ['2022', '08', '15'], ['2022', '08', '24'], ['2022', '08', '29'], ['2022', '09', '05'], ['2022', '09', '13'], ['2022', '09', '22'], ['2022', '09', '29'], ['2022', '10', '03'], ['2022', '10', '11'], ['2022', '10', '19'], ['2022', '10', '24'], ['2022', '11', '01'], ['2022', '11', '07'], ['2022', '11', '14'], ['2022', '11', '22'], ['2022', '11', '28'], ['2022', '12', '05'], ['2022', '12', '14'], ['2022', '12', '19'], ['2022', '12', '26'], ['2023', '01', '02'], ['2023', '01', '09'], ['2023', '01', '20'], ['2023', '01', '23'], ['2023', '01', '30'], ['2023', '02', '06'], ['2023', '02', '13'], ['2023', '02', '20'], ['2023', '02', '27'], ['2023', '03', '06'], ['2023', '03', '14'], ['2023', '03', '20'], ['2023', '03', '29'], ['2023', '04', '05'], ['2023', '04', '11'], ['2023', '04', '17'], ['2023', '04', '24'], ['2023', '05', '01'], ['2023', '05', '09'],
                                 ['2023', '05', '18'], ['2023', '05', '22'], ['2023', '05', '29'], ['2023', '06', '07'], ['2023', '06', '13'], ['2023', '06', '20'], ['2023', '06', '26'], ['2023', '07', '03'], ['2023', '07', '10'], ['2023', '07', '11'], ['2023', '07', '17'], ['2023', '07', '26'], ['2023', '08', '03'], ['2023', '08', '15'], ['2023', '08', '23'], ['2023', '08', '29'], ['2023', '09', '04'], ['2023', '09', '12'], ['2023', '09', '22'], ['2023', '09', '27'], ['2023', '10', '02'], ['2023', '10', '10'],
                                 ['2023', '10', '16'], ['2023', '10', '25'], ['2023', '10', '31'], ['2023', '11', '14'], ['2023', '11', '17'], ['2023', '11', '30'], ['2023', '12', '04'], ['2023', '12', '11'], ['2023', '12', '18'], ['2023', '12', '25'], ['2024', '01', '02'], ['2024', '01', '09'], ['2024', '01', '16'], ['2024', '01', '23'], ['2024', '01', '30'], ['2024', '02', '05'], ['2024', '02', '14'], ['2024', '02', '20'], ['2024', '02', '26'], ['2024', '03', '05'], ['2024', '03', '13'], ['2024', '03', '20'], ['2024', '03', '25'], ['2024', '04', '03']
                                ]
        sopac_useful_time_list = [['2016', '06', '02'], ['2016', '06', '09'], ['2016', '06', '24'], ['2016', '07', '02'], ['2016', '07', '09'], ['2016', '07', '15'], ['2016', '07', '22'], ['2016', '07', '28'], ['2016', '08', '04'], ['2016', '08', '19'], ['2016', '08', '25'], ['2016', '09', '02'], ['2016', '09', '07'], ['2016', '09', '15'], ['2016', '09', '22'], ['2016', '09', '29'], ['2016', '10', '07'], ['2016', '10', '14'], ['2016', '10', '21'], ['2016', '10', '29'], ['2016', '11', '04'], ['2016', '11', '10'], ['2016', '11', '18'], ['2016', '11', '24'], ['2016', '12', '05'], ['2016', '12', '09'], ['2016', '12', '15'], ['2016', '12', '25'], ['2016', '12', '31'], ['2017', '01', '09'], ['2017', '01', '15'], ['2017', '01', '30'], ['2017', '02', '18'], ['2017', '02', '22'], ['2017', '02', '24'], ['2017', '03', '02'], ['2017', '03', '21'], ['2017', '03', '27'], ['2017', '04', '01'], ['2017', '04', '08'], ['2017', '04', '21'], ['2017', '04', '28'], ['2017', '05', '06'], ['2017', '05', '26'], ['2017', '06', '04'], ['2017', '06', '09'], ['2017', '06', '17'], ['2017', '06', '26'], ['2017', '07', '02'], ['2017', '07', '08'], ['2017', '07', '16'], ['2017', '07', '21'], ['2017', '07', '29'], ['2017', '08', '13'], ['2017', '08', '23'], ['2017', '09', '04'], ['2017', '09', '10'], ['2017', '09', '30'], ['2017', '10', '03'], ['2017', '10', '11'], ['2017', '10', '14'], ['2017', '10', '15'], ['2017', '10', '17'], ['2017', '10', '18'], ['2017', '11', '09'], ['2017', '11', '23'], ['2017', '12', '06'], ['2017', '12', '17'], ['2018', '06', '07'], ['2018', '06', '26'], ['2018', '07', '25'], ['2018', '08', '15'], ['2018', '08', '28'], ['2018', '09', '11'], ['2018', '10', '01'], ['2018', '10', '30'], ['2018', '11', '06'], ['2018', '12', '19'], ['2019', '01', '04'], ['2019', '01', '15'], ['2019', '01', '18'], ['2019', '03', '06'], ['2019', '03', '22'], ['2019', '04', '01'], ['2019', '04', '21'], ['2019', '05', '09'], ['2019', '05', '19'], ['2019', '05', '31'], ['2019', '06', '27'], ['2019', '07', '09'], ['2019', '07', '27'], ['2019', '08', '04'], ['2019', '08', '13'], ['2019', '09', '13'], ['2019', '10', '02'], ['2019', '10', '15'], ['2019', '11', '20'], ['2019', '12', '01'], ['2019', '12', '19'], ['2020', '01', '01'], ['2020', '02', '03'], ['2020', '02', '07'], ['2020', '03', '19'], ['2020', '03', '27'], ['2020', '05', '03'], ['2020', '05', '07'], ['2020', '05', '11'], ['2020', '05', '19'], ['2020', '05', '28'], ['2020', '06', '01'], ['2020', '06', '15'], ['2020', '06', '23'], ['2020', '07', '01'], ['2020', '07', '21'], ['2020', '07', '28'], ['2020', '08', '04'], ['2020', '08', '11'], ['2020', '08', '18'], ['2020', '08', '25'], ['2020', '09', '02'], ['2020', '09', '10'], ['2020', '09', '17'], ['2020', '09', '23'], ['2020', '09', '28'], ['2020', '10', '12'], ['2020', '10', '20'], ['2020', '10', '27'], ['2020', '11', '03'], ['2020', '11', '09'], ['2020', '11', '25'], ['2020', '12', '06'], ['2020', '12', '15'], ['2020', '12', '21'], ['2021', '01', '04'], ['2021', '01', '19'], ['2021', '01', '30'], ['2021', '02', '02'], ['2021', '02', '08'], ['2021', '02', '15'], ['2021', '02', '22'], ['2021', '03', '01'], ['2021', '03', '03'], ['2021', '03', '07'], ['2021', '03', '14'], ['2021', '03', '28'], ['2021', '03', '31'], ['2021', '04', '01'], ['2021', '04', '05'], ['2021', '04', '12'], ['2021', '04', '19'], ['2021', '04', '26'], ['2021', '05', '07'], ['2021', '05', '10'], ['2021', '05', '15'], ['2021', '05', '24'], ['2021', '06', '01'], ['2021', '06', '07'], ['2021', '06', '13'], ['2021', '06', '20'], ['2021', '06', '27'], ['2021', '07', '03'], ['2021', '07', '10'], ['2021', '07', '18'], ['2021', '07', '25'], ['2021', '07', '31'], ['2021', '08', '08'], ['2021', '08', '14'], ['2021', '08', '29'], ['2021', '09', '18'], ['2021', '10', '02'], ['2021', '10', '11'], ['2021', '10', '18'], ['2021', '10', '23'], ['2021', '11', '10'], ['2021', '11', '14'], ['2021', '11', '27'], ['2021', '12', '06'], ['2021', '12', '14'], ['2021', '12', '20'], ['2021', '12', '27'], ['2022', '01', '06'], ['2022', '01', '11'], ['2022', '01', '17'], ['2022', '01', '24'], ['2022', '02', '06'], ['2022', '02', '16'], ['2022', '02', '26'], ['2022', '03', '07'], ['2022', '03', '12'], ['2022', '03', '27'], ['2022', '04', '07'], ['2022', '04', '10'], ['2022', '04', '17'], ['2022', '04', '24'], ['2022', '05', '01'], ['2022', '05', '09'], ['2022', '05', '16'], ['2022', '05', '22'], ['2022', '05', '30'], ['2022', '06', '07'], ['2022', '06', '13'], ['2022', '06', '19'], ['2022', '06', '26'], ['2022', '07', '03'], ['2022', '07', '10'], ['2022', '07', '17'], ['2022', '07', '24'], ['2022', '07', '31'], ['2022', '08', '07'], ['2022', '08', '14'], ['2022', '08', '21'], ['2022', '08', '28'], ['2022', '09', '04'], ['2022', '09', '12'], ['2022', '09', '21'], ['2022', '09', '28'], ['2022', '10', '02'], ['2022', '10', '10'], ['2022', '10', '18'], ['2022', '10', '23'], ['2022', '10', '31'], ['2022', '11', '06'], ['2022', '11', '13'], ['2022', '11', '21'], ['2022', '11', '27'], ['2022', '12', '04'], ['2022', '12', '13'], ['2022', '12', '18'], ['2022', '12', '25'], ['2023', '01', '01'], ['2023', '01', '08'], ['2023', '01', '19'], ['2023', '01', '22'], ['2023', '01', '29'], ['2023', '02', '05'], ['2023', '02', '12'], ['2023', '02', '19'], ['2023', '02', '26'], ['2023', '03', '05'], ['2023', '03', '12'], ['2023', '03', '19'], ['2023', '03', '28'], ['2023', '04', '04'], ['2023', '04', '09'], ['2023', '04', '16'], ['2023', '04', '23'], ['2023', '04', '30'], ['2023', '05', '08'], ['2023', '05', '16'],
                                  ['2023', '05', '21'], ['2023', '05', '28'], ['2023', '06', '04'], ['2023', '06', '12'], ['2023', '06', '19'], ['2023', '06', '25'], ['2023', '07', '02'], ['2023', '07', '09'], ['2023', '07', '16'], ['2023', '07', '24'], ['2023', '07', '30'], ['2023', '08', '08'], ['2023', '08', '14'], ['2023', '08', '21'], ['2023', '08', '27'], ['2023', '09', '03'], ['2023', '09', '11'], ['2023', '09', '17'], ['2023', '09', '26'], ['2023', '10', '01'], ['2023', '10', '09'],
                                  ['2023', '10', '15'], ['2023', '10', '24'], ['2023', '10', '30'], ['2023', '11', '06'], ['2023', '11', '16'], ['2023', '11', '20'], ['2023', '11', '29'], ['2023', '12', '03'], ['2023', '12', '10'], ['2023', '12', '17'], ['2023', '12', '24'], ['2024', '01', '01'], ['2024', '01', '08'], ['2024', '01', '15'], ['2024', '01', '22'], ['2024', '01', '29'], ['2024', '02', '04'], ['2024', '02', '11'], ['2024', '02', '19'], ['2024', '02', '25'], ['2024', '03', '04'], ['2024', '03', '11'], ['2024', '03', '18'], ['2024', '03', '24'], ['2024', '04', '01']
                                  ]
        jpl_useful_time_list = [['2016', '06', '01'], ['2016', '06', '09'], ['2016', '06', '23'], ['2016', '07', '02'], ['2016', '07', '09'], ['2016', '07', '15'], ['2016', '07', '21'], ['2016', '07', '27'], ['2016', '08', '04'], ['2016', '08', '19'], ['2016', '08', '24'], ['2016', '09', '02'], ['2016', '09', '07'], ['2016', '09', '15'], ['2016', '09', '21'], ['2016', '09', '29'], ['2016', '10', '06'], ['2016', '10', '14'], ['2016', '10', '20'], ['2016', '10', '29'], ['2016', '11', '04'], ['2016', '11', '10'], ['2016', '11', '17'], ['2016', '11', '23'], ['2016', '12', '05'], ['2016', '12', '09'], ['2016', '12', '15'], ['2016', '12', '25'], ['2016', '12', '30'], ['2017', '01', '08'], ['2017', '01', '14'], ['2017', '01', '18'], ['2017', '01', '24'], ['2017', '01', '29'], ['2017', '02', '08'], ['2017', '02', '18'], ['2017', '02', '22'], ['2017', '02', '23'], ['2017', '03', '02'], ['2017', '03', '21'], ['2017', '03', '27'], ['2017', '04', '01'], ['2017', '04', '07'], ['2017', '04', '21'], ['2017', '04', '28'], ['2017', '05', '05'], ['2017', '05', '25'], ['2017', '06', '03'], ['2017', '06', '08'], ['2017', '06', '17'], ['2017', '06', '26'], ['2017', '07', '02'], ['2017', '07', '08'], ['2017', '07', '16'], ['2017', '07', '28'], ['2017', '08', '12'], ['2017', '08', '23'], ['2017', '09', '03'], ['2017', '09', '10'], ['2017', '10', '04'], ['2017', '11', '09'], ['2017', '11', '23'], ['2017', '12', '05'], ['2017', '12', '16'], ['2018', '05', '21'], ['2018', '06', '07'], ['2018', '06', '21'], ['2018', '07', '24'], ['2018', '08', '10'], ['2018', '08', '28'], ['2018', '09', '10'], ['2018', '10', '01'], ['2018', '10', '30'], ['2018', '12', '18'], ['2019', '01', '03'], ['2019', '01', '14'], ['2019', '02', '07'], ['2019', '03', '06'], ['2019', '03', '21'], ['2019', '04', '20'], ['2019', '05', '09'], ['2019', '05', '18'], ['2019', '05', '30'], ['2019', '06', '27'], ['2019', '07', '09'], ['2019', '07', '11'], ['2019', '07', '27'], ['2019', '08', '03'], ['2019', '08', '13'], ['2019', '09', '13'], ['2019', '10', '02'], ['2019', '10', '14'], ['2019', '10', '15'], ['2019', '11', '25'], ['2020', '03', '04'], ['2020', '03', '30'], ['2020', '04', '23'], ['2020', '04', '24'], ['2020', '05', '01'], ['2020', '05', '18'], ['2020', '05', '25'], ['2020', '06', '02'], ['2020', '06', '03'], ['2020', '06', '17'], ['2020', '06', '22'], ['2020', '07', '14'], ['2020', '07', '27'], ['2020', '08', '03'], ['2020', '08', '10'], ['2020', '08', '17'], ['2020', '08', '24'], ['2020', '09', '01'], ['2020', '09', '08'], ['2020', '09', '16'], ['2020', '09', '21'], ['2020', '09', '29'], ['2020', '10', '05'], ['2020', '10', '13'], ['2020', '10', '19'], ['2020', '10', '26'], ['2020', '11', '06'], ['2020', '11', '10'], ['2020', '11', '16'], ['2020', '11', '24'], ['2020', '12', '07'], ['2020', '12', '16'], ['2021', '01', '05'], ['2021', '01', '13'], ['2021', '01', '18'], ['2021', '01', '25'], ['2021', '01', '29'], ['2021', '02', '06'], ['2021', '02', '16'], ['2021', '02', '20'], ['2021', '02', '26'], ['2021', '03', '06'], ['2021', '03', '16'], ['2021', '03', '27'], ['2021', '04', '04'], ['2021', '04', '09'], ['2021', '04', '20'], ['2021', '05', '04'], ['2021', '05', '06'], ['2021', '05', '14'], ['2021', '05', '21'], ['2021', '05', '28'], ['2021', '06', '08'], ['2021', '06', '17'], ['2021', '06', '21'], ['2021', '06', '25'], ['2021', '07', '05'], ['2021', '07', '09'], ['2021', '07', '17'], ['2021', '07', '24'], ['2021', '08', '07'], ['2021', '08', '18'], ['2021', '08', '20'], ['2021', '08', '27'], ['2021', '09', '03'], ['2021', '09', '14'], ['2021', '09', '17'], ['2021', '09', '24'], ['2021', '10', '01'], ['2021', '10', '08'], ['2021', '10', '21'], ['2021', '10', '29'], ['2021', '11', '08'], ['2021', '11', '09'], ['2021', '11', '12'], ['2021', '11', '19'], ['2021', '11', '24'], ['2021', '12', '05'], ['2021', '12', '13'], ['2021', '12', '21'], ['2022', '01', '07'], ['2022', '01', '16'], ['2022', '01', '23'], ['2022', '01', '27'], ['2022', '02', '11'], ['2022', '02', '18'], ['2022', '02', '24'], ['2022', '03', '07'], ['2022', '03', '10'], ['2022', '03', '16'], ['2022', '03', '23'], ['2022', '04', '05'], ['2022', '04', '08'], ['2022', '04', '14'], ['2022', '04', '21'], ['2022', '04', '28'], ['2022', '05', '08'], ['2022', '05', '12'], ['2022', '05', '18'], ['2022', '05', '25'], ['2022', '06', '02'], ['2022', '06', '09'], ['2022', '06', '17'], ['2022', '06', '24'], ['2022', '06', '30'], ['2022', '07', '11'], ['2022', '07', '14'], ['2022', '07', '22'], ['2022', '07', '28'], ['2022', '08', '04'], ['2022', '08', '12'], ['2022', '08', '18'], ['2022', '08', '26'], ['2022', '09', '02'], ['2022', '09', '10'], ['2022', '09', '20'], ['2022', '09', '23'], ['2022', '10', '01'], ['2022', '10', '07'], ['2022', '10', '13'], ['2022', '10', '20'], ['2022', '10', '28'], ['2022', '11', '04'], ['2022', '11', '11'], ['2022', '11', '17'], ['2022', '11', '24'], ['2022', '12', '02'], ['2022', '12', '09'], ['2022', '12', '16'], ['2022', '12', '23'], ['2022', '12', '29'], ['2023', '01', '07'], ['2023', '01', '13'], ['2023', '01', '21'], ['2023', '01', '27'], ['2023', '02', '02'], ['2023', '02', '11'], ['2023', '02', '17'], ['2023', '02', '23'], ['2023', '03', '02'], ['2023', '03', '09'], ['2023', '03', '16'], ['2023', '03', '24'], ['2023', '04', '02'], ['2023', '04', '07'], ['2023', '04', '15'], ['2023', '04', '20'], ['2023', '04', '29'], ['2023', '05', '07'],
                                ['2023', '05', '12'], ['2023', '05', '20'], ['2023', '05', '26'], ['2023', '06', '01'], ['2023', '06', '10'], ['2023', '06', '18'], ['2023', '06', '23'], ['2023', '07', '01'], ['2023', '07', '07'], ['2023', '07', '15'], ['2023', '07', '25'], ['2023', '08', '02'], ['2023', '08', '10'], ['2023', '08', '12'], ['2023', '08', '22'], ['2023', '08', '28'], ['2023', '09', '02'], ['2023', '09', '08'], ['2023', '09', '21'], ['2023', '09', '25'], ['2023', '09', '30'], ['2023', '10', '08'],
                                ['2023', '10', '13'], ['2023', '10', '20'], ['2023', '10', '27'], ['2023', '11', '04'], ['2023', '11', '13'], ['2023', '11', '15'], ['2023', '11', '28'], ['2023', '12', '02'], ['2023', '12', '09'], ['2023', '12', '15'], ['2023', '12', '23'], ['2023', '12', '28'], ['2024', '01', '07'], ['2024', '01', '13'], ['2024', '01', '21'], ['2024', '01', '27'], ['2024', '02', '03'], ['2024', '02', '13'], ['2024', '02', '17'], ['2024', '02', '24'], ['2024', '03', '01'], ['2024', '03', '12'], ['2024', '03', '16'], ['2024', '03', '23'], ['2024', '03', '30'], ['2024', '04', '06']
                                ]
        if self.sopac_comb_input_check.isChecked():
            Sopac_input_file_url_list = []
            for time in all_YearAccuDay_GpsWeek:
                test_judge = False
                now_time_list = [str(time[0]), str(time[2]).rjust(2, '0'), str(time[3]).rjust(2, '0')]
                sopac_institution = self.sopac_comb_input_box.currentText()
                if sopac_institution == 'comb':
                    match_time_list = comb_useful_time_list
                elif sopac_institution == 'sopac':
                    match_time_list = sopac_useful_time_list
                elif sopac_institution == 'jpl':
                    match_time_list = jpl_useful_time_list
                if now_time_list in match_time_list:
                    test_judge = True
                if test_judge:
                    file_name = sopac_institution+'_input_'+str(time[0])+str(time[2]).rjust(2,'0')+str(time[3]).rjust(2,'0')+'.tar'
                    if int(time[0]) < 2017:
                        file_name = file_name + '.gz'
                        pass
                    elif int(time[0]) == 2017 and int(time[2]) < 5:
                        file_name = file_name + '.gz'
                        pass
                    elif int(time[0]) == 2017 and int(time[2]) == 5 and int(time[3]) < 7:
                        file_name = file_name + '.gz'
                        pass
                    #   ftp://sopac-ftp.ucsd.edu/pub/timeseries/measures/ats/inputFiles/comb_input_20211024.tar
                    download_url = 'ftp://sopac-ftp.ucsd.edu/pub/timeseries/measures/ats/inputFiles/' + file_name
                    list = [download_url, file_name]
                    Sopac_input_file_url_list = Sopac_input_file_url_list + [list]
                    pass

        ###                    ***          UNAVCO   TimeSeries          ***                        ###
        # self.unavco_itrf08_check        self.unavco_itrf14_check
        # UNAVCO_itrf08_url_list    UNAVCO_itrf14_url_list
        #   UNAVCO  itrf08  file
        if self.unavco_itrf08_check.isChecked():
            if igs_lowercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Prompt', 'No added to the station！')
                return
            else:
                UNAVCO_itrf08_url_list = []
                for station_name in igs_lowercase:
                    #  https://geodesy.noaa.gov/corsdata/coord/coord_08/ab02_08.coord.txt
                    file_name = station_name + '_08.coord.txt'
                    download_url = 'https://geodesy.noaa.gov/corsdata/coord/coord_08/' + file_name
                    list = [download_url, file_name]
                    UNAVCO_itrf08_url_list = UNAVCO_itrf08_url_list + [list]
                    pass

        #   UNAVCO  itrf14  file
        if self.unavco_itrf14_check.isChecked():
            if igs_lowercase == []:
                self.show_download_process_state.setText('')
                QMessageBox.information(self, 'Prompt', 'No added to the station！')
                return
            else:
                UNAVCO_itrf14_url_list = []
                for station_name in igs_lowercase:
                    #  https://geodesy.noaa.gov/corsdata/coord/coord_14/ab02_14.coord.txt
                    file_name = station_name + '_14.coord.txt'
                    download_url = 'https://geodesy.noaa.gov/corsdata/coord/coord_14/' + file_name
                    list = [download_url, file_name]
                    UNAVCO_itrf14_url_list = UNAVCO_itrf14_url_list + [list]
                    pass

        ###                    ***          IERS   TimeSeries          ***                        ###
        # self.iers_data_check
        # self.iers_itrf_box.addItems(['ITRF 2020', 'ITRF 2014', 'ITRF 2008'])
        # self.iers_technique_box.addItems(['GNSS', 'SLR', 'VLBI', 'DORIS'])
        #   IERS   file
        if self.iers_data_check.isChecked():
            itrf_name = self.iers_itrf_box.currentText().replace(' ', '')
            technique_name = self.iers_technique_box.currentText()
            if self.iers_itrf_box.currentText() == 'ITRF 2008':
                if technique_name == 'GNSS':
                    technique_name = 'GPS'
                #  https://itrf.ign.fr/ftp/pub/itrf/itrf2008/ITRF2008-RES-DORIS.tar
                file_name = itrf_name.upper() + '-RES-' + technique_name.upper() + '.tar'
                pass
            elif self.iers_itrf_box.currentText() == 'ITRF 2014':
                #  https://itrf.ign.fr/ftp/pub/itrf/itrf2014/ITRF2014-psd-doris.dat
                file_name = itrf_name.upper() + '-psd-' + technique_name.lower() + '.dat'
                pass
            elif self.iers_itrf_box.currentText() == 'ITRF 2020':
                #  https://itrf.ign.fr/ftp/pub/itrf/itrf2020/ITRF2020-psd-doris.dat
                file_name = itrf_name.upper() + '-psd-' + technique_name.lower() + '.dat'
                pass
            download_url = 'https://itrf.ign.fr/ftp/pub/itrf/' + itrf_name.lower() + '/' + file_name
            list = [download_url, file_name]
            Iers_itrf_url_list = Iers_itrf_url_list + [list]
            pass


        combination_url_list = [Ced_raw_url_list, Ced_deal_url_list, Nevada_enu_url_list, Nevada_xyz_url_list,
                                Nevada_plot_url_list, Sopac_input_file_url_list, UNAVCO_itrf08_url_list,
                                UNAVCO_itrf14_url_list, Iers_itrf_url_list]
        target_url_list = []
        for i in combination_url_list:
            if i != []:
                target_url_list = target_url_list + i
        if target_url_list == []:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Prompt', 'No set the file type！')
            return
        print(target_url_list)

        # * wuhan Download
        thread_list = locals()
        thread_list_original_length = len(thread_list)  #
        for i, j in zip(target_url_list, range(len(target_url_list))):
            download_ftp_function = threading.Thread(target=self.WUHAN_function, args=(i[0], i[1]))
            thread_list['thread_' + str(j)] = []
            thread_list['thread_' + str(j)].append(download_ftp_function)
            pass
        # view thread_list
        ftp_list_length = len(thread_list) - thread_list_original_length
        self.download_Progress_bar.setRange(0, int(ftp_list_length))
        for j in range(ftp_list_length):
            thread_list['thread_' + str(j)][0].start()
        for j in range(ftp_list_length):
            thread_list['thread_' + str(j)][0].join()
        pass

        #  19. dispaly detail
        function_end_time = datetime.now()
        used_time = (function_end_time - function_start_time).seconds
        used_time_miniter = used_time // 60
        used_time_seconds = used_time % 60
        if used_time_miniter == 0:
            used_time = str(used_time_seconds) + 's'
        else:
            used_time = str(used_time_miniter) + 'min' + str(used_time_seconds) + 's'
            pass
        #
        self.show_download_information.setText('Total Download task:%d  success:%d  failure:%d （Time:%s）               Download Completed！' % ((len(successful_library) + len(failed_library)), len(successful_library), len(failed_library), used_time))
        self.download_Progress_bar.setValue(int(len(target_url_list)))
        self.show_download_process_state.setText('')
        # print('Download end')

    # help
    def open_download_help_file_but_line(self):
        self.s = open_download_help_file_windows01()
        self.s.show()


    def download_details_report_view(self):
        self.s = download_details_report_main01(successful_library, failed_library)
        self.s.show()


# -------------------------------------------------------------------------------------------------
""" download_details gui """
class download_details_report_main01(QWidget):
    def __init__(self, success, fail):
        super().__init__()
        self.setWindowTitle('Log')
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

        self.show_text.append('Download Log')
        self.show_text.append('Total Task:%d  success:%d  failure:%d' %(all, len(success), len(fail)))
        self.show_text.append('Format : [’Download URL‘,’Filename‘]')
        self.show_text.append('\n')
        self.show_text.append('Success :')
        for i in success:
            self.show_text.append(str(i))
        self.show_text.append('\n')

        if len(fail) != 0:
            self.show_text.append('Failure :')
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
        self.setWindowTitle('Help')
        self.browser = QWebEngineView()
        url = str(curdir) + r'/tutorial/GDDS User Manual.html'
        self.browser.setUrl(QUrl.fromLocalFile(url))
        # self.browser.load(QUrl(QFileInfo("./GDDS User Manual.html").absoluteFilePath()))
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
        self.setGeometry(360/1920*win_width, 105/1080*win_height, 1250/1920*win_width, 870/1080*win_height)
        self.browser = QWebEngineView()
        curdir = os.getcwd()
        url = str(curdir) + r'/templates/TempDisplayMapTemplate02.html'
        self.browser.setUrl(QUrl.fromLocalFile(url))
        # self.browser.load(QUrl(QFileInfo("./templates/TempDisplayMapTemplate02.html").absoluteFilePath()))
        self.setCentralWidget(self.browser)


# -------------------------------------------------------------------------------------------------
""" Return to map gui """
class Return_Map_Names(QMainWindow):
    def __init__(self, route):
        super().__init__()
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle('Station Map')
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
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = Time_Serise_Download()
    win.show()
    sys.exit(app.exec_())