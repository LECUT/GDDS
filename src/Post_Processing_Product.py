from ftplib import FTP_TLS as FTP
import socket
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QIcon
import sys
import gnsscal
from datetime import *
from time import sleep
import requests
import requests_ftp
import threading
import os
import json
import platform
from retrying import retry
import shutil
import subprocess
import _thread as thread
from bs4 import BeautifulSoup
from PyQt5.QtCore import QUrl, Qt, QLocale, QDate, QDateTime, QFileInfo
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDesktopWidget, QLabel, QComboBox, QLineEdit, QPushButton, QFileDialog, QMessageBox, QTextEdit, QCheckBox, QDateTimeEdit, QTextEdit, QFrame, QDateTimeEdit, QListWidget, QAction, QListWidgetItem, QProgressBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
import resources_rc
import global_var
JD = 3.21
MJD = 1.23

global curdir
curdir = os.getcwd()

'''
-----------------------------------------------------------------------------------------------------------------------
Function: Download post-processing product 
Principle: 1. Preparation stage. Acquisition of time (year, day of year, GPS week, day of the week).
2. Generate the target URL address. File type selection judgment - > time list cycle - > splicing to generate target URL list
   (URL list format: [[url1, file_name1], [URL2, file_name2], ~])
3. Merge to generate a total URL list. Merge all the URL lists generated in step 2 into one total URL list
4. Crawler download phase. Execute in the same session: simulate login (after login, there is a jump of the interface. Only after the program execution completes the jump of the interface can valid cookie information be generated)
   ——>Loop total URL list - > execute URL web address - > write file (multithreading)
-----------------------------------------------------------------------------------------------------------------------
'''

# -------------------------------------------------------------------------------------------------
""" post processing product gui """
class Analysis_Center_Products(QWidget):
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
        self.setWindowTitle("Post-Processing Product")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        # print('screen size', win_width, win_height)
        if win_width <= 720:
            if win_height <= 480:
                self.setFixedSize(995 /1280*win_width, 830/1080*win_height)
            elif win_height <= 500:
                self.setFixedSize(995 /1450*win_width, 830/1080*win_height)
            else:
                self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        elif win_width <= 800 and win_width > 720:
            if win_height <= 500:
                self.setFixedSize(995/1520*win_width, 830/1080*win_height)
            elif win_height <= 515:
                self.setFixedSize(995/1480*win_width, 820/1080*win_height)
            elif win_height <= 600:
                self.setFixedSize(995/1050*win_width, 790/1080*win_height)
            self.move((screen.width() - 935/1040*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 840 and win_width > 800:
            self.setFixedSize(995/1260*win_width, 830/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 960 and win_width > 840:
            if win_height <= 550:
                self.setFixedSize(995/1250*win_width, 810/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            elif win_height <= 720:
                self.setFixedSize(995/1280*win_width, 770/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 800/1080*win_height)/2)
            else:
                self.setFixedSize(995/1320*win_width, 810/1080*win_height)
                self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1024 and win_width > 960:
            self.setFixedSize(995/1290*win_width, 740/1080*win_height)
            self.move((screen.width() - 935/1200*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1152 and win_width > 1024:
            self.setFixedSize(995/1500*win_width, 740/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1176 and win_width > 1152:
            self.setFixedSize(995/1500*win_width, 780/1080*win_height)
            self.move((screen.width() - 935/1280*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1280 and win_width > 1176:
            self.setFixedSize(995/1525*win_width, 680/1080*win_height)
            self.move((screen.width() - 935/1320*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1366 and win_width > 1280:
            self.setFixedSize(995/1730*win_width, 680/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1440 and win_width > 1366:
            self.setFixedSize(995/1750*win_width, 680/1080*win_height)
            self.move((screen.width() - 935/1350*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1600 and win_width > 1440:
            self.setFixedSize(995/1800*win_width, 680/1080*win_height)
            self.move((screen.width() - 935/1420*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1680 and win_width > 1600:
            self.setFixedSize(995/1830*win_width, 680/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 780/1080*win_height)/2)
        elif win_width <= 1792 and win_width > 1680:
            self.setFixedSize(995/1820*win_width, 580/1080*win_height)
            self.move((screen.width() - 935/1650*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        elif win_width <= 2048 and win_width > 1920:
            self.setFixedSize(995/1920*win_width, 600/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 820/1080*win_height)/2)
        elif win_width <= 2560 and win_width > 1920:
            self.setFixedSize(995/1920*win_width, 600/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 800/1080*win_height)/2)
        else:
            self.setFixedSize(995/1920*win_width, 580/1080*win_height)
            self.move((screen.width() - 935/1920*win_width)/2, (screen.height() - 580/1080*win_height)/2)

        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))


        global Now_Code_Surrind
        Now_Code_Surrind = os.getcwd()
        self.setup_ui()
    # -------------------------------------------------------------------------------------------------
    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        if win_width <= 700:
            # win_width = win_width + 630
            if win_height <= 480:
                win_width = win_width + 300
            elif win_height <= 500:
                win_width = win_width + 250
            elif win_height <= 600:
                win_width = win_width + 350
            else:
                win_width = win_width + 630
            win_height = win_height + 200
        elif win_width <= 800:
            # win_width = win_width + 630
            if win_height <= 500:
                win_width = win_width + 330
            elif win_height < 600:
                win_width = win_width + 250
            else:
                win_width = win_width + 630
                win_height = win_height + 30
            win_height = win_height + 200
        elif win_width <= 1024:
            win_width = win_width + 480
            win_height = win_height + 230
        elif win_width <= 1152:
            win_width = win_width + 300
            win_height = win_height + 230
        elif win_width <= 1176:
            win_width = win_width + 300
            win_height = win_height + 230
        elif win_width <= 1280:
            win_width = win_width + 300
            win_height = win_height + 150
        elif win_width <= 1366:
            win_width = win_width + 140
            win_height = win_height + 150
        elif win_width <= 1440:
            win_width = win_width + 160
            win_height = win_height + 150
        elif win_width <= 1600:
            win_width = win_width + 140
            win_height = win_height + 150
        elif win_width <= 1680:
            win_width = win_width + 100
            win_height = win_height + 200
        elif win_width < 1920:
            win_width = win_width + 100
            win_height = win_height + 400

        print(win_width)
        print(win_height)

        self.choose_dowunload_source_label = QLabel('Institution :', self)
        self.choose_dowunload_source_label.setFont(QFont("Times New Roman"))
        self.choose_dowunload_source_label.setGeometry(45/1920*win_width, 25/1080*win_height, 400/1920*win_width, 30/1080*win_height)

        self.choose_local_area_box = QComboBox(self)
        self.choose_local_area_box.setGeometry(180/1920*win_width, 21/1080*win_height, 250/1920*win_width, 35/1080*win_height)
        self.choose_local_area_box.addItems(['IGS', 'CODE(Switzerland)', 'JPL(USA)', 'GFZ(Germany)', 'EMR(Canada)',
                                             'ESA(Europe)', 'CAS(China)', 'WHU(China)', 'GRG(France)', 'MIT(USA)',
                                             'SIO(USA)', 'NGS(USA)', 'UPC(Spain)'])
        self.choose_local_area_box.currentTextChanged.connect(self.dowunload_source_changed)

        self.choose_product_url_box = QComboBox(self)
        self.choose_product_url_box.setGeometry(440/1920*win_width, 21/1080*win_height, 400/1920*win_width, 35/1080*win_height)
        self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/',  'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
                                              'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/', 'http://garner.ucsd.edu/pub/products/'])
        self.select_url = self.choose_product_url_box.currentText()
        self.choose_product_url_box.currentTextChanged.connect(self.dowunload_url_changed)
        self.choose_product_url_box.setEnabled(True)

        self.tips_btn = QPushButton(self)
        self.tips_btn.setGeometry(890 / 1920 * win_width, 21 / 1080 * win_height, 54 / 1920 * win_width,
                                   27 / 1080 * win_height)
        self.tips_btn.setStyleSheet("QPushButton{border-image: url(':/icon/tips.png')}")
        self.tips_btn.clicked.connect(self.tips_info_links)

        self.choose_download_files_type_label = QLabel('Product Type :', self)
        self.choose_download_files_type_label.setFont(QFont("Times New Roman"))
        self.choose_download_files_type_label.move(35/1920*win_width, 132/1080*win_height)

        # -------------------------------------------------------------------------------------------------
        # IGS product
        # Precise Ephemeris
        self.igs_Precisi_track_check = QCheckBox('', self)
        self.igs_Precisi_track_check.move(180/1920*win_width, 75/1080*win_height)

        self.igs_Precisi_track_box = QComboBox(self)
        self.igs_Precisi_track_box.setGeometry(203/1920*win_width, 71/1080*win_height, 97/1920*win_width, 28/1080*win_height)
        self.igs_Precisi_track_box.addItems(['Final', 'Rapid', 'Ultra'])

        self.igs_Precisi_track_label = QLabel('Precise Ephemeris(.sp3)', self)
        self.igs_Precisi_track_label.move(307/1920*win_width, 77/1080*win_height)

        # Precise Clock
        self.igs_Precisi_clock_check = QCheckBox('', self)
        self.igs_Precisi_clock_check.move(560/1920*win_width, 75/1080*win_height)

        self.igs_Precisi_clock_box = QComboBox(self)
        self.igs_Precisi_clock_box.setGeometry(583/1920*win_width, 71/1080*win_height, 105/1920*win_width, 28/1080*win_height)
        self.igs_Precisi_clock_box.addItems(['Final', 'Rapid'])

        self.igs_Precisi_clock_interv_box = QComboBox(self)
        self.igs_Precisi_clock_interv_box.setGeometry(692/1920*win_width, 71/1080*win_height, 80/1920*win_width, 28/1080*win_height)
        self.igs_Precisi_clock_interv_box.addItems(['30s', '300s'])

        self.igs_Precisi_clock_label = QLabel('Precise Clock(.clk)', self)
        self.igs_Precisi_clock_label.move(775/1920*win_width, 77/1080*win_height)

        # troposphere
        self.igs_tro_check = QCheckBox(self)
        self.igs_tro_check.move(180/1920*win_width, 120/1080*win_height)

        add_items = json.load(open(str(curdir) + r'/lib/json/IGS_Tro.json', 'r'))
        self.igs_tro_box = ComboCheckBox_rewrite(self)
        self.igs_tro_box.setGeometry(203/1920*win_width, 116/1080*win_height, 97/1920*win_width, 28/1080*win_height)
        self.igs_tro_box.loadItems(add_items)

        self.igs_tro_label = QLabel('Trop(.zpd)', self)
        self.igs_tro_label.move(307/1920*win_width, 122/1080*win_height)

        # weekly station positions
        self.igs_snx_check = QCheckBox(self)
        self.igs_snx_check.move(560/1920*win_width, 120/1080*win_height)

        self.igs_snx_box = QComboBox(self)
        self.igs_snx_box.setGeometry(583/1920*win_width, 116/1080*win_height, 105/1920*win_width, 28/1080*win_height)
        self.igs_snx_box.addItems(['Daily', 'Weekly'])

        self.igs_snx_label = QLabel('Solution(.snx)', self)
        self.igs_snx_label.move(695/1920*win_width, 122/1080*win_height)

        # Earth rotation parameters
        self.igs_erp_check = QCheckBox(self)
        self.igs_erp_check.move(180/1920*win_width, 165/1080*win_height)

        self.igs_erp_box = QComboBox(self)
        self.igs_erp_box.setGeometry(203/1920*win_width, 161/1080*win_height, 97/1920*win_width, 28/1080*win_height)
        self.igs_erp_box.addItems(['Final', 'Rapid', 'Ultra'])

        self.igs_erp_label = QLabel('Earth Rotation Parm(.erp)', self)
        self.igs_erp_label.move(307/1920*win_width, 167/1080*win_height)

        # satellite antenna phase center offset
        self.igs_atx_check = QCheckBox(self)
        self.igs_atx_check.move(560/1920*win_width, 165/1080*win_height)

        self.igs_atx_box = QComboBox(self)
        self.igs_atx_box.setGeometry(583/1920*win_width, 160/1080*win_height, 105/1920*win_width, 28/1080*win_height)
        self.igs_atx_box.addItems(['igs14', 'igs14_2223', 'igs20', 'igs20_2221', 'igs08', 'igs05'])

        self.igs_atx_label = QLabel('Antenna Phase Center Model(.atx)', self)
        self.igs_atx_label.move(695/1920*win_width, 167/1080*win_height)

        # Ionosphere
        self.igs_i_check = QCheckBox(self)
        self.igs_i_check.move(180/1920*win_width, 210/1080*win_height)

        self.igs_i_box = QComboBox(self)
        self.igs_i_box.setGeometry(203/1920*win_width, 206/1080*win_height, 97/1920*win_width, 28/1080*win_height)
        self.igs_i_box.addItems(['Final', 'Rapid'])

        self.igs_i_label = QLabel('Global Ionosphere Maps(.*i)', self)
        self.igs_i_label.move(307/1920*win_width, 212/1080*win_height)

        # Rate of ionosphere TEC
        self.igs_rate_TEC_check = QCheckBox('Rate of TEC Index(.*f)', self)
        self.igs_rate_TEC_check.move(560/1920*win_width, 210/1080*win_height)

        # self.igs_Precisi_track_check.setVisible(False)
        # self.igs_Precisi_clock_check.setVisible(False)
        # self.igs_tro_check.setVisible(False)
        # self.igs_snx_check.setVisible(False)
        # self.igs_erp_check.setVisible(False)
        # self.igs_atx_check.setVisible(False)
        # self.igs_Precisi_track_box.setVisible(False)
        # self.igs_Precisi_track_label.setVisible(False)
        # self.igs_Precisi_clock_box.setVisible(False)
        # self.igs_Precisi_clock_interv_box.setVisible(False)
        # self.igs_Precisi_clock_label.setVisible(False)
        # self.igs_tro_box.setVisible(False)
        # self.igs_tro_label.setVisible(False)
        # self.igs_snx_box.setVisible(False)
        # self.igs_snx_label.setVisible(False)
        # self.igs_erp_box.setVisible(False)
        # self.igs_erp_label.setVisible(False)
        # self.igs_atx_box.setVisible(False)
        # self.igs_atx_label.setVisible(False)
        # self.igs_i_check.setVisible(False)
        # self.igs_i_box.setVisible(False)
        # self.igs_i_label.setVisible(False)
        # self.igs_rate_TEC_check.setVisible(False)

        # IGS product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # CODE product
        self.code_Precisi_track_check = QCheckBox(self)
        self.code_Precisi_track_check.move(180/1920*win_width, 70/1080*win_height)

        # Precise Ephemeris
        self.code_Precisi_track_box = QComboBox(self)
        self.code_Precisi_track_box.setGeometry(203/1920*win_width, 66/1080*win_height, 82/1920*win_width, 28/1080*win_height)
        self.code_Precisi_track_box.addItems(['G/R', 'MGEX'])

        self.code_Precisi_track_label = QLabel('Precise Ephemeris(.sp3/.eph)', self)
        self.code_Precisi_track_label.move(292/1920*win_width, 72/1080*win_height)

        # Precise Clock
        self.code_Precisi_clock_check = QCheckBox('', self)
        self.code_Precisi_clock_check.move(580/1920*win_width, 70/1080*win_height)

        self.code_Precisi_clock_interv_box = QComboBox(self)
        self.code_Precisi_clock_interv_box.setGeometry(602/1920*win_width, 66/1080*win_height, 110/1920*win_width, 28/1080*win_height)
        self.code_Precisi_clock_interv_box.addItems(['5s G/R', '30s G/R', '30s MGEX'])

        self.code_Precisi_clock_label = QLabel('Precise Clock(.clk)', self)
        self.code_Precisi_clock_label.move(715/1920*win_width, 73/1080*win_height)

        # Satellite Attitude
        self.code_obx_check = QCheckBox(self)
        self.code_obx_check.move(180/1920*win_width, 105/1080*win_height)

        self.code_obx_box = QComboBox(self)
        self.code_obx_box.setGeometry(203/1920*win_width, 101/1080*win_height, 82/1920*win_width, 28/1080*win_height)
        self.code_obx_box.addItems(['G/R', 'MGEX'])

        self.code_obx_label = QLabel('Satellite Attitude Info(.obx)', self)
        self.code_obx_label.move(292/1920*win_width, 107/1080*win_height)

        # Earth rotation parameters
        self.code_erp_check = QCheckBox(self)
        self.code_erp_check.move(580/1920*win_width, 105/1080*win_height)

        self.code_erp_box = QComboBox(self)
        self.code_erp_box.setGeometry(603/1920*win_width, 101/1080*win_height, 82/1920*win_width, 28/1080*win_height)
        self.code_erp_box.addItems(['G/R', 'MGEX'])

        # Earth Rotation Parm
        self.code_erp_label = QLabel('Earth Rotation Parm(.erp)', self)
        self.code_erp_label.move(692/1920*win_width, 107/1080*win_height)

        # Ionosphere
        self.code_ion_check = QCheckBox('ION-Spherical Harmonic Model(.ion)', self)
        self.code_ion_check.move(180/1920*win_width, 140/1080*win_height)

        self.code_i_check = QCheckBox('Global Ionosphere Maps(.*i)', self)
        self.code_i_check.move(580/1920*win_width, 140/1080*win_height)

        # OSB Bias-SINEX
        self.code_bia_check = QCheckBox('', self)
        self.code_bia_check.move(180/1920*win_width, 175/1080*win_height)

        self.code_bia_box = QComboBox(self)
        self.code_bia_box.setGeometry(203/1920*win_width, 171/1080*win_height, 82/1920*win_width, 28/1080*win_height)
        self.code_bia_box.addItems(['G/R', 'MGEX'])

        self.code_bia_label = QLabel('OSB Bias-SINEX(.bia)', self)
        self.code_bia_label.move(292/1920*win_width, 177/1080*win_height)

        # 3-Day station positions
        self.code_snx_check = QCheckBox('3-Day Solution(.snx)', self)
        self.code_snx_check.move(580/1920*win_width, 175/1080*win_height)

        # Differential Code Bias
        self.code_dcb_check = QCheckBox('', self)
        self.code_dcb_check.move(180/1920*win_width, 210/1080*win_height)

        self.code_dcb_box = QComboBox(self)
        self.code_dcb_box.setGeometry(203/1920*win_width, 206/1080*win_height, 82/1920*win_width, 28/1080*win_height)
        self.code_dcb_box.addItems(['P1-C1', 'P1-P2', 'P2-C2', 'MGEX'])

        self.code_dcb_label = QLabel('Differential Code Bias(.dcb)', self)
        self.code_dcb_label.move(289/1920*win_width, 212/1080*win_height)

        # troposphere
        self.code_tro_check = QCheckBox('Trop(.tro)', self)
        self.code_tro_check.move(580/1920*win_width, 210/1080*win_height)

        self.code_Precisi_track_check.setVisible(False)
        self.code_Precisi_clock_check.setVisible(False)
        self.code_obx_check.setVisible(False)
        self.code_ion_check.setVisible(False)
        self.code_i_check.setVisible(False)
        self.code_tro_check.setVisible(False)
        self.code_erp_check.setVisible(False)
        self.code_dcb_check.setVisible(False)
        self.code_bia_check.setVisible(False)
        self.code_snx_check.setVisible(False)
        self.code_Precisi_clock_interv_box.setVisible(False)
        self.code_Precisi_clock_label.setVisible(False)
        self.code_Precisi_track_box.setVisible(False)
        self.code_Precisi_track_label.setVisible(False)
        self.code_obx_box.setVisible(False)
        self.code_obx_label.setVisible(False)
        self.code_erp_box.setVisible(False)
        self.code_erp_label.setVisible(False)
        self.code_bia_box.setVisible(False)
        self.code_bia_label.setVisible(False)
        self.code_dcb_box.setVisible(False)
        self.code_dcb_label.setVisible(False)

        # CODE product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # CAS product
        # ION-Spherical Harmonic Model
        self.cas_ion_check = QCheckBox('ION-Spherical Harmonic Model(.ION)', self)
        self.cas_ion_check.move(180/1920*win_width, 100/1080*win_height)

        # Global Ionosphere Maps
        self.cas_i_check = QCheckBox(self)
        self.cas_i_check.move(590/1920*win_width, 100/1080*win_height)

        self.cas_i_box = QComboBox(self)
        self.cas_i_box.setGeometry(613/1920*win_width, 96/1080*win_height, 170/1920*win_width, 28/1080*win_height)
        self.cas_i_box.addItems(['Final', 'Rapid'])

        self.cas_i_label = QLabel('Global Ionosphere Maps(.*i)', self)
        self.cas_i_label.move(787/1920*win_width, 102/1080*win_height)

        # OSB Bias-SINEX
        self.cas_bia_check = QCheckBox('', self)
        self.cas_bia_check.move(180/1920*win_width, 140/1080*win_height)

        self.cas_bia_box = QComboBox(self)
        # self.cas_bia_box.setGeometry(203/1920*win_width, 139/1080*win_height, 83/1920*win_width, 25/1080*win_height)
        self.cas_bia_box.setGeometry(203/1920*win_width, 139/1080*win_height, 170/1920*win_width, 25/1080*win_height)
        self.cas_bia_box.addItems(['G/R (no APC)', 'MGEX(no APC)', 'MGEX(APC)'])

        self.cas_bia_label = QLabel('OSB Bias-SINEX(.BIA)', self)
        self.cas_bia_label.move(377/1920*win_width, 142/1080*win_height)

        # DCB Bias-SINEX
        self.cas_bsx_check = QCheckBox('', self)
        self.cas_bsx_check.move(590/1920*win_width, 140/1080*win_height)

        self.cas_bsx_box = QComboBox(self)
        self.cas_bsx_box.setGeometry(613/1920*win_width, 139/1080*win_height, 170/1920*win_width, 25/1080*win_height)
        self.cas_bsx_box.addItems(['G/R (no APC)', 'MGEX(no APC)', 'MGEX(APC)'])

        self.cas_bsx_label = QLabel('DCB Bias-SINEX(.BSX)', self)
        self.cas_bsx_label.move(787/1920*win_width, 142/1080*win_height)

        # Differential Code Bias
        self.cas_dcb_check = QCheckBox('', self)
        self.cas_dcb_check.move(180/1920*win_width, 180/1080*win_height)

        self.cas_dcb_box = QComboBox(self)
        self.cas_dcb_box.setGeometry(203/1920*win_width, 179/1080*win_height, 170/1920*win_width, 25/1080*win_height)
        self.cas_dcb_box.addItems(['P1-C1', 'P2-C2'])

        self.cas_dcb_label = QLabel('Differential Code Bias(.DCB)', self)
        self.cas_dcb_label.move(377/1920*win_width, 185/1080*win_height)

        self.cas_dcb_check.setVisible(False)
        self.cas_bia_check.setVisible(False)
        self.cas_bsx_check.setVisible(False)
        self.cas_ion_check.setVisible(False)
        self.cas_i_check.setVisible(False)
        self.cas_dcb_box.setVisible(False)
        self.cas_dcb_label.setVisible(False)
        self.cas_bia_box.setVisible(False)
        self.cas_bsx_box.setVisible(False)
        self.cas_bia_label.setVisible(False)
        self.cas_bsx_label.setVisible(False)
        self.cas_ion_check.setVisible(False)
        self.cas_i_box.setVisible(False)
        self.cas_i_label.setVisible(False)
        # CAS product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # WHU product
        # Precise Ephemeris
        self.whu_Precisi_track_check = QCheckBox('', self)
        self.whu_Precisi_track_check.move(180/1920*win_width, 95/1080*win_height)

        self.whu_Precisi_track_box = QComboBox(self)
        self.whu_Precisi_track_box.setGeometry(200/1920*win_width, 92/1080*win_height, 98/1920*win_width, 29/1080*win_height)
        self.whu_Precisi_track_box.addItems(['Final', 'Rapid', 'Ultra'])

        self.whu_Precisi_track_label = QLabel('MGEX Precise Ephemeris(.sp3)', self)
        self.whu_Precisi_track_label.move(305/1920*win_width, 98/1080*win_height)

        # Precise Clock
        self.whu_Precisi_clock_check = QCheckBox('', self)
        self.whu_Precisi_clock_check.move(560/1920*win_width, 95/1080*win_height)

        self.whu_Precisi_clock_box = QComboBox(self)
        self.whu_Precisi_clock_box.setGeometry(580/1920*win_width, 92/1080*win_height, 98/1920*win_width, 29/1080*win_height)
        self.whu_Precisi_clock_box.addItems(['Final', 'Rapid', 'Ultra'])

        self.whu_Precisi_clock_label = QLabel('MGEX Precise Clock(.clk)', self)
        self.whu_Precisi_clock_label.move(685/1920*win_width, 98/1080*win_height)

        # MGEX OSB Bias-SINEX
        self.whu_bia_check = QCheckBox('   MGEX OSB Bias-SINEX(.bia)', self)
        self.whu_bia_check.move(180/1920*win_width, 140/1080*win_height)

        # Ionosphere
        self.whu_i_check = QCheckBox('', self)
        self.whu_i_check.move(560/1920*win_width, 140/1080*win_height)

        self.whu_i_box = QComboBox(self)
        self.whu_i_box.setGeometry(580/1920*win_width, 138/1080*win_height, 98/1920*win_width, 28/1080*win_height)
        self.whu_i_box.addItems(['Final', 'Rapid'])

        self.whu_i_label = QLabel('Global Ionosphere Maps(.*i)', self)
        self.whu_i_label.move(685/1920*win_width, 144/1080*win_height)

        # Earth rotation parameters
        self.whu_erp_check = QCheckBox('', self)
        self.whu_erp_check.move(180/1920*win_width, 185/1080*win_height)

        self.whu_erp_box = QComboBox(self)
        self.whu_erp_box.setGeometry(200/1920*win_width, 182/1080*win_height, 98/1920*win_width, 29/1080*win_height)
        self.whu_erp_box.addItems(['Final', 'Rapid', 'Ultra'])

        self.whu_erp_label = QLabel('MGEX Earth Rotation Parm(.erp)', self)
        self.whu_erp_label.move(305/1920*win_width, 188/1080*win_height)

        self.whu_Precisi_track_check.setVisible(False)
        self.whu_Precisi_clock_check.setVisible(False)
        self.whu_bia_check.setVisible(False)
        self.whu_erp_check.setVisible(False)
        self.whu_i_check.setVisible(False)
        self.whu_Precisi_track_box.setVisible(False)
        self.whu_Precisi_clock_box.setVisible(False)
        self.whu_erp_box.setVisible(False)
        self.whu_i_box.setVisible(False)
        self.whu_Precisi_track_label.setVisible(False)
        self.whu_Precisi_clock_label.setVisible(False)
        self.whu_erp_label.setVisible(False)
        self.whu_i_label.setVisible(False)
        # WHU product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # GFZ product
        # Precise Ephemeris
        self.gfz_Precisi_track_check = QCheckBox('', self)
        self.gfz_Precisi_track_check.move(180/1920*win_width, 80/1080*win_height)

        self.gfz_Precisi_track_box = QComboBox(self)
        self.gfz_Precisi_track_box.setGeometry(203/1920*win_width, 77/1080*win_height, 98/1920*win_width, 29/1080*win_height)
        self.gfz_Precisi_track_box.addItems(['Final', 'Rapid', 'Ultra', 'MGEX'])

        self.gfz_Precisi_track_label = QLabel('Precise Ephemeris(.sp3)', self)
        self.gfz_Precisi_track_label.move(305/1920*win_width, 83/1080*win_height)

        # Precise Clock
        self.gfz_Precisi_clock_check = QCheckBox('', self)
        self.gfz_Precisi_clock_check.move(560/1920*win_width, 80/1080*win_height)

        self.gfz_Precisi_clock_box = QComboBox(self)
        self.gfz_Precisi_clock_box.setGeometry(583/1920*win_width, 77/1080*win_height, 90/1920*win_width, 29/1080*win_height)
        self.gfz_Precisi_clock_box.addItems(['Final', 'Rapid', 'MGEX'])
        self.gfz_Precisi_clock_box.currentTextChanged.connect(self.GFZ_Precisi_clock_box_change)

        self.gfz_Precisi_clock_label = QLabel(self)
        self.gfz_Precisi_clock_label.move(679/1920*win_width, 83/1080*win_height)
        self.gfz_Precisi_clock_label.setText('30s Precise Clock(.clk)      ')

        # Earth rotation parameters
        self.gfz_erp_check = QCheckBox('', self)
        self.gfz_erp_check.move(180/1920*win_width, 120/1080*win_height)

        self.gfz_erp_box = QComboBox(self)
        self.gfz_erp_box.setGeometry(203/1920*win_width, 117/1080*win_height, 98/1920*win_width, 29/1080*win_height)
        self.gfz_erp_box.addItems(['Final', 'Rapid', 'Ultra', 'MGEX'])

        self.gfz_erp_label = QLabel('Earth Rotation Parm(.erp)', self)
        self.gfz_erp_label.move(305/1920*win_width, 123/1080*win_height)

        # Daily station positions
        self.gfz_snx_check = QCheckBox('Daily Solution(.snx)', self)
        self.gfz_snx_check.move(560/1920*win_width, 120/1080*win_height)

        # MGEX OSB Bias-SINEX
        self.gfz_osb_bis_check = QCheckBox('MGEX OSB Bias-SINEX(.bia)', self)
        self.gfz_osb_bis_check.move(180/1920*win_width, 160/1080*win_height)

        # MGEX REL Bias-SINEX
        self.gfz_rel_bis_check = QCheckBox('MGEX REL Bias-SINEX(.bia)', self)
        self.gfz_rel_bis_check.move(560/1920*win_width, 160/1080*win_height)

        # troposphere
        self.gfz_tro_check = QCheckBox('', self)
        self.gfz_tro_check.move(180/1920*win_width, 200/1080*win_height)

        gfz_tro_add_items = json.load(open(str(curdir) + r'/lib/json/GFZ_Trop.json', 'r'))
        self.gfz_tro_box = ComboCheckBox_rewrite(self)
        self.gfz_tro_box.setGeometry(203/1920*win_width, 197/1080*win_height, 98/1920*win_width, 29/1080*win_height)
        self.gfz_tro_box.loadItems(gfz_tro_add_items)

        self.gfz_tro_label = QLabel('Trop(.tro)', self)
        self.gfz_tro_label.move(305/1920*win_width, 203/1080*win_height)

        self.gfz_zpd_check = QCheckBox('', self)
        self.gfz_zpd_check.move(420/1920*win_width, 200/1080*win_height)

        self.gfz_zpd_box = ComboCheckBox_rewrite(self)
        self.gfz_zpd_box.setGeometry(443/1920*win_width, 197/1080*win_height, 98/1920*win_width, 29/1080*win_height)
        self.gfz_zpd_box.loadItems(gfz_tro_add_items)

        self.gfz_zpd_label = QLabel('Trop(.zpd)', self)
        self.gfz_zpd_label.move(545/1920*win_width, 203/1080*win_height)

        # MGEX Satellite Attitude
        self.gfz_obx_check = QCheckBox('MGEX Satellite Attitude Info(.obx)', self)
        self.gfz_obx_check.move(660/1920*win_width, 200/1080*win_height)

        self.gfz_Precisi_track_check.setVisible(False)
        self.gfz_Precisi_clock_check.setVisible(False)
        self.gfz_tro_check.setVisible(False)
        self.gfz_zpd_check.setVisible(False)
        self.gfz_obx_check.setVisible(False)
        self.gfz_osb_bis_check.setVisible(False)
        self.gfz_rel_bis_check.setVisible(False)
        self.gfz_erp_check.setVisible(False)
        self.gfz_snx_check.setVisible(False)
        self.gfz_Precisi_track_box.setVisible(False)
        self.gfz_Precisi_track_label.setVisible(False)
        self.gfz_Precisi_clock_box.setVisible(False)
        self.gfz_tro_box.setVisible(False)
        self.gfz_zpd_box.setVisible(False)
        self.gfz_Precisi_clock_label.setVisible(False)
        self.gfz_zpd_label.setVisible(False)
        self.gfz_tro_label.setVisible(False)
        self.gfz_erp_box.setVisible(False)
        self.gfz_erp_label.setVisible(False)
        # GFZ product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # ESA product
        # Precise Ephemeris
        self.esa_Precisi_track_check = QCheckBox('Precise Ephemeris(.sp3)', self)
        self.esa_Precisi_track_check.move(180/1920*win_width, 95/1080*win_height)

        # Precise Clock
        self.esa_Precisi_clock_check = QCheckBox('30s Precise Clock(.clk)', self)
        self.esa_Precisi_clock_check.move(550/1920*win_width, 95/1080*win_height)

        # Precise Clock
        self.esa_erp_check = QCheckBox('Earth Rotation Parm(.erp)', self)
        self.esa_erp_check.move(180/1920*win_width, 135/1080*win_height)

        # Daily station positions
        self.esa_snx_check = QCheckBox('Daily Solution(.snx)', self)
        self.esa_snx_check.move(550/1920*win_width, 135/1080*win_height)

        # Earth rotation parameters
        self.esa_i_check = QCheckBox(self)
        self.esa_i_check.move(180/1920*win_width, 175/1080*win_height)

        # Ionosphere
        self.esa_i_box = QComboBox(self)
        self.esa_i_box.setGeometry(203/1920*win_width, 171/1080*win_height, 97/1920*win_width, 28/1080*win_height)
        self.esa_i_box.addItems(['Final', 'Rapid'])

        self.esa_i_label = QLabel('Global Ionosphere Maps(.*i)', self)
        self.esa_i_label.move(307/1920*win_width, 177/1080*win_height)

        self.esa_Precisi_track_check.setVisible(False)
        self.esa_Precisi_clock_check.setVisible(False)
        self.esa_erp_check.setVisible(False)
        self.esa_snx_check.setVisible(False)
        self.esa_i_check.setVisible(False)
        self.esa_i_box.setVisible(False)
        self.esa_i_label.setVisible(False)
        # ESA product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # JPL product
        # Precise Ephemeris
        self.jpl_Precisi_track_check = QCheckBox('Precise Ephemeris(.sp3)', self)
        self.jpl_Precisi_track_check.move(180/1920*win_width, 80/1080*win_height)

        # Precise Clock
        self.jpl_Precisi_clock_check = QCheckBox('30s Precise Clock(.clk)', self)
        self.jpl_Precisi_clock_check.move(550/1920*win_width, 80/1080*win_height)

        # Earth rotation parameters
        self.jpl_erp_check = QCheckBox('Earth Rotation Parm(.erp)', self)
        self.jpl_erp_check.move(180/1920*win_width, 120/1080*win_height)

        # Satellite Yaw
        self.jpl_yaw_check = QCheckBox('Satellite Yaw Info(.yaw)', self)
        self.jpl_yaw_check.move(550/1920*win_width, 120/1080*win_height)

        # Daily station positions
        self.jpl_snx_check = QCheckBox('Daily Solution(.snx)', self)
        self.jpl_snx_check.move(180/1920*win_width, 160/1080*win_height)

        self.jpl_tro_check = QCheckBox('Trop(.tro)', self)
        self.jpl_tro_check.move(550/1920*win_width, 160/1080*win_height)

        # Ionosphere
        self.jpl_i_check = QCheckBox(self)
        self.jpl_i_check.move(180/1920*win_width, 200/1080*win_height)

        self.jpl_i_box = QComboBox(self)
        self.jpl_i_box.setGeometry(203/1920*win_width, 196/1080*win_height, 97/1920*win_width, 28/1080*win_height)
        self.jpl_i_box.addItems(['Final', 'Rapid'])

        self.jpl_i_label = QLabel('Global Ionosphere Maps(.*i)', self)
        self.jpl_i_label.move(307/1920*win_width, 202/1080*win_height)

        self.jpl_Precisi_track_check.setVisible(False)
        self.jpl_Precisi_clock_check.setVisible(False)
        self.jpl_erp_check.setVisible(False)
        self.jpl_snx_check.setVisible(False)
        self.jpl_tro_check.setVisible(False)
        self.jpl_yaw_check.setVisible(False)
        self.jpl_i_check.setVisible(False)
        self.jpl_i_box.setVisible(False)
        self.jpl_i_label.setVisible(False)
        # JPL product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # MIT product
        # Precise Ephemeris
        self.mit_Precisi_track_check = QCheckBox('Precise Ephemeris(.sp3)', self)
        self.mit_Precisi_track_check.move(180/1920*win_width, 105/1080*win_height)

        # Precise Clock
        self.mit_Precisi_clock_check = QCheckBox('30s Precise Clock(.clk)', self)
        self.mit_Precisi_clock_check.move(550/1920*win_width, 105/1080*win_height)

        # Earth rotation parameters
        self.mit_erp_check = QCheckBox('Earth Rotation Parm(.erp)', self)
        self.mit_erp_check.move(180/1920*win_width, 175/1080*win_height)

        # Daily station positions
        self.mit_snx_check = QCheckBox('Daily Solution(.snx)', self)
        self.mit_snx_check.move(550/1920*win_width, 175/1080*win_height)

        self.mit_Precisi_track_check.setVisible(False)
        self.mit_Precisi_clock_check.setVisible(False)
        self.mit_erp_check.setVisible(False)
        self.mit_snx_check.setVisible(False)
        # MIT product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # GRG product
        # Precise Ephemeris
        self.grg_Precisi_track_check = QCheckBox(self)
        self.grg_Precisi_track_check.move(180/1920*win_width, 90/1080*win_height)

        self.grg_Precisi_track_box = QComboBox(self)
        self.grg_Precisi_track_box.setGeometry(203/1920*win_width, 86/1080*win_height, 82/1920*win_width, 28/1080*win_height)
        self.grg_Precisi_track_box.addItems(['G/R', 'MGEX'])

        self.grg_Precisi_track_label = QLabel('Precise Ephemeris(.sp3)', self)
        self.grg_Precisi_track_label.move(292/1920*win_width, 92/1080*win_height)

        # Precise Clock
        self.grg_Precisi_clock_check = QCheckBox(self)
        self.grg_Precisi_clock_check.move(550/1920*win_width, 90/1080*win_height)

        self.grg_Precisi_clock_box = QComboBox(self)
        self.grg_Precisi_clock_box.setGeometry(573/1920*win_width, 86/1080*win_height, 82/1920*win_width, 28/1080*win_height)
        self.grg_Precisi_clock_box.addItems(['G/R', 'MGEX'])

        self.grg_Precisi_clock_label = QLabel('Precise Clock(.clk)', self)
        self.grg_Precisi_clock_label.move(662/1920*win_width, 92/1080*win_height)

        # MGEX OSB Bias-SINEX
        self.grg_osb_check = QCheckBox('MGEX OSB Bias-SINEX(.bia)', self)
        self.grg_osb_check.move(180/1920*win_width, 135/1080*win_height)

        # MGEX Satellite Attitude
        self.grg_obx_check = QCheckBox('MGEX Satellite Attitude Info(.obx)', self)
        self.grg_obx_check.move(550/1920*win_width, 135/1080*win_height)

        # Earth rotation parameters
        self.grg_erp_check = QCheckBox('Earth Rotation Parm(.erp)', self)
        self.grg_erp_check.move(180/1920*win_width, 180/1080*win_height)

        # Daily station positions
        self.grg_snx_check = QCheckBox(self)
        self.grg_snx_check.move(550/1920*win_width, 180/1080*win_height)

        self.grg_snx_box = QComboBox(self)
        self.grg_snx_box.setGeometry(573/1920*win_width, 176/1080*win_height, 82/1920*win_width, 28/1080*win_height)
        self.grg_snx_box.addItems(['G/R', 'MGEX'])

        self.grg_snx_label = QLabel('Daily Solution(.snx)', self)
        self.grg_snx_label.move(662/1920*win_width, 182/1080*win_height)

        self.grg_Precisi_track_check.setVisible(False)
        self.grg_Precisi_clock_check.setVisible(False)
        self.grg_Precisi_track_box.setVisible(False)
        self.grg_Precisi_track_label.setVisible(False)
        self.grg_Precisi_clock_box.setVisible(False)
        self.grg_Precisi_clock_label.setVisible(False)
        self.grg_snx_box.setVisible(False)
        self.grg_snx_label.setVisible(False)
        self.grg_osb_check.setVisible(False)
        self.grg_obx_check.setVisible(False)
        self.grg_erp_check.setVisible(False)
        self.grg_snx_check.setVisible(False)
        # GRG product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # EMR product
        # Precise Ephemeris
        self.emr_Precisi_track_check = QCheckBox('Precise Ephemeris(.sp3)', self)
        self.emr_Precisi_track_check.move(180/1920*win_width, 105/1080*win_height)

        # Precise Clock
        self.emr_Precisi_clock_check = QCheckBox('30s Precise Clock(.clk)', self)
        self.emr_Precisi_clock_check.move(550/1920*win_width, 105/1080*win_height)

        # Earth rotation parameters
        self.emr_erp_check = QCheckBox('Earth Rotation Parm(.erp)', self)
        self.emr_erp_check.move(180/1920*win_width, 175/1080*win_height)

        # Daily station positions
        self.emr_snx_check = QCheckBox('Daily Solution(.snx)', self)
        self.emr_snx_check.move(550/1920*win_width, 175/1080*win_height)

        self.emr_Precisi_track_check.setVisible(False)
        self.emr_Precisi_clock_check.setVisible(False)
        self.emr_erp_check.setVisible(False)
        self.emr_snx_check.setVisible(False)
        # EMR product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # SIO product
        # Precise Ephemeris
        self.sio_Precisi_track_check = QCheckBox('', self)
        self.sio_Precisi_track_check.move(180/1920*win_width, 105/1080*win_height)

        self.sio_Precisi_track_box = QComboBox(self)
        self.sio_Precisi_track_box.setGeometry(203/1920*win_width, 102/1080*win_height, 95/1920*win_width, 29/1080*win_height)
        self.sio_Precisi_track_box.addItems(['Final', 'Rapid'])

        self.sio_Precisi_track_label = QLabel('Precise Ephemeris(.sp3)', self)
        self.sio_Precisi_track_label.move(305/1920*win_width, 108/1080*win_height)

        # Daily station positions
        self.sio_snx_check = QCheckBox('Daily Solution(.snx)', self)
        self.sio_snx_check.move(590/1920*win_width, 105/1080*win_height)

        # Earth rotation parameters
        self.sio_erp_check = QCheckBox('', self)
        self.sio_erp_check.move(180/1920*win_width, 175/1080*win_height)

        self.sio_erp_box = QComboBox(self)
        self.sio_erp_box.setGeometry(203/1920*win_width, 172/1080*win_height, 95/1920*win_width, 29/1080*win_height)
        self.sio_erp_box.addItems(['Final', 'Rapid'])

        self.sio_erp_label = QLabel('Earth Rotation Parm(.erp)', self)
        self.sio_erp_label.move(305/1920*win_width, 178/1080*win_height)

        self.sio_Precisi_track_check.setVisible(False)
        self.sio_erp_check.setVisible(False)
        self.sio_snx_check.setVisible(False)
        self.sio_Precisi_track_box.setVisible(False)
        self.sio_Precisi_track_label.setVisible(False)
        self.sio_erp_box.setVisible(False)
        self.sio_erp_label.setVisible(False)
        # SIO product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # NGS product
        # Precise Ephemeris
        self.ngs_Precisi_track_check = QCheckBox('Precise Ephemeris(.sp3)', self)
        self.ngs_Precisi_track_check.move(180/1920*win_width, 105/1080*win_height)

        # Daily station positions
        self.ngs_snx_check = QCheckBox('Daily Solution(.snx)', self)
        self.ngs_snx_check.move(550/1920*win_width, 105/1080*win_height)

        # Earth rotation parameters
        self.ngs_erp_check = QCheckBox('Earth Rotation Parm(.erp)', self)
        self.ngs_erp_check.move(180/1920*win_width, 175/1080*win_height)

        self.ngs_Precisi_track_check.setVisible(False)
        self.ngs_erp_check.setVisible(False)
        self.ngs_snx_check.setVisible(False)
        # NGS product
        # -------------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------
        # UPC product
        # Ionosphere
        self.upc_i_check = QCheckBox(self)
        self.upc_i_check.move(180/1920*win_width, 135/1080*win_height)

        self.upc_i_box = QComboBox(self)
        self.upc_i_box.setGeometry(203/1920*win_width, 131/1080*win_height, 97/1920*win_width, 28/1080*win_height)
        self.upc_i_box.addItems(['Final', 'Rapid'])

        self.upc_i_label = QLabel('Global Ionosphere Maps(.*i)', self)
        self.upc_i_label.move(307/1920*win_width, 137/1080*win_height)

        self.upc_i_check.setVisible(False)
        self.upc_i_box.setVisible(False)
        self.upc_i_label.setVisible(False)
        # UPC product
        # -------------------------------------------------------------------------------------------------

        self.choose_start_end_time_label = QLabel('Time Range :', self)
        self.choose_start_end_time_label.setFont(QFont("Times New Roman"))
        self.choose_start_end_time_label.setGeometry(35/1920*win_width, 281/1080*win_height, 400/1920*win_width, 30/1080*win_height)

        #  day, month, year
        self.YearMonDay_label0101 = QLabel('Year-Month-Day :', self)
        self.YearMonDay_label0101.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0101.move(180/1920*win_width, 257/1080*win_height)
        # Starte Time
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.start_time.setLocale(QLocale(QLocale.English))
        self.start_time.setGeometry(440/1920*win_width, 248/1080*win_height, 150/1920*win_width, 30/1080*win_height)
        self.start_time.setDisplayFormat('yyyy-MM-dd')
        self.start_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.start_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.start_time.setCalendarPopup(True)
        self.start_time.dateChanged.connect(self.onDateChanged01)
        # day, month, year
        self.YearMonDay_label0102 = QLabel('Year, Day of Year :', self)
        self.YearMonDay_label0102.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0102.move(180/1920*win_width, 289/1080*win_height)
        # year
        self.changday0201 = QLineEdit(self)
        self.changday0201.setGeometry(440/1920*win_width, 283/1080*win_height, 95/1920*win_width, 30/1080*win_height)
        # doy
        self.changday0202 = QLineEdit(self)
        self.changday0202.setGeometry(540/1920*win_width, 283/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0201.textEdited.connect(self.YearAcumulateDay_to_all01)
        self.changday0202.textEdited.connect(self.YearAcumulateDay_to_all01)

        # GPS Wek
        self.YearMonDay_label0103 = QLabel('GPS Week, Day of Week :', self)
        self.YearMonDay_label0103.setFont(QFont("Times New Roman"))
        self.YearMonDay_label0103.move(180/1920*win_width, 325/1080*win_height)
        # GPS Wek
        self.changday0301 = QLineEdit(self)
        self.changday0301.setGeometry(440/1920*win_width, 318/1080*win_height, 95/1920*win_width, 30/1080*win_height)
        # Sunday
        self.changday0302 = QLineEdit(self)
        self.changday0302.setGeometry(540/1920*win_width, 318/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0301.textEdited.connect(self.GPSweeks_to_all01)
        self.changday0302.textEdited.connect(self.GPSweeks_to_all01)

        # Starte Time
        time_yearmothday = self.start_time.text()
        year = int(time_yearmothday[0:4])
        mon = int(str(time_yearmothday[5:7]))
        day = int(str(time_yearmothday[8:10]))
        conbin_date = date(year, mon, day)
        # Gregorian calendar to year, doy
        year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
        self.changday0201.setText(str(year_accumulate_list[0]))
        self.changday0202.setText(str(year_accumulate_list[1]))
        # Gregorian calendar to GPS Week, Sunday
        GPS_weeks = gnsscal.date2gpswd(conbin_date)
        self.changday0301.setText(str(GPS_weeks[0]))
        self.changday0302.setText(str(GPS_weeks[1]))

        self.time_start_to_end = QLabel('>>>', self)
        self.time_start_to_end.move(604 / 1920 * win_width, 291 / 1080 * win_height)

        # End time
        self.end_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.end_time.setLocale(QLocale(QLocale.English))
        self.end_time.setGeometry(660/1920*win_width, 248/1080*win_height, 150/1920*win_width, 30/1080*win_height)
        self.end_time.setDisplayFormat('yyyy-MM-dd')
        self.end_time.setMinimumDate(QDate.currentDate().addDays(-365 * 40))
        self.end_time.setMaximumDate(QDate.currentDate().addDays(365 * 0))
        self.end_time.setCalendarPopup(True)
        self.end_time.dateChanged.connect(self.onDateChanged02)
        # year
        self.changday0401 = QLineEdit(self)
        self.changday0401.setGeometry(660/1920*win_width, 283/1080*win_height, 95/1920*win_width, 30/1080*win_height)
        # doy
        self.changday0402 = QLineEdit(self)
        self.changday0402.setGeometry(760/1920*win_width, 283/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0401.textEdited.connect(self.YearAcumulateDay_to_all02)
        self.changday0402.textEdited.connect(self.YearAcumulateDay_to_all02)

        # GPS Week
        self.changday0501 = QLineEdit(self)
        self.changday0501.setGeometry(660/1920*win_width, 318/1080*win_height, 95/1920*win_width, 30/1080*win_height)
        # Sunday
        self.changday0502 = QLineEdit(self)
        self.changday0502.setGeometry(760/1920*win_width, 318/1080*win_height, 50/1920*win_width, 30/1080*win_height)
        self.changday0501.textEdited.connect(self.GPSweeks_to_all02)
        self.changday0502.textEdited.connect(self.GPSweeks_to_all02)

        # Initialization end time
        time_yearmothday = self.end_time.text()
        year = int(time_yearmothday[0:4])
        mon = int(str(time_yearmothday[5:7]))
        day = int(str(time_yearmothday[8:10]))
        conbin_date = date(year, mon, day)
        # Gregorian calendar to year, doy
        year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
        self.changday0401.setText(str(year_accumulate_list[0]))
        self.changday0402.setText(str(year_accumulate_list[1]))
        # Gregorian calendar to GPS Week, Sunday
        GPS_weeks = gnsscal.date2gpswd(conbin_date)
        self.changday0501.setText(str(GPS_weeks[0]))
        self.changday0502.setText(str(GPS_weeks[1]))

        # output path
        self.choose_save_path_wuyong_label = QLabel('Output Path :', self)
        self.choose_save_path_wuyong_label.setFont(QFont("Times New Roman"))
        self.choose_save_path_wuyong_label.setGeometry(35/1920*win_width, 370/1080*win_height, 400/1920*win_width, 30/1080*win_height)

        self.show_outsave_files_path_button = QLineEdit(self)
        self.show_outsave_files_path_button.setGeometry(180/1920*win_width, 368/1080*win_height, 700/1920*win_width, 35/1080*win_height)
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        classial_desktop_path = desktop_path + '/' + 'Download'
        self.show_outsave_files_path_button.setText(classial_desktop_path)

        self.choose_outsave_files_path_button = QPushButton('<<<', self)
        self.choose_outsave_files_path_button.setGeometry(895/1920*win_width, 370/1080*win_height, 45/1920*win_width, 30/1080*win_height)
        self.choose_outsave_files_path_button.clicked.connect(self.save_download_files_path_function)

        # download
        self.igs_name_sure_but = QPushButton('Download', self)
        self.igs_name_sure_but.setFont(QFont("Times New Roman"))
        self.igs_name_sure_but.setGeometry(115/1920*win_width, 430/1080*win_height, 100/1920*win_width, 35/1080*win_height)
        self.igs_name_sure_but.clicked.connect(self.data_download_function02)

        # Download Report
        self.download_details_report_but = QPushButton('Detail', self)
        self.download_details_report_but.setFont(QFont("Times New Roman"))
        self.download_details_report_but.setGeometry(342/1920*win_width, 430/1080*win_height, 100/1920*win_width, 35/1080*win_height)
        self.download_details_report_but.clicked.connect(self.download_details_report_view)

        # View download Report
        self.open_have_download_file_path_but = QPushButton('Open', self)
        self.open_have_download_file_path_but.setFont(QFont("Times New Roman"))
        self.open_have_download_file_path_but.setGeometry(574/1920*win_width, 430/1080*win_height, 100/1920*win_width, 35/1080*win_height)
        self.open_have_download_file_path_but.clicked.connect(self.open_have_download_path)

        # View usage help
        self.open_help_file_but = QPushButton('Help', self)
        self.open_help_file_but.setFont(QFont("Times New Roman"))
        self.open_help_file_but.setGeometry(790/1920*win_width, 430/1080*win_height, 100/1920*win_width, 35/1080*win_height)
        self.open_help_file_but.clicked.connect(self.open_download_help_file_but_line)

        # Download completion prompt
        self.show_download_information = QLabel(self)
        self.show_download_information.setGeometry(55/1920*win_width, 480/1080*win_height, 800/1920*win_width, 35/1080*win_height)
        self.show_download_process_state = QLabel(self)
        self.show_download_process_state.setGeometry(420/1920*win_width, 480/1080*win_height, 360/1920*win_width, 35/1080*win_height)

        # progress bar
        self.download_Progress_bar = QProgressBar(self)
        self.download_Progress_bar.setGeometry(50/1920*win_width, 515/1080*win_height, 910/1920*win_width, 35/1080*win_height)
        self_step = 0
        self.download_Progress_bar.setValue(self_step)
        QApplication.processEvents()

    def tips_info_links(self):
        QMessageBox.information(self, 'Tips', "G/R: GPS/GLONASS \nMGEX: multi-GNSS \nUnclaimed: GPS/GLONASS")
        pass

    def GFZ_Precisi_clock_box_change(self):
        if self.gfz_Precisi_clock_box.currentText() == 'Final':
            self.gfz_Precisi_clock_label.setText('30s Precise Clock(.clk)')
        elif self.gfz_Precisi_clock_box.currentText() == 'Rapid':
            self.gfz_Precisi_clock_label.setText('300s Precise Clock(.clk)')
        pass

    def dowunload_url_changed(self):
        self.select_url = self.choose_product_url_box.currentText()
        if self.choose_local_area_box.currentText() == 'IGS':
            if (self.select_url == 'ftp://igs.ign.fr/pub/igs/products/') or (self.select_url == 'ftp://nfs.kasi.re.kr/gps/products/') | (self.select_url == 'http://garner.ucsd.edu/pub/products/'):
                self.igs_Precisi_track_check.setEnabled(True)
                self.igs_Precisi_clock_check.setEnabled(True)
                self.igs_tro_check.setEnabled(False)
                self.igs_snx_check.setEnabled(True)
                self.igs_erp_check.setEnabled(True)
                self.igs_atx_check.setEnabled(True)
                self.igs_Precisi_track_check.setChecked(False)
                self.igs_Precisi_clock_check.setChecked(False)
                self.igs_tro_check.setChecked(False)
                self.igs_snx_check.setChecked(False)
                self.igs_erp_check.setChecked(False)
                self.igs_atx_check.setChecked(False)
                self.igs_Precisi_track_box.setEnabled(True)
                self.igs_Precisi_track_label.setEnabled(True)
                self.igs_Precisi_clock_box.setEnabled(True)
                self.igs_Precisi_clock_interv_box.setEnabled(True)
                self.igs_Precisi_clock_label.setEnabled(True)
                self.igs_tro_box.setEnabled(False)
                self.igs_tro_label.setEnabled(False)
                self.igs_snx_box.setEnabled(True)
                self.igs_snx_label.setEnabled(True)
                self.igs_erp_box.setEnabled(True)
                self.igs_erp_label.setEnabled(True)
                self.igs_atx_box.setEnabled(True)
                self.igs_atx_label.setEnabled(True)
                self.igs_i_check.setEnabled(False)
                self.igs_i_box.setEnabled(False)
                self.igs_i_label.setEnabled(False)
                self.igs_rate_TEC_check.setEnabled(False)
                self.igs_i_check.setChecked(False)
                self.igs_rate_TEC_check.setChecked(False)
            else:
                self.igs_Precisi_track_check.setEnabled(True)
                self.igs_Precisi_clock_check.setEnabled(True)
                self.igs_tro_check.setEnabled(True)
                self.igs_snx_check.setEnabled(True)
                self.igs_erp_check.setEnabled(True)
                self.igs_atx_check.setEnabled(True)
                self.igs_Precisi_track_check.setChecked(False)
                self.igs_Precisi_clock_check.setChecked(False)
                self.igs_tro_check.setChecked(False)
                self.igs_snx_check.setChecked(False)
                self.igs_erp_check.setChecked(False)
                self.igs_atx_check.setChecked(False)
                self.igs_Precisi_track_box.setEnabled(True)
                self.igs_Precisi_track_label.setEnabled(True)
                self.igs_Precisi_clock_box.setEnabled(True)
                self.igs_Precisi_clock_interv_box.setEnabled(True)
                self.igs_Precisi_clock_label.setEnabled(True)
                self.igs_tro_box.setEnabled(True)
                self.igs_tro_label.setEnabled(True)
                self.igs_snx_box.setEnabled(True)
                self.igs_snx_label.setEnabled(True)
                self.igs_erp_box.setEnabled(True)
                self.igs_erp_label.setEnabled(True)
                self.igs_atx_box.setEnabled(True)
                self.igs_atx_label.setEnabled(True)
                self.igs_i_check.setEnabled(True)
                self.igs_i_box.setEnabled(True)
                self.igs_i_label.setEnabled(True)
                self.igs_rate_TEC_check.setEnabled(True)
                self.igs_i_check.setChecked(False)
                self.igs_rate_TEC_check.setChecked(False)

        elif self.choose_local_area_box.currentText() == 'CODE(Switzerland)':
            # self.choose_product_url_box.addItems(['http://ftp.aiub.unibe.ch/', 'ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/',
            #                                       'gdc.cddis.eosdis.nasa.gov/pub/gps/products/', 'ftp://igs.ign.fr/pub/igs/products/, 'ftp://nfs.kasi.re.kr/gps/products/',
            #                                       'http://garner.ucsd.edu/pub/products/'])
            if self.select_url == 'ftp://nfs.kasi.re.kr/gps/products/':
                self.code_Precisi_track_check.setEnabled(True)
                self.code_Precisi_clock_check.setEnabled(True)
                self.code_obx_check.setEnabled(True)
                self.code_ion_check.setEnabled(False)
                self.code_i_check.setEnabled(False)
                self.code_tro_check.setEnabled(True)
                self.code_erp_check.setEnabled(False)
                self.code_dcb_check.setEnabled(False)
                self.code_bia_check.setEnabled(True)
                self.code_snx_check.setEnabled(True)
                self.code_Precisi_track_check.setChecked(False)
                self.code_Precisi_clock_check.setChecked(False)
                self.code_obx_check.setChecked(False)
                self.code_ion_check.setChecked(False)
                self.code_i_check.setChecked(False)
                self.code_tro_check.setChecked(False)
                self.code_erp_check.setChecked(False)
                self.code_dcb_check.setChecked(False)
                self.code_bia_check.setChecked(False)
                self.code_snx_check.setChecked(False)
                self.code_Precisi_clock_interv_box.setEnabled(True)
                self.code_Precisi_clock_interv_box.clear()
                self.code_Precisi_clock_interv_box.addItems(['5s G/R', '30s G/R'])
                self.code_Precisi_clock_label.setEnabled(True)
                self.code_Precisi_track_box.setEnabled(True)
                self.code_Precisi_track_box.clear()
                self.code_Precisi_track_box.addItems(['G/R'])
                self.code_Precisi_track_label.setEnabled(True)
                self.code_obx_box.setEnabled(True)
                self.code_obx_box.clear()
                self.code_obx_box.addItems(['G/R'])
                self.code_obx_label.setEnabled(True)
                self.code_erp_box.setEnabled(False)
                self.code_erp_label.setEnabled(False)
                self.code_bia_box.setEnabled(True)
                self.code_bia_box.clear()
                self.code_bia_box.addItems(['G/R'])
                self.code_bia_label.setEnabled(True)
                self.code_dcb_box.setEnabled(False)
                self.code_dcb_label.setEnabled(False)
            elif self.select_url == 'http://garner.ucsd.edu/pub/products/':
                self.code_Precisi_track_check.setEnabled(True)
                self.code_Precisi_clock_check.setEnabled(True)
                self.code_obx_check.setEnabled(True)
                self.code_ion_check.setEnabled(False)
                self.code_i_check.setEnabled(False)
                self.code_tro_check.setEnabled(True)
                self.code_erp_check.setEnabled(False)
                self.code_dcb_check.setEnabled(False)
                self.code_bia_check.setEnabled(True)
                self.code_snx_check.setEnabled(False)
                self.code_Precisi_track_check.setChecked(False)
                self.code_Precisi_clock_check.setChecked(False)
                self.code_obx_check.setChecked(False)
                self.code_ion_check.setChecked(False)
                self.code_i_check.setChecked(False)
                self.code_tro_check.setChecked(False)
                self.code_erp_check.setChecked(False)
                self.code_dcb_check.setChecked(False)
                self.code_bia_check.setChecked(False)
                self.code_snx_check.setChecked(False)
                self.code_Precisi_clock_interv_box.setEnabled(True)
                self.code_Precisi_clock_interv_box.clear()
                self.code_Precisi_clock_interv_box.addItems(['30s G/R'])
                self.code_Precisi_clock_label.setEnabled(True)
                self.code_Precisi_track_box.setEnabled(True)
                self.code_Precisi_track_box.clear()
                self.code_Precisi_track_box.addItems(['G/R'])
                self.code_Precisi_track_label.setEnabled(True)
                self.code_obx_box.setEnabled(False)
                self.code_obx_label.setEnabled(False)
                self.code_erp_box.setEnabled(False)
                self.code_erp_label.setEnabled(False)
                self.code_bia_box.setEnabled(True)
                self.code_bia_box.setEnabled(True)
                self.code_bia_box.clear()
                self.code_bia_box.addItems(['G/R'])
                self.code_bia_label.setEnabled(True)
                self.code_dcb_box.setEnabled(False)
                self.code_dcb_label.setEnabled(False)
            elif self.select_url == 'http://ftp.aiub.unibe.ch/':
                self.code_Precisi_track_check.setEnabled(True)
                self.code_Precisi_clock_check.setEnabled(True)
                self.code_obx_check.setEnabled(True)
                self.code_ion_check.setEnabled(True)
                self.code_i_check.setEnabled(True)
                self.code_tro_check.setEnabled(True)
                self.code_erp_check.setEnabled(True)
                self.code_dcb_check.setEnabled(True)
                self.code_bia_check.setEnabled(True)
                self.code_snx_check.setEnabled(True)
                self.code_Precisi_track_check.setChecked(False)
                self.code_Precisi_clock_check.setChecked(False)
                self.code_obx_check.setChecked(False)
                self.code_ion_check.setChecked(False)
                self.code_i_check.setChecked(False)
                self.code_tro_check.setChecked(False)
                self.code_erp_check.setChecked(False)
                self.code_dcb_check.setChecked(False)
                self.code_bia_check.setChecked(False)
                self.code_snx_check.setChecked(False)
                self.code_Precisi_clock_interv_box.setEnabled(True)
                self.code_Precisi_clock_interv_box.clear()
                self.code_Precisi_clock_interv_box.addItems(['5s G/R', '30s G/R', '30s MGEX'])
                self.code_Precisi_clock_label.setEnabled(True)
                self.code_Precisi_track_box.setEnabled(True)
                self.code_Precisi_track_box.clear()
                self.code_Precisi_track_box.addItems(['G/R', 'MGEX'])
                self.code_Precisi_track_label.setEnabled(True)
                self.code_obx_box.setEnabled(True)
                self.code_obx_label.setEnabled(True)
                self.code_erp_box.setEnabled(True)
                self.code_erp_box.clear()
                self.code_erp_box.addItems(['G/R', 'MGEX'])
                self.code_erp_label.setEnabled(True)
                self.code_bia_box.setEnabled(True)
                self.code_bia_box.clear()
                self.code_bia_box.addItems(['G/R', 'MGEX'])
                self.code_bia_label.setEnabled(True)
                self.code_dcb_box.setEnabled(True)
                self.code_dcb_label.setEnabled(True)
            elif self.select_url == 'ftp://igs.ign.fr/pub/igs/products/':
                self.code_Precisi_track_check.setEnabled(True)
                self.code_Precisi_clock_check.setEnabled(True)
                self.code_obx_check.setEnabled(True)
                self.code_ion_check.setEnabled(False)
                self.code_i_check.setEnabled(False)
                self.code_tro_check.setEnabled(False)
                self.code_erp_check.setEnabled(True)
                self.code_dcb_check.setEnabled(False)
                self.code_bia_check.setEnabled(True)
                self.code_snx_check.setEnabled(True)
                self.code_Precisi_track_check.setChecked(False)
                self.code_Precisi_clock_check.setChecked(False)
                self.code_obx_check.setChecked(False)
                self.code_ion_check.setChecked(False)
                self.code_i_check.setChecked(False)
                self.code_tro_check.setChecked(False)
                self.code_erp_check.setChecked(False)
                self.code_dcb_check.setChecked(False)
                self.code_bia_check.setChecked(False)
                self.code_snx_check.setChecked(False)
                self.code_Precisi_clock_interv_box.setEnabled(True)
                self.code_Precisi_clock_interv_box.clear()
                self.code_Precisi_clock_interv_box.addItems(['5s G/R', '30s G/R', '30s MGEX'])
                self.code_Precisi_clock_label.setEnabled(True)
                self.code_Precisi_track_box.setEnabled(True)
                self.code_Precisi_track_box.clear()
                self.code_Precisi_track_box.addItems(['G/R', 'MGEX'])
                self.code_Precisi_track_label.setEnabled(True)
                self.code_obx_box.setEnabled(True)
                self.code_obx_label.setEnabled(True)
                self.code_erp_box.setEnabled(True)
                self.code_erp_box.clear()
                self.code_erp_box.addItems(['MGEX'])
                self.code_erp_label.setEnabled(True)
                self.code_bia_box.setEnabled(True)
                self.code_bia_box.clear()
                self.code_bia_box.addItems(['MGEX'])
                self.code_bia_label.setEnabled(True)
                self.code_dcb_box.setEnabled(False)
                self.code_dcb_label.setEnabled(False)
            else:
                self.code_Precisi_track_check.setEnabled(True)
                self.code_Precisi_clock_check.setEnabled(True)
                self.code_obx_check.setEnabled(True)
                self.code_ion_check.setEnabled(False)
                self.code_i_check.setEnabled(True)
                self.code_tro_check.setEnabled(True)
                self.code_erp_check.setEnabled(True)
                self.code_dcb_check.setEnabled(False)
                self.code_bia_check.setEnabled(True)
                self.code_snx_check.setEnabled(True)
                self.code_Precisi_track_check.setChecked(False)
                self.code_Precisi_clock_check.setChecked(False)
                self.code_obx_check.setChecked(False)
                self.code_ion_check.setChecked(False)
                self.code_i_check.setChecked(False)
                self.code_tro_check.setChecked(False)
                self.code_erp_check.setChecked(False)
                self.code_dcb_check.setChecked(False)
                self.code_bia_check.setChecked(False)
                self.code_snx_check.setChecked(False)
                self.code_Precisi_clock_interv_box.setEnabled(True)
                self.code_Precisi_clock_interv_box.clear()
                self.code_Precisi_clock_interv_box.addItems(['5s G/R', '30s G/R', '30s MGEX'])
                self.code_Precisi_clock_label.setEnabled(True)
                self.code_Precisi_track_box.setEnabled(True)
                self.code_Precisi_track_box.clear()
                self.code_Precisi_track_box.addItems(['G/R', 'MGEX'])
                self.code_Precisi_track_label.setEnabled(True)
                self.code_obx_box.setEnabled(True)
                self.code_obx_label.setEnabled(True)
                self.code_erp_box.setEnabled(True)
                self.code_erp_box.clear()
                self.code_erp_box.addItems(['MGEX'])
                self.code_erp_label.setEnabled(True)
                self.code_bia_box.setEnabled(True)
                self.code_bia_box.clear()
                self.code_bia_box.addItems(['MGEX'])
                self.code_bia_label.setEnabled(True)
                self.code_dcb_box.setEnabled(False)
                self.code_dcb_label.setEnabled(False)

        elif self.choose_local_area_box.currentText() == 'CAS(China)':
            # self.choose_product_url_box.addItems(['ftp://182.92.166.182/product/', 'ftp://ftp.gipp.org.cn/product/', 'ftp://gssc.esa.int/gnss/products/',
            #                                       'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/','ftp://igs.ign.fr/pub/igs/products/'])
            if self.select_url == 'ftp://182.92.166.182/product/':
                self.cas_dcb_check.setEnabled(True)
                self.cas_bia_check.setEnabled(True)
                self.cas_bsx_check.setEnabled(True)
                self.cas_ion_check.setEnabled(True)
                self.cas_dcb_check.setChecked(False)
                self.cas_bia_check.setChecked(False)
                self.cas_bsx_check.setChecked(False)
                self.cas_ion_check.setChecked(False)
                self.cas_dcb_box.setEnabled(True)
                self.cas_dcb_label.setEnabled(True)
                self.cas_bia_box.setEnabled(True)
                self.cas_bia_box.clear()
                self.cas_bia_box.addItems(['G/R (no APC)', 'MGEX(no APC)', 'MGEX(APC)'])
                self.cas_bia_label.setEnabled(True)
                self.cas_bsx_box.setEnabled(True)
                self.cas_bsx_box.clear()
                self.cas_bsx_box.addItems(['G/R (no APC)', 'MGEX(no APC)', 'MGEX(APC)'])
                self.cas_bsx_label.setEnabled(True)
                self.cas_i_check.setEnabled(False)
                self.cas_i_box.setEnabled(False)
                self.cas_i_label.setEnabled(False)
                self.cas_i_check.setChecked(False)
            elif self.select_url == 'ftp://ftp.gipp.org.cn/product/':
                self.cas_dcb_check.setEnabled(False)
                self.cas_bia_check.setEnabled(True)
                self.cas_bsx_check.setEnabled(True)
                self.cas_ion_check.setEnabled(False)
                self.cas_dcb_check.setChecked(False)
                self.cas_bia_check.setChecked(False)
                self.cas_bsx_check.setChecked(False)
                self.cas_ion_check.setChecked(False)
                self.cas_dcb_box.setEnabled(False)
                self.cas_dcb_label.setEnabled(False)
                self.cas_bia_box.setEnabled(True)
                self.cas_bia_box.clear()
                self.cas_bia_box.addItems(['G/R (no APC)', 'MGEX(no APC)', 'MGEX(APC)'])
                self.cas_bia_label.setEnabled(True)
                self.cas_bsx_box.setEnabled(True)
                self.cas_bsx_box.clear()
                self.cas_bsx_box.addItems(['G/R (no APC)', 'MGEX(no APC)', 'MGEX(APC)'])
                self.cas_bsx_label.setEnabled(True)
                self.cas_i_check.setEnabled(True)
                self.cas_i_box.setEnabled(True)
                self.cas_i_label.setEnabled(True)
                self.cas_i_check.setChecked(False)
            elif self.select_url == 'ftp://igs.ign.fr/pub/igs/products/':
                self.cas_dcb_check.setEnabled(False)
                self.cas_bia_check.setEnabled(False)
                self.cas_bsx_check.setEnabled(True)
                self.cas_ion_check.setEnabled(False)
                self.cas_dcb_check.setChecked(False)
                self.cas_bia_check.setChecked(False)
                self.cas_bsx_check.setChecked(False)
                self.cas_ion_check.setChecked(False)
                self.cas_dcb_box.setEnabled(False)
                self.cas_dcb_label.setEnabled(False)
                self.cas_bia_box.setEnabled(False)
                self.cas_bia_label.setEnabled(False)
                self.cas_bsx_box.setEnabled(True)
                self.cas_bsx_box.clear()
                self.cas_bsx_box.addItems(['MGEX(no APC)'])
                self.cas_bsx_label.setEnabled(True)
                self.cas_i_check.setEnabled(False)
                self.cas_i_box.setEnabled(False)
                self.cas_i_label.setEnabled(False)
                self.cas_i_check.setChecked(False)
            else:
                self.cas_dcb_check.setEnabled(False)
                self.cas_bia_check.setEnabled(False)
                self.cas_bsx_check.setEnabled(True)
                self.cas_ion_check.setEnabled(False)
                self.cas_dcb_check.setChecked(False)
                self.cas_bia_check.setChecked(False)
                self.cas_bsx_check.setChecked(False)
                self.cas_ion_check.setChecked(False)
                self.cas_dcb_box.setEnabled(False)
                self.cas_dcb_label.setEnabled(False)
                self.cas_bia_box.setEnabled(False)
                self.cas_bia_label.setEnabled(False)
                self.cas_bsx_box.setEnabled(True)
                self.cas_bsx_box.clear()
                self.cas_bsx_box.addItems(['MGEX(no APC)', 'MGEX(APC)'])
                self.cas_bsx_label.setEnabled(True)
                self.cas_i_check.setEnabled(True)
                self.cas_i_box.setEnabled(True)
                self.cas_i_label.setEnabled(True)
                self.cas_i_check.setChecked(False)

        elif self.choose_local_area_box.currentText() == 'WHU(China)':
            # self.choose_product_url_box.addItems(['ftp://igs.gnsswhu.cn/pub/gps/products/', 'ftp://gssc.esa.int/gnss/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
            #                                       'ftp://igs.ign.fr/pub/igs/products/', 'ftp://igs.gnsswhu.cn/pub/whu/'])
            if self.select_url == 'ftp://igs.gnsswhu.cn/pub/gps/products/':
                self.whu_Precisi_track_check.setEnabled(True)
                self.whu_Precisi_clock_check.setEnabled(True)
                self.whu_bia_check.setEnabled(True)
                self.whu_erp_check.setEnabled(True)
                self.whu_i_check.setEnabled(False)
                self.whu_i_check.setChecked(False)
                self.whu_Precisi_track_box.setEnabled(True)
                self.whu_Precisi_clock_box.setEnabled(True)
                self.whu_erp_box.setEnabled(True)
                self.whu_i_box.setEnabled(False)
                self.whu_Precisi_track_box.clear()
                self.whu_Precisi_track_box.addItems(['Final', 'Ultra'])
                self.whu_Precisi_clock_box.clear()
                self.whu_Precisi_clock_box.addItems(['Final', 'Ultra'])
                self.whu_erp_box.clear()
                self.whu_erp_box.addItems(['Final', 'Ultra'])
                self.whu_Precisi_track_label.setEnabled(True)
                self.whu_Precisi_clock_label.setEnabled(True)
                self.whu_erp_label.setEnabled(True)
                self.whu_i_label.setEnabled(False)
            elif self.select_url == 'ftp://igs.gnsswhu.cn/pub/whu/':
                self.whu_Precisi_track_check.setEnabled(True)
                self.whu_Precisi_clock_check.setEnabled(True)
                self.whu_bia_check.setEnabled(True)
                self.whu_erp_check.setEnabled(True)
                self.whu_i_check.setEnabled(True)
                self.whu_i_check.setChecked(False)
                self.whu_Precisi_track_box.setEnabled(True)
                self.whu_Precisi_clock_box.setEnabled(True)
                self.whu_erp_box.setEnabled(True)
                self.whu_i_box.setEnabled(True)
                self.whu_Precisi_track_box.clear()
                self.whu_Precisi_track_box.addItems(['Rapid'])
                self.whu_Precisi_clock_box.clear()
                self.whu_Precisi_clock_box.addItems(['Rapid'])
                self.whu_erp_box.clear()
                self.whu_erp_box.addItems(['Rapid'])
                self.whu_Precisi_track_label.setEnabled(True)
                self.whu_Precisi_clock_label.setEnabled(True)
                self.whu_erp_label.setEnabled(True)
                self.whu_i_label.setEnabled(True)
            else:
                self.whu_Precisi_track_check.setEnabled(True)
                self.whu_Precisi_clock_check.setEnabled(True)
                self.whu_bia_check.setEnabled(True)
                self.whu_erp_check.setEnabled(True)
                self.whu_i_check.setEnabled(True)
                self.whu_i_check.setChecked(False)
                self.whu_Precisi_track_box.setEnabled(True)
                self.whu_Precisi_clock_box.setEnabled(True)
                self.whu_erp_box.setEnabled(True)
                self.whu_i_box.setEnabled(True)
                self.whu_Precisi_track_box.clear()
                self.whu_Precisi_track_box.addItems(['Final', 'Ultra'])
                self.whu_Precisi_clock_box.clear()
                self.whu_Precisi_clock_box.addItems(['Final', 'Ultra'])
                self.whu_erp_box.clear()
                self.whu_erp_box.addItems(['Final', 'Ultra'])
                self.whu_Precisi_track_label.setEnabled(True)
                self.whu_Precisi_clock_label.setEnabled(True)
                self.whu_erp_label.setEnabled(True)
                self.whu_i_label.setEnabled(True)

        elif self.choose_local_area_box.currentText() == 'GFZ(Germany)':
            # self.choose_product_url_box.addItems(['ftp://ftp.gfz-potsdam.de/GNSS/products/', 'ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/',
            #                                       'gdc.cddis.eosdis.nasa.gov/pub/gps/products/','ftp://igs.ign.fr/pub/igs/products/','ftp://nfs.kasi.re.kr/gnss/products/',
            #                                       'http://garner.ucsd.edu/pub/products/'])
            if self.select_url == 'ftp://ftp.gfz-potsdam.de/GNSS/products/':
                self.gfz_Precisi_track_check.setEnabled(True)
                self.gfz_Precisi_clock_check.setEnabled(True)
                self.gfz_tro_check.setEnabled(True)
                self.gfz_zpd_check.setEnabled(True)
                self.gfz_obx_check.setEnabled(True)
                self.gfz_osb_bis_check.setEnabled(True)
                self.gfz_rel_bis_check.setEnabled(True)
                self.gfz_erp_check.setEnabled(True)
                self.gfz_snx_check.setEnabled(True)
                self.gfz_Precisi_track_check.setChecked(False)
                self.gfz_Precisi_clock_check.setChecked(False)
                self.gfz_tro_check.setChecked(False)
                self.gfz_zpd_check.setChecked(False)
                self.gfz_obx_check.setChecked(False)
                self.gfz_osb_bis_check.setChecked(False)
                self.gfz_rel_bis_check.setChecked(False)
                self.gfz_erp_check.setChecked(False)
                self.gfz_snx_check.setChecked(False)
                self.gfz_Precisi_track_box.setEnabled(True)
                self.gfz_Precisi_track_box.clear()
                self.gfz_Precisi_track_box.addItems(['Final', 'Rapid', 'Ultra', 'MGEX'])
                self.gfz_Precisi_track_label.setEnabled(True)
                self.gfz_Precisi_clock_box.setEnabled(True)
                self.gfz_Precisi_clock_box.clear()
                self.gfz_Precisi_clock_box.addItems(['Final', 'Rapid', 'MGEX'])
                self.gfz_tro_box.setEnabled(True)
                self.gfz_zpd_box.setEnabled(True)
                self.gfz_Precisi_clock_label.setEnabled(True)
                self.gfz_tro_label.setEnabled(True)
                self.gfz_zpd_label.setEnabled(True)
                self.gfz_erp_box.setEnabled(True)
                self.gfz_erp_box.clear()
                self.gfz_erp_box.addItems(['Final', 'Rapid', 'Ultra', 'MGEX'])
                self.gfz_erp_label.setEnabled(True)
            elif self.select_url == 'ftp://nfs.kasi.re.kr/gnss/products/' or self.select_url == 'http://garner.ucsd.edu/pub/products/':
                self.gfz_Precisi_track_check.setEnabled(True)
                self.gfz_Precisi_clock_check.setEnabled(True)
                self.gfz_tro_check.setEnabled(False)
                self.gfz_zpd_check.setEnabled(False)
                self.gfz_obx_check.setEnabled(False)
                self.gfz_osb_bis_check.setEnabled(False)
                self.gfz_rel_bis_check.setEnabled(False)
                self.gfz_erp_check.setEnabled(True)
                self.gfz_snx_check.setEnabled(False)
                self.gfz_Precisi_track_check.setChecked(False)
                self.gfz_Precisi_clock_check.setChecked(False)
                self.gfz_tro_check.setChecked(False)
                self.gfz_zpd_check.setChecked(False)
                self.gfz_obx_check.setChecked(False)
                self.gfz_osb_bis_check.setChecked(False)
                self.gfz_rel_bis_check.setChecked(False)
                self.gfz_erp_check.setChecked(False)
                self.gfz_snx_check.setChecked(False)
                self.gfz_Precisi_track_box.setEnabled(True)
                self.gfz_Precisi_track_box.clear()
                self.gfz_Precisi_track_box.addItems(['Final', 'Rapid', 'Ultra'])
                self.gfz_Precisi_track_label.setEnabled(True)
                self.gfz_Precisi_clock_box.setEnabled(True)
                self.gfz_Precisi_clock_box.clear()
                self.gfz_Precisi_clock_box.addItems(['Final', 'Rapid'])
                self.gfz_tro_box.setEnabled(False)
                self.gfz_zpd_box.setEnabled(False)
                self.gfz_Precisi_clock_label.setEnabled(True)
                self.gfz_tro_label.setEnabled(False)
                self.gfz_zpd_label.setEnabled(False)
                self.gfz_erp_box.setEnabled(True)
                self.gfz_erp_box.clear()
                self.gfz_erp_box.addItems(['Final', 'Rapid', 'Ultra'])
                self.gfz_erp_label.setEnabled(True)
            else:
                self.gfz_Precisi_track_check.setEnabled(True)
                self.gfz_Precisi_clock_check.setEnabled(True)
                self.gfz_tro_check.setEnabled(False)
                self.gfz_zpd_check.setEnabled(False)
                self.gfz_obx_check.setEnabled(True)
                self.gfz_osb_bis_check.setEnabled(True)
                self.gfz_rel_bis_check.setEnabled(True)
                self.gfz_erp_check.setEnabled(True)
                self.gfz_snx_check.setEnabled(False)
                self.gfz_Precisi_track_check.setChecked(False)
                self.gfz_Precisi_clock_check.setChecked(False)
                self.gfz_tro_check.setChecked(False)
                self.gfz_zpd_check.setChecked(False)
                self.gfz_obx_check.setChecked(False)
                self.gfz_osb_bis_check.setChecked(False)
                self.gfz_rel_bis_check.setChecked(False)
                self.gfz_erp_check.setChecked(False)
                self.gfz_snx_check.setChecked(False)
                self.gfz_Precisi_track_box.setEnabled(True)
                self.gfz_Precisi_track_box.clear()
                self.gfz_Precisi_track_box.addItems(['Final', 'Rapid', 'Ultra', 'MGEX'])
                self.gfz_Precisi_track_label.setEnabled(True)
                self.gfz_Precisi_clock_box.setEnabled(True)
                self.gfz_Precisi_clock_box.clear()
                self.gfz_Precisi_clock_box.addItems(['Final', 'Rapid', 'MGEX'])
                self.gfz_tro_box.setEnabled(False)
                self.gfz_zpd_box.setEnabled(False)
                self.gfz_Precisi_clock_label.setEnabled(True)
                self.gfz_tro_label.setEnabled(False)
                self.gfz_zpd_label.setEnabled(False)
                self.gfz_erp_box.setEnabled(True)
                self.gfz_erp_box.clear()
                self.gfz_erp_box.addItems(['Final', 'Rapid', 'Ultra', 'MGEX'])
                self.gfz_erp_label.setEnabled(True)

        elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
            # self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
            #                                       'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/', 'http://garner.ucsd.edu/pub/products/'])
            if (self.select_url == 'ftp://igs.ign.fr/pub/igs/products/') or (self.select_url == 'ftp://nfs.kasi.re.kr/gps/products/') | (self.select_url == 'http://garner.ucsd.edu/pub/products/'):
                self.esa_Precisi_track_check.setEnabled(True)
                self.esa_Precisi_clock_check.setEnabled(True)
                self.esa_erp_check.setEnabled(True)
                self.esa_snx_check.setEnabled(True)
                self.esa_i_check.setEnabled(False)
                self.esa_Precisi_track_check.setChecked(False)
                self.esa_Precisi_clock_check.setChecked(False)
                self.esa_erp_check.setChecked(False)
                self.esa_snx_check.setChecked(False)
                self.esa_i_check.setChecked(False)
                self.esa_i_box.setEnabled(False)
                self.esa_i_label.setEnabled(False)
            else:
                self.esa_Precisi_track_check.setEnabled(True)
                self.esa_Precisi_clock_check.setEnabled(True)
                self.esa_erp_check.setEnabled(True)
                self.esa_snx_check.setEnabled(True)
                self.esa_i_check.setEnabled(True)
                self.esa_Precisi_track_check.setChecked(False)
                self.esa_Precisi_clock_check.setChecked(False)
                self.esa_erp_check.setChecked(False)
                self.esa_snx_check.setChecked(False)
                self.esa_i_check.setChecked(False)
                self.esa_i_box.setEnabled(True)
                self.esa_i_label.setEnabled(True)

        elif self.choose_local_area_box.currentText() == 'JPL(USA)':
            # self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
            #                                       'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/', 'http://garner.ucsd.edu/pub/products/'])
            if (self.select_url == 'ftp://igs.ign.fr/pub/igs/products/') or (self.select_url == 'ftp://nfs.kasi.re.kr/gps/products/') | (self.select_url == 'http://garner.ucsd.edu/pub/products/'):
                self.jpl_Precisi_track_check.setEnabled(True)
                self.jpl_Precisi_clock_check.setEnabled(True)
                self.jpl_erp_check.setEnabled(True)
                self.jpl_snx_check.setEnabled(True)
                self.jpl_tro_check.setEnabled(True)
                self.jpl_yaw_check.setEnabled(False)
                self.jpl_i_check.setEnabled(False)
                self.jpl_Precisi_track_check.setChecked(False)
                self.jpl_Precisi_clock_check.setChecked(False)
                self.jpl_erp_check.setChecked(False)
                self.jpl_snx_check.setChecked(False)
                self.jpl_tro_check.setChecked(False)
                self.jpl_yaw_check.setChecked(False)
                self.jpl_i_check.setChecked(False)
                self.jpl_i_box.setEnabled(False)
                self.jpl_i_label.setEnabled(False)
            else:
                self.jpl_Precisi_track_check.setEnabled(True)
                self.jpl_Precisi_clock_check.setEnabled(True)
                self.jpl_erp_check.setEnabled(True)
                self.jpl_snx_check.setEnabled(True)
                self.jpl_tro_check.setEnabled(True)
                self.jpl_yaw_check.setEnabled(True)
                self.jpl_i_check.setEnabled(True)
                self.jpl_Precisi_track_check.setChecked(False)
                self.jpl_Precisi_clock_check.setChecked(False)
                self.jpl_erp_check.setChecked(False)
                self.jpl_snx_check.setChecked(False)
                self.jpl_tro_check.setChecked(False)
                self.jpl_yaw_check.setChecked(False)
                self.jpl_i_check.setChecked(False)
                self.jpl_i_box.setEnabled(True)
                self.jpl_i_label.setEnabled(True)

        elif self.choose_local_area_box.currentText() == 'MIT(USA)':
            # self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
            #                                       'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/', 'http://garner.ucsd.edu/pub/products/'])
            if (self.select_url == 'ftp://igs.ign.fr/pub/igs/products/') or (self.select_url == 'ftp://nfs.kasi.re.kr/gps/products/'):
                self.mit_Precisi_track_check.setEnabled(True)
                self.mit_Precisi_clock_check.setEnabled(True)
                self.mit_erp_check.setEnabled(True)
                self.mit_snx_check.setEnabled(True)
                self.mit_Precisi_track_check.setChecked(False)
                self.mit_Precisi_clock_check.setChecked(False)
                self.mit_erp_check.setChecked(False)
                self.mit_snx_check.setChecked(False)
            elif (self.select_url == 'http://garner.ucsd.edu/pub/products/'):
                self.mit_Precisi_track_check.setEnabled(True)
                self.mit_Precisi_clock_check.setEnabled(False)
                self.mit_erp_check.setEnabled(False)
                self.mit_snx_check.setEnabled(True)
                self.mit_Precisi_track_check.setChecked(False)
                self.mit_Precisi_clock_check.setChecked(False)
                self.mit_erp_check.setChecked(False)
                self.mit_snx_check.setChecked(False)
            else:
                self.mit_Precisi_track_check.setEnabled(True)
                self.mit_Precisi_clock_check.setEnabled(True)
                self.mit_erp_check.setEnabled(True)
                self.mit_snx_check.setEnabled(True)
                self.mit_Precisi_track_check.setChecked(False)
                self.mit_Precisi_clock_check.setChecked(False)
                self.mit_erp_check.setChecked(False)
                self.mit_snx_check.setChecked(False)

        elif self.choose_local_area_box.currentText() == 'GRG(France)':
            # self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
            #                                       'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/'])
            if self.select_url == self.select_url == 'ftp://nfs.kasi.re.kr/gps/products/':
                self.grg_Precisi_track_box.setEnabled(True)
                self.grg_Precisi_track_box.clear()
                self.grg_Precisi_track_box.addItems(['G/R'])
                self.grg_Precisi_track_label.setEnabled(True)
                self.grg_Precisi_clock_box.setEnabled(True)
                self.grg_Precisi_clock_box.clear()
                self.grg_Precisi_clock_box.addItems(['G/R'])
                self.grg_Precisi_clock_label.setEnabled(True)
                self.grg_Precisi_track_check.setEnabled(True)
                self.grg_Precisi_clock_check.setEnabled(True)
                self.grg_Precisi_track_check.setChecked(False)
                self.grg_Precisi_clock_check.setChecked(False)
                self.grg_snx_box.setEnabled(True)
                self.grg_snx_box.clear()
                self.grg_snx_box.addItems(['G/R'])
                self.grg_snx_label.setEnabled(True)
                self.grg_osb_check.setEnabled(False)
                self.grg_obx_check.setEnabled(False)
                self.grg_erp_check.setEnabled(True)
                self.grg_snx_check.setEnabled(True)
                self.grg_osb_check.setChecked(False)
                self.grg_obx_check.setChecked(False)
                self.grg_erp_check.setChecked(False)
                self.grg_snx_check.setChecked(False)
            else:
                self.grg_Precisi_track_box.setEnabled(True)
                self.grg_Precisi_track_box.clear()
                self.grg_Precisi_track_box.addItems(['G/R', 'MGEX'])
                self.grg_Precisi_track_label.setEnabled(True)
                self.grg_Precisi_clock_box.setEnabled(True)
                self.grg_Precisi_clock_label.setEnabled(True)
                self.grg_Precisi_track_check.setEnabled(True)
                self.grg_Precisi_clock_check.setEnabled(True)
                self.grg_Precisi_track_check.setChecked(False)
                self.grg_Precisi_clock_check.setChecked(False)
                self.grg_snx_box.setEnabled(True)
                self.grg_snx_box.clear()
                self.grg_snx_box.addItems(['G/R', 'MGEX'])
                self.grg_snx_label.setEnabled(True)
                self.grg_osb_check.setEnabled(True)
                self.grg_obx_check.setEnabled(True)
                self.grg_erp_check.setEnabled(True)
                self.grg_snx_check.setEnabled(True)
                self.grg_osb_check.setChecked(False)
                self.grg_obx_check.setChecked(False)
                self.grg_erp_check.setChecked(False)
                self.grg_snx_check.setChecked(False)

        elif self.choose_local_area_box.currentText() == 'EMR(Canada)':
            # self.choose_product_url_box.addItems(['ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/','ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/',
            #                                       'gdc.cddis.eosdis.nasa.gov/pub/gps/products/', 'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/'])
            self.emr_Precisi_track_check.setEnabled(True)
            self.emr_Precisi_clock_check.setEnabled(True)
            self.emr_erp_check.setEnabled(True)
            self.emr_snx_check.setEnabled(True)

        elif self.choose_local_area_box.currentText() == 'SIO(USA)':
            # self.choose_product_url_box.addItems(['http://garner.ucsd.edu/pub/products/', 'ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/',
            #                                       'gdc.cddis.eosdis.nasa.gov/pub/gps/products/', 'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/'])
            if self.select_url == 'http://garner.ucsd.edu/pub/products/':
                self.sio_Precisi_track_check.setEnabled(True)
                self.sio_erp_check.setEnabled(True)
                self.sio_snx_check.setEnabled(True)
                self.sio_Precisi_track_box.setEnabled(True)
                self.sio_Precisi_track_box.clear()
                self.sio_Precisi_track_box.addItems(['Rapid'])
                self.sio_Precisi_track_label.setEnabled(True)
                self.sio_erp_box.setEnabled(True)
                self.sio_erp_box.clear()
                self.sio_erp_box.addItems(['Rapid'])
                self.sio_erp_label.setEnabled(True)
            else:
                self.sio_Precisi_track_check.setEnabled(True)
                self.sio_erp_check.setEnabled(True)
                self.sio_snx_check.setEnabled(True)
                self.sio_Precisi_track_box.setEnabled(True)
                self.sio_Precisi_track_box.clear()
                self.sio_Precisi_track_box.addItems(['Final'])
                self.sio_Precisi_track_label.setEnabled(True)
                self.sio_erp_box.setEnabled(True)
                self.sio_erp_box.clear()
                self.sio_erp_box.addItems(['Final'])
                self.sio_erp_label.setEnabled(True)

        elif self.choose_local_area_box.currentText() == 'NGS(USA)':
            # self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
            #                                       'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/'])
            self.ngs_Precisi_track_check.setEnabled(True)
            self.ngs_erp_check.setEnabled(True)
            self.ngs_snx_check.setEnabled(True)

        elif self.choose_local_area_box.currentText() == 'UPC(Spain)':
            # self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/'])

            self.upc_i_check.setEnabled(True)
            self.upc_i_box.setEnabled(True)
            self.upc_i_label.setEnabled(True)
        pass

    def dowunload_source_changed(self):
        # IGS
        self.igs_Precisi_track_check.setChecked(False)
        self.igs_Precisi_clock_check.setChecked(False)
        self.igs_tro_check.setChecked(False)
        self.igs_snx_check.setChecked(False)
        self.igs_erp_check.setChecked(False)
        self.igs_atx_check.setChecked(False)
        self.igs_i_check.setChecked(False)
        self.igs_rate_TEC_check.setChecked(False)
        self.igs_Precisi_track_check.setVisible(False)
        self.igs_Precisi_clock_check.setVisible(False)
        self.igs_tro_check.setVisible(False)
        self.igs_snx_check.setVisible(False)
        self.igs_erp_check.setVisible(False)
        self.igs_atx_check.setVisible(False)
        self.igs_Precisi_track_box.setVisible(False)
        self.igs_Precisi_track_label.setVisible(False)
        self.igs_Precisi_clock_box.setVisible(False)
        self.igs_Precisi_clock_interv_box.setVisible(False)
        self.igs_Precisi_clock_label.setVisible(False)
        self.igs_tro_box.setVisible(False)
        self.igs_tro_label.setVisible(False)
        self.igs_snx_box.setVisible(False)
        self.igs_snx_label.setVisible(False)
        self.igs_erp_box.setVisible(False)
        self.igs_erp_label.setVisible(False)
        self.igs_atx_box.setVisible(False)
        self.igs_atx_label.setVisible(False)
        self.igs_i_check.setVisible(False)
        self.igs_i_box.setVisible(False)
        self.igs_i_label.setVisible(False)
        self.igs_rate_TEC_check.setVisible(False)

        # CODE
        self.code_Precisi_track_check.setChecked(False)
        self.code_Precisi_clock_check.setChecked(False)
        self.code_obx_check.setChecked(False)
        self.code_ion_check.setChecked(False)
        self.code_i_check.setChecked(False)
        self.code_tro_check.setChecked(False)
        self.code_erp_check.setChecked(False)
        self.code_dcb_check.setChecked(False)
        self.code_bia_check.setChecked(False)
        self.code_snx_check.setChecked(False)
        self.code_Precisi_track_check.setVisible(False)
        self.code_Precisi_clock_check.setVisible(False)
        self.code_obx_check.setVisible(False)
        self.code_ion_check.setVisible(False)
        self.code_i_check.setVisible(False)
        self.code_tro_check.setVisible(False)
        self.code_erp_check.setVisible(False)
        self.code_dcb_check.setVisible(False)
        self.code_bia_check.setVisible(False)
        self.code_snx_check.setVisible(False)
        self.code_Precisi_clock_interv_box.setVisible(False)
        self.code_Precisi_clock_label.setVisible(False)
        self.code_Precisi_track_box.setVisible(False)
        self.code_Precisi_track_label.setVisible(False)
        self.code_obx_box.setVisible(False)
        self.code_obx_label.setVisible(False)
        self.code_erp_box.setVisible(False)
        self.code_erp_label.setVisible(False)
        self.code_bia_box.setVisible(False)
        self.code_bia_label.setVisible(False)
        self.code_dcb_box.setVisible(False)
        self.code_dcb_label.setVisible(False)

        # CAS
        self.cas_dcb_check.setChecked(False)
        self.cas_bia_check.setChecked(False)
        self.cas_bsx_check.setChecked(False)
        self.cas_ion_check.setChecked(False)
        self.cas_i_check.setChecked(False)
        self.cas_dcb_check.setVisible(False)
        self.cas_bia_check.setVisible(False)
        self.cas_bsx_check.setVisible(False)
        self.cas_ion_check.setVisible(False)
        self.cas_dcb_box.setVisible(False)
        self.cas_dcb_label.setVisible(False)
        self.cas_bia_box.setVisible(False)
        self.cas_bia_label.setVisible(False)
        self.cas_bsx_box.setVisible(False)
        self.cas_bsx_label.setVisible(False)
        self.cas_ion_check.setVisible(False)
        self.cas_i_check.setVisible(False)
        self.cas_i_box.setVisible(False)
        self.cas_i_label.setVisible(False)

        # WHU
        self.whu_Precisi_track_check.setVisible(False)
        self.whu_Precisi_clock_check.setVisible(False)
        self.whu_bia_check.setVisible(False)
        self.whu_erp_check.setVisible(False)
        self.whu_i_check.setVisible(False)
        self.whu_Precisi_track_check.setChecked(False)
        self.whu_Precisi_clock_check.setChecked(False)
        self.whu_bia_check.setChecked(False)
        self.whu_erp_check.setChecked(False)
        self.whu_i_check.setChecked(False)
        self.whu_Precisi_track_box.setVisible(False)
        self.whu_Precisi_clock_box.setVisible(False)
        self.whu_erp_box.setVisible(False)
        self.whu_i_box.setVisible(False)
        self.whu_Precisi_track_label.setVisible(False)
        self.whu_Precisi_clock_label.setVisible(False)
        self.whu_erp_label.setVisible(False)
        self.whu_i_label.setVisible(False)

        # GFZ
        self.gfz_Precisi_track_check.setChecked(False)
        self.gfz_Precisi_clock_check.setChecked(False)
        self.gfz_tro_check.setChecked(False)
        self.gfz_zpd_check.setChecked(False)
        self.gfz_obx_check.setChecked(False)
        self.gfz_osb_bis_check.setChecked(False)
        self.gfz_rel_bis_check.setChecked(False)
        self.gfz_erp_check.setChecked(False)
        self.gfz_snx_check.setChecked(False)
        self.gfz_Precisi_track_check.setVisible(False)
        self.gfz_Precisi_clock_check.setVisible(False)
        self.gfz_tro_check.setVisible(False)
        self.gfz_zpd_check.setVisible(False)
        self.gfz_obx_check.setVisible(False)
        self.gfz_osb_bis_check.setVisible(False)
        self.gfz_rel_bis_check.setVisible(False)
        self.gfz_erp_check.setVisible(False)
        self.gfz_snx_check.setVisible(False)
        self.gfz_Precisi_track_box.setVisible(False)
        self.gfz_Precisi_track_label.setVisible(False)
        self.gfz_Precisi_clock_box.setVisible(False)
        self.gfz_tro_box.setVisible(False)
        self.gfz_zpd_box.setVisible(False)
        self.gfz_Precisi_clock_label.setVisible(False)
        self.gfz_tro_label.setVisible(False)
        self.gfz_zpd_label.setVisible(False)
        self.gfz_erp_box.setVisible(False)
        self.gfz_erp_label.setVisible(False)

        # ESA
        self.esa_Precisi_track_check.setChecked(False)
        self.esa_Precisi_clock_check.setChecked(False)
        self.esa_erp_check.setChecked(False)
        self.esa_snx_check.setChecked(False)
        self.esa_i_check.setChecked(False)
        self.esa_Precisi_track_check.setVisible(False)
        self.esa_Precisi_clock_check.setVisible(False)
        self.esa_erp_check.setVisible(False)
        self.esa_snx_check.setVisible(False)
        self.esa_i_check.setVisible(False)
        self.esa_i_box.setVisible(False)
        self.esa_i_label.setVisible(False)

        # JPL
        self.jpl_Precisi_track_check.setChecked(False)
        self.jpl_Precisi_clock_check.setChecked(False)
        self.jpl_erp_check.setChecked(False)
        self.jpl_snx_check.setChecked(False)
        self.jpl_tro_check.setChecked(False)
        self.jpl_yaw_check.setChecked(False)
        self.jpl_i_check.setChecked(False)
        self.jpl_Precisi_track_check.setVisible(False)
        self.jpl_Precisi_clock_check.setVisible(False)
        self.jpl_erp_check.setVisible(False)
        self.jpl_snx_check.setVisible(False)
        self.jpl_tro_check.setVisible(False)
        self.jpl_yaw_check.setVisible(False)
        self.jpl_i_check.setVisible(False)
        self.jpl_i_box.setVisible(False)
        self.jpl_i_label.setVisible(False)

        # MIT
        self.mit_Precisi_track_check.setChecked(False)
        self.mit_Precisi_clock_check.setChecked(False)
        self.mit_erp_check.setChecked(False)
        self.mit_snx_check.setChecked(False)
        self.mit_Precisi_track_check.setVisible(False)
        self.mit_Precisi_clock_check.setVisible(False)
        self.mit_erp_check.setVisible(False)
        self.mit_snx_check.setVisible(False)

        # GRG
        self.grg_Precisi_track_check.setChecked(False)
        self.grg_Precisi_clock_check.setChecked(False)
        self.grg_osb_check.setChecked(False)
        self.grg_obx_check.setChecked(False)
        self.grg_erp_check.setChecked(False)
        self.grg_snx_check.setChecked(False)
        self.grg_Precisi_track_box.setVisible(False)
        self.grg_Precisi_track_label.setVisible(False)
        self.grg_Precisi_clock_box.setVisible(False)
        self.grg_Precisi_clock_label.setVisible(False)
        self.grg_Precisi_track_check.setVisible(False)
        self.grg_Precisi_clock_check.setVisible(False)
        self.grg_osb_check.setVisible(False)
        self.grg_obx_check.setVisible(False)
        self.grg_erp_check.setVisible(False)
        self.grg_snx_check.setVisible(False)
        self.grg_snx_box.setVisible(False)
        self.grg_snx_label.setVisible(False)

        # EMR
        self.emr_Precisi_track_check.setChecked(False)
        self.emr_Precisi_clock_check.setChecked(False)
        self.emr_erp_check.setChecked(False)
        self.emr_snx_check.setChecked(False)
        self.emr_Precisi_track_check.setVisible(False)
        self.emr_Precisi_clock_check.setVisible(False)
        self.emr_erp_check.setVisible(False)
        self.emr_snx_check.setVisible(False)

        # SIO
        self.sio_Precisi_track_check.setChecked(False)
        self.sio_erp_check.setChecked(False)
        self.sio_snx_check.setChecked(False)
        self.sio_Precisi_track_check.setVisible(False)
        self.sio_erp_check.setVisible(False)
        self.sio_snx_check.setVisible(False)
        self.sio_Precisi_track_box.setVisible(False)
        self.sio_Precisi_track_label.setVisible(False)
        self.sio_erp_box.setVisible(False)
        self.sio_erp_label.setVisible(False)

        # NGS
        self.ngs_Precisi_track_check.setChecked(False)
        self.ngs_erp_check.setChecked(False)
        self.ngs_snx_check.setChecked(False)
        self.ngs_Precisi_track_check.setVisible(False)
        self.ngs_erp_check.setVisible(False)
        self.ngs_snx_check.setVisible(False)

        # UPC
        self.upc_i_check.setChecked(False)
        self.upc_i_check.setVisible(False)
        self.upc_i_box.setVisible(False)
        self.upc_i_label.setVisible(False)

        if self.choose_local_area_box.currentText() == 'IGS':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
                                                  'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/', 'http://garner.ucsd.edu/pub/products/'])
            self.igs_Precisi_track_check.setVisible(True)
            self.igs_Precisi_clock_check.setVisible(True)
            self.igs_tro_check.setVisible(True)
            self.igs_snx_check.setVisible(True)
            self.igs_erp_check.setVisible(True)
            self.igs_atx_check.setVisible(True)
            self.igs_Precisi_track_box.setVisible(True)
            self.igs_Precisi_track_label.setVisible(True)
            self.igs_Precisi_clock_box.setVisible(True)
            self.igs_Precisi_clock_interv_box.setVisible(True)
            self.igs_Precisi_clock_label.setVisible(True)
            self.igs_tro_box.setVisible(True)
            self.igs_tro_label.setVisible(True)
            self.igs_snx_box.setVisible(True)
            self.igs_snx_label.setVisible(True)
            self.igs_erp_box.setVisible(True)
            self.igs_erp_label.setVisible(True)
            self.igs_atx_box.setVisible(True)
            self.igs_atx_label.setVisible(True)
            self.igs_i_check.setVisible(True)
            self.igs_i_box.setVisible(True)
            self.igs_i_label.setVisible(True)
            self.igs_rate_TEC_check.setVisible(True)
            pass
        elif self.choose_local_area_box.currentText() == 'CODE(Switzerland)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['http://ftp.aiub.unibe.ch/','ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/',
                                                  'gdc.cddis.eosdis.nasa.gov/pub/gps/products/','ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/',
                                                  'http://garner.ucsd.edu/pub/products/'])
            self.code_Precisi_track_check.setVisible(True)
            self.code_Precisi_clock_check.setVisible(True)
            self.code_obx_check.setVisible(True)
            self.code_ion_check.setVisible(True)
            self.code_i_check.setVisible(True)
            self.code_tro_check.setVisible(True)
            self.code_erp_check.setVisible(True)
            self.code_dcb_check.setVisible(True)
            self.code_bia_check.setVisible(True)
            self.code_snx_check.setVisible(True)
            self.code_Precisi_clock_interv_box.setVisible(True)
            self.code_Precisi_clock_label.setVisible(True)
            self.code_Precisi_track_box.setVisible(True)
            self.code_Precisi_track_label.setVisible(True)
            self.code_obx_box.setVisible(True)
            self.code_obx_label.setVisible(True)
            self.code_erp_box.setVisible(True)
            self.code_erp_label.setVisible(True)
            self.code_bia_box.setVisible(True)
            self.code_bia_label.setVisible(True)
            self.code_dcb_box.setVisible(True)
            self.code_dcb_label.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'CAS(China)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://182.92.166.182/product/', 'ftp://ftp.gipp.org.cn/product/', 'ftp://gssc.esa.int/gnss/products/',
                                                  'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/','ftp://igs.ign.fr/pub/igs/products/'])
            self.cas_dcb_check.setVisible(True)
            self.cas_bia_check.setVisible(True)
            self.cas_bsx_check.setVisible(True)
            self.cas_ion_check.setVisible(True)
            self.cas_dcb_box.setVisible(True)
            self.cas_dcb_label.setVisible(True)
            self.cas_bia_box.setVisible(True)
            self.cas_bia_label.setVisible(True)
            self.cas_bsx_box.setVisible(True)
            self.cas_bsx_label.setVisible(True)
            self.cas_i_check.setVisible(True)
            self.cas_i_box.setVisible(True)
            self.cas_i_label.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'WHU(China)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://igs.gnsswhu.cn/pub/gps/products/', 'ftp://igs.gnsswhu.cn/pub/whu/', 'ftp://gssc.esa.int/gnss/products/',
                                                  'gdc.cddis.eosdis.nasa.gov/pub/gps/products/', 'ftp://igs.ign.fr/pub/igs/products/'])
            self.whu_Precisi_track_check.setVisible(True)
            self.whu_Precisi_clock_check.setVisible(True)
            self.whu_bia_check.setVisible(True)
            self.whu_erp_check.setVisible(True)
            self.whu_i_check.setVisible(True)
            self.whu_Precisi_track_box.setVisible(True)
            self.whu_Precisi_clock_box.setVisible(True)
            self.whu_erp_box.setVisible(True)
            self.whu_i_box.setVisible(True)
            self.whu_Precisi_track_label.setVisible(True)
            self.whu_Precisi_clock_label.setVisible(True)
            self.whu_erp_label.setVisible(True)
            self.whu_i_label.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'GFZ(Germany)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://ftp.gfz-potsdam.de/GNSS/products/', 'ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/',
                                                  'gdc.cddis.eosdis.nasa.gov/pub/gps/products/','ftp://igs.ign.fr/pub/igs/products/','ftp://nfs.kasi.re.kr/gnss/products/',
                                                  'http://garner.ucsd.edu/pub/products/'])
            self.gfz_Precisi_track_check.setVisible(True)
            self.gfz_Precisi_clock_check.setVisible(True)
            self.gfz_tro_check.setVisible(True)
            self.gfz_zpd_check.setVisible(True)
            self.gfz_obx_check.setVisible(True)
            self.gfz_osb_bis_check.setVisible(True)
            self.gfz_rel_bis_check.setVisible(True)
            self.gfz_erp_check.setVisible(True)
            self.gfz_snx_check.setVisible(True)
            self.gfz_Precisi_track_box.setVisible(True)
            self.gfz_Precisi_track_label.setVisible(True)
            self.gfz_Precisi_clock_box.setVisible(True)
            self.gfz_tro_box.setVisible(True)
            self.gfz_zpd_box.setVisible(True)
            self.gfz_Precisi_clock_label.setVisible(True)
            self.gfz_tro_label.setVisible(True)
            self.gfz_zpd_label.setVisible(True)
            self.gfz_erp_box.setVisible(True)
            self.gfz_erp_label.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'ESA(Europe)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
                                                  'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/', 'http://garner.ucsd.edu/pub/products/'])
            self.esa_Precisi_track_check.setVisible(True)
            self.esa_Precisi_clock_check.setVisible(True)
            self.esa_erp_check.setVisible(True)
            self.esa_snx_check.setVisible(True)
            self.esa_i_check.setVisible(True)
            self.esa_i_box.setVisible(True)
            self.esa_i_label.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'JPL(USA)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
                                                  'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/', 'http://garner.ucsd.edu/pub/products/'])
            self.jpl_Precisi_track_check.setVisible(True)
            self.jpl_Precisi_clock_check.setVisible(True)
            self.jpl_erp_check.setVisible(True)
            self.jpl_snx_check.setVisible(True)
            self.jpl_tro_check.setVisible(True)
            self.jpl_yaw_check.setVisible(True)
            self.jpl_i_check.setVisible(True)
            self.jpl_i_box.setVisible(True)
            self.jpl_i_label.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'MIT(USA)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
                                                  'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/', 'http://garner.ucsd.edu/pub/products/'])
            self.mit_Precisi_track_check.setVisible(True)
            self.mit_Precisi_clock_check.setVisible(True)
            self.mit_erp_check.setVisible(True)
            self.mit_snx_check.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'GRG(France)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
                                                  'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/'])
            self.grg_Precisi_track_box.setVisible(True)
            self.grg_Precisi_track_label.setVisible(True)
            self.grg_Precisi_clock_box.setVisible(True)
            self.grg_Precisi_clock_label.setVisible(True)
            self.grg_Precisi_track_check.setVisible(True)
            self.grg_Precisi_clock_check.setVisible(True)
            self.grg_osb_check.setVisible(True)
            self.grg_obx_check.setVisible(True)
            self.grg_erp_check.setVisible(True)
            self.grg_snx_check.setVisible(True)
            self.grg_snx_box.setVisible(True)
            self.grg_snx_label.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'EMR(Canada)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/','ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/',
                                                  'gdc.cddis.eosdis.nasa.gov/pub/gps/products/', 'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/'])
            self.emr_Precisi_track_check.setVisible(True)
            self.emr_Precisi_clock_check.setVisible(True)
            self.emr_erp_check.setVisible(True)
            self.emr_snx_check.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'SIO(USA)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['http://garner.ucsd.edu/pub/products/', 'ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/',
                                                  'gdc.cddis.eosdis.nasa.gov/pub/gps/products/', 'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/'])
            self.sio_Precisi_track_check.setVisible(True)
            self.sio_erp_check.setVisible(True)
            self.sio_snx_check.setVisible(True)
            self.sio_Precisi_track_box.setVisible(True)
            self.sio_Precisi_track_label.setVisible(True)
            self.sio_erp_box.setVisible(True)
            self.sio_erp_label.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'NGS(USA)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/',
                                                  'ftp://igs.ign.fr/pub/igs/products/', 'ftp://nfs.kasi.re.kr/gps/products/'])
            self.ngs_Precisi_track_check.setVisible(True)
            self.ngs_erp_check.setVisible(True)
            self.ngs_snx_check.setVisible(True)
        elif self.choose_local_area_box.currentText() == 'UPC(Spain)':
            self.choose_product_url_box.setEnabled(True)
            self.choose_product_url_box.clear()
            self.choose_product_url_box.addItems(['ftp://gssc.esa.int/gnss/products/', 'ftp://igs.gnsswhu.cn/pub/gps/products/', 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/'])
            self.upc_i_check.setVisible(True)
            self.upc_i_box.setVisible(True)
            self.upc_i_label.setVisible(True)
        pass

    # -------------------------------------------------------------------------------------------------
    # start Time system conversion
    # date to GNSS time
    def onDateChanged01(self):
        try:
            time_yearmothday = self.start_time.text()
            year = int(time_yearmothday[0:4])
            mon = int(str(time_yearmothday[5:7]))
            day = int(str(time_yearmothday[8:10]))
            conbin_date = date(year, mon, day)

            # date to yrdoy
            year_accumulate_list = gnsscal.date2yrdoy(conbin_date)
            self.changday0201.setText(str(year_accumulate_list[0]))
            self.changday0202.setText(str(year_accumulate_list[1]))

            # date to gpswd
            GPS_weeks = gnsscal.date2gpswd(conbin_date)
            self.changday0301.setText(str(GPS_weeks[0]))
            self.changday0302.setText(str(GPS_weeks[1]))
            pass
        except:
            pass

    # year, doy to year, month, day
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

    # GPS Week to data
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
    # end Time system conversion
    # date to GNSS time
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

    # year, doy to year, month, day
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

    # GPS Week to data
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
    # -------------------------------------------------------------------------------------------------
    # output path
    def save_download_files_path_function(self):
       save_path = QFileDialog.getExistingDirectory(self, 'Select Output File', 'C:/')
       if save_path == '':
           print('No record path selected')
       else:
           self.show_outsave_files_path_button.setText(save_path)
       pass

    # all data of time interval
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
    # GPS time calculation
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
        str_mon = str(time_yearmothday[5:7])
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
        GPS_week_year_list.append(str_mon)
        return GPS_week_year_list
    # -------------------------------------------------------------------------------------------------
    # Enter the download directory
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
            pass

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
            except requests.exceptions.Timeout:
                print('请求超时')
            except requests.exceptions.RequestException as e:
                print('请求发生错误:', str(e))
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

    # -------------------------------------------------------------------------------------------------
    # main function
    def data_download_function02(self):
        self.show_download_process_state.setText('downloading...')
        # Determine whether the network exists
        try:
            html = requests.get("http://www.baidu.com", timeout=2)
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
        # Download report initialization
        global successful_library
        global failed_library
        successful_library = []
        failed_library = []
        #  the folder exist
        if os.path.exists(self.show_outsave_files_path_button.text()):
            pass
        else:
            os.mkdir(self.show_outsave_files_path_button.text())

        # Time list
        start_time_T = str(self.start_time.dateTime().toString(Qt.ISODate))
        start_time = start_time_T[0:10] + ' ' + start_time_T[11:19]
        start_time_date = start_time_T[0:10]
        end_time_T = str(self.end_time.dateTime().toString(Qt.ISODate))
        end_time = end_time_T[0:10] + ' ' + end_time_T[11:19]
        end_time_date = end_time_T[0:10]
        # Time interval calculation
        dt1 = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        dt2 = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        difference_time = dt2 - dt1
        print('Total data：', difference_time.days)
        if difference_time.days >= 0:
            Judgement_time = 1
        else:
            Judgement_time = 0
        # print('Time size order', Judgement_time)
        if Judgement_time == 0:
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips', 'Please adjust time range !')
            return
        else:
            date_list = self.getEveryDay(start_time_date, end_time_date)
            print('Total data', date_list)
            all_YearAccuDay_GpsWeek = []
            for i in date_list:
                YearAccuDay_GpsWeek = self.GpsWeek_YearAccuDay(i)
                list = [YearAccuDay_GpsWeek[0], YearAccuDay_GpsWeek[1], YearAccuDay_GpsWeek[2], YearAccuDay_GpsWeek[3], YearAccuDay_GpsWeek[4], YearAccuDay_GpsWeek[5], YearAccuDay_GpsWeek[6]]
                all_YearAccuDay_GpsWeek = all_YearAccuDay_GpsWeek + [list]
                pass
            print(all_YearAccuDay_GpsWeek)

        # Generate download file list
        IGS_igu_list = []
        IGS_clk_list = []
        IGS_track_analyze_tempe = []
        IGS_track_analyze = []
        IGS_clock_analyze = []
        IGS_erp_list_tempe = []
        IGS_erp_list = []

        CODE_eph_list = []
        CODE_clk_list = []
        CODE_obx_list = []
        CODE_ion_list = []
        CODE_i_list = []
        CODE_tro_list = []
        CODE_dcb_list_temp = []
        CODE_dcb_list = []
        CODE_bia_list = []
        CODE_erp_list = []
        CODE_snx_list = []

        CAS_dcb_list = []
        CAS_bia_list = []
        CAS_bsx_list = []
        CAS_ion_list = []
        CAS_i_list = []

        WHU_sp3_list = []
        WHU_clock_list = []
        WHU_bia_list = []
        WHU_i_list = []
        WHU_erp_list = []

        GFZ_sp3_list = []
        GFZ_clock_list = []
        GFZ_tro_list = []
        GFZ_zpd_list = []
        GFZ_obx_list = []
        GFZ_osb_list = []
        GFZ_rel_list = []
        GFZ_erp_list_temp = []
        GFZ_erp_list = []
        GFZ_snx_list = []

        ESA_sp3_list = []
        ESA_clock_list = []
        ESA_erp_list_temp = []
        ESA_erp_list = []
        ESA_snx_list = []

        JPL_sp3_list = []
        JPL_clock_list = []
        JPL_erp_list_temp = []
        JPL_erp_list = []
        JPL_snx_list = []
        JPL_tro_list = []
        JPL_yaw_list = []

        MIT_sp3_list = []
        MIT_clock_list = []
        MIT_erp_list_temp = []
        MIT_erp_list = []
        MIT_snx_list = []

        GRG_sp3_list = []
        GRG_clock_list = []
        GRG_erp_list_temp = []
        GRG_osb_list = []
        GRG_obx_list = []
        GRG_erp_list = []
        GRG_snx_list = []

        EMR_sp3_list = []
        EMR_clock_list = []
        EMR_erp_list_temp = []
        EMR_erp_list = []
        EMR_snx_list = []

        SIO_sp3_list = []
        SIO_erp_list_temp = []
        SIO_erp_list = []
        SIO_snx_list = []

        NGS_sp3_list = []
        NGS_erp_list_temp = []
        NGS_erp_list = []
        NGS_snx_list = []


        # IGS
        # generate Precise Ephemeris url
        if self.igs_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.igs_Precisi_track_box.currentText() == 'Ultra':
                    for i in ['00', '06', '12', '18']:
                        if time[4] < 2238:
                            file_name = 'igu'+str(time[4])+str(time[5])+'_'+i+'.sp3.Z'
                            #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/igu21600_06.sp3.Z
                        else:
                            file_name = 'IGS0OPSULT_' + str(time[0]) + str(time[3]) + i + '00_02D_15M_ORB.SP3.gz'
                            #  ftp://igs.gnsswhu.cn/pub/gps/products/IGS0OPSULT_20223311200_02D_15M_ORB.SP3.gz
                        url = select_url + str(time[4]) + '/' + file_name
                        list = [url, file_name]
                        IGS_igu_list = IGS_igu_list + [list]
                        pass
                    pass
                elif self.igs_Precisi_track_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        file_name = 'igr'+str(time[4])+str(time[5])+'.sp3.Z'
                        #   ftp://igs.gnsswhu.cn/pub/gps/products/2121/igr21210.sp3.Z
                    else:
                        file_name = 'IGS0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_15M_ORB.SP3.gz'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/IGS0OPSRAP_20223320000_01D_15M_ORB.SP3.gz
                    url = select_url + str(time[4])+'/'+file_name
                    list = [url, file_name]
                    IGS_igu_list = IGS_igu_list + [list]
                    pass
                elif self.igs_Precisi_track_box.currentText() == 'Final':
                    if time[4] < 2238:
                        file_name = 'igs'+str(time[4])+str(time[5])+'.sp3.Z'
                        #   ftp://igs.gnsswhu.cn/pub/gps/products/2121/igs21210.sp3.Z
                    else:
                        file_name = 'IGS0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_15M_ORB.SP3.gz'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/IGS0OPSFIN_20223320000_01D_15M_ORB.SP3.gz
                    url = select_url + str(time[4])+'/'+file_name
                    print('------------------', url)
                    list = [url, file_name]
                    IGS_igu_list = IGS_igu_list + [list]
        pass

        # generate Precise Clock url
        if self.igs_Precisi_clock_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.igs_Precisi_clock_box.currentText() == 'Rapid':
                    ##  ftp://igs.gnsswhu.cn/pub/gps/products/2160/igr21601.clk.Z
                    if self.igs_Precisi_clock_interv_box.currentText() == '30s':
                        if time[4] < 2238:
                            file_name = 'igr'+str(time[4])+str(time[5])+'.clk_30s.Z'
                        else:
                            # IGS0OPSRAP_20223320000_01D_05M_CLK.CLK.gz
                            file_name = 'IGS0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                        url = select_url + str(time[4])+'/'+file_name
                        list = [url, file_name]
                        IGS_clk_list = IGS_clk_list + [list]
                    elif self.igs_Precisi_clock_interv_box.currentText() == '300s':
                        if time[4] < 2238:
                            file_name = 'igr'+str(time[4])+str(time[5])+'.clk.Z'
                        else:
                            # IGS0OPSRAP_20223320000_01D_05M_CLK.CLK.gz
                            file_name = 'IGS0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_05M_CLK.CLK.gz'
                        url = select_url + str(time[4])+'/'+file_name
                        list = [url, file_name]
                        IGS_clk_list = IGS_clk_list + [list]
                elif self.igs_Precisi_clock_box.currentText() == 'Final':
                    ##  ftp://igs.gnsswhu.cn/pub/gps/products/2160/igs21606.clk_30s.Z
                    if self.igs_Precisi_clock_interv_box.currentText() == '30s':
                        if time[4] < 2238:
                            file_name = 'igs'+str(time[4])+str(time[5])+'.clk_30s.Z'
                        else:
                            # IGS0OPSFIN_20223320000_01D_30S_CLK.CLK.gz
                            file_name = 'IGS0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                        url = select_url + str(time[4])+'/'+file_name
                        list = [url, file_name]
                        IGS_clk_list = IGS_clk_list + [list]
                    elif self.igs_Precisi_clock_interv_box.currentText() == '300s':
                        if time[4] < 2238:
                            file_name = 'igs'+str(time[4])+str(time[5])+'.clk.Z'
                        else:
                            # IGS0OPSFIN_20223330000_01D_05M_CLK.CLK.gz
                            file_name = 'IGS0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_CLK.CLK.gz'
                        url = select_url + str(time[4])+'/'+file_name
                        list = [url, file_name]
                        IGS_clk_list = IGS_clk_list + [list]
        # print(IGS_clk_list)
        pass

        # generate troposphere url
        if self.igs_tro_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                for igs_station in self.igs_tro_box.currentText():
                    file_name = igs_station + str(time[3]) + str(0) + '.' + str(time[1]) + 'zpd.gz'
                    if select_url.find("esa") != -1:
                        #  ftp://gssc.esa.int/gnss/products/troposphere_zpd/2022/001/abmf0010.22zpd.gz
                        url = select_url + 'troposphere_zpd/' + str(time[0])+'/'+str(time[3]) + '/' + file_name
                    else:
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/troposphere/new/2022/001/abmf0010.22zpd.gz
                        url = select_url + 'troposphere/new/' + str(time[0])+'/'+str(time[3]) + '/' + file_name
                    list = [url, file_name]
                    IGS_track_analyze_tempe = IGS_track_analyze_tempe + [list]
            for i in IGS_track_analyze_tempe:
                if i not in IGS_track_analyze:
                    IGS_track_analyze.append(i)
        # print(IGS_track_analyze)

        # generate weekly station positions
        if self.igs_snx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            IGS_clock_analyze_tempe = []
            for time in all_YearAccuDay_GpsWeek:
                if self.igs_snx_box.currentText() == 'Daily':
                    if select_url.find("garner.ucsd") != -1:
                        ##  ftp://igs.gnsswhu.cn/pub/gps/products/2118/igs20p2118.snx.Z
                        file_name = 'igs' + str(time[1]) + 'p' + str(time[4]) + str(time[5]) + '.snx.Z'
                    ##  ftp://igs.gnsswhu.cn/pub/gps/products/2118/igs20P2118.snx.Z
                    else:
                        if self.choose_product_url_box.currentText() == 'ftp://igs.ign.fr/pub/igs/products/':
                            if time[0] == 2022 and time[4] == 2190:
                                file_name = 'igs' + '21' + 'P' + str(time[4]) + str(time[5]) + '.snx.Z'
                            else:
                                file_name = 'igs' + str(time[1]) + 'P' + str(time[4]) + str(time[5]) + '.snx.Z'
                        else:
                            if time[4] < 2238:
                                file_name = 'igs' + str(time[1]) + 'P' + str(time[4]) + str(time[5]) + '.snx.Z'
                            else:
                                # IGS0OPSSNX_20230580000_01D_01D_SOL.SNX.gz
                                file_name = 'IGS0OPSSNX_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                    url = select_url + str(time[4])+'/'+file_name
                    list = [url, file_name]
                    IGS_clock_analyze_tempe = IGS_clock_analyze_tempe + [list]

                elif self.igs_snx_box.currentText() == 'Weekly':
                    if time[2] <= 6 and time[2] < time[5]:
                        gps_week_year = time[1] - 1
                    else:
                        gps_week_year = time[1]
                    if select_url.find("garner.ucsd") != -1:
                        ##  ftp://igs.gnsswhu.cn/pub/gps/products/2118/igs20p21180.snx.Z
                        file_name = 'igs' + str(gps_week_year) + 'p' + str(time[4]) + '.snx.Z'
                    else:
                        if self.choose_product_url_box.currentText() == 'ftp://igs.ign.fr/pub/igs/products/':
                            if time[0] == 2022 and time[4] == 2190:
                                file_name = 'igs' + '21' + 'P' + str(time[4]) + str(time[5]) + '.snx.Z'
                            else:
                                file_name = 'igs' + str(time[1]) + 'P' + str(time[4]) + str(time[5]) + '.snx.Z'
                        else:
                            if time[4] < 2238:
                                ##  ftp://igs.gnsswhu.cn/pub/gps/products/2118/igs20P21180.snx.Z
                                file_name = 'igs' + str(gps_week_year) + 'P' + str(time[4]) + '.snx.Z'
                            else:
                                # IGS0OPSSNX_20230570000_07D_07D_SOL.SNX.gz
                                file_name = 'IGS0OPSSNX_' + str(time[0]) + str(time[3]) + '0000_07D_07D_SOL.SNX.gz'
                    url = select_url + str(time[4])+'/'+file_name
                    list = [url, file_name]
                    IGS_clock_analyze_tempe = IGS_clock_analyze_tempe + [list]
                for i in IGS_clock_analyze_tempe:
                    if i not in IGS_clock_analyze:
                        IGS_clock_analyze.append(i)
        # print(IGS_track_analyze)
        pass

        # generate Earth rotation parameters
        if self.igs_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.igs_erp_box.currentText() == 'Ultra':
                    for i in ['00', '06', '12', '18']:
                        if time[4] < 2238:
                            file_name = 'igu' + str(time[4]) + str(time[5]) + '_' + i + '.erp.Z'
                            #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/igu21600_00.erp.Z
                        else:
                            file_name = 'IGS0OPSULT_' + str(time[0]) + str(time[3]) + i + '00_02D_01D_ERP.ERP.gz'
                            #  IGS0OPSULT_20223310600_02D_01D_ERP.ERP.gz
                        url = select_url + str(time[4]) + '/' + file_name
                        list = [url, file_name]
                        IGS_erp_list_tempe = IGS_erp_list_tempe + [list]
                elif self.igs_erp_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        ##  ftp://igs.gnsswhu.cn/pub/gps/products/2160/igr21605.erp.Z
                        file_name = 'igr' + str(time[4]) + str(time[5]) + '.erp.Z'
                    else:
                        file_name = 'IGS0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                        #  IGS0OPSRAP_20223310000_01D_01D_ERP.ERP.gz
                    url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    IGS_erp_list_tempe = IGS_erp_list_tempe + [list]
                elif self.igs_erp_box.currentText() == 'Final':
                    if time[4] < 2238:
                        ##  ftp://igs.gnsswhu.cn/pub/gps/products/2160/igs21607.erp.Z
                        file_name = 'igs' + str(time[4]) + '7.erp.Z'
                    else:
                        file_name = 'IGS0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_07D_01D_ERP.ERP.gz'
                        #  IGS0OPSFIN_20223310000_07D_01D_ERP.ERP.gz
                    url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    IGS_erp_list_tempe = IGS_erp_list_tempe + [list]
                for i in IGS_erp_list_tempe:
                    if i not in IGS_erp_list:
                        IGS_erp_list.append(i)

        # generate satellite antenna phase center offset
        if self.igs_atx_check.isChecked():
            if self.igs_atx_box.currentText() == 'igs14':
                atx_file_name = 'igs14.atx'
            elif self.igs_atx_box.currentText() == 'igs14_2223':
                atx_file_name = 'igs14_2223.atx'
            elif self.igs_atx_box.currentText() == 'igs20':
                atx_file_name = 'igs20.atx'
            elif self.igs_atx_box.currentText() == 'igs20_2221':
                atx_file_name = 'igs20_2221.atx'
            elif self.igs_atx_box.currentText() == 'igs08':
                atx_file_name = 'igs08.atx'
            elif self.igs_atx_box.currentText() == 'igs05':
                atx_file_name = 'igs05.atx'
            Sourcr_igs_atx_path = "./lib/atx files/" + atx_file_name
            New_igs_atx_path = self.show_outsave_files_path_button.text() + '/' + atx_file_name
            atx_f1 = open(Sourcr_igs_atx_path, "r")
            atx_f2 = open(New_igs_atx_path, "w")
            shutil.copyfileobj(atx_f1, atx_f2, length=1024)
            atx_f1.close()

        #  generate Ionosphere url
        if self.igs_i_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.igs_i_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/001/igrg0010.21i.Z
                        file_name = 'igrg'+str(time[3])+'0.'+str(time[1])+'i.Z'
                    else:
                        ##  IGS0OPSRAP_20230200000_01D_02H_GIM.INX.gz
                        file_name = 'IGS0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_02H_GIM.INX.gz'
                    url = select_url + 'ionex/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]
                elif self.igs_i_box.currentText() == 'Final':
                    if time[4] < 2238:
                        ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/001/igsg0010.21i.Z
                        file_name = 'igsg' + str(time[3]) + '0.' + str(time[1]) + 'i.Z'
                    else:
                        ##  IGS0OPSFIN_20230200000_01D_02H_GIM.INX.gz
                        file_name = 'IGS0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_02H_GIM.INX.gz'
                    url = select_url + 'ionex/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]

        if self.igs_rate_TEC_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/300/roti3000.21f.Z
                file_name = 'roti'+str(time[3])+'0.'+str(time[1])+'f.Z'
                url = select_url + 'ionex/' + str(time[0])+'/'+str(time[3])+'/'+file_name
                list = [url, file_name]
                CODE_tro_list = CODE_tro_list + [list]

        # CODE
        # generate Precise Ephemeris url
        if self.code_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            #  self.code_Precisi_track_box.addItems(['G/R', 'MGEX'])
            for time in all_YearAccuDay_GpsWeek:
                if self.code_Precisi_track_box.currentText() == 'MGEX':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COM' + str(time[4]) + str(time[5]) + '.EPH.Z'
                            #  http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/2022/COM21906.EPH.Z
                        else:
                            ##  COD0MGXFIN_20223310000_01D_05M_ORB.SP3.gz
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_01D_05M_ORB.SP3.gz
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/1961/com19610.eph.Z
                        if time[4] >= 1962:
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                        else:
                            file_name = 'com' + str(time[4]) + str(time[5]) + '.eph.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_01D_05M_ORB.SP3.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_eph_list = CODE_eph_list + [list]
                elif self.code_Precisi_track_box.currentText() == 'G/R':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COD' + str(time[4]) + str(time[5]) + '.EPH.Z'
                            #  http://ftp.aiub.unibe.ch/CODE/2021/COD21385.EPH.Z
                        else:
                            ##  COD0MGXFIN_20223310000_01D_05M_ORB.SP3.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        if time[4] < 2238:
                            file_name = 'cod' + str(time[4]) + str(time[5]) + '.eph.Z'
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2237/cod22370.eph.Z
                        else:
                            ##  COD0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_eph_list = CODE_eph_list + [list]
            pass

        # generate Precise Clock url
        #  self.code_Precisi_clock_interv_box.addItems(['5s', '30s', '30s MGEX'])
        if self.code_Precisi_clock_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.code_Precisi_clock_interv_box.currentText() == '5s G/R':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COD'+str(time[4])+str(time[5])+'.CLK_05S.Z'
                            #     http://ftp.aiub.unibe.ch/CODE/2021/COD21386.CLK_05S.Z
                        else:
                            ##  COD0OPSFIN_20223310000_01D_05S_CLK.CLK.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05S_CLK.CLK.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        if time[4] < 2238:
                            file_name = 'cod' + str(time[4]) + str(time[5]) + '.clk_05s.Z'
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2237/cod22370.erp.Z
                        else:
                            ##  COD0OPSFIN_20223310000_01D_05S_CLK.CLK.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05S_CLK.CLK.gz'
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_clk_list = CODE_clk_list + [list]
                elif self.code_Precisi_clock_interv_box.currentText() == '30s G/R':
                    #     http://ftp.aiub.unibe.ch/CODE/2021/COD21386.CLK.Z
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COD'+str(time[4])+str(time[5])+'.CLK.Z'
                        else:
                            ##  COD0OPSFIN_20223310000_01D_30S_CLK.CLK.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        if time[4] < 2238:
                            file_name = 'cod' + str(time[4]) + str(time[5]) + '.clk.Z'
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2237/cod22370.erp.Z
                        else:
                            ##  COD0OPSFIN_20223310000_01D_30S_CLK.CLK.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_clk_list = CODE_clk_list + [list]
                elif self.code_Precisi_clock_interv_box.currentText() == '30s MGEX':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            #   http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/2022/COM21906.CLK.Z
                            file_name = 'COM'+str(time[4])+str(time[5])+'.CLK.Z'
                        else:
                            ##  COD0MGXFIN_20223310000_01D_30S_CLK.CLK.gz
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_01D_30S_CLK.CLK.gz
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/1961/com19610.clk.Z
                        if time[4] >= 1962:
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                        else:
                            file_name = 'com' + str(time[4]) + str(time[5]) + '.clk.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_03D_12H_ERP.ERP.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_clk_list = CODE_clk_list + [list]

        # generate MGEX Satellite Attitude url
        #  self.code_obx_box.addItems(['G/R', 'MGEX'])
        if self.code_obx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.code_obx_box.currentText() == 'MGEX':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COM'+str(time[4])+str(time[5])+'.OBX.Z'
                            #    http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/COM21906.OBX.Z
                        else:
                            ##  COD0MGXFIN_20223310000_01D_30S_ATT.OBX.gz
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_ATT.OBX.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_01D_15M_ATT.OBX.gz
                        if time[4] >= 1962 and time[4] < 2238:
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_15M_ATT.OBX.gz'
                        elif time[4] >= 2238:
                            #  COD0MGXFIN_20223380000_01D_30S_ATT.OBX.gz
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_ATT.OBX.gz'
                        else:
                            file_name = 'com' + str(time[4]) + str(time[5]) + '.obx.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_01D_15M_ATT.OBX.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_obx_list = CODE_obx_list + [list]
                elif self.code_obx_box.currentText() == 'G/R':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COD' + str(time[4]) + str(time[5]) + '.OBX.Z'
                            #    http://ftp.aiub.unibe.ch/CODE/2021/COD21391.OBX.Z
                        else:
                            ##  COD0OPSFIN_20223310000_01D_30S_ATT.OBX.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_ATT.OBX.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        if time[4] < 2238:
                            file_name = 'cod' + str(time[4]) + str(time[5]) + '.obx.Z'
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2237/cod22370.obx.Z
                        elif time[4] >= 2238:
                            #  COD0OPSFIN_20223310000_01D_30S_ATT.OBX.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_ATT.OBX.gz'
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_obx_list = CODE_obx_list + [list]
            pass

        # generate Ionosphere url
        if self.code_ion_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'COD'+str(time[4])+str(time[5])+'.ION.Z'
                    #  http://ftp.aiub.unibe.ch/CODE/2021/COD21385.ION.Z
                else:
                    ##  COD0OPSFIN_20223310000_01D_01H_GIM.ION.gz
                    file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01H_GIM.ION.gz'
                url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                list = [url, file_name]
                CODE_ion_list = CODE_ion_list + [list]
            pass

        if self.code_i_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("aiub") != -1:
                    if time[4] < 2238:
                        file_name = 'CODG'+str(time[3])+'0.'+str(time[1])+'I.Z'
                        #  http://ftp.aiub.unibe.ch/CODE/2020/CODG0010.20I.Z
                    else:
                        ##  COD0OPSFIN_20223310000_01D_01H_GIM.INX.gz
                        file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01H_GIM.INX.gz'
                    url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                else:
                    if time[4] < 2238:
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2022/347/
                        file_name = 'codg' + str(time[3]) + '0.' + str(time[1]) + 'i.Z'
                    else:
                        ##  COD0OPSFIN_20223470000_01D_01H_GIM.INX.gz
                        file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01H_GIM.INX.gz'
                    url = select_url + 'ionex/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                list = [url, file_name]
                CODE_i_list = CODE_i_list + [list]
            pass

        # generate troposphere url
        if self.code_tro_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("aiub") != -1:
                    if time[4] < 2238:
                        file_name = 'COD'+str(time[4])+str(time[5])+'.TRO.Z'
                        #  http://ftp.aiub.unibe.ch/CODE/2021/COD21385.TRO.Z
                    else:
                        ##  COD0OPSFIN_20223310000_01D_01H_TRO.TRO.gz
                        file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01H_TRO.TRO.gz'
                    url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                else:
                    if time[4] < 2238:
                        file_name = 'cod' + str(time[4]) + str(time[5]) + '.tro.Z'
                        # ftp://igs.gnsswhu.cn/pub/gps/products/2237/cod22370.tro.Z
                    else:
                        ##  COD0OPSFIN_20230500000_01D_01H_TRO.TRO.gz
                        file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01H_TRO.TRO.gz'
                    url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                CODE_tro_list = CODE_tro_list + [list]
            pass

        #  generate DCB url
        #  self.code_dcb_box.addItems(['P1-C1', 'P1-P2', 'P2-C2'])
        if self.code_dcb_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.code_dcb_box.currentText() == 'P1-C1':
                    file_name = 'P1C1'+str(time[1])+str(time[6])+'_RINEX.DCB.Z'
                    #  http://ftp.aiub.unibe.ch/CODE/2021/P1C12101_RINEX.DCB.Z
                    url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CODE_dcb_list_temp = CODE_dcb_list_temp + [list]
                elif self.code_dcb_box.currentText() == 'P1-P2':
                    file_name = 'P1P2'+str(time[1])+str(time[6])+'_ALL.DCB.Z'
                    #  http://ftp.aiub.unibe.ch/CODE/2021/P1P22106_ALL.DCB.Z
                    url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CODE_dcb_list_temp = CODE_dcb_list_temp + [list]
                elif self.code_dcb_box.currentText() == 'P2-C2':
                    file_name = 'P2C2'+str(time[1])+str(time[6])+'_RINEX.DCB.Z'
                    #  http://ftp.aiub.unibe.ch/CODE/2021/P2C22102_RINEX.DCB.Z
                    url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CODE_dcb_list_temp = CODE_dcb_list_temp + [list]
                elif self.code_dcb_box.currentText() == 'MGEX':
                    file_name = 'COM'+str(time[4])+str(time[5])+'.DCB.Z'
                    #  http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/2021/COM21385.DCB.Z
                    url = 'http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CODE_dcb_list_temp = CODE_dcb_list_temp + [list]
            for i in CODE_dcb_list_temp:
                if i not in CODE_dcb_list:
                    CODE_dcb_list.append(i)

        # generate BIA url
        #  self.code_bia_box.addItems(['G/R', 'MGEX'])
        if self.code_bia_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.code_bia_box.currentText() == 'MGEX':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COM'+str(time[4])+str(time[5])+'.BIA.Z'
                            #  http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/2022/COM21910.OBX.Z
                        else:
                            ##  COD0MGXFIN_20223310000_01D_01D_OSB.BIA.gz
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_OSB.BIA.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_01D_01D_OSB.BIA.gz
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/1961/com19610.bia.Z
                        if time[4] >= 1962:
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_OSB.BIA.gz'
                        else:
                            file_name = 'com' + str(time[4]) + str(time[5]) + '.bia.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_03D_12H_ERP.ERP.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_bia_list = CODE_bia_list + [list]
                elif self.code_bia_box.currentText() == 'G/R':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COD' + str(time[4]) + str(time[5]) + '.BIA.Z'
                            #  http://ftp.aiub.unibe.ch/CODE/2021/COD21385.BIA.Z
                        else:
                            ##  COD0OPSFIN_20223310000_01D_01D_OSB.BIA.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_OSB.BIA.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        if time[4] < 2238:
                            file_name = 'cod' + str(time[4]) + str(time[5]) + '.bia.Z'
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2237/cod22370.bia.Z
                        else:
                            ##  COD0OPSFIN_20223380000_01D_01D_OSB.BIA.gz
                            file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_OSB.BIA.gz'
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_bia_list = CODE_bia_list + [list]
            pass

        # generate Earth rotation parameters url
        #  self.code_erp_box.addItems(['G/R', 'MGEX'])
        if self.code_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.code_erp_box.currentText() == 'MGEX':
                    if select_url.find("aiub") != -1:
                        if time[4] < 2238:
                            file_name = 'COM'+str(time[4])+str(time[5])+'.ERP.Z'
                            #  http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/2022/COM21906.ERP.Z
                        else:
                            ##  COD0MGXFIN_20223310000_01D_12H_ERP.ERP.gz
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_12H_ERP.ERP.gz'
                        url = 'http://ftp.aiub.unibe.ch/CODE_MGEX/CODE/' + str(time[0]) + '/' + file_name
                    else:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_03D_12H_ERP.ERP.gz
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/1961/com19610.erp.Z
                        if time[4] >= 1962:
                            file_name = 'COD0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_03D_12H_ERP.ERP.gz'
                        else:
                            file_name = 'com' + str(time[4]) + str(time[5]) + '.erp.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2237/COD0MGXFIN_20223240000_03D_12H_ERP.ERP.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    CODE_erp_list = CODE_erp_list + [list]
                elif self.code_erp_box.currentText() == 'G/R':
                    if time[4] < 2238:
                        file_name = 'COD' + str(time[4]) + str(time[5]) + '.ERP.Z'
                        #  http://ftp.aiub.unibe.ch/CODE/2020/COD21385.ERP.Z
                    else:
                        ##  COD0OPSFIN_20223310000_01D_01D_ERP.ERP.gz
                        file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                    url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CODE_erp_list = CODE_erp_list + [list]
            pass

        # generate SNX url
        if self.code_snx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("aiub") != -1:
                    if time[4] < 2238:
                        file_name = 'COD'+str(time[4])+str(time[5])+'.SNX.Z'
                        #  http://ftp.aiub.unibe.ch/CODE/2021/COD21385.SNX.Z
                    else:
                        ##  COD0OPSFIN_20223310000_01D_01D_SOL.SNX.gz
                        file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                    url = 'http://ftp.aiub.unibe.ch/CODE/' + str(time[0]) + '/' + file_name
                else:
                    if time[4] < 2238:
                        file_name = 'cod' + str(time[4]) + str(time[5]) + '.snx.Z'
                        # ftp://igs.gnsswhu.cn/pub/gps/products/2237/cod22370.snx.Z
                    else:
                        ##  COD0OPSFIN_20223310000_01D_01D_SOL.SNX.gz
                        file_name = 'COD0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                    url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                CODE_snx_list = CODE_snx_list + [list]
            pass

        # CAS
        # generate DCB url
        if self.cas_dcb_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.cas_dcb_box.currentText() == 'P1-C1':
                    file_name = 'P1C1'+str(time[1])+str(time[3])+'.DCB'
                    #  ftp://182.92.166.182/product/final/2021/001/P1C121001.DCB
                    url = 'ftp://182.92.166.182/product/final/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    list = [url, file_name]
                    CAS_dcb_list = CAS_dcb_list + [list]
                elif self.cas_dcb_box.currentText() == 'P2-C2':
                    file_name = 'P2C2'+str(time[1])+str(time[3])+'.DCB'
                    #  ftp://182.92.166.182/product/final/2021/001/P2C221001.DCB
                    url = 'ftp://182.92.166.182/product/final/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    list = [url, file_name]
                    CAS_dcb_list = CAS_dcb_list + [list]

        # generate bia url
        #  self.cas_bia_box.addItems(['IGS', 'MGEX'])
        if self.cas_bia_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.cas_bia_box.currentText() == 'G/R (no APC)':
                    if select_url.find("gipp") != -1:
                        ##  ftp://ftp.gipp.org.cn/product/dcb/igs/2022/CAS0IGSRAP_20220010000_01D_01D_OSB.BIA.gz
                        file_name = 'CAS0IGSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA.gz'
                        url = select_url + 'dcb/igs/' + str(time[0]) + '/' + file_name
                    if select_url.find("182.92") != -1:
                        file_name = 'CAS0IGSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA'
                        #  ftp://182.92.166.182/product/igsdcb/2021/CAS0IGSRAP_20210010000_01D_01D_OSB.BIA.gz
                        url = select_url + 'igsdcb/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CAS_bia_list = CAS_bia_list + [list]
                elif self.cas_bia_box.currentText() == 'MGEX(no APC)':
                    if select_url.find("gipp") != -1:
                        ##  ftp://ftp.gipp.org.cn/product/dcb/mgex/2022/CAS0IGSRAP_20220010000_01D_01D_OSB.BIA.gz
                        if time[4] >= 2297:
                            file_name = 'CAS0OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA.gz'
                        else:
                            file_name = 'CAS0MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA.gz'
                        url = select_url + 'dcb/mgex/' + str(time[0]) + '/' + file_name
                    if select_url.find("182.92") != -1:
                        if time[4] >= 2297:
                            file_name = 'CAS0OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA'
                        else:
                            file_name = 'CAS0MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA'
                        #  ftp://182.92.166.182/product/mgexdcb/2021/CAS0MGXRAP_20210010000_01D_01D_OSB.BIA.gz
                        url = select_url + 'mgexdcb/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CAS_bia_list = CAS_bia_list + [list]
                elif self.cas_bia_box.currentText() == 'MGEX(APC)':
                    if select_url.find("gipp") != -1:
                        ##  ftp://ftp.gipp.org.cn/product/dcb/mgex/2022/CAS1IGSRAP_20220010000_01D_01D_OSB.BIA.gz
                        if time[4] >= 2297:
                            file_name = 'CAS1OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA.gz'
                        else:
                            file_name = 'CAS1MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA.gz'
                        url = select_url + 'dcb/mgex/' + str(time[0]) + '/' + file_name
                    elif select_url.find("182.92") != -1:
                        if time[4] >= 2297:
                            file_name = 'CAS1OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA'
                        else:
                            file_name = 'CAS1MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_OSB.BIA'
                        #  ftp://182.92.166.182/product/mgexdcb/2021/CAS1MGXRAP_20210010000_01D_01D_OSB.BIA.gz
                        url = 'ftp://182.92.166.182/product/mgexdcb/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CAS_bia_list = CAS_bia_list + [list]

        # generate BSX url
        #  self.cas_bsx_box.addItems(['IGS', 'MGEX'])
        if self.cas_bsx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.cas_bsx_box.currentText() == 'G/R (no APC)':
                    if select_url.find("gipp") != -1:
                        ##  ftp://ftp.gipp.org.cn/product/dcb/igs/2022/CAS0IGSRAP_20220010000_01D_01D_DCB.BSX.gz
                        file_name = 'CAS0IGSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        url = select_url + 'dcb/igs/' + str(time[0]) + '/' + file_name
                    if select_url.find("182.92") != -1:
                        file_name = 'CAS0IGSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX'
                        #  ftp://182.92.166.182/product/igsdcb/2021/CAS0IGSRAP_20210010000_01D_01D_DCB.BSX.gz
                        url = 'ftp://182.92.166.182/product/igsdcb/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CAS_bsx_list = CAS_bsx_list + [list]
                elif self.cas_bsx_box.currentText() == 'MGEX(no APC)':
                    if select_url.find("gipp") != -1:
                        ##  ftp://ftp.gipp.org.cn/product/dcb/mgex/2022/CAS0IGSRAP_20220010000_01D_01D_DCB.BSX.gz
                        if time[4] >= 2297:
                            file_name = 'CAS0OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA.gz'
                        else:
                            file_name = 'CAS0MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        url = select_url + 'dcb/mgex/' + str(time[0]) + '/' + file_name
                    elif select_url.find("182.92") != -1:
                        if time[4] >= 2297:
                            file_name = 'CAS0OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA'
                        else:
                            file_name = 'CAS0MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX'
                        #  ftp://182.92.166.182/product/mgexdcb/2021/CAS0MGXRAP_20210010000_01D_01D_DCB.BSX.gz
                        url = 'ftp://182.92.166.182/product/mgexdcb/' + str(time[0]) + '/' + file_name
                    elif select_url.find("cddis") != -1:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/CAS0MGXRAP_20220150000_01D_01D_DCB.BSX.gz
                        if time[4] >= 2238:
                            file_name = 'CAS0OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA.gz'
                        else:
                            file_name = 'CAS0MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/
                        url = select_url + 'mgex/dcb/' + str(time[0]) + '/' + file_name
                    elif select_url.find("gnsswhu") != -1 or select_url.find("esa") != -1:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/CAS0MGXRAP_20220150000_01D_01D_DCB.BSX.gz
                        if time[4] >= 2295:
                            file_name = 'CAS0OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA.gz'
                        else:
                            file_name = 'CAS0MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/
                        url = select_url + 'mgex/dcb/' + str(time[0]) + '/' + file_name
                    else:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/CAS0MGXRAP_20220150000_01D_01D_DCB.BSX.gz
                        if time[4] >= 2297:
                            file_name = 'CAS0OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA.gz'
                        else:
                            file_name = 'CAS0MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/
                        url = select_url + 'mgex/dcb/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CAS_bsx_list = CAS_bsx_list + [list]
                elif self.cas_bsx_box.currentText() == 'MGEX(APC)':
                    if select_url.find("gipp") != -1:
                        ##  ftp://ftp.gipp.org.cn/product/dcb/mgex/2022/CAS1IGSRAP_20220010000_01D_01D_DCB.BSX.gz
                        if time[4] >= 2297:
                            file_name = 'CAS1OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA.gz'
                        else:
                            file_name = 'CAS1MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        url = select_url + 'dcb/mgex/' + str(time[0]) + '/' + file_name
                    elif select_url.find("182.92") != -1:
                        if time[4] >= 2297:
                            file_name = 'CAS1OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA'
                        else:
                            file_name = 'CAS1MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX'
                        #  ftp://182.92.166.182/product/mgexdcb/2021/CAS1MGXRAP_20210010000_01D_01D_DCB.BSX.gz
                        url = 'ftp://182.92.166.182/product/mgexdcb/' + str(time[0]) + '/' + file_name
                    elif select_url.find("cddis") != -1:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/CAS0MGXRAP_20220150000_01D_01D_DCB.BSX.gz
                        if time[4] >= 2238:
                            file_name = 'CAS1OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA.gz'
                        else:
                            file_name = 'CAS1MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/
                        url = select_url + 'mgex/dcb/' + str(time[0]) + '/' + file_name
                    elif select_url.find("gnsswhu") != -1 or select_url.find("esa") != -1:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/CAS0MGXRAP_20220150000_01D_01D_DCB.BSX.gz
                        if time[4] >= 2295:
                            file_name = 'CAS1OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA.gz'
                        else:
                            file_name = 'CAS1MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/
                        url = select_url + 'mgex/dcb/' + str(time[0]) + '/' + file_name
                    else:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/CAS0MGXRAP_20220150000_01D_01D_DCB.BSX.gz
                        if time[4] >= 2297:
                            file_name = 'CAS1OPSRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BIA.gz'
                        else:
                            file_name = 'CAS1MGXRAP_'+str(time[0])+str(time[3])+'0000_01D_01D_DCB.BSX.gz'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/dcb/2022/
                        url = select_url + 'mgex/dcb/' + str(time[0]) + '/' + file_name
                    list = [url, file_name]
                    CAS_bia_list = CAS_bia_list + [list]

        # generate Ionosphere url
        if self.cas_ion_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                file_name = 'cas'+str(time[1])+str(time[3])+'.ION'
                #  ftp://182.92.166.182/product/final/2021/001/cas21001.ION
                url = 'ftp://182.92.166.182/product/final/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                list = [url, file_name]
                CAS_ion_list = CAS_ion_list + [list]
            pass

        if self.cas_i_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.cas_i_box.currentText() == 'Rapid':
                    if select_url.find("gipp") != -1:
                        ##  ftp://ftp.gipp.org.cn/product/ionex/2022/001/carg0010.21i.Z
                        file_name = 'carg'+str(time[3])+'0.'+str(time[1])+'i.Z'
                        url = select_url + 'ionex/' +str(time[0])+'/'+str(time[3])+'/'+file_name
                    else:
                        ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/001/carg0010.21i.Z
                        file_name = 'carg'+str(time[3])+'0.'+str(time[1])+'i.Z'
                        url = select_url + 'ionex/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]
                elif self.cas_i_box.currentText() == 'Final':
                    if select_url.find("gipp") != -1:
                        ##  ftp://ftp.gipp.org.cn/product/ionex/2022/001/casg0010.21i.Z
                        file_name = 'casg'+str(time[3])+'0.'+str(time[1])+'i.Z'
                        url = select_url + 'ionex/' +str(time[0])+'/'+str(time[3])+'/'+file_name
                    else:
                        ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/001/casg0010.21i.Z
                        file_name = 'casg' + str(time[3]) + '0.' + str(time[1]) + 'i.Z'
                        url = select_url + 'ionex/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]

        # WHU
        # generate Precise Ephemeris url
        #                 if time[4] < 2238:
        if self.whu_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.whu_Precisi_track_box.currentText() == 'Ultra':
                    for i in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                              '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
                              '22', '23']:
                        if time[4] < 2243:
                            file_name = 'WUM0MGXULA_' + str(time[0]) + time[3] + i + '00_01D_05M_ORB.SP3.gz'
                            #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2231/WUM0MGXULA_20222821000_01D_05M_ORB.SP3.gz
                        else:
                            file_name = 'WUM0MGXULT_' + str(time[0]) + time[3] + i + '00_01D_05M_ORB.SP3.gz'
                            #  WUM0MGXULT_20222821000_01D_05M_ORB.SP3.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                        list = [url, file_name]
                        WHU_sp3_list = WHU_sp3_list + [list]
                elif self.whu_Precisi_track_box.currentText() == 'Rapid':
                    file_name = 'WUM0MGXRAP_' + str(time[0]) + time[3] + '0000_01D_05M_ORB.SP3.gz'
                    #  ftp://igs.gnsswhu.cn/pub/whu/phasebias/2022/orbit/WUM0MGXRAP_20220040000_01D_01M_ORB.SP3.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    elif select_url.find("ftp://igs.gnsswhu.cn/pub/whu/") != -1:
                        file_name = 'WUM0MGXRAP_' + str(time[0]) + time[3] + '0000_01D_01M_ORB.SP3.gz'
                        url = 'ftp://igs.gnsswhu.cn/pub/whu/phasebias/' + str(time[0]) + '/orbit/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    WHU_sp3_list = WHU_sp3_list + [list]
                elif self.whu_Precisi_track_box.currentText() == 'Final':
                    file_name = 'WUM0MGXFIN_' + str(time[0]) + time[3] + '0000_01D_05M_ORB.SP3.gz'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2231/WUM0MGXFIN_20222820000_01D_05M_ORB.SP3.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    WHU_sp3_list = WHU_sp3_list + [list]

        # generate Precise Clock url
        if self.whu_Precisi_clock_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.whu_Precisi_clock_box.currentText() == 'Ultra':
                    for i in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                              '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
                              '22', '23', '24']:
                        if time[4] < 2243:
                            file_name = 'WUM0MGXULA_' + str(time[0]) + time[3] + i + '00_01D_05M_CLK.CLK.gz'
                            #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2231/WUM0MGXULA_20222821000_01D_05M_CLK.CLK.gz
                        else:
                            file_name = 'WUM0MGXULT_' + str(time[0]) + time[3] + i + '00_01D_05M_CLK.CLK.gz'
                            #  WUM0MGXULA_20222821000_01D_05M_CLK.CLK.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                        list = [url, file_name]
                        WHU_clock_list = WHU_clock_list + [list]

                elif self.whu_Precisi_clock_box.currentText() == 'Rapid':
                    file_name = 'WUM0MGXRAP_' + str(time[0]) + time[3] + '0000_01D_30S_CLK.CLK.gz'
                    #  ftp://igs.gnsswhu.cn/pub/whu/phasebias/2022/orbit/WUM0MGXRAP_20220040000_01D_30S_CLK.CLK.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    elif select_url.find("ftp://igs.gnsswhu.cn/pub/whu/") != -1:
                        url = 'ftp://igs.gnsswhu.cn/pub/whu/phasebias/' + str(time[0]) + '/clock/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    WHU_clock_list = WHU_clock_list + [list]

                elif self.whu_Precisi_clock_box.currentText() == 'Final':
                    file_name = 'WUM0MGXFIN_' + str(time[0]) + time[3] + '0000_01D_30S_CLK.CLK.gz'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2231/WUM0MGXFIN_20222820000_01D_30S_CLK.CLK.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    WHU_clock_list = WHU_clock_list + [list]

        # generate bia url
        if self.whu_bia_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                file_name = 'WUM0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_OSB.BIA.gz'
                if select_url.find("ftp://igs.gnsswhu.cn/pub/whu/") != -1:
                    #  ftp://igs.gnsswhu.cn/pub/whu/MGEX/DCB/2021/WUM0MGXRAP_20210020000_01D_01D_OSB.BIA.gz
                    url = 'ftp://igs.gnsswhu.cn/pub/whu/MGEX/DCB/'+str(time[0])+'/'+file_name
                else:
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2231/WUM0MGXRAP_20222820000_01D_01D_OSB.BIA.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                WHU_bia_list = WHU_bia_list + [list]

        # generate Ionosphere url
        if self.whu_i_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if self.whu_i_box.currentText() == 'Rapid':
                    file_name = 'whrg'+str(time[3])+'0.'+str(time[1])+'i.Z'
                    #  ftp://igs.gnsswhu.cn/pub/whu/MGEX/ionosphere/2021/whrg0010.21i.Z
                    url = 'ftp://igs.gnsswhu.cn/pub/whu/MGEX/ionosphere/'+str(time[0])+'/'+file_name
                    list = [url, file_name]
                    WHU_i_list = WHU_i_list + [list]
                elif self.whu_i_box.currentText() == 'Final':
                    file_name = 'whug'+str(time[3])+'0.'+str(time[1])+'i.Z'
                    #  ftp://igs.gnsswhu.cn/pub/whu/MGEX/ionosphere/2021/whug0010.21i.Z
                    url = 'ftp://igs.gnsswhu.cn/pub/whu/MGEX/ionosphere/'+str(time[0])+'/'+file_name
                    list = [url, file_name]
                    WHU_i_list = WHU_i_list + [list]

        # generate Earth rotation parameters url
        if self.whu_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2204/WUM0MGXFIN_20220940000_01D_01D_ERP.ERP.gz
                # file_name = 'WUM0MGXFIN_'+str(time[0])+str(time[3])+'0000_01D_01D_ERP.ERP.gz'
                if select_url.find("esa") != -1:
                    file_name = 'WUM0MGXULA_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                    url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                else:
                    file_name = 'WUM0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                    url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                WHU_erp_list = WHU_erp_list + [list]

                if self.whu_erp_box.currentText() == 'Ultra':
                    for i in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                              '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
                              '22', '23']:
                        if time[4] < 2243:
                            file_name = 'WUM0MGXULA_' + str(time[0]) + time[3] + i + '00_01D_01D_ERP.ERP.gz'
                            #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2231/WUM0MGXULA_20222821000_01D_01D_ERP.ERP.gz
                        else:
                            file_name = 'WUM0MGXULT_' + str(time[0]) + time[3] + i + '00_01D_01D_ERP.ERP.gz'
                            #  WUM0MGXULT_20222821000_01D_01D_ERP.ERP.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                        list = [url, file_name]
                        WHU_erp_list = WHU_erp_list + [list]

                elif self.whu_erp_box.currentText() == 'Rapid':
                    file_name = 'WUM0MGXRAP_' + str(time[0]) + time[3] + '0000_01D_01D_ERP.ERP.gz'
                    #  ftp://igs.gnsswhu.cn/pub/whu/phasebias/2022/orbit/WUM0MGXRAP_20220040000_01D_01D_ERP.ERP.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    elif select_url.find("ftp://igs.gnsswhu.cn/pub/whu/") != -1:
                        url = 'ftp://igs.gnsswhu.cn/pub/whu/phasebias/' + str(time[0]) + '/orbit/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    WHU_erp_list = WHU_erp_list + [list]

                elif self.whu_erp_box.currentText() == 'Final':
                    file_name = 'WUM0MGXFIN_' + str(time[0]) + time[3] + '0000_01D_01D_ERP.ERP.gz'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2231/WUM0MGXFIN_20222820000_01D_01D_ERP.ERP.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    WHU_erp_list = WHU_erp_list + [list]

        # GFZ
        # generate Precise Ephemeris url
        if self.gfz_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.gfz_Precisi_track_box.currentText() == 'Ultra':
                    for i in ['00', '06', '12', '18']:
                        if time[4] < 2238:
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2160/gfz21600.sp3.Z
                            file_name = 'gfu'+str(time[4])+str(time[5])+'_'+i+'.sp3.gz'
                        else:
                            #  GFZ0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                            file_name = 'GFZ0OPSULT_' + str(time[0]) + str(time[3]) + i + '00_02D_05M_ORB.SP3.gz'
                        # file_name = 'gfu'+str(time[4])+str(time[5])+'_'+i+'.sp3.gz'
                        #  ftp://ftp.gfz-potsdam.de/GNSS/products/ultra/w2160/gfu21600_00.sp3.gz
                        if select_url.find("gfz-potsdam") != -1:
                            url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/ultra/w'+str(time[4]) + '/' + file_name
                        else:
                            url = select_url + str(time[4]) + '/' + file_name
                        list = [url, file_name]
                        GFZ_sp3_list = GFZ_sp3_list + [list]
                elif self.gfz_Precisi_track_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/2160/gfz21600.sp3.Z
                        file_name = 'gfz' + str(time[4]) + str(time[5]) + '.sp3.Z'
                    else:
                        #  GFZ0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                        file_name = 'GFZ0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'

                    if select_url.find("gfz-potsdam") != -1:
                        #  ftp://ftp.gfz-potsdam.de/GNSS/products/rapid/w2200/gfz21600.sp3.gz
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/rapid/w' + str(time[4]) + '/' + file_name
                    else:
                        url = select_url + str(time[4]) + '/' + file_name

                    list = [url, file_name]
                    GFZ_sp3_list = GFZ_sp3_list + [list]
                elif self.gfz_Precisi_track_box.currentText() == 'Final':
                    if select_url.find("gfz-potsdam") != -1:
                        if time[4] < 2237:
                            #  ftp://ftp.gfz-potsdam.de/GNSS/products/final/w2160/gfz21600.sp3.Z
                            file_name = 'gfz' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        else:
                            #  GFZ0OPSFIN_20223240000_01D_15M_ORB.SP3.gz
                            file_name = 'GFZ0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_15M_ORB.SP3.gz'
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/final/w' + str(time[4]) + '/' + file_name
                    else:
                        if time[4] < 2238:
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2160/gfz21600.sp3.Z
                            file_name = 'gfz' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        else:
                            #  GFZ0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                            file_name = 'GFZ0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_sp3_list = GFZ_sp3_list + [list]
                elif self.gfz_Precisi_track_box.currentText() == 'MGEX':
                    if select_url.find("gfz-potsdam") != -1:
                        if time[4] >= 2083:
                            file_name = 'GBM0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                        else:
                            file_name = 'gbm' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        #  ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/2200/GBM0MGXRAP_20220650000_01D_05M_ORB.SP3.gz
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/' + str(time[4]) + '/' + file_name
                    else:
                        if time[4] >= 1962:
                            file_name = 'GFZ0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                        else:
                            file_name = 'gbm' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GFZ0MGXRAP_20223230000_01D_05M_ORB.SP3.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_sp3_list = GFZ_sp3_list + [list]

        # generate Precise Clock url
        if self.gfz_Precisi_clock_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.gfz_Precisi_clock_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/2160/gfz21600.sp3.Z
                        file_name = 'gfz' + str(time[4]) + str(time[5]) + '.clk.Z'
                    else:
                        #  GFZ0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                        file_name = 'GFZ0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_05M_CLK.CLK.gz'

                    # file_name = 'gfz' + str(time[4]) + str(time[5]) + '.clk.gz'
                    #  ftp://ftp.gfz-potsdam.de/GNSS/products/rapid/w2160/gfz21600.clk.gz
                    if select_url.find("gfz-potsdam") != -1:
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/ultra/w' + str(time[4]) + '/' + file_name
                    else:
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_clock_list = GFZ_clock_list + [list]
                elif self.gfz_Precisi_clock_box.currentText() == 'Final':
                    if select_url.find("gfz-potsdam") != -1:
                        if time[4] < 2237:
                            file_name = 'gfz' + str(time[4]) + str(time[5]) + '.clk.Z'
                            #  ftp://ftp.gfz-potsdam.de/GNSS/products/final/w2237/
                        else:
                            file_name = 'GFZ0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                            #  GFZ0OPSFIN_20223240000_01D_30S_CLK.CLK.gz
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/final/w' + str(time[4]) + '/' + file_name
                    else:
                        if time[4] < 2238:
                            file_name = 'gfz' + str(time[4]) + str(time[5]) + '.clk.Z'
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2160/gfz21600.clk.Z
                        else:
                            file_name = 'GFZ0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                            #  GFZ0OPSFIN_20223310000_01D_30S_CLK.CLK.gz
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_clock_list = GFZ_clock_list + [list]
                elif self.gfz_Precisi_clock_box.currentText() == 'MGEX':
                    if select_url.find("gfz-potsdam") != -1:
                        if time[4] >= 2083:
                            file_name = 'GBM0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_05M_CLK.CLK.gz'
                        else:
                            file_name = 'gbm' + str(time[4]) + str(time[5]) + '.clk.Z'
                        #  ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/2200/GBM0MGXRAP_20220650000_01D_05M_CLK.CLK.gz
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/' + str(time[4]) + '/' + file_name
                    else:
                        if time[4] >= 1962:
                            file_name = 'GFZ0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_05M_CLK.CLK.gz'
                        else:
                            file_name = 'gbm' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GBM0MGXRAP_20220650000_01D_05M_CLK.CLK.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_clock_list = GFZ_clock_list + [list]

        # generate troposphere url
        if self.gfz_tro_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                for gfz_tro_station in self.gfz_tro_box.currentText():
                    file_name = gfz_tro_station + str(time[4]) + str(time[5]) + '.tro'
                    #  ftp://ftp.gfz-potsdam.de/GNSS/products/nrttrop/sinex_trop_GLOBAL_EPOS8/w2204/yell22045.tro
                    url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/nrttrop/sinex_trop_GLOBAL_EPOS8/w' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_tro_list = GFZ_tro_list + [list]

        # generate Ionosphere url
        if self.gfz_zpd_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                for gfz_zpd_station in self.gfz_zpd_box.currentText():
                    file_name = gfz_zpd_station + str(time[4]) + str(time[5]) + '.zpd'
                    #  ftp://ftp.gfz-potsdam.de/GNSS/products/nrttrop/sinex_trop_GLOBAL_EPOS8/w2204/yell22045.zpd
                    url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/nrttrop/sinex_trop_GLOBAL_EPOS8/w' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_zpd_list = GFZ_zpd_list + [list]

        # generate Satellite Attitude url
        if self.gfz_obx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("gfz-potsdam") != -1:
                    if time[4] >= 2083:
                        file_name = 'GBM0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_30S_ATT.OBX.gz'
                    else:
                        file_name = 'gbm' + str(time[4]) + str(time[5]) + '.obx.Z'
                    #  ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/2200/GBM0MGXRAP_20220650000_01D_30S_ATT.OBX.gz
                    url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/' + str(time[4]) + '/' + file_name
                else:
                    if time[4] >= 1962:
                        file_name = 'GFZ0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_30S_ATT.OBX.gz'
                    else:
                        file_name = 'gbm' + str(time[4]) + str(time[5]) + '.obx.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GBM0MGXRAP_20220650000_01D_30S_ATT.OBX.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                GFZ_obx_list = GFZ_obx_list + [list]

        # generate OSB url
        if self.gfz_osb_bis_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("gfz-potsdam") != -1:
                    if time[4] >= 2083:
                        file_name = 'GBM0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_OSB.BIA.gz'
                    else:
                        file_name = 'gbm' + str(time[4]) + str(time[5]) + '.bia.Z'
                    #  ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/2200/GBM0MGXRAP_20220650000_01D_01D_OSB.BIA.gz
                    url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/' + str(time[4]) + '/' + file_name
                else:
                    if time[4] >= 1962:
                        file_name = 'GFZ0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_OSB.BIA.gz'
                    else:
                        file_name = 'gbm' + str(time[4]) + str(time[5]) + '.bia.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GBM0MGXRAP_20220650000_01D_01D_OSB.BIA.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                GFZ_osb_list = GFZ_osb_list + [list]

        # generate REL url
        if self.gfz_rel_bis_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("gfz-potsdam") != -1:
                    file_name = 'GBM0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_REL.BIA.gz'
                    #  ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/2200/GBM0MGXRAP_20220650000_01D_01D_REL.BIA.gz
                    url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/' + str(time[4]) + '/' + file_name
                else:
                    file_name = 'GFZ0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_REL.BIA.gz'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GBM0MGXRAP_20220650000_01D_01D_REL.BIA.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                GFZ_rel_list = GFZ_rel_list + [list]

        # generate Earth rotation parameters url
        if self.gfz_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.gfz_erp_box.currentText() == 'Ultra':
                    for i in ['00', '06', '12', '18']:
                        if time[4] < 2238:
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2160/gfz21600.sp3.Z
                            file_name = 'gfu' + str(time[4]) + str(time[5]) + '_' + i + '.erp.gz'
                        else:
                            #  GFZ0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                            file_name = 'GFZ0OPSULT_'  + str(time[0]) + str(time[3]) + i + '00_02D_01D_ERP.ERP.gz'

                        # file_name = 'gfu' + str(time[4]) + str(time[5]) + '_' + i + '.erp.gz'
                        #  ftp://ftp.gfz-potsdam.de/GNSS/products/Ul-Rapid/w2160/gfu21600_00.erp.gz

                        if select_url.find("gfz-potsdam") != -1:
                            url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/ultra/w' + str(time[4]) + '/' + file_name
                        else:
                            url = select_url + str(time[4]) + '/' + file_name
                        list = [url, file_name]
                        GFZ_erp_list_temp = GFZ_erp_list_temp + [list]

                elif self.gfz_erp_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        # ftp://igs.gnsswhu.cn/pub/gps/products/2160/gfz21600.sp3.Z
                        file_name = 'gfz' + str(time[4]) + str(time[5]) + '.erp.gz'
                    else:
                        #  GFZ0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                        file_name = 'GFZ0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                    # file_name = 'gfz' + str(time[4]) + str(time[5]) + '.erp.gz'
                    #  ftp://ftp.gfz-potsdam.de/GNSS/products/rapid/w2160/gfz21600.erp.gz
                    # url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/rapid/w' + str(time[4]) + '/' + file_name
                    if select_url.find("gfz-potsdam") != -1:
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/ultra/w' + str(time[4]) + '/' + file_name
                    else:
                        url = select_url + str(time[4]) + '/' + file_name

                    list = [url, file_name]
                    GFZ_erp_list_temp = GFZ_erp_list_temp + [list]
                elif self.gfz_erp_box.currentText() == 'Final':
                    if select_url.find("gfz-potsdam") != -1:
                        if time[4] < 2237:
                            file_name = 'gfz' + str(time[4]) + '7.erp.Z'
                            #  ftp://ftp.gfz-potsdam.de/GNSS/products/final/w2160/gfz21607.erp.Z
                        else:
                            file_name = 'GFZ0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_07D_01D_ERP.ERP.gz'
                            #  GFZ0OPSFIN_20223250000_07D_01D_ERP.ERP.gz
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/final/w' + str(time[4]) + '/' + file_name
                    else:
                        if time[4] < 2238:
                            file_name = 'gfz' + str(time[4]) + '7.erp.Z'
                            # ftp://igs.gnsswhu.cn/pub/gps/products/2160/gfz21600.erp.gz
                        else:
                            file_name = 'GFZ0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_07D_01D_ERP.ERP.gz'
                            #  GFZ0OPSFIN_20223310000_07D_01D_ERP.ERP.gz
                        url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_erp_list_temp = GFZ_erp_list_temp + [list]

                elif self.gfz_erp_box.currentText() == 'MGEX':
                    if select_url.find("gfz-potsdam") != -1:
                        if time[4] >= 2083:
                            file_name = 'GBM0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                        else:
                            file_name = 'gbm' + str(time[4]) + str(time[5]) + '.erp.Z'
                        #  ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/2200/GBM0MGXRAP_20220650000_01D_01D_ERP.ERP.gz
                        url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/mgex/' + str(time[4]) + '/' + file_name
                    else:
                        if time[4] >= 1962:
                            file_name = 'GFZ0MGXRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                        else:
                            file_name = 'gbm' + str(time[4]) + str(time[5]) + '.erp.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GBM0MGXRAP_20220650000_01D_01D_ERP.ERP.gz
                        if select_url.find("esa") != -1:
                            url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                        else:
                            url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GFZ_erp_list_temp = GFZ_erp_list_temp + [list]
                for i in GFZ_erp_list_temp:
                    if i not in GFZ_erp_list:
                        GFZ_erp_list.append(i)

        # generate Daily station positions url
        if self.gfz_snx_check.isChecked():
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2237:
                    file_name = 'gfz' + str(time[4]) + str(time[5]) + '.snx.Z'
                    #  ftp://ftp.gfz-potsdam.de/GNSS/products/final/w2200/gfz22001.snx.Z
                else:
                    file_name = 'GFZ0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                    #  GFZ0OPSFIN_20223240000_01D_01D_SOL.SNX.gz
                url = 'ftp://ftp.gfz-potsdam.de/GNSS/products/final/w' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                GFZ_snx_list = GFZ_snx_list + [list]

        # ESA
        # generate Precise Ephemeris positions url
        if self.esa_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'esa' + str(time[4]) + str(time[5]) + '.sp3.Z'
                    #  ftp://gssc.esa.int/gnss/products/2226/esa21600.sp3.Z
                else:
                    file_name = 'ESA0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                    #  ESA0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                ESA_sp3_list = ESA_sp3_list + [list]

        # generate Precise Clock positions url
        if self.esa_Precisi_clock_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'esa' + str(time[4]) + str(time[5]) + '.clk.Z'
                    #  ftp://gssc.esa.int/gnss/products/2160/esa21601.clk.Z
                else:
                    file_name = 'ESA0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                    #  ESA0OPSFIN_20230850000_01D_30S_CLK.CLK.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                ESA_clock_list = ESA_clock_list + [list]

        # generate Earth rotation parameters positions url
        if self.esa_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'esa' + str(time[4]) + '7.erp.Z'
                    #  ftp://gssc.esa.int/gnss/products/2160/esa21607.erp.Z
                else:
                    file_name = 'ESA0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_07D_01D_ERP.ERP.gz'
                    #  ESA0OPSFIN_20230850000_07D_01D_ERP.ERP.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                ESA_erp_list_temp = ESA_erp_list_temp + [list]
            for i in ESA_erp_list_temp:
                if i not in ESA_erp_list:
                    ESA_erp_list.append(i)

        # generate Daily station positions url
        if self.esa_snx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'esa' + str(time[4]) + str(time[5]) + '.snx.Z'
                    #  ftp://gssc.esa.int/gnss/products/2160/esa21601.snx.Z
                else:
                    file_name = 'ESA0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                    #  ESA0OPSFIN_20230850000_01D_01D_SOL.SNX.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                ESA_snx_list = ESA_snx_list + [list]

        # generate Ionosphere url
        if self.esa_i_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.esa_i_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        ##  ftp://gssc.esa.int/gnss/products/ionex/2021/001/esrg0010.21i.Z
                        file_name = 'esrg'+str(time[3])+'0.'+str(time[1])+'i.Z'
                    else:
                        file_name = 'ESA0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01H_GIM.INX.gz'
                        #  ESA0OPSRAP_20230930000_01D_01H_GIM.INX.gz
                    url = select_url + 'ionex/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]
                elif self.esa_i_box.currentText() == 'Final':
                    if time[4] < 2238:
                        ##  ftp://gssc.esa.int/gnss/products/ionex/2021/001/esag0010.21i.Z
                        file_name = 'esag' + str(time[3]) + '0.' + str(time[1]) + 'i.Z'
                    else:
                        file_name = 'ESA0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_02H_GIM.INX.gz'
                        #  ESA0OPSFIN_20230930000_01D_02H_GIM.INX.gz
                    url = select_url + 'ionex/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]

        # JPL
        # generate Precise Ephemeris url
        if self.jpl_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] <= 2253:
                    file_name = 'jpl' + str(time[4]) + str(time[5]) + '.sp3.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/jpl21600.sp3.Z
                else:
                    file_name = 'JPL0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                    #  JPL0OPSFIN_20230780000_01D_05M_ORB.SP3.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                JPL_sp3_list = JPL_sp3_list + [list]

        # generate  Precise Clock url
        if self.jpl_Precisi_clock_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] <= 2253:
                    file_name = 'jpl' + str(time[4]) + str(time[5]) + '.clk.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/jpl21600.clk.Z
                else:
                    file_name = 'JPL0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                    #  JPL0OPSFIN_20230780000_01D_30S_CLK.CLK.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                JPL_clock_list = JPL_clock_list + [list]

        # generate Daily station positions url
        if self.jpl_snx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] <= 2253:
                    file_name = 'jpl' + str(time[4]) + str(time[5]) + '.snx.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/jpl21604.snx.Z
                else:
                    file_name = 'JPL0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                    #  JPL0OPSFIN_20230780000_01D_01D_SOL.SNX.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                JPL_snx_list = JPL_snx_list + [list]

        # generate Earth rotation parameters url
        if self.jpl_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] <= 2253:
                    file_name = 'jpl' + str(time[4]) + '7.erp.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/jpl21607.erp.Z
                else:
                    file_name = 'JPL0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01W_01D_ERP.ERP.gz'
                    #  JPL0OPSFIN_20230780000_01W_01D_ERP.ERP.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                JPL_erp_list_temp = JPL_erp_list_temp + [list]
            for i in JPL_erp_list_temp:
                if i not in JPL_erp_list:
                    JPL_erp_list.append(i)

        # generate Precise Ephemeris url
        if self.jpl_tro_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] <= 2253:
                    file_name = 'jpl' + str(time[4]) + str(time[5]) + '.tro.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/jpl21604.tro.Z
                else:
                    file_name = 'JPL0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_TRO.TRO.gz'
                    #  JPL0OPSFIN_20230780000_01D_30S_TRO.TRO.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                JPL_tro_list = JPL_tro_list + [list]

        # generate Satellite Yaw url
        if self.jpl_yaw_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] <= 2253:
                    file_name = 'jpl' + str(time[4]) + str(time[5]) + '.yaw.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/jpl21604.yaw.Z
                else:
                    file_name = 'JPL0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_YAW.YAW.gz'
                    #  JPL0OPSFIN_20230780000_01D_30S_TRO.TRO.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                JPL_yaw_list = JPL_yaw_list + [list]

        # generate Ionosphere url
        if self.jpl_i_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.jpl_i_box.currentText() == 'Rapid':
                    ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/001/jprg0010.21i.Z
                    file_name = 'jprg'+str(time[3])+'0.'+str(time[1])+'i.Z'
                    url = select_url + 'ionex/' + str(time[0])+'/'+str(time[3])+'/'+file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]
                elif self.jpl_i_box.currentText() == 'Final':
                    ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/001/jplg0010.21i.Z
                    file_name = 'jplg' + str(time[3]) + '0.' + str(time[1]) + 'i.Z'
                    url = select_url + 'ionex/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]

        # MIT
        # generate Ionosphere url
        if self.mit_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'mit' + str(time[4]) + str(time[5]) + '.sp3.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/esa21600.sp3.Z
                else:
                    file_name = 'MIT0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                    #  MIT0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                MIT_sp3_list = MIT_sp3_list + [list]

        # generate Precise Clock url
        if self.mit_Precisi_clock_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'mit' + str(time[4]) + str(time[5]) + '.clk.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/esa21601.clk.Z
                else:
                    file_name = 'MIT0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_CLK.CLK.gz'
                    #  MIT0OPSFIN_20223320000_01D_05M_CLK.CLK.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                MIT_clock_list = MIT_clock_list + [list]

        # generate Earth rotation parameters url
        if self.mit_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'mit' + str(time[4]) + '7.erp.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/esa21607.erp.Z
                else:
                    file_name = 'MIT0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_07D_01D_ERP.ERP.gz'
                    #  MIT0OPSFIN_20223310000_07D_01D_ERP.ERP.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                MIT_erp_list_temp = MIT_erp_list_temp + [list]
            for i in MIT_erp_list_temp:
                if i not in MIT_erp_list:
                    MIT_erp_list.append(i)

        # generate Daily station positions url
        if self.mit_snx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'mit' + str(time[4]) + str(time[5]) + '.snx.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/esa21601.snx.Z
                else:
                    file_name = 'MIT0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                    #  MIT0OPSFIN_20223320000_01D_01D_SOL.SNX.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                MIT_snx_list = MIT_snx_list + [list]

        # GRG
        # generate Daily station positions url
        # self.grg_Precisi_track_box.addItems(['G/R', 'MGEX'])
        if self.grg_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.grg_Precisi_track_box.currentText() == 'G/R':
                    if time[4] < 2238:
                        file_name = 'grg' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/grg21600.sp3.Z
                    else:
                        file_name = 'GRG0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                        #  GRG0OPSFIN_20223310000_01D_05M_ORB.SP3.gz
                    url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GRG_sp3_list = GRG_sp3_list + [list]
                elif self.grg_Precisi_track_box.currentText() == 'MGEX':
                    file_name = 'GRG0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_05M_ORB.SP3.gz'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GRG0MGXFIN_20220650000_01D_05M_ORB.SP3.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GRG_sp3_list = GRG_sp3_list + [list]

        # generate Daily station positions url
        #  self.grg_Precisi_clock_box.addItems(['G/R', 'MGEX'])
        if self.grg_Precisi_clock_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.grg_Precisi_clock_box.currentText() == 'G/R':
                    if time[4] < 2238:
                        file_name = 'grg' + str(time[4]) + str(time[5]) + '.clk.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/grg21601.clk.Z
                    else:
                        file_name = 'GRG0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                        #  GRG0OPSFIN_20223310000_01D_30S_CLK.CLK.gz
                    url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GRG_clock_list = GRG_clock_list + [list]
                elif self.grg_Precisi_clock_box.currentText() == 'MGEX':
                    file_name = 'GRG0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_CLK.CLK.gz'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GRG0MGXFIN_20220650000_01D_30S_CLK.CLK.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    GRG_clock_list = GRG_clock_list + [list]

        # generate Daily station positions url
        if self.grg_osb_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                file_name = 'GRG0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_OSB.BIA.gz'
                #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GRG0MGXFIN_20220660000_01D_01D_OSB.BIA.gz
                if select_url.find("esa") != -1:
                    url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                else:
                    url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                GRG_osb_list = GRG_osb_list + [list]

        # generate Daily station positions url
        if self.grg_obx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                file_name = 'GRG0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_30S_ATT.OBX.gz'
                #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2200/GRG0MGXFIN_20220650000_01D_30S_ATT.OBX.gz
                if select_url.find("esa") != -1:
                    url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                else:
                    url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                GRG_obx_list = GRG_obx_list + [list]

        # generate Daily station positions url
        if self.grg_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'grg' + str(time[4]) + '7.erp.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/grg21607.erp.Z
                else:
                    file_name = 'GRG0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                    #  GRG0OPSFIN_20223310000_01D_01D_ERP.ERP.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                GRG_erp_list_temp = GRG_erp_list_temp + [list]
            for i in GRG_erp_list_temp:
                if i not in GRG_erp_list:
                    GRG_erp_list.append(i)

        # generate Daily station positions url
        if self.grg_snx_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.grg_snx_box.currentText() == 'G/R':
                    if time[4] < 2238:
                        file_name = 'grg' + str(time[4]) + str(time[5]) + '.snx.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/grg21601.snx.Z
                    else:
                        file_name = 'GRG0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_000_SOL.SNX.gz'
                        #  GRG0OPSFIN_20223310000_01D_000_SOL.SNX.gz
                    url = select_url + str(time[4]) + '/' + file_name

                elif self.grg_snx_box.currentText() == 'MGEX':
                    file_name = 'GRG0MGXFIN_' + str(time[0]) + str(time[3]) + '0000_01D_000_SOL.SNX.gz'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/mgex/2233/GRG0MGXFIN_20222960000_01D_000_SOL.SNX.gz
                    if select_url.find("esa") != -1:
                        url = select_url + str(time[4]) + '/' + 'mgex/' + file_name
                    else:
                        url = select_url + 'mgex/' + str(time[4]) + '/' + file_name
                list = [url, file_name]
                GRG_snx_list = GRG_snx_list + [list]

        # EMR
        # generate Precise Ephemeris url
        if self.emr_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("rtopsdata1") != -1:
                    file_name = 'emr' + str(time[4]) + str(time[5]) + '.sp3.Z'
                    #  ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/final/2218/emr22180.sp3.Z
                    url = 'ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/final/' + str(time[4]) + '/' + file_name
                else:
                    if time[4] < 2238:
                        file_name = 'emr' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2237/emr22370.sp3.Z
                    else:
                        file_name = 'EMR0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_15M_ORB.SP3.gz'
                        #  EMR0OPSRAP_20223310000_01D_15M_ORB.SP3.gz
                    url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                EMR_sp3_list = EMR_sp3_list + [list]

        # generate Precise Clock url
        if self.emr_Precisi_clock_check.isChecked():
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("rtopsdata1") != -1:
                    file_name = 'emr' + str(time[4]) + str(time[5]) + '.clk.Z'
                    #  ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/final/2218/emr22181.clk.Z
                    url = 'ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/final/' + str(time[4]) + '/' + file_name
                else:
                    if time[4] < 2238:
                        file_name = 'emr' + str(time[4]) + str(time[5]) + '.clk.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2237/emr22370.clk.Z
                    else:
                        file_name = 'EMR0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_05M_CLK.CLK.gz'
                        #  EMR0OPSRAP_20223310000_01D_05M_CLK.CLK.gz
                    url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                EMR_clock_list = EMR_clock_list + [list]

        # generate Earth rotation parameters url
        if self.emr_erp_check.isChecked():
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("rtopsdata1") != -1:
                    file_name = 'emr' + str(time[4]) + '7.erp.Z'
                    #  ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/final/2160/emr21607.erp.Z
                    url = 'ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/final/' + str(time[4]) + '/' + file_name
                else:
                    if time[4] < 2238:
                        file_name = 'emr' + str(time[4]) + '7.erp.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2237/emr22370.erp.Z
                    else:
                        file_name = 'EMR0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_ERP.ERP.gz'
                        #  EMR0OPSRAP_20223320000_01D_01D_ERP.ERP.gz
                    url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                EMR_erp_list_temp = EMR_erp_list_temp + [list]
            for i in EMR_erp_list_temp:
                if i not in EMR_erp_list:
                    EMR_erp_list.append(i)

        # generate Daily station positions url
        if self.emr_snx_check.isChecked():
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("rtopsdata1") != -1:
                    file_name = 'emr' + str(time[4]) + str(time[5]) + '.snx.Z'
                    #  ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/final/2160/emr21601.snx.Z
                    url = 'ftp://rtopsdata1.geod.nrcan.gc.ca/gps/products/final/' + str(time[4]) + '/' + file_name
                else:
                    if time[4] < 2238:
                        file_name = 'emr' + str(time[4]) + str(time[5]) + '.snx.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2237/emr22370.snx.Z
                    else:
                        file_name = 'EMR0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                        #  EMR0OPSRAP_20223320000_01D_01D_SOL.SNX.gz
                    url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                EMR_snx_list = EMR_snx_list + [list]

        # SIO
        # generate Precise Ephemeris url
        if self.sio_Precisi_track_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.sio_Precisi_track_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        file_name = 'sir' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        #  http://garner.ucsd.edu/pub/products/2160/sir21601.sp3.Z
                    else:
                        file_name = 'SIO0OPSRAP_' + str(time[0]) + str(time[3]) + '0000_01D_15M_ORB.SP3.gz'
                        #  SIO0OPSRAP_20223310000_01D_15M_ORB.SP3.gz
                    url = 'http://garner.ucsd.edu/pub/products/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    SIO_sp3_list = SIO_sp3_list + [list]
                elif self.sio_Precisi_track_box.currentText() == 'Final':
                    if time[4] < 2238:
                        file_name = 'sio' + str(time[4]) + str(time[5]) + '.sp3.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/sio21600.sp3.Z
                    else:
                        file_name = 'SIO0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_15M_ORB.SP3.gz'
                        #  SIO0OPSFIN_20223320000_01D_15M_ORB.SP3.gz
                    url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    SIO_sp3_list = SIO_sp3_list + [list]

        # generate Earth rotation parameters url
        if self.sio_erp_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.sio_erp_box.currentText() == 'Rapid':
                    if time[4] < 2238:
                        file_name = 'sir' + str(time[4]) + str(time[5]) + '.erp.Z'
                        #  http://garner.ucsd.edu/pub/products/2160/sir21602.erp.Z
                    else:
                        file_name = 'SIO0OPSRAP_' + str(time[0]) + str(time[3]) + '1200_01D_01D_ERP.ERP.gz'
                        #  SIO0OPSRAP_20223311200_01D_01D_ERP.ERP.gz
                    url = 'http://garner.ucsd.edu/pub/products/' + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    SIO_erp_list_temp = SIO_erp_list_temp + [list]
                elif self.sio_erp_box.currentText() == 'Final':
                    if time[4] < 2238:
                        file_name = 'sio' + str(time[4]) + '7.erp.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/sio21607.erp.Z
                    else:
                        file_name = 'SIO0OPSFIN_' + str(time[0]) + str(time[3]) + '1200_07D_01D_ERP.ERP.gz'
                        #  SIO0OPSFIN_20223311200_07D_01D_ERP.ERP.gz
                    url = select_url + str(time[4]) + '/' + file_name
                    list = [url, file_name]
                    SIO_erp_list_temp = SIO_erp_list_temp + [list]
                for i in SIO_erp_list_temp:
                    if i not in SIO_erp_list:
                        SIO_erp_list.append(i)

        # generate Daily station positions url
        if self.sio_snx_check.isChecked():
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if select_url.find("garner.ucsd") != -1:
                    file_name = 'sioigs' + str(time[4]) + str(time[5]) + '.snx.Z'
                    #  http://garner.ucsd.edu/pub/products/2160/sioigs21600.snx.Z
                    url = 'http://garner.ucsd.edu/pub/products/' + str(time[4]) + '/' + file_name
                else:
                    if time[4] < 2238:
                        file_name = 'sio' + str(time[4]) + str(time[5]) + '.snx.Z'
                        #  ftp://igs.gnsswhu.cn/pub/gps/products/2232/sio22320.snx.Z
                    else:
                        file_name = 'SIO0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                        #  SIO0OPSFIN_20223320000_01D_01D_SOL.SNX.gz
                    url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                SIO_snx_list = SIO_snx_list + [list]

        # NGS
        # generate Precise Ephemeris url
        if self.ngs_Precisi_track_check.isChecked():
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'ngs' + str(time[4]) + str(time[5]) + '.sp3.Z'
                    #  https://geodesy.noaa.gov/corsdata/rinex/2022/001/igs21600.sp3.gz
                else:
                    file_name = 'IGS0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_15M_ORB.SP3.gz'
                    #  IGS0OPSFIN_20223310000_01D_15M_ORB.SP3.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                NGS_sp3_list = NGS_sp3_list + [list]

        # generate Daily station positions url
        if self.ngs_snx_check.isChecked():
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'ngs' + str(time[4]) + str(time[5]) + '.snx.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/ngs21600.snx.Z
                else:
                    file_name = 'NGS0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_01D_01D_SOL.SNX.gz'
                    #  NGS0OPSFIN_20223320000_01D_01D_SOL.SNX.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                NGS_snx_list = NGS_snx_list + [list]

        # generate Earth rotation parameters url
        if self.ngs_erp_check.isChecked():
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if time[4] < 2238:
                    file_name = 'ngs' + str(time[4]) + '7.erp.Z'
                    #  ftp://igs.gnsswhu.cn/pub/gps/products/2160/ngs21607.erp.Z
                else:
                    file_name = 'NGS0OPSFIN_' + str(time[0]) + str(time[3]) + '0000_07D_01D_ERP.ERP.gz'
                    #  NGS0OPSFIN_20223310000_07D_01D_ERP.ERP.gz
                url = select_url + str(time[4]) + '/' + file_name
                list = [url, file_name]
                NGS_erp_list_temp = NGS_erp_list_temp + [list]
            for i in NGS_erp_list_temp:
                if i not in NGS_erp_list:
                    NGS_erp_list.append(i)

        # UPC
        # generate Ionosphere url
        if self.upc_i_check.isChecked():
            # determine the download source
            if self.choose_product_url_box.isEnabled():
                select_url = self.select_url
            else:
                select_url = ''
            for time in all_YearAccuDay_GpsWeek:
                if self.upc_i_box.currentText() == 'Rapid':
                    ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/001/uprg0010.21i.Z
                    file_name = 'uprg'+str(time[3])+'0.'+str(time[1])+'i.Z'
                    url = select_url + 'ionex/'+str(time[0])+'/'+str(time[3])+'/'+file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]
                elif self.upc_i_box.currentText() == 'Final':
                    ##  ftp://igs.gnsswhu.cn/pub/gps/products/ionex/2021/001/upcg0010.21i.Z
                    file_name = 'upcg' + str(time[3]) + '0.' + str(time[1]) + 'i.Z'
                    url = select_url + 'ionex/' + str(time[0]) + '/' + str(time[3]) + '/' + file_name
                    list = [url, file_name]
                    CODE_i_list = CODE_i_list + [list]

        # Generate list
        combination_url_list = [IGS_igu_list, IGS_clk_list, IGS_track_analyze, IGS_clock_analyze, IGS_erp_list, CODE_eph_list, CODE_clk_list, CODE_obx_list, CODE_ion_list, CODE_i_list, CODE_tro_list, CODE_dcb_list, CODE_bia_list, CODE_erp_list, CODE_snx_list, CAS_dcb_list, CAS_bia_list, CAS_bsx_list, CAS_ion_list, CAS_i_list, WHU_sp3_list, WHU_clock_list, WHU_bia_list, WHU_i_list, WHU_erp_list, GFZ_sp3_list, GFZ_clock_list, GFZ_tro_list, GFZ_zpd_list, GFZ_obx_list, GFZ_osb_list, GFZ_rel_list, GFZ_erp_list, GFZ_snx_list, ESA_sp3_list, ESA_clock_list, ESA_erp_list, ESA_snx_list, JPL_sp3_list, JPL_clock_list, JPL_snx_list, JPL_erp_list, JPL_tro_list, JPL_yaw_list, MIT_sp3_list, MIT_clock_list, MIT_erp_list, MIT_snx_list, GRG_sp3_list, GRG_clock_list, GRG_erp_list, GRG_snx_list, GRG_osb_list, GRG_obx_list, EMR_sp3_list, EMR_clock_list, EMR_erp_list, EMR_snx_list, SIO_sp3_list, SIO_erp_list, SIO_snx_list, NGS_sp3_list, NGS_erp_list, NGS_snx_list]
        target_url_list = []
        for i in combination_url_list:
            if i != []:
                target_url_list = target_url_list + i
        # print(target_url_list)
        if target_url_list == []:
            if self.igs_atx_check.isChecked():
                self.show_download_information.setText('Total Tasks:1  Succeeded:1  Failed:0 （Time Consumed:0）     Download completed!')
                self.download_Progress_bar.setValue(100)
                QApplication.processEvents()
                self.show_download_process_state.setText('')
                return
            self.show_download_process_state.setText('')
            QMessageBox.information(self, 'Tips', 'No file type selected !')
            return
        print(target_url_list)

        # Set download thread
        global session
        global ftp_max_thread
        if self.choose_product_url_box.currentText() == 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/':
            self.download_Progress_bar.setRange(0, len(target_url_list))
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
        else:
            # session initialization and Set maximum threads

            requests_ftp.monkeypatch_session()
            session = requests.Session()
            if self.choose_product_url_box.currentText() == 'ftp://gssc.esa.int/gnss/products/':
                ftp_max_thread = threading.Semaphore(2)
            elif self.choose_product_url_box.currentText() == 'ftp://igs.gnsswhu.cn/pub/gps/products/':
                ftp_max_thread = threading.Semaphore(10)
            elif self.choose_product_url_box.currentText() == 'gdc.cddis.eosdis.nasa.gov/pub/gps/products/':
                ftp_max_thread = threading.Semaphore(10)
            elif self.choose_product_url_box.currentText() == 'ftp://igs.ign.fr/pub/igs/products/':
                ftp_max_thread = threading.Semaphore(10)
            elif self.choose_product_url_box.currentText() == 'ftp://nfs.kasi.re.kr/gps/products/':
                ftp_max_thread = threading.Semaphore(10)
            elif self.choose_product_url_box.currentText() == 'http://garner.ucsd.edu/pub/products/':
                ftp_max_thread = threading.Semaphore(10)
            else:
                ftp_max_thread = threading.Semaphore(10)
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
        print('Download ended')

    # Help document
    def open_download_help_file_but_line(self):
        self.s = open_download_help_file_windows01()
        self.s.show()

    def download_details_report_view(self):
        self.s = download_details_report_main01(successful_library,failed_library)
        self.s.show()

# -------------------------------------------------------------------------------------------------
""" main gui """
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
        self.setCentralWidget(self.browser)

# -------------------------------------------------------------------------------------------------
""" refactor Checkbox """
class ComboCheckBox_rewrite(QComboBox):
    def loadItems(self, items):
        self.items = items
        if self.items[0] != 'All':
            self.items.insert(0, 'All')
        self.row_num = len(self.items)
        self.Selectedrow_num = 0
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setStyleSheet('''QWidget{background-color:rgb(220, 220, 220);}''')
        self.qLineEdit.setReadOnly(True)
        self.qListWidget = QListWidget()
        self.addQCheckBox(0)
        self.qCheckBox[0].stateChanged.connect(self.All)
        for i in range(0, self.row_num):
            self.addQCheckBox(i)
            self.qCheckBox[i].stateChanged.connect(self.showMessage)
        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)
        self.setLineEdit(self.qLineEdit)

    def showPopup(self):
        select_list = self.Selectlist()
        self.loadItems(items=self.items[1:])
        for select in select_list:
            index = self.items[:].index(select)
            self.qCheckBox[index].setChecked(True)
        return QComboBox.showPopup(self)

    def printResults(self):
        list = self.Selectlist()

    def addQCheckBox(self, i):
        self.qCheckBox.append(QCheckBox())
        qItem = QListWidgetItem(self.qListWidget)
        self.qCheckBox[i].setText(self.items[i])
        self.qListWidget.setItemWidget(qItem, self.qCheckBox[i])

    def Selectlist(self):
        Outputlist = []
        for i in range(1, self.row_num):
            if self.qCheckBox[i].isChecked() == True:
                Outputlist.append(self.qCheckBox[i].text())
        self.Selectedrow_num = len(Outputlist)
        return Outputlist

    def showMessage(self):
        Outputlist = self.Selectlist()
        self.qLineEdit.setReadOnly(False)
        self.qLineEdit.clear()
        show = ';'.join(Outputlist)
        if self.Selectedrow_num == 0:
            self.qCheckBox[0].setCheckState(0)
        elif self.Selectedrow_num == self.row_num - 1:
            self.qCheckBox[0].setCheckState(2)
        else:
            self.qCheckBox[0].setCheckState(1)
        self.qLineEdit.setText(show)
        self.qLineEdit.setReadOnly(True)

    def All(self, zhuangtai):
        if zhuangtai == 2:
            for i in range(1, self.row_num):
                self.qCheckBox[i].setChecked(True)
        elif zhuangtai == 1:
            if self.Selectedrow_num == 0:
                self.qCheckBox[0].setCheckState(2)
        elif zhuangtai == 0:
            self.clear()

    def clear(self):
        for i in range(self.row_num):
            self.qCheckBox[i].setChecked(False)

    def currentText(self):
        text = QComboBox.currentText(self).split(';')
        if text.__len__() == 1:
            if not text[0]:
                return []
        return text

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
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
    win = Analysis_Center_Products()
    win.show()
    sys.exit(app.exec_())