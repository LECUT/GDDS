from Global_IGS_Data import *
from Post_Processing_Product import *
from Regional_CORS_Data import *
from Time_Series_Product import *
from Custom_Download import *
from Data_Decompression import *
from PyQt5.QtWidgets import QGridLayout
from OpenGL import GL
JD = 3.21
MJD = 1.23

'''
-----------------------------------------------------------------------------------------------------------------------
Function: Download IGS/CORS data and products
Introduce: 1. 'main.py' is the main interface of the software.
2. 'main.py' first creates the 'app1' channel, based on which the software can interact with Baidu Maps.
3. Then there is the QT Design of the software, and the functional modules are bound to the controls.
Author: Liang Qiao
Time: April 15, 2021
-----------------------------------------------------------------------------------------------------------------------
'''

#  GNSS Data Pre-processing Software，GDPS
global curdir
curdir = os.getcwd()
app1 = Flask(__name__, template_folder=str(curdir) + r'/templates')

@app1.route('/IGS')
def IGS():
    return render_template('WorldwideIGS.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_all')
def IGS_all():
    return render_template('WorldwideIGS-ALL.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_all_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_rinex2')
def IGS_rinex2():
    return render_template('WorldwideIGS-Rinex2.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_rinex2_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_rinex3')
def IGS_rinex3():
    return render_template('WorldwideIGS-Rinex3.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_rinex3_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_rinex23')
def IGS_rinex23():
    return render_template('WorldwideIGS-Rinex23.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_rinex23_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_met_rinex2')
def IGS_met_rinex2():
    return render_template('WorldwideIGS-Met_Rinex2.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_met_rinex2_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_met_rinex3')
def IGS_met_rinex3():
    return render_template('WorldwideIGS-Met_Rinex3.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_met_rinex3_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_met_rinex23')
def IGS_met_rinex23():
    return render_template('WorldwideIGS-Met_Rinex23.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_met_rinex23_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_obs_met_rinex2')
def IGS_obs_met_rinex2():
    return render_template('WorldwideIGS-Obs-Met_Rinex2.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_obs_met_rinex2_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_obs_met_rinex3')
def IGS_obs_met_rinex3():
    return render_template('WorldwideIGS-Obs-Met_Rinex3.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_obs_met_rinex3_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_obs_met_rinex23')
def IGS_obs_met_rinex23():
    return render_template('WorldwideIGS-Obs-Met_Rinex23.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_obs_met_rinex23_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_higt_rate_rinex2')
def IGS_high_rate_rinex2():
    return render_template('WorldwideIGS-HighRate_Rinex2.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_high_rate_rinex2_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_higt_rate_rinex3')
def IGS_high_rate_rinex3():
    return render_template('WorldwideIGS-HighRate_Rinex3.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_high_rate_rinex3_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/IGS_higt_rate_rinex23')
def IGS_high_rate_rinex23():
    return render_template('WorldwideIGS-HighRate_Rinex23.html')
@app1.route('/IGSajax', methods=["get", "post"])
def IGS_high_rate_rinex23_1():
    Map_IGS_name = request.get_json()
    global_var.set_value('IGS_station_list', Map_IGS_name)
    return Map_IGS_name

@app1.route('/HongKong')
def HongKong():
    return render_template('HongKongCORS.html')
@app1.route('/HongKongajax', methods=["get", "post"])
def HongKong_1():
    Map_HongKongCORS_name = request.get_json()
    global_var.set_value('HongKong_station_list', Map_HongKongCORS_name)
    return Map_HongKongCORS_name

@app1.route('/Curtin')
def Curtin():
    return render_template('CurtinCORS.html')
@app1.route('/Curtinajax', methods=["get", "post"])
def Curtin_1():
    Map_CurtinCORS_name = request.get_json()
    global_var.set_value('Curtin_station_list', Map_CurtinCORS_name)
    return Map_CurtinCORS_name

@app1.route('/Enrope')
def Enrope():
    return render_template('EnropeCORS.html')
@app1.route('/Enropeajax', methods=["get", "post"])
def Enrope_1():
    Map_EnropeCORS_name = request.get_json()
    global_var.set_value('ENP_station_list', Map_EnropeCORS_name)
    return Map_EnropeCORS_name

@app1.route('/Japan')
def Japan():
    return render_template('JapanCORS.html')
@app1.route('/Japanajax', methods=["get", "post"])
def Japan_1():
    Map_JapanCORS_name = request.get_json()
    global_var.set_value('JPN_station_list', Map_JapanCORS_name)
    return Map_JapanCORS_name

@app1.route('/Spain')
def Spain():
    return render_template('SpainCORS.html')
@app1.route('/Spainajax', methods=["get", "post"])
def Spain_1():
    Map_SpainCORS_name = request.get_json()
    global_var.set_value('Spain_station_list', Map_SpainCORS_name)
    return Map_SpainCORS_name

@app1.route('/USA')
def USA():
    return render_template('USACORS.html')
@app1.route('/USAajax', methods=["get", "post"])
def USA_1():
    Map_USACORS_name = request.get_json()
    global_var.set_value('USA_station_list', Map_USACORS_name)
    return Map_USACORS_name

@app1.route('/Apref')
def Apref():
    return render_template('AprefCORS.html')
@app1.route('/Aprefajax', methods=["get", "post"])
def Apref_1():
    Map_AprefCORS_name = request.get_json()
    global_var.set_value('Apref_station_list', Map_AprefCORS_name)
    return Map_AprefCORS_name

@app1.route('/Nevada')
def Nevada():
    return render_template('NevadaCORS.html')
@app1.route('/Nevadaajax', methods=["get", "post"])
def Nevada_1():
    Map_NevadaGNSS_name = request.get_json()
    global_var.set_value('Nevada_station_list', Map_NevadaGNSS_name)
    return Map_NevadaGNSS_name

@app1.route('/Ced')
def Ced():
    return render_template('CedCORS.html')
@app1.route('/Cedajax', methods=["get", "post"])
def Ced_1():
    Map_CedGNSS_name = request.get_json()
    global_var.set_value('Ced_station_list', Map_CedGNSS_name)
    return Map_CedGNSS_name

@app1.route('/Unavco')
def Unavco():
    return render_template('UnavcoCORS.html')
@app1.route('/Unavcoajax', methods=["get", "post"])
def Unavco_1():
    Map_UnavcoGNSS_name = request.get_json()
    global_var.set_value('Unavco_station_list', Map_UnavcoGNSS_name)
    return Map_UnavcoGNSS_name


# -------------------------------------------------------------------------------------------------
""" main gui """
class GNSS_data_downloader_all(QWidget):
    def __init__(self):
        super().__init__()
        global_var._init()
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height())/2))
        self.setWindowTitle("GDDS V1.2")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        Code_Envir = os.getcwd()
        global_var.set_value('code_environment', Code_Envir)
        self.setup_ui()

    def setup_ui(self):
        self.head_name_lable = QLabel('GNSS  Data  Download  Software ', self)
        self.head_name_lable.setFont(QFont('Times New Roman', 15))
        self.head_name_lable.setAlignment(Qt.AlignCenter)
        # self.head_name_lable.move(64, 30)

        self.all_IGS_data_btn = QPushButton('Global IGS Data', self)
        self.all_IGS_data_btn.setFont(QFont("Times New Roman", 13))
        self.all_IGS_data_btn.setMinimumWidth(60)
        # self.all_IGS_data_btn.setGeometry(50, 90, 340, 40)
        self.all_IGS_data_btn.clicked.connect(self.IGS_data_Download_link)

        self.all_product_btn = QPushButton('Post-Processing Product', self)
        self.all_product_btn.setFont(QFont("Times New Roman", 13))
        self.all_product_btn.setMinimumWidth(60)
        # self.all_product_btn.setGeometry(50, 150, 340, 40)
        self.all_product_btn.clicked.connect(self.Product_dealed_link)

        self.all_area_data_btn = QPushButton('Regional CORS Data', self)
        self.all_area_data_btn.setFont(QFont("Times New Roman", 13))
        self.all_area_data_btn.setMinimumWidth(60)
        # self.all_area_data_btn.setGeometry(50, 210, 340, 40)
        self.all_area_data_btn.clicked.connect(self.Area_data_Download_link)


        self.all_time_data_btn = QPushButton('Time Serise Product', self)
        self.all_time_data_btn.setFont(QFont("Times New Roman", 13))
        self.all_time_data_btn.setMinimumWidth(60)
        # self.all_area_data_btn.setGeometry(50, 210, 340, 40)
        self.all_time_data_btn.clicked.connect(self.Time_data_Download_link)

        self.custom_download_btn = QPushButton('Custom Download', self)
        self.custom_download_btn.setFont(QFont("Times New Roman", 13))
        self.custom_download_btn.setMinimumWidth(60)
        # self.custom_download_btn.setGeometry(50, 210, 340, 40)
        self.custom_download_btn.clicked.connect(self.Custom_Download_link)

        self.all_unzip_btn = QPushButton('Data Decompression ', self)
        self.all_unzip_btn.setFont(QFont("Times New Roman", 13))
        self.all_unzip_btn.setMinimumWidth(60)
        # self.all_unzip_btn.setGeometry(50, 270, 165, 40)
        self.all_unzip_btn.clicked.connect(self.all_unzip_link)

        self.all_about_btn = QLabel("<A href='www.baidu.com'>About</a>")
        self.all_about_btn.setFont(QFont("Times New Roman", 10))
        self.all_about_btn.setAlignment(Qt.AlignRight)
        self.all_about_btn.linkActivated.connect(self.all_about_link)

        gride = QGridLayout(self)
        gride.setContentsMargins(40, 30, 40, 5)
        gride.setSpacing(20)
        gride.addWidget(self.head_name_lable, 0, 0, 3, 5)
        gride.addWidget(self.all_IGS_data_btn, 3, 0, 3, 5)
        gride.addWidget(self.all_product_btn, 6, 0, 3, 5)
        gride.addWidget(self.all_area_data_btn, 9, 0, 3, 5)
        gride.addWidget(self.all_time_data_btn, 12, 0, 3, 5)
        gride.addWidget(self.custom_download_btn, 15, 0, 3, 5)
        gride.addWidget(self.all_unzip_btn, 18, 0, 3, 5)
        gride.addWidget(self.all_about_btn, 22, 4, 1, 1)


    def IGS_data_Download_link(self):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.s = IGS_data_Download()
        self.s.show()

    def Product_dealed_link(self):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.s = Analysis_Center_Products()
        self.s.show()

    def Area_data_Download_link(self):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.s = CORS_data_Download()
        self.s.show()

    def Time_data_Download_link(self):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.s = Time_Serise_Download()
        self.s.show()

    def Custom_Download_link(self):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.s = Custom_Download()
        self.s.show()

    def all_unzip_link(self):
        file_decompression(self)
        Code_Operat_Envir = global_var.get_value('code_environment')
        os.chdir(Code_Operat_Envir)

    def all_about_link(self):
        self.s = Software_About_View()
        self.s.show()

    def closeEvent(self, event):
        sys.exit(0)
# -------------------------------------------------------------------------------------------------
""" about gui """
class Software_About_View(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("About GDDS")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height())/2))
        self.setup_ui()

    def setup_ui(self):
        self.title_label = QLabel('GNSS Data Download Software (GDDS)', self)
        self.title_label.setFont(QFont('Times New Roman', 15))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.version_label = QLabel('Version : 1.2', self)
        self.version_label.setFont(QFont('Times New Roman', 13))
        self.version_label.setAlignment(Qt.AlignCenter)

        self.developer_label = QLabel('Developer : L-Team', self)
        self.developer_label.setFont(QFont('Times New Roman', 13))
        # self.developer_label.setAlignment(Qt.AlignCenter)

        self.agenccy_label = QLabel('Institution  : East China University of Technology (ECUT)', self)
        self.agenccy_label.setFont(QFont('Times New Roman', 13))
        # self.agenccy_label.setAlignment(Qt.AlignCenter)

        self.emeil_label = QLabel('Contact us :  lglu66@163.com', self)
        self.emeil_label.setFont(QFont('Times New Roman', 13))
        # self.emeil_label.setAlignment(Qt.AlignCenter)

        self.copyright_label = QLabel('Copyright © 2023 ECUT. All rights reserved.', self)
        self.copyright_label.setFont(QFont('Times New Roman', 13))
        # self.copyright_label.setAlignment(Qt.AlignCenter)

        gride = QGridLayout(self)
        gride.setContentsMargins(40, 20, 40, 30)
        gride.setSpacing(25)
        gride.addWidget(self.title_label, 0, 0, 2, 1)
        gride.addWidget(self.version_label, 1, 0, 2, 1)
        gride.addWidget(self.developer_label, 3, 0, 1, 1)
        gride.addWidget(self.agenccy_label, 4, 0, 1, 1)
        gride.addWidget(self.emeil_label, 5, 0, 1, 1)
        gride.addWidget(self.copyright_label, 6, 0, 1, 1)

# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    screen = QDesktopWidget().screenGeometry()
    win_width = screen.width()
    win_height = screen.height()
    font = QFont()
    pointsize = font.pointSize()
    if win_width <= 1920:
        font.setPointSize(10)
    # else:
    #     font.setPointSize(pointsize - 3)
    font.setFamily("Times New Roman")
    app.setFont(font)
    kwargs = {'host': '127.0.0.1', 'port': '5000', 'threaded': True, 'use_reloader': False, 'debug': False}
    threading.Thread(target=app1.run, daemon=True, kwargs=kwargs).start()
    win = GNSS_data_downloader_all()
    win.show()
    sys.exit(app.exec_())