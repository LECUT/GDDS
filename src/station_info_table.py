import sys
import re
from PyQt5.Qt import QHeaderView
from PyQt5.QtCore import pyqtSignal, Qt, QRect
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLineEdit, QPushButton, QMessageBox, QCheckBox, QAction, QHBoxLayout, QStyleOptionButton, QStyle, QTableWidget, QAbstractItemView, QTableWidgetItem, QGridLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QIcon, QBrush, QColor, QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
import shutil
import json
import xlwt
import global_var
from XYZ_BLH_BD09 import *
import os
global curdir
curdir = os.getcwd()

'''
-----------------------------------------------------------------------------------------------------------------------
Function: View station information table
Principle: 1. Create a QTableWidget and set its parameters;
2. Open the json file with the station information externally, read the data and load it into QTableWidget;
3. Add operations such as modifying, adding and deleting, searching, exporting and saving the station information in QTableWidget.
-----------------------------------------------------------------------------------------------------------------------
'''

def python_json_html(file, add_list):
    with open(file, 'r') as f:
        str_text = f.read()
        start_list_local = str_text.find('[')
        head_text = str_text[:start_list_local]
        list_content = eval(str_text[7:])
        list_content.extend(add_list)
        str_content = str(list_content).replace("'", "\"").replace(r"\n", "")
        new_str = head_text + str_content
        f.close()
    with open(file, 'w') as f:
        f.write(new_str)
        f.close()


# global variable
header_field_IGS = ['All', 'Station', 'Nation', 'Area', 'Institution', 'Start Time', 'End Time', 'Longitude/(°)',
                    'Latitude/(°)', 'Receiver Type', 'Antenna Type']
header_field_HongKong = ['All', 'Station', 'Area', 'Location', 'Longitude/(°)', 'Latitude/(°)', 'Receiver Type',
                         'Antenna Type']

all_header_combobox = []

class CheckBoxHeader(QHeaderView):
    """ Custom header class """
    select_all_clicked = pyqtSignal(bool)
    # 4 variables that control the column header check box
    _x_offset = 0
    _y_offset = 0
    _width = 20
    _height = 20

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.isOn = False

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()

        self._y_offset = int((rect.height() - self._width) / 2.)

        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(rect.x() + self._x_offset, rect.y() + self._y_offset, self._width, self._height)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isOn:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if 0 == index:
            x = self.sectionPosition(index)
            if x + self._x_offset < event.pos().x() < x + self._x_offset + self._width and self._y_offset < event.pos().y() < self._y_offset + self._height:
                if self.isOn:
                    self.isOn = False
                else:
                    self.isOn = True
                self.select_all_clicked.emit(self.isOn)

                self.updateSection(0)
        super(CheckBoxHeader, self).mousePressEvent(event)

    # Custom signal select_all_clicked
    def change_state(self, isOn):
        if isOn:
            for i in all_header_combobox:
                i.setCheckState(Qt.Checked)
        else:
            for i in all_header_combobox:
                i.setCheckState(Qt.Unchecked)

# -------------------------------------------------------------------------------------------------
# main gui
class IGS_Station_Info_Table(QWidget):
    def __init__(self):
        super().__init__()
        all_header_combobox.clear()
        self.setWindowTitle("IGS Station-Info")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))
        # self.move(190 / 1920 * win_width, 100 / 1080 * win_height)
        # self.setFixedSize(1590 / 1920 * win_width, 798 / 1080 * win_height)
        self.resize(1000*win_height/1080, 600*win_height/1080)
        self.setup_ui()

    my_Signal_IGS = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.my_Signal_IGS.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()
        # layout0.setSpacing(40)

        self.searchLab = QLineEdit(self)
        self.searchLab.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.searchLab.setPlaceholderText('e.g. ABMF:ASHTECH UZ-12')
        # self.searchLab.setGeometry(0, 0, 1355 / 1920 * win_width, 35 / 1080 * win_height)
        self.searchLab.setMinimumWidth(100)
        self.searchLab.setMinimumHeight(20)
        # self.searchLab.setMaximumHeight(40)
        # self.searchLab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout0.addWidget( self.searchLab)


        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(str(curdir) + r'/slib/logo/magnifier.jpg'))
        self.searchLab.addAction(station_search_icon, QLineEdit.LeadingPosition)
        station_search_icon.triggered.connect(self.showMessage)

        self.confirm_btn = QPushButton(self)
        # self.confirm_btn.setGeometry(1360 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.confirm_btn)
        self.confirm_btn.setMinimumWidth(10)
        self.confirm_btn.setMinimumHeight(15)
        # self.confirm_btn.setMaximumWidth(15)
        # self.confirm_btn.resize(20, 25)
        self.confirm_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.confirm_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/sure.png')}")
        self.confirm_btn.clicked.connect(self.addInformationStations)

        self.add_btn = QPushButton(self)
        # self.add_btn.setGeometry(1401 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.add_btn)
        self.add_btn.setMinimumWidth(10)
        self.add_btn.setMinimumHeight(15)
        self.add_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.add_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/plus.png')}")
        self.add_btn.clicked.connect(self.add_info_links)

        self.minus_btn = QPushButton(self)
        # self.minus_btn.setGeometry(1438 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.minus_btn)
        self.minus_btn.setMinimumWidth(10)
        self.minus_btn.setMinimumHeight(15)
        self.minus_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/minus.png')}")
        self.minus_btn.clicked.connect(self.minus_info_links)

        self.export_btn = QPushButton(self)
        # self.export_btn.setGeometry(1475 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.export_btn)
        self.export_btn.setMinimumWidth(10)
        self.export_btn.setMinimumHeight(15)
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.export_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/export.png')}")
        self.export_btn.clicked.connect(self.saveCheckedInformation)

        self.save_btn = QPushButton(self)
        # self.save_btn.setGeometry(1512 / 1920 * win_width, 0, 35 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.save_btn)
        self.save_btn.setMinimumWidth(10)
        self.save_btn.setMinimumHeight(15)
        self.save_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.save_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/save.png')}")
        self.save_btn.clicked.connect(self.Update_ionfo)

        self.recovery_btn = QPushButton(self)
        # self.recovery_btn.setGeometry(1550 / 1920 * win_width, 1 / 1080 * win_height, 29 / 1920 * win_width, 29 / 1080 * win_height)
        layout0.addWidget(self.recovery_btn)
        self.recovery_btn.setMinimumWidth(10)
        self.recovery_btn.setMinimumHeight(15)
        self.recovery_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.recovery_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/recovery.png')}")
        self.recovery_btn.clicked.connect(self.load_origain_file)

        json_text = json.load(open(str(curdir) + r'/slib/json/IGS_Info.json', encoding='utf-8'))
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(11)
        self.main_table.setRowCount(len(json_text))
        # self.main_table.setGeometry(0, 35 / 1080 * win_height, 1590 / 1920 * win_width, 760 / 1080 * win_height)
        # gride.addWidget(layout, 0, 5, 2, 1)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set checkbox header
        header = CheckBoxHeader()
        self.main_table.setHorizontalHeader(header)
        self.main_table.setHorizontalHeaderLabels(header_field_IGS)
        # Set column width
        # self.main_table.setColumnWidth(0, 60 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 70 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 150 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 150 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 90 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 170 / 1920 * win_width)
        # self.main_table.setColumnWidth(6, 170 / 1920 * win_width)
        # self.main_table.setColumnWidth(7, 120 / 1920 * win_width)
        # self.main_table.setColumnWidth(8, 120 / 1920 * win_width)
        # self.main_table.setColumnWidth(9, 210 / 1920 * win_width)
        # self.main_table.setColumnWidth(10, 210 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header.select_all_clicked.connect(header.change_state)

        self.main_table.setHorizontalHeaderLabels(
            ['All', 'Station', 'Nation', 'Area', 'Institution', 'Start Time', 'End Time', 'Longitude/(°)',
             'Latitude/(°)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(json_text)), json_text):
            # Set checkbox function
            checkbox_son = QCheckBox()
            all_header_combobox.append(checkbox_son)
            # add checkbox
            self.main_table.setCellWidget(i, 0, checkbox_son)
            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j + 1, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout0)
        vlayout.addLayout(layout)
        self.setLayout(vlayout)


    def add_info_links(self):
        self.s = Add_Other_Info_Windows01()
        self.s.Add_Info_Close_Signal.connect(self.add_info_windows_close)
        global station_xyz_list
        station_xyz_list = []
        self.s.show()

    def add_info_windows_close(self):
        try:
            # print('load', station_xyz_list)
            for one_list in station_xyz_list:
                self.main_table.insertRow(0)
                # 0 Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.insert(0, checkbox_son)
                self.main_table.setCellWidget(0, 0, checkbox_son)
                # 1
                newItem = QTableWidgetItem(one_list[0])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 1, newItem)
                # 2
                newItem = QTableWidgetItem(one_list[1])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 2, newItem)
                # 3
                newItem = QTableWidgetItem(one_list[2])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 3, newItem)
                # 4
                newItem = QTableWidgetItem(one_list[3])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 4, newItem)
                # 5
                newItem = QTableWidgetItem(one_list[4])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 5, newItem)
                # 6
                newItem = QTableWidgetItem(one_list[5])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 6, newItem)
                # 7
                text_2 = str(format(one_list[7][1], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_2)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 7, newItem)
                # 8
                text_3 = str(format(one_list[7][0], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_3)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 8, newItem)
                # 9
                newItem = QTableWidgetItem(one_list[9])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 9, newItem)
                # 10
                newItem = QTableWidgetItem(one_list[10])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 10, newItem)
        except:
            pass
        print('Close the add interface')

    def minus_info_links(self):
        choosed_row = self.main_table.selectionModel().currentIndex().row()
        self.main_table.removeRow(choosed_row)

    def load_origain_file(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial station-info? ', QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            shutil.copy(str(curdir) + r'/slib/json/origin/IGS_Info.json', str(curdir) + r'/slib/json/IGS_Info.json')
            shutil.copy(str(curdir) + r'/slib/json/origin/IGS_Statios.json', str(curdir) + r'/slib/json/IGS_Statios.json')
            shutil.copy(str(curdir) + r'/slib/json/origin/IGS_Statios_BaiDu_Coordinate.json', str(curdir) + r'/slib/json/IGS_Statios_BaiDu_Coordinate.json')
            origain_json_text = json.load(open(str(curdir) + r'/slib/json/IGS_Info.json', 'r'))
            self.main_table.setRowCount(len(origain_json_text))
            for i, line_text in zip(range(len(origain_json_text)), origain_json_text):
                # Set checkbox function
                checkbox_son = QCheckBox()
                all_header_combobox.append(checkbox_son)
                self.main_table.setCellWidget(i, 0, checkbox_son)
                for j in range(len(line_text)):
                    newItem = QTableWidgetItem(line_text[j])
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(i, j + 1, newItem)

    # Override keyboard events
    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.showMessage()
            # self.bt1.click()

    #  Add Stations
    def addInformationStations(self):
        checked_stations = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_station = self.main_table.item(checked_c, 1).text()
                checked_stations.append(checked_station)
        global_var.set_value('Info_table_checked_IGS_stations', checked_stations)
        print(checked_stations)
        self.close()

    #  Save Info
    def saveCheckedInformation(self):
        checked_c_list = []
        checked_text = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_c_list.append(checked_c)
        for i in checked_c_list:
            checked_row_text = []
            for j in range(self.main_table.columnCount()):
                if j != 0:
                    single_text = self.main_table.item(i, j).text()
                    checked_row_text.append(single_text)
            checked_text = checked_text + [checked_row_text]
        print(checked_text)

        # Save as
        saveInformationPath, ok2 = QFileDialog.getSaveFileName(self, 'File save', "/", "Text Files(*.xls)")
        if saveInformationPath:
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet("Station-Info")
            sheet1.write(0, 0, 'Station')
            sheet1.write(0, 1, 'Nation')
            sheet1.write(0, 2, 'Area')
            sheet1.write(0, 3, 'Institution')
            sheet1.write(0, 4, 'Start Time')
            sheet1.write(0, 5, 'End Time')
            sheet1.write(0, 6, 'Longitude/(°)')
            sheet1.write(0, 7, 'Latitude/(°)')
            sheet1.write(0, 8, 'Receiver Type')
            sheet1.write(0, 9, 'Antenna Type')
            for i in range(len(checked_text)):
                for j in range(len(checked_text[0])):
                    sheet1.write(i + 1, j, checked_text[i][j])
            workbook.save(saveInformationPath)
            pass

    def Update_ionfo(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Update station-info? ', QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            all_table_list = []
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount() - 1):
                    temp_list.append(self.main_table.item(r, c + 1).text())
                all_table_list.append(temp_list)
            with open(str(curdir) + r'/slib/json/IGS_Info.json', 'w', encoding='utf-8') as f:
                json.dump(all_table_list, f, ensure_ascii=False)
                print('Update!')

            json_text = json.load(open(str(curdir) + r'/slib/json/IGS_Statios.json', 'r'))
            try:
                add_station_list = []
                for one_add_info_list in station_xyz_list:
                    if one_add_info_list[0] != '':
                        json_text[0].insert(0, one_add_info_list[0])
                        json_text[1].insert(0, one_add_info_list[0])
                        json_text[2].insert(0, one_add_info_list[0])
                        json_text[3].insert(0, one_add_info_list[0])
                        json_text[4].insert(0, one_add_info_list[0])
                        json_text[5].insert(0, one_add_info_list[0])
                        json_text[6].insert(0, one_add_info_list[0])
                        json_text[7].insert(0, one_add_info_list[0])
                        json_text[8].insert(0, one_add_info_list[0])
                        json_text[9].insert(0, one_add_info_list[0])
                        json_text[10].insert(0, one_add_info_list[0])
                        json_text[11].insert(0, one_add_info_list[0])
                        json_text[12].insert(0, one_add_info_list[0])
                with open(str(curdir) + r'/slib/json/IGS_Statios.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
                add_coord_list = []
                for one_add_coord_list in station_xyz_list:
                    if one_add_coord_list[0] != '' and one_add_coord_list[8] != []:
                        add_coord_list.append([one_add_coord_list[0], one_add_coord_list[8][0], one_add_coord_list[8][1]])
                python_json_html(str(curdir) + r'/static/WorldwideIGS-ALL_01.json', add_coord_list)
                python_json_html(str(curdir) + r'/static/WorldwideIGS_01.json', add_coord_list)
                python_json_html(str(curdir) + r'/static/WorldwideIGS-Rinex2_01.json', add_coord_list)
                python_json_html(str(curdir) + r'/static/WorldwideIGS-Rinex3_01.json', add_coord_list)
                json_text = json.load(open(str(curdir) + r'/slib/json/IGS_Statios_BaiDu_Coordinate.json', 'r'))
                json_text[0].insert(0, [one_add_coord_list[0], one_add_coord_list[8][0], one_add_coord_list[8][1]])
                with open(str(curdir) + r'/slib/json/IGS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
            except:
                pass


    def showMessage(self):
        for r in range(self.main_table.rowCount()):
            for c in range(self.main_table.columnCount()):
                if c != 0:
                    self.main_table.item(r, c).setBackground(QBrush(QColor(255, 255, 255)))

        wen_Text = self.searchLab.text()
        wen_list = wen_Text.split(':')
        print(wen_list)
        for wen in reversed(wen_list):
            if len(wen) <= 4:
                wen = wen.upper()
            items = self.main_table.findItems(wen, Qt.MatchExactly)

            if items:
                temp_text_list = []
                temp_color_list = []
                for i in items:
                    i = i.row()
                    lie_text_list = []
                    lie_color_list = []
                    for j in range(10):
                        select_text = self.main_table.item(i, j + 1).text()
                        select_color = self.main_table.item(i, j + 1).background()
                        lie_text_list.append(select_text)
                        lie_color_list.append(select_color)
                    self.main_table.removeRow(i)
                    all_header_combobox.remove(all_header_combobox[i])
                    temp_text_list = temp_text_list + [lie_text_list]
                    temp_color_list = temp_color_list + [lie_color_list]

                # Insert the information of the search target in the first line
                # print(temp_text_list)
                for i, m in zip(reversed(temp_text_list), reversed(temp_color_list)):
                    self.main_table.insertRow(0)
                    # Set checkbox function
                    checkbox_son = QCheckBox()
                    all_header_combobox.insert(0, checkbox_son)
                    self.main_table.setCellWidget(0, 0, checkbox_son)
                    for j in range(10):
                        newItem = QTableWidgetItem(i[j])
                        newItem.setBackground(m[j])
                        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.main_table.setItem(0, j + 1, newItem)

                items = self.main_table.findItems(wen, Qt.MatchExactly)

                # Secondary search, highlight
                # Scroll to the selected table and highlight it
                print(items[0].row())
                if len(items) > 0:
                    for item in items:
                        item.setBackground(QBrush(QColor(0, 255, 0)))
                self.main_table.verticalScrollBar().setSliderPosition(0)
            # else:
            #     QMessageBox.information(self, 'Hint', 'What you are looking for is not in the table !')

# -------------------------------------------------------------------------------------------------
# 2
class HongKong_Station_Info_Table(QWidget):
    def __init__(self):
        super().__init__()
        all_header_combobox.clear()
        self.setWindowTitle("HongKongStation-Info")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        # self.move(400 / 1920 * win_width, 120 / 1080 * win_height)
        # self.setFixedSize(1192 / 1920 * win_width, 685 / 1080 * win_height)
        self.resize(1192*win_height/1080, 685*win_height/1080)
        self.setup_ui()

    my_Signal_AreaCors = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.my_Signal_AreaCors.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.searchLab = QLineEdit(self)
        self.searchLab.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.searchLab.setPlaceholderText('e.g. HKSL:Leica GR50')
        # self.searchLab.setGeometry(0, 0, 952 / 1920 * win_width, 35 / 1080 * win_height)
        self.searchLab.setMinimumWidth(60)
        self.searchLab.setMinimumHeight(20)
        layout0.addWidget( self.searchLab)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(str(curdir) + r'/slib/logo/magnifier.jpg'))
        self.searchLab.addAction(station_search_icon, QLineEdit.LeadingPosition)
        station_search_icon.triggered.connect(self.showMessage)

        self.confirm_btn = QPushButton(self)
        # self.confirm_btn.setGeometry(957 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.confirm_btn)
        self.confirm_btn.setMinimumWidth(10)
        self.confirm_btn.setMinimumHeight(15)
        self.confirm_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.confirm_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/sure.png')}")
        self.confirm_btn.clicked.connect(self.addInformationStations)

        self.add_btn = QPushButton(self)
        # self.add_btn.setGeometry(998 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.add_btn)
        self.add_btn.setMinimumWidth(10)
        self.add_btn.setMinimumHeight(15)
        self.add_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.add_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/plus.png')}")
        self.add_btn.clicked.connect(self.add_info_links)

        self.minus_btn = QPushButton(self)
        # self.minus_btn.setGeometry(1035 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/minus.png')}")
        self.minus_btn.clicked.connect(self.minus_info_links)
        layout0.addWidget(self.minus_btn)
        self.minus_btn.setMinimumWidth(10)
        self.minus_btn.setMinimumHeight(15)
        self.minus_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.export_btn = QPushButton(self)
        # self.export_btn.setGeometry(1072 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.export_btn)
        self.export_btn.setMinimumWidth(10)
        self.export_btn.setMinimumHeight(15)
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.export_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/export.png')}")
        self.export_btn.clicked.connect(self.saveCheckedInformation)

        self.save_btn = QPushButton(self)
        # self.save_btn.setGeometry(1109 / 1920 * win_width, 0, 35 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.save_btn)
        self.save_btn.setMinimumWidth(10)
        self.save_btn.setMinimumHeight(15)
        self.save_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.save_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/save.png')}")
        self.save_btn.clicked.connect(self.Update_ionfo)

        self.recovery_btn = QPushButton(self)
        # self.recovery_btn.setGeometry(1147 / 1920 * win_width, 1 / 1080 * win_height, 29 / 1920 * win_width, 29 / 1080 * win_height)
        layout0.addWidget(self.recovery_btn)
        self.recovery_btn.setMinimumWidth(10)
        self.recovery_btn.setMinimumHeight(15)
        self.recovery_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.recovery_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/recovery.png')}")
        self.recovery_btn.clicked.connect(self.load_origain_file)

        vlayout.addLayout(layout0)

        json_text = json.load(open(str(curdir) + r'/slib/json/HongKong_Info.json', 'r'))
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(7)
        self.main_table.setRowCount(len(json_text))
        # self.main_table.setGeometry(0, 35 / 1080 * win_height, 1190 / 1920 * win_width, 650 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set checkbox header
        header = CheckBoxHeader()
        self.main_table.setHorizontalHeader(header)
        self.main_table.setHorizontalHeaderLabels(header_field_HongKong)
        # Set column width
        # self.main_table.setColumnWidth(0, 60 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 120 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 150 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 150 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 150 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 250 / 1920 * win_width)
        # self.main_table.setColumnWidth(6, 259 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header.select_all_clicked.connect(header.change_state)

        self.main_table.setHorizontalHeaderLabels(
            ['All', 'Station', 'Location', 'Longitude/(°)', 'Latitude/(°)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(json_text)), json_text):
            # Set checkbox function
            checkbox_son = QCheckBox()
            all_header_combobox.append(checkbox_son)
            # add checkbox
            self.main_table.setCellWidget(i, 0, checkbox_son)
            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j + 1, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout0)
        vlayout.addLayout(layout)
        self.setLayout(vlayout)

    def add_info_links(self):
        self.s = Add_Other_Info_Windows03()
        self.s.Add_Info_Close_Signal.connect(self.add_info_windows_close)
        global station_xyz_list
        station_xyz_list = []
        self.s.show()

    def add_info_windows_close(self):
        try:
            # print('load', station_xyz_list)
            for one_list in station_xyz_list:
                self.main_table.insertRow(0)
                # 0 Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.insert(0, checkbox_son)
                self.main_table.setCellWidget(0, 0, checkbox_son)
                # 1
                newItem = QTableWidgetItem(one_list[0])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 1, newItem)
                # 2
                newItem = QTableWidgetItem(one_list[1])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 2, newItem)
                # 3
                text_2 = str(format(one_list[3][1], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_2)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 3, newItem)
                ##  4
                text_3 = str(format(one_list[3][0], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_3)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 4, newItem)
                # 5
                newItem = QTableWidgetItem(one_list[5])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 5, newItem)
                # 6
                newItem = QTableWidgetItem(one_list[6])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 6, newItem)
        except:
            pass
        print('Close the add interface')

    def minus_info_links(self):
        choosed_row = self.main_table.selectionModel().currentIndex().row()
        self.main_table.removeRow(choosed_row)

    def load_origain_file(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        shutil.copy(str(curdir) + r'/slib/json/origin/HongKong_Info.json', str(curdir) + r'/slib/json/HongKong_Info.json')
        if whether_update == QMessageBox.Yes:
            origain_json_text = json.load(open(str(curdir) + r'/slib/json/HongKong_Info.json', 'r'))
            self.main_table.setRowCount(len(origain_json_text))
            for i, line_text in zip(range(len(origain_json_text)), origain_json_text):
                # Set checkbox function
                checkbox_son = QCheckBox()
                all_header_combobox.append(checkbox_son)
                self.main_table.setCellWidget(i, 0, checkbox_son)
                for j in range(len(line_text)):
                    newItem = QTableWidgetItem(line_text[j])
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(i, j + 1, newItem)
            now_json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            origin_json_text = json.load(open(str(curdir) + r'/slib/json/origin/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            now_json_text[4] = origin_json_text[4]
            with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                json.dump(now_json_text, f, ensure_ascii=False)

    # Override keyboard events
    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.showMessage()
            # self.bt1.click()

    #  Add Stations
    def addInformationStations(self):
        checked_stations = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_station = self.main_table.item(checked_c, 1).text()
                checked_stations.append(checked_station)
        global_var.set_value('Info_table_checked_AreaCORS_stations', checked_stations)
        print(checked_stations)
        self.close()

    #  Save Info
    def saveCheckedInformation(self):
        checked_c_list = []
        checked_text = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_c_list.append(checked_c)
        for i in checked_c_list:
            checked_row_text = []
            for j in range(self.main_table.columnCount()):
                if j != 0:
                    single_text = self.main_table.item(i, j).text()
                    checked_row_text.append(single_text)
        print(checked_text)

        # Save as
        saveInformationPath, ok2 = QFileDialog.getSaveFileName(self, 'File save', "/", "Text Files(*.xls)")
        if saveInformationPath:
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet("Station-Info")
            sheet1.write(0, 0, 'Station')
            sheet1.write(0, 1, 'Area')
            sheet1.write(0, 2, 'Location')
            sheet1.write(0, 3, 'Longitude/(°)')
            sheet1.write(0, 4, 'Latitude/(°)')
            sheet1.write(0, 5, 'Receiver Type')
            sheet1.write(0, 6, 'Antenna Type')
            for i in range(len(checked_text)):
                for j in range(len(checked_text[0])):
                    sheet1.write(i + 1, j, checked_text[i][j])
            workbook.save(saveInformationPath)
            pass

    def Update_ionfo(self):
        whether_update = QMessageBox.question(self, 'Tips',
                                              'Update station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            all_table_list = []
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount() - 1):
                    temp_list.append(self.main_table.item(r, c + 1).text())
                all_table_list.append(temp_list)
            with open(str(curdir) + r'/slib/json/HongKong_Info.json', 'w', encoding='utf-8') as f:
                json.dump(all_table_list, f, ensure_ascii=False)
            try:
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios.json', 'r'))
                for one_add_info_list in station_xyz_list:
                    if one_add_info_list[0] != '':
                        json_text[1].insert(0, one_add_info_list[0])
                        json_text[2].insert(0, one_add_info_list[0])
                with open(str(curdir) + r'/slib/json/CORS_Statios.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
                add_coord_list = []
                for one_add_coord_list in station_xyz_list:
                    if one_add_coord_list[0] != '' and one_add_coord_list[4] != []:
                        add_coord_list.append(
                            [one_add_coord_list[0], one_add_coord_list[4][0], one_add_coord_list[4][1]])
                python_json_html(str(curdir) + r'/static/HongKongCORS.json', add_coord_list)
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
                json_text[4].insert(0, [one_add_coord_list[0], one_add_coord_list[4][0], one_add_coord_list[4][1]])
                with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
            except:
                pass
            print('Update!')

    def showMessage(self):
        for r in range(self.main_table.rowCount()):
            for c in range(self.main_table.columnCount()):
                if c != 0:
                    self.main_table.item(r, c).setBackground(QBrush(QColor(255, 255, 255)))

        wen_Text = self.searchLab.text()
        wen_list = wen_Text.split(':')
        print(wen_list)
        for wen in reversed(wen_list):
            if len(wen) == 4:
                wen = wen.upper()
            items = self.main_table.findItems(wen, Qt.MatchExactly)

            if items:
                temp_text_list = []
                temp_color_list = []
                for i in items:
                    i = i.row()
                    lie_text_list = []
                    lie_color_list = []
                    for j in range(6):
                        select_text = self.main_table.item(i, j + 1).text()
                        select_color = self.main_table.item(i, j + 1).background()
                        lie_text_list.append(select_text)
                        lie_color_list.append(select_color)
                    self.main_table.removeRow(i)
                    all_header_combobox.remove(all_header_combobox[i])
                    temp_text_list = temp_text_list + [lie_text_list]
                    temp_color_list = temp_color_list + [lie_color_list]

                # Insert the information of the search target in the first line
                # print(temp_text_list)
                for i, m in zip(reversed(temp_text_list), reversed(temp_color_list)):
                    self.main_table.insertRow(0)
                    # Set checkbox function
                    checkbox_son = QCheckBox()
                    all_header_combobox.insert(0, checkbox_son)
                    self.main_table.setCellWidget(0, 0, checkbox_son)
                    for j in range(6):
                        newItem = QTableWidgetItem(i[j])
                        newItem.setBackground(m[j])
                        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.main_table.setItem(0, j + 1, newItem)

                items = self.main_table.findItems(wen, Qt.MatchExactly)

                # Secondary search, highlight
                # Scroll to the selected table and highlight it
                print(items[0].row())
                if len(items) > 0:
                    for item in items:
                        item.setBackground(QBrush(QColor(0, 255, 0)))
                self.main_table.verticalScrollBar().setSliderPosition(0)
            # else:
            #     QMessageBox.information(self, 'Hint', 'What you are looking for is not in the table !')

# -------------------------------------------------------------------------------------------------
# 3
class Curtin_Station_Info_Table(QWidget):
    def __init__(self):
        super().__init__()
        all_header_combobox.clear()
        self.setWindowTitle("Curtin University Station-Info")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))
        # self.move(430 / 1920 * win_width, 190 / 1080 * win_height)
        # self.setFixedSize(1000 / 1920 * win_width, 620 / 1080 * win_height)
        self.resize(1000*win_height/1080, 620*win_height/1080)
        self.setup_ui()

    my_Signal_AreaCors = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.my_Signal_AreaCors.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.searchLab = QLineEdit(self)
        self.searchLab.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.searchLab.setPlaceholderText('e.g. CUBB:TRM 59800.00 SCIS')
        # self.searchLab.setGeometry(0, 0, 760 / 1920 * win_width, 35 / 1080 * win_height)
        self.searchLab.setMinimumWidth(60)
        self.searchLab.setMinimumHeight(30)
        layout0.addWidget( self.searchLab)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(str(curdir) + r'/slib/logo/magnifier.jpg'))
        self.searchLab.addAction(station_search_icon, QLineEdit.LeadingPosition)
        station_search_icon.triggered.connect(self.showMessage)

        self.confirm_btn = QPushButton(self)
        # self.confirm_btn.setGeometry(765 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.confirm_btn)
        self.confirm_btn.setMinimumWidth(10)
        self.confirm_btn.setMinimumHeight(15)
        self.confirm_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.confirm_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/sure.png')}")
        self.confirm_btn.clicked.connect(self.addInformationStations)

        self.add_btn = QPushButton(self)
        # self.add_btn.setGeometry(806 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.add_btn)
        self.add_btn.setMinimumWidth(10)
        self.add_btn.setMinimumHeight(15)
        self.add_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.add_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/plus.png')}")
        self.add_btn.clicked.connect(self.add_info_links)

        self.minus_btn = QPushButton(self)
        # self.minus_btn.setGeometry(843 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.minus_btn)
        self.minus_btn.setMinimumWidth(10)
        self.minus_btn.setMinimumHeight(15)
        self.minus_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/minus.png')}")
        self.minus_btn.clicked.connect(self.minus_info_links)

        self.export_btn = QPushButton(self)
        # self.export_btn.setGeometry(880 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.export_btn)
        self.export_btn.setMinimumWidth(10)
        self.export_btn.setMinimumHeight(15)
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.export_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/export.png')}")
        self.export_btn.clicked.connect(self.saveCheckedInformation)

        self.save_btn = QPushButton(self)
        # self.save_btn.setGeometry(917 / 1920 * win_width, 0, 35 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.save_btn)
        self.save_btn.setMinimumWidth(10)
        self.save_btn.setMinimumHeight(15)
        self.save_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.save_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/save.png')}")
        self.save_btn.clicked.connect(self.Update_ionfo)

        self.recovery_btn = QPushButton(self)
        # self.recovery_btn.setGeometry(955 / 1920 * win_width, 1 / 1080 * win_height, 29 / 1920 * win_width, 29 / 1080 * win_height)
        layout0.addWidget(self.recovery_btn)
        self.recovery_btn.setMinimumWidth(10)
        self.recovery_btn.setMinimumHeight(15)
        self.recovery_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.recovery_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/recovery.png')}")
        self.recovery_btn.clicked.connect(self.load_origain_file)

        json_text = json.load(open(str(curdir) + r'/slib/json/Curtin_Info.json', 'r'))
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(6)
        self.main_table.setRowCount(len(json_text))
        # self.main_table.setGeometry(0, 35 / 1080 * win_height, 1290 / 1920 * win_width, 760 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set checkbox header
        header = CheckBoxHeader()
        self.main_table.setHorizontalHeader(header)
        self.main_table.setHorizontalHeaderLabels(header_field_HongKong)
        # Set column width
        # self.main_table.setColumnWidth(0, 60 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 110 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 140 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 140 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 260 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 260 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header.select_all_clicked.connect(header.change_state)

        self.main_table.setHorizontalHeaderLabels(
            ['All', 'Station', 'Longitude/(°)', 'Latitude/(°)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(json_text)), json_text):
            # Set checkbox function
            checkbox_son = QCheckBox()
            all_header_combobox.append(checkbox_son)
            # add checkbox
            self.main_table.setCellWidget(i, 0, checkbox_son)

            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j + 1, newItem)
                pass

        layout.addWidget(self.main_table)
        vlayout.addLayout(layout0)
        vlayout.addLayout(layout)
        self.setLayout(vlayout)


    def add_info_links(self):
        self.s = Add_Other_Info_Windows02()
        self.s.Add_Info_Close_Signal.connect(self.add_info_windows_close)
        global station_xyz_list
        station_xyz_list = []
        self.s.show()

    def add_info_windows_close(self):
        try:
            # print('load', station_xyz_list)
            for one_list in station_xyz_list:
                self.main_table.insertRow(0)
                # 0 Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.insert(0, checkbox_son)
                self.main_table.setCellWidget(0, 0, checkbox_son)
                # 1
                newItem = QTableWidgetItem(one_list[0])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 1, newItem)
                # 2
                text_2 = str(format(one_list[2][1], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_2)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 2, newItem)
                # 3
                text_3 = str(format(one_list[2][0], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_3)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 3, newItem)
                # 4
                newItem = QTableWidgetItem(one_list[4])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 4, newItem)
                # 5
                newItem = QTableWidgetItem(one_list[5])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 5, newItem)
        except:
            pass
        print('Close the add interface')

    def minus_info_links(self):
        choosed_row = self.main_table.selectionModel().currentIndex().row()
        self.main_table.removeRow(choosed_row)

    def load_origain_file(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        shutil.copy(str(curdir) + r'/slib/json/origin/Curtin_Info.json', str(curdir) + r'/slib/json/Curtin_Info.json')
        if whether_update == QMessageBox.Yes:
            origain_json_text = json.load(open(str(curdir) + r'/slib/json/Curtin_Info.json', 'r'))
            self.main_table.setRowCount(len(origain_json_text))
            for i, line_text in zip(range(len(origain_json_text)), origain_json_text):
                # Set checkbox function
                checkbox_son = QCheckBox()
                all_header_combobox.append(checkbox_son)
                self.main_table.setCellWidget(i, 0, checkbox_son)
                for j in range(len(line_text)):
                    newItem = QTableWidgetItem(line_text[j])
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(i, j + 1, newItem)

            now_json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            origin_json_text = json.load(open(str(curdir) + r'/slib/json/origin/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            now_json_text[5] = origin_json_text[5]
            with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                json.dump(now_json_text, f, ensure_ascii=False)

    # Override keyboard events
    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.showMessage()
            # self.bt1.click()

    #  Add Stations
    def addInformationStations(self):
        checked_stations = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_station = self.main_table.item(checked_c, 1).text()
                checked_stations.append(checked_station)
        global_var.set_value('Info_table_checked_AreaCORS_stations', checked_stations)
        print(checked_stations)
        self.close()

    #  Save Info
    def saveCheckedInformation(self):
        checked_c_list = []
        checked_text = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_c_list.append(checked_c)
        for i in checked_c_list:
            checked_row_text = []
            for j in range(self.main_table.columnCount()):
                if j != 0:
                    single_text = self.main_table.item(i, j).text()
                    checked_row_text.append(single_text)
            checked_text = checked_text + [checked_row_text]
        print(checked_text)

        # Save as
        saveInformationPath, ok2 = QFileDialog.getSaveFileName(self, 'File save', "/", "Text Files(*.xls)")
        if saveInformationPath:
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet("Station-Info")
            sheet1.write(0, 0, 'Station')
            sheet1.write(0, 1, 'Longitude/(°)')
            sheet1.write(0, 2, 'Latitude/(°)')
            sheet1.write(0, 3, 'Receiver Type')
            sheet1.write(0, 4, 'Antenna Type')
            for i in range(len(checked_text)):
                for j in range(len(checked_text[0])):
                    sheet1.write(i + 1, j, checked_text[i][j])
            workbook.save(saveInformationPath)
            pass

    def Update_ionfo(self):
        whether_update = QMessageBox.question(self, 'Tips',
                                              'Update station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            all_table_list = []
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount() - 1):
                    temp_list.append(self.main_table.item(r, c + 1).text())
                all_table_list.append(temp_list)
            with open(str(curdir) + r'/slib/json/Curtin_Info.json', 'w', encoding='utf-8') as f:
                json.dump(all_table_list, f, ensure_ascii=False)
            try:
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios.json', 'r'))
                for one_add_info_list in station_xyz_list:
                    if one_add_info_list[0] != '':
                        json_text[6].insert(0, one_add_info_list[0])
                with open(str(curdir) + r'/slib/json/CORS_Statios.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
                add_coord_list = []
                for one_add_coord_list in station_xyz_list:
                    if one_add_coord_list[0] != '' and one_add_coord_list[3] != []:
                        add_coord_list.append(
                            [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                python_json_html(str(curdir) + r'/static/CurtinCORS.json', add_coord_list)
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
                json_text[5].insert(0, [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
            except:
                pass
            print('Update!')

    def showMessage(self):
        for r in range(self.main_table.rowCount()):
            for c in range(self.main_table.columnCount()):
                if c != 0:
                    self.main_table.item(r, c).setBackground(QBrush(QColor(255, 255, 255)))

        wen_Text = self.searchLab.text()
        wen_list = wen_Text.split(':')
        print(wen_list)
        for wen in reversed(wen_list):
            if len(wen) == 4:
                wen = wen.upper()
            items = self.main_table.findItems(wen, Qt.MatchExactly)

            if items:
                temp_text_list = []
                temp_color_list = []
                for i in items:
                    i = i.row()
                    lie_text_list = []
                    lie_color_list = []
                    for j in range(5):
                        select_text = self.main_table.item(i, j + 1).text()
                        select_color = self.main_table.item(i, j + 1).background()
                        lie_text_list.append(select_text)
                        lie_color_list.append(select_color)
                    self.main_table.removeRow(i)
                    all_header_combobox.remove(all_header_combobox[i])
                    temp_text_list = temp_text_list + [lie_text_list]
                    temp_color_list = temp_color_list + [lie_color_list]

                # Insert the information of the search target in the first line
                # print(temp_text_list)
                for i, m in zip(reversed(temp_text_list), reversed(temp_color_list)):
                    self.main_table.insertRow(0)
                    # Set checkbox function
                    checkbox_son = QCheckBox()
                    all_header_combobox.insert(0, checkbox_son)
                    self.main_table.setCellWidget(0, 0, checkbox_son)
                    for j in range(5):
                        newItem = QTableWidgetItem(i[j])
                        newItem.setBackground(m[j])
                        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.main_table.setItem(0, j + 1, newItem)

                items = self.main_table.findItems(wen, Qt.MatchExactly)

                # Secondary search, highlight
                # Scroll to the selected table and highlight it
                print(items[0].row())
                if len(items) > 0:
                    for item in items:
                        item.setBackground(QBrush(QColor(0, 255, 0)))
                self.main_table.verticalScrollBar().setSliderPosition(0)
            # else:
            #     QMessageBox.information(self, 'Hint', 'What you are looking for is not in the table !')

# -------------------------------------------------------------------------------------------------
# 4
class APREF_CORS_Info_Table(QWidget):
    def __init__(self):
        super().__init__()
        all_header_combobox.clear()
        self.setWindowTitle("APREF CORS Station-Info")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))
        # self.move(370 / 1920 * win_width, 100 / 1080 * win_height)
        # self.setFixedSize(1250 / 1920 * win_width, 685 / 1080 * win_height)
        self.resize(1000*win_height/1080, 798*win_height/1080)
        self.setup_ui()

    my_Signal_AreaCors = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.my_Signal_AreaCors.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.searchLab = QLineEdit(self)
        self.searchLab.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.searchLab.setPlaceholderText('e.g. ABMF:SEPT POLARX5')
        # self.searchLab.setGeometry(0, 0, 1010 / 1920 * win_width, 35 / 1080 * win_height)
        self.searchLab.setMinimumWidth(60)
        self.searchLab.setMinimumHeight(20)
        layout0.addWidget( self.searchLab)


        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(str(curdir) + r'/slib/logo/magnifier.jpg'))
        self.searchLab.addAction(station_search_icon, QLineEdit.LeadingPosition)
        station_search_icon.triggered.connect(self.showMessage)

        self.confirm_btn = QPushButton(self)
        # self.confirm_btn.setGeometry(1015 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.confirm_btn)
        self.confirm_btn.setMinimumWidth(10)
        self.confirm_btn.setMinimumHeight(15)
        self.confirm_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.confirm_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/sure.png')}")
        self.confirm_btn.clicked.connect(self.addInformationStations)

        self.add_btn = QPushButton(self)
        # self.add_btn.setGeometry(1056 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.add_btn)
        self.add_btn.setMinimumWidth(10)
        self.add_btn.setMinimumHeight(15)
        self.add_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.add_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/plus.png')}")
        self.add_btn.clicked.connect(self.add_info_links)

        self.minus_btn = QPushButton(self)
        # self.minus_btn.setGeometry(1093 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.minus_btn)
        self.minus_btn.setMinimumWidth(10)
        self.minus_btn.setMinimumHeight(15)
        self.minus_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/minus.png')}")
        self.minus_btn.clicked.connect(self.minus_info_links)

        self.export_btn = QPushButton(self)
        # self.export_btn.setGeometry(1130 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.export_btn)
        self.export_btn.setMinimumWidth(10)
        self.export_btn.setMinimumHeight(15)
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.export_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/export.png')}")
        self.export_btn.clicked.connect(self.saveCheckedInformation)

        self.save_btn = QPushButton(self)
        # self.save_btn.setGeometry(1167 / 1920 * win_width, 0, 35 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.save_btn)
        self.save_btn.setMinimumWidth(10)
        self.save_btn.setMinimumHeight(15)
        self.save_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.save_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/save.png')}")
        self.save_btn.clicked.connect(self.Update_ionfo)

        self.recovery_btn = QPushButton(self)
        # self.recovery_btn.setGeometry(1205 / 1920 * win_width, 1 / 1080 * win_height, 29 / 1920 * win_width, 29 / 1080 * win_height)
        layout0.addWidget(self.recovery_btn)
        self.recovery_btn.setMinimumWidth(10)
        self.recovery_btn.setMinimumHeight(15)
        self.recovery_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.recovery_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/recovery.png')}")
        self.recovery_btn.clicked.connect(self.load_origain_file)

        json_text = json.load(open(str(curdir) + r'/slib/json/APREF_CORS_Info.json', 'r'))
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(6)
        self.main_table.setRowCount(len(json_text))
        # self.main_table.setGeometry(0, 35 / 1080 * win_height, 1250 / 1920 * win_width, 650 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set checkbox header
        header = CheckBoxHeader()
        self.main_table.setHorizontalHeader(header)
        self.main_table.setHorizontalHeaderLabels(header_field_HongKong)
        # Set column width
        # self.main_table.setColumnWidth(0, 60 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 130 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 300 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 300 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header.select_all_clicked.connect(header.change_state)

        self.main_table.setHorizontalHeaderLabels(
            ['All', 'Station', 'Longitude/(°)', 'Latitude/(°)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(json_text)), json_text):
            # Set checkbox function
            checkbox_son = QCheckBox()
            all_header_combobox.append(checkbox_son)
            # add checkbox
            self.main_table.setCellWidget(i, 0, checkbox_son)
            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j + 1, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout0)
        vlayout.addLayout(layout)
        self.setLayout(vlayout)

    def add_info_links(self):
        self.s = Add_Other_Info_Windows02()
        self.s.Add_Info_Close_Signal.connect(self.add_info_windows_close)
        global station_xyz_list
        station_xyz_list = []
        self.s.show()

    def add_info_windows_close(self):
        try:
            # print('load', station_xyz_list)
            for one_list in station_xyz_list:
                self.main_table.insertRow(0)
                # 0 Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.insert(0, checkbox_son)
                self.main_table.setCellWidget(0, 0, checkbox_son)
                # 1
                newItem = QTableWidgetItem(one_list[0])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 1, newItem)
                # 2
                text_2 = str(format(one_list[2][1], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_2)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 2, newItem)
                # 3
                text_3 = str(format(one_list[2][0], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_3)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 3, newItem)
                # 4
                newItem = QTableWidgetItem(one_list[4])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 4, newItem)
                ##  5
                newItem = QTableWidgetItem(one_list[5])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 5, newItem)
        except:
            pass
        print('Close the add interface')

    def minus_info_links(self):
        choosed_row = self.main_table.selectionModel().currentIndex().row()
        self.main_table.removeRow(choosed_row)

    def load_origain_file(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        shutil.copy(str(curdir) + r'/slib/json/origin/APREF_CORS_Info.json', str(curdir) + r'/slib/json/APREF_CORS_Info.json')
        if whether_update == QMessageBox.Yes:
            origain_json_text = json.load(open(str(curdir) + r'/slib/json/APREF_CORS_Info.json', 'r'))
            self.main_table.setRowCount(len(origain_json_text))
            for i, line_text in zip(range(len(origain_json_text)), origain_json_text):
                # Set checkbox function
                checkbox_son = QCheckBox()
                all_header_combobox.append(checkbox_son)
                self.main_table.setCellWidget(i, 0, checkbox_son)
                for j in range(len(line_text)):
                    newItem = QTableWidgetItem(line_text[j])
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(i, j + 1, newItem)

            now_json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            origin_json_text = json.load(open(str(curdir) + r'/slib/json/origin/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            now_json_text[6] = origin_json_text[6]
            with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                json.dump(now_json_text, f, ensure_ascii=False)

    # Override keyboard events
    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.showMessage()
            # self.bt1.click()

    #  Add Stations
    def addInformationStations(self):
        checked_stations = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_station = self.main_table.item(checked_c, 1).text()
                checked_stations.append(checked_station)
        global_var.set_value('Info_table_checked_AreaCORS_stations', checked_stations)
        print(checked_stations)
        self.close()

    #  Save Info
    def saveCheckedInformation(self):
        checked_c_list = []
        checked_text = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_c_list.append(checked_c)
        for i in checked_c_list:
            checked_row_text = []
            for j in range(self.main_table.columnCount()):
                if j != 0:
                    single_text = self.main_table.item(i, j).text()
                    checked_row_text.append(single_text)
            checked_text = checked_text + [checked_row_text]
        print(checked_text)

        # Save as
        saveInformationPath, ok2 = QFileDialog.getSaveFileName(self, 'File save', "/", "Text Files(*.xls)")
        if saveInformationPath:
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet("Station-Info")
            sheet1.write(0, 0, 'Station')
            sheet1.write(0, 1, 'Longitude/(°)')
            sheet1.write(0, 2, 'Latitude/(°)')
            sheet1.write(0, 3, 'Receiver Type')
            sheet1.write(0, 4, 'Antenna Type')
            for i in range(len(checked_text)):
                for j in range(len(checked_text[0])):
                    sheet1.write(i + 1, j, checked_text[i][j])
            workbook.save(saveInformationPath)
            pass

    def Update_ionfo(self):
        whether_update = QMessageBox.question(self, 'Tips',
                                              'Update station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            all_table_list = []
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount() - 1):
                    temp_list.append(self.main_table.item(r, c + 1).text())
                all_table_list.append(temp_list)
            with open(str(curdir) + r'/slib/json/APREF_CORS_Info.json', 'w', encoding='utf-8') as f:
                json.dump(all_table_list, f, ensure_ascii=False)
            try:
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios.json', 'r'))
                for one_add_info_list in station_xyz_list:
                    if one_add_info_list[0] != '':
                        json_text[3].insert(0, one_add_info_list[0])
                        json_text[4].insert(0, one_add_info_list[0])
                        json_text[5].insert(0, one_add_info_list[0])
                        json_text[7].insert(0, one_add_info_list[0])
                with open(str(curdir) + r'/slib/json/CORS_Statios.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
                add_coord_list = []
                for one_add_coord_list in station_xyz_list:
                    if one_add_coord_list[0] != '' and one_add_coord_list[3] != []:
                        add_coord_list.append(
                            [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                python_json_html(str(curdir) + r'/static/AprefCORS.json', add_coord_list)

                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
                json_text[6].insert(0, [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
            except:
                pass
            print('Update!')

    def showMessage(self):
        for r in range(self.main_table.rowCount()):
            for c in range(self.main_table.columnCount()):
                if c != 0:
                    self.main_table.item(r, c).setBackground(QBrush(QColor(255, 255, 255)))

        wen_Text = self.searchLab.text()
        wen_list = wen_Text.split(':')
        print(wen_list)
        for wen in reversed(wen_list):
            if len(wen) == 4:
                wen = wen.upper()
            items = self.main_table.findItems(wen, Qt.MatchExactly)

            if items:
                temp_text_list = []
                temp_color_list = []
                for i in items:
                    i = i.row()
                    lie_text_list = []
                    lie_color_list = []
                    for j in range(5):
                        select_text = self.main_table.item(i, j + 1).text()
                        select_color = self.main_table.item(i, j + 1).background()
                        lie_text_list.append(select_text)
                        lie_color_list.append(select_color)
                    self.main_table.removeRow(i)
                    all_header_combobox.remove(all_header_combobox[i])
                    temp_text_list = temp_text_list + [lie_text_list]
                    temp_color_list = temp_color_list + [lie_color_list]

                # Insert the information of the search target in the first line
                # print(temp_text_list)
                for i, m in zip(reversed(temp_text_list), reversed(temp_color_list)):
                    self.main_table.insertRow(0)
                    # Set checkbox function
                    checkbox_son = QCheckBox()
                    all_header_combobox.insert(0, checkbox_son)
                    self.main_table.setCellWidget(0, 0, checkbox_son)
                    for j in range(5):
                        newItem = QTableWidgetItem(i[j])
                        newItem.setBackground(m[j])
                        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.main_table.setItem(0, j + 1, newItem)

                items = self.main_table.findItems(wen, Qt.MatchExactly)

                # Secondary search, highlight
                # Scroll to the selected table and highlight it
                print(items[0].row())
                if len(items) > 0:
                    for item in items:
                        item.setBackground(QBrush(QColor(0, 255, 0)))
                self.main_table.verticalScrollBar().setSliderPosition(0)
            # else:
            #     QMessageBox.information(self, 'Hint', 'What you are looking for is not in the table !')

# -------------------------------------------------------------------------------------------------
# 5
class JPN_Info_Table(QWidget):
    def __init__(self):
        super().__init__()
        all_header_combobox.clear()
        self.setWindowTitle("JPN Station-Info")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))
        # self.move(370 / 1920 * win_width, 100 / 1080 * win_height)
        # self.setFixedSize(1241 / 1920 * win_width, 685 / 1080 * win_height)
        self.resize(1000*win_height/1080, 798*win_height/1080)
        self.setup_ui()

    my_Signal_AreaCors = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.my_Signal_AreaCors.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.searchLab = QLineEdit(self)
        self.searchLab.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.searchLab.setPlaceholderText('e.g. ANMG:TRIMBLE NETR9')
        # self.searchLab.setGeometry(0, 0, 1001 / 1920 * win_width, 35 / 1080 * win_height)
        self.searchLab.setMinimumWidth(60)
        self.searchLab.setMinimumHeight(20)
        layout0.addWidget( self.searchLab)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(str(curdir) + r'/slib/logo/magnifier.jpg'))
        self.searchLab.addAction(station_search_icon, QLineEdit.LeadingPosition)
        station_search_icon.triggered.connect(self.showMessage)

        self.confirm_btn = QPushButton(self)
        # self.confirm_btn.setGeometry(1006 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.confirm_btn)
        self.confirm_btn.setMinimumWidth(10)
        self.confirm_btn.setMinimumHeight(15)
        self.confirm_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.confirm_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/sure.png')}")
        self.confirm_btn.clicked.connect(self.addInformationStations)

        self.add_btn = QPushButton(self)
        # self.add_btn.setGeometry(1047 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.add_btn)
        self.add_btn.setMinimumWidth(10)
        self.add_btn.setMinimumHeight(15)
        self.add_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.add_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/plus.png')}")
        self.add_btn.clicked.connect(self.add_info_links)

        self.minus_btn = QPushButton(self)
        # self.minus_btn.setGeometry(1084 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.minus_btn)
        self.minus_btn.setMinimumWidth(10)
        self.minus_btn.setMinimumHeight(15)
        self.minus_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/minus.png')}")
        self.minus_btn.clicked.connect(self.minus_info_links)

        self.export_btn = QPushButton(self)
        # self.export_btn.setGeometry(1121 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.export_btn)
        self.export_btn.setMinimumWidth(10)
        self.export_btn.setMinimumHeight(15)
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.export_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/export.png')}")
        self.export_btn.clicked.connect(self.saveCheckedInformation)

        self.save_btn = QPushButton(self)
        # self.save_btn.setGeometry(1158 / 1920 * win_width, 0, 35 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.save_btn)
        self.save_btn.setMinimumWidth(10)
        self.save_btn.setMinimumHeight(15)
        self.save_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.save_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/save.png')}")
        self.save_btn.clicked.connect(self.Update_ionfo)

        self.recovery_btn = QPushButton(self)
        # self.recovery_btn.setGeometry(1196 / 1920 * win_width, 1 / 1080 * win_height, 29 / 1920 * win_width, 29 / 1080 * win_height)
        layout0.addWidget(self.recovery_btn)
        self.recovery_btn.setMinimumWidth(10)
        self.recovery_btn.setMinimumHeight(15)
        self.recovery_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.recovery_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/recovery.png')}")
        self.recovery_btn.clicked.connect(self.load_origain_file)

        json_text = json.load(open(str(curdir) + r'/slib/json/JPN_Info.json', 'r'))
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(6)
        self.main_table.setRowCount(len(json_text))
        # self.main_table.setGeometry(0, 35 / 1080 * win_height, 1241 / 1920 * win_width, 650 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set checkbox header
        header = CheckBoxHeader()
        self.main_table.setHorizontalHeader(header)
        self.main_table.setHorizontalHeaderLabels(header_field_HongKong)
        # Set column width
        # self.main_table.setColumnWidth(0, 60 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 130 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 300 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 300 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header.select_all_clicked.connect(header.change_state)

        self.main_table.setHorizontalHeaderLabels(
            ['All', 'Station', 'Longitude/(°)', 'Latitude/(°)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(json_text)), json_text):
            # Set checkbox function
            checkbox_son = QCheckBox()
            all_header_combobox.append(checkbox_son)
            # add checkbox
            self.main_table.setCellWidget(i, 0, checkbox_son)
            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j + 1, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout0)
        vlayout.addLayout(layout)
        self.setLayout(vlayout)

    def add_info_links(self):
        self.s = Add_Other_Info_Windows02()
        self.s.Add_Info_Close_Signal.connect(self.add_info_windows_close)
        global station_xyz_list
        station_xyz_list = []
        self.s.show()

    def add_info_windows_close(self):
        try:
            # print('load', station_xyz_list)
            for one_list in station_xyz_list:
                self.main_table.insertRow(0)
                # 0 Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.insert(0, checkbox_son)
                self.main_table.setCellWidget(0, 0, checkbox_son)
                # 1
                newItem = QTableWidgetItem(one_list[0])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 1, newItem)
                # 2
                text_2 = str(format(one_list[2][1], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_2)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 2, newItem)
                # 3
                text_3 = str(format(one_list[2][0], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_3)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 3, newItem)
                # 4
                newItem = QTableWidgetItem(one_list[4])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 4, newItem)
                # 5
                newItem = QTableWidgetItem(one_list[5])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 5, newItem)
        except:
            pass
        print('Close the add interface')

    def minus_info_links(self):
        choosed_row = self.main_table.selectionModel().currentIndex().row()
        self.main_table.removeRow(choosed_row)

    def load_origain_file(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        shutil.copy(str(curdir) + r'/slib/json/origin/JPN_Info.json', str(curdir) + r'/slib/json/JPN_Info.json')
        if whether_update == QMessageBox.Yes:
            origain_json_text = json.load(open(str(curdir) + r'/slib/json/JPN_Info.json', 'r'))
            self.main_table.setRowCount(len(origain_json_text))
            for i, line_text in zip(range(len(origain_json_text)), origain_json_text):
                # Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.append(checkbox_son)
                self.main_table.setCellWidget(i, 0, checkbox_son)
                for j in range(len(line_text)):
                    newItem = QTableWidgetItem(line_text[j])
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(i, j + 1, newItem)

            now_json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            origin_json_text = json.load(open(str(curdir) + r'/slib/json/origin/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            now_json_text[3] = origin_json_text[3]
            with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                json.dump(now_json_text, f, ensure_ascii=False)

    # Override keyboard events
    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.showMessage()
            # self.bt1.click()

    #  Add Stations
    def addInformationStations(self):
        checked_stations = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_station = self.main_table.item(checked_c, 1).text()
                checked_stations.append(checked_station)
        global_var.set_value('Info_table_checked_AreaCORS_stations', checked_stations)
        print(checked_stations)
        self.close()

    #  Save Info
    def saveCheckedInformation(self):
        checked_c_list = []
        checked_text = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_c_list.append(checked_c)
        for i in checked_c_list:
            checked_row_text = []
            for j in range(self.main_table.columnCount()):
                if j != 0:
                    single_text = self.main_table.item(i, j).text()
                    checked_row_text.append(single_text)
            checked_text = checked_text + [checked_row_text]
        print(checked_text)

        # Save as
        saveInformationPath, ok2 = QFileDialog.getSaveFileName(self, 'File save', "/", "Text Files(*.xls)")
        if saveInformationPath:
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet("Station-Info")
            sheet1.write(0, 0, 'Station')
            sheet1.write(0, 1, 'Longitude/(°)')
            sheet1.write(0, 2, 'Latitude/(°)')
            sheet1.write(0, 3, 'Receiver Type')
            sheet1.write(0, 4, 'Antenna Type')
            for i in range(len(checked_text)):
                for j in range(len(checked_text[0])):
                    sheet1.write(i + 1, j, checked_text[i][j])
            workbook.save(saveInformationPath)
            pass

    def Update_ionfo(self):
        whether_update = QMessageBox.question(self, 'Tips',
                                              'Update station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            all_table_list = []
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount() - 1):
                    temp_list.append(self.main_table.item(r, c + 1).text())
                all_table_list.append(temp_list)
            with open(str(curdir) + r'/slib/json/JPN_Info.json', 'w', encoding='utf-8') as f:
                json.dump(all_table_list, f, ensure_ascii=False)
            try:
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios.json', 'r'))
                for one_add_info_list in station_xyz_list:
                    if one_add_info_list[0] != '':
                        json_text[11].insert(0, one_add_info_list[0])
                with open(str(curdir) + r'/slib/json/CORS_Statios.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
                add_coord_list = []
                for one_add_coord_list in station_xyz_list:
                    if one_add_coord_list[0] != '' and one_add_coord_list[3] != []:
                        add_coord_list.append(
                            [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                python_json_html(str(curdir) + r'/static/JapanCORS.json', add_coord_list)

                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
                json_text[3].insert(0, [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
            except:
                pass
            print('Update!')

    def showMessage(self):
        for r in range(self.main_table.rowCount()):
            for c in range(self.main_table.columnCount()):
                if c != 0:
                    self.main_table.item(r, c).setBackground(QBrush(QColor(255, 255, 255)))

        wen_Text = self.searchLab.text()
        wen_list = wen_Text.split(':')
        print(wen_list)
        for wen in reversed(wen_list):
            if len(wen) == 4:
                wen = wen.upper()
            items = self.main_table.findItems(wen, Qt.MatchExactly)

            if items:
                temp_text_list = []
                temp_color_list = []
                for i in items:
                    i = i.row()
                    lie_text_list = []
                    lie_color_list = []
                    for j in range(5):
                        select_text = self.main_table.item(i, j + 1).text()
                        select_color = self.main_table.item(i, j + 1).background()
                        lie_text_list.append(select_text)
                        lie_color_list.append(select_color)
                    self.main_table.removeRow(i)
                    all_header_combobox.remove(all_header_combobox[i])
                    temp_text_list = temp_text_list + [lie_text_list]
                    temp_color_list = temp_color_list + [lie_color_list]

                # Insert the information of the search target in the first line
                # print(temp_text_list)
                for i, m in zip(reversed(temp_text_list), reversed(temp_color_list)):
                    self.main_table.insertRow(0)
                    # Set checkbox function
                    checkbox_son = QCheckBox()
                    all_header_combobox.insert(0, checkbox_son)
                    self.main_table.setCellWidget(0, 0, checkbox_son)
                    for j in range(5):
                        newItem = QTableWidgetItem(i[j])
                        newItem.setBackground(m[j])
                        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.main_table.setItem(0, j + 1, newItem)

                items = self.main_table.findItems(wen, Qt.MatchExactly)

                # Secondary search, highlight
                # Scroll to the selected table and highlight it
                print(items[0].row())
                if len(items) > 0:
                    for item in items:
                        item.setBackground(QBrush(QColor(0, 255, 0)))
                self.main_table.verticalScrollBar().setSliderPosition(0)
            # else:
            #     QMessageBox.information(self, 'Hint', 'What you are looking for is not in the table !')

# -------------------------------------------------------------------------------------------------
# 6
class Spain_CORS_Info_Table(QWidget):
    def __init__(self):
        super().__init__()
        all_header_combobox.clear()
        self.setWindowTitle("Spain CORS Station-Info")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        # self.move(370 / 1920 * win_width, 100 / 1080 * win_height)
        # self.setFixedSize(1241 / 1920 * win_width, 685 / 1080 * win_height)
        self.resize(1000*win_height/1080, 600*win_height/1080)
        self.setup_ui()

    my_Signal_AreaCors = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.my_Signal_AreaCors.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.searchLab = QLineEdit(self)
        self.searchLab.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.searchLab.setPlaceholderText('e.g. ACNS:TRIMBLE NETR9')
        # self.searchLab.setGeometry(0, 0, 1001 / 1920 * win_width, 35 / 1080 * win_height)
        self.searchLab.setMinimumWidth(60)
        self.searchLab.setMinimumHeight(20)
        layout0.addWidget( self.searchLab)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(str(curdir) + r'/slib/logo/magnifier.jpg'))
        self.searchLab.addAction(station_search_icon, QLineEdit.LeadingPosition)
        station_search_icon.triggered.connect(self.showMessage)

        self.confirm_btn = QPushButton(self)
        # self.confirm_btn.setGeometry(1006 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.confirm_btn)
        self.confirm_btn.setMinimumWidth(10)
        self.confirm_btn.setMinimumHeight(15)
        self.confirm_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.confirm_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/sure.png')}")
        self.confirm_btn.clicked.connect(self.addInformationStations)

        self.add_btn = QPushButton(self)
        # self.add_btn.setGeometry(1047 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.add_btn)
        self.add_btn.setMinimumWidth(10)
        self.add_btn.setMinimumHeight(15)
        self.add_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.add_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/plus.png')}")
        self.add_btn.clicked.connect(self.add_info_links)

        self.minus_btn = QPushButton(self)
        # self.minus_btn.setGeometry(1084 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)

        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/minus.png')}")
        self.minus_btn.clicked.connect(self.minus_info_links)
        layout0.addWidget(self.minus_btn)
        self.minus_btn.setMinimumWidth(10)
        self.minus_btn.setMinimumHeight(15)
        self.minus_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.export_btn = QPushButton(self)
        # self.export_btn.setGeometry(1121 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.export_btn)
        self.export_btn.setMinimumWidth(10)
        self.export_btn.setMinimumHeight(15)
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.export_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/export.png')}")
        self.export_btn.clicked.connect(self.saveCheckedInformation)

        self.save_btn = QPushButton(self)
        # self.save_btn.setGeometry(1158 / 1920 * win_width, 0, 35 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.save_btn)
        self.save_btn.setMinimumWidth(10)
        self.save_btn.setMinimumHeight(15)
        self.save_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.save_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/save.png')}")
        self.save_btn.clicked.connect(self.Update_ionfo)

        self.recovery_btn = QPushButton(self)
        # self.recovery_btn.setGeometry(1196 / 1920 * win_width, 1 / 1080 * win_height, 29 / 1920 * win_width, 29 / 1080 * win_height)
        layout0.addWidget(self.recovery_btn)
        self.recovery_btn.setMinimumWidth(10)
        self.recovery_btn.setMinimumHeight(15)
        self.recovery_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.recovery_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/recovery.png')}")
        self.recovery_btn.clicked.connect(self.load_origain_file)

        json_text = json.load(open(str(curdir) + r'/slib/json/Spain_CORS_Info.json', 'r'))
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(6)
        self.main_table.setRowCount(len(json_text))
        # self.main_table.setGeometry(0, 35 / 1080 * win_height, 1241 / 1920 * win_width, 650 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set checkbox header
        header = CheckBoxHeader()
        self.main_table.setHorizontalHeader(header)
        self.main_table.setHorizontalHeaderLabels(header_field_HongKong)
        # Set column width
        # self.main_table.setColumnWidth(0, 60 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 130 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 300 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 300 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header.select_all_clicked.connect(header.change_state)

        self.main_table.setHorizontalHeaderLabels(
            ['All', 'Station', 'Longitude/(°)', 'Latitude/(°)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(json_text)), json_text):
            # Set checkbox function
            checkbox_son = QCheckBox()
            all_header_combobox.append(checkbox_son)
            # add checkbox
            self.main_table.setCellWidget(i, 0, checkbox_son)

            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j + 1, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout0)
        vlayout.addLayout(layout)
        self.setLayout(vlayout)

    def add_info_links(self):
        self.s = Add_Other_Info_Windows02()
        self.s.Add_Info_Close_Signal.connect(self.add_info_windows_close)
        global station_xyz_list
        station_xyz_list = []
        self.s.show()

    def add_info_windows_close(self):
        try:
            # print('load', station_xyz_list)
            for one_list in station_xyz_list:
                self.main_table.insertRow(0)
                # 0 Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.insert(0, checkbox_son)
                self.main_table.setCellWidget(0, 0, checkbox_son)
                # 1
                newItem = QTableWidgetItem(one_list[0])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 1, newItem)
                # 2
                text_2 = str(format(one_list[2][1], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_2)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 2, newItem)
                # 3
                text_3 = str(format(one_list[2][0], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_3)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 3, newItem)
                # 4
                newItem = QTableWidgetItem(one_list[4])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 4, newItem)
                # 5
                newItem = QTableWidgetItem(one_list[5])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 5, newItem)
        except:
            pass
        print('Close the add interface')

    def minus_info_links(self):
        choosed_row = self.main_table.selectionModel().currentIndex().row()
        self.main_table.removeRow(choosed_row)

    def load_origain_file(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        shutil.copy(str(curdir) + r'/slib/json/origin/Spain_CORS_Info.json', str(curdir) + r'/slib/json/Spain_CORS_Info.json')
        if whether_update == QMessageBox.Yes:
            origain_json_text = json.load(open(str(curdir) + r'/slib/json/Spain_CORS_Info.json', 'r'))
            self.main_table.setRowCount(len(origain_json_text))
            for i, line_text in zip(range(len(origain_json_text)), origain_json_text):
                # Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.append(checkbox_son)
                self.main_table.setCellWidget(i, 0, checkbox_son)  # 为每一行添加复选框
                for j in range(len(line_text)):
                    newItem = QTableWidgetItem(line_text[j])
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(i, j + 1, newItem)

            now_json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            origin_json_text = json.load(open(str(curdir) + r'/slib/json/origin/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            now_json_text[2] = origin_json_text[2]
            with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                json.dump(now_json_text, f, ensure_ascii=False)

    # Override keyboard events
    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.showMessage()
            # self.bt1.click()

    #  Add Stations
    def addInformationStations(self):
        checked_stations = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_station = self.main_table.item(checked_c, 1).text()
                checked_stations.append(checked_station)
        global_var.set_value('Info_table_checked_AreaCORS_stations', checked_stations)
        print(checked_stations)
        self.close()

    #  Save Info
    def saveCheckedInformation(self):
        checked_c_list = []
        checked_text = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_c_list.append(checked_c)
        for i in checked_c_list:
            checked_row_text = []
            for j in range(self.main_table.columnCount()):
                if j != 0:
                    single_text = self.main_table.item(i, j).text()
                    checked_row_text.append(single_text)
            checked_text = checked_text + [checked_row_text]
        print(checked_text)

        # Save as
        saveInformationPath, ok2 = QFileDialog.getSaveFileName(self, 'File save', "/", "Text Files(*.xls)")
        if saveInformationPath:
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet("Station-Info")
            sheet1.write(0, 0, 'Station')
            sheet1.write(0, 1, 'Longitude/(°)')
            sheet1.write(0, 2, 'Latitude/(°)')
            sheet1.write(0, 3, 'Receiver Type')
            sheet1.write(0, 4, 'Antenna Type')
            for i in range(len(checked_text)):
                for j in range(len(checked_text[0])):
                    sheet1.write(i + 1, j, checked_text[i][j])
            workbook.save(saveInformationPath)
            pass

    def Update_ionfo(self):
        whether_update = QMessageBox.question(self, 'Tips',
                                              'Update station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            all_table_list = []
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount() - 1):
                    temp_list.append(self.main_table.item(r, c + 1).text())
                all_table_list.append(temp_list)
            with open(str(curdir) + r'/slib/json/Spain_CORS_Info.json', 'w', encoding='utf-8') as f:
                json.dump(all_table_list, f, ensure_ascii=False)
            try:
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios.json', 'r'))
                for one_add_info_list in station_xyz_list:
                    if one_add_info_list[0] != '':
                        json_text[9].insert(0, one_add_info_list[0])
                with open(str(curdir) + r'/slib/json/CORS_Statios.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
                add_coord_list = []
                for one_add_coord_list in station_xyz_list:
                    if one_add_coord_list[0] != '' and one_add_coord_list[3] != []:
                        add_coord_list.append(
                            [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                python_json_html(str(curdir) + r'/static/SpainCORS.json', add_coord_list)

                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
                json_text[2].insert(0, [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
            except:
                pass
            print('Update!')

    def showMessage(self):
        for r in range(self.main_table.rowCount()):
            for c in range(self.main_table.columnCount()):
                if c != 0:
                    self.main_table.item(r, c).setBackground(QBrush(QColor(255, 255, 255)))

        wen_Text = self.searchLab.text()
        wen_list = wen_Text.split(':')
        print(wen_list)
        for wen in reversed(wen_list):
            if len(wen) == 4:
                wen = wen.upper()
            items = self.main_table.findItems(wen, Qt.MatchExactly)

            if items:
                temp_text_list = []
                temp_color_list = []
                for i in items:
                    i = i.row()
                    lie_text_list = []
                    lie_color_list = []
                    for j in range(5):
                        select_text = self.main_table.item(i, j + 1).text()
                        select_color = self.main_table.item(i, j + 1).background()
                        lie_text_list.append(select_text)
                        lie_color_list.append(select_color)
                    self.main_table.removeRow(i)
                    all_header_combobox.remove(all_header_combobox[i])
                    temp_text_list = temp_text_list + [lie_text_list]
                    temp_color_list = temp_color_list + [lie_color_list]

                # Insert the information of the search target in the first line
                # print(temp_text_list)
                for i, m in zip(reversed(temp_text_list), reversed(temp_color_list)):
                    self.main_table.insertRow(0)
                    # Set checkbox function
                    checkbox_son = QCheckBox()
                    all_header_combobox.insert(0, checkbox_son)
                    self.main_table.setCellWidget(0, 0, checkbox_son)
                    for j in range(5):
                        newItem = QTableWidgetItem(i[j])
                        newItem.setBackground(m[j])
                        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.main_table.setItem(0, j + 1, newItem)

                items = self.main_table.findItems(wen, Qt.MatchExactly)

                # Secondary search, highlight
                # Scroll to the selected table and highlight it
                print(items[0].row())
                if len(items) > 0:
                    for item in items:
                        item.setBackground(QBrush(QColor(0, 255, 0)))
                self.main_table.verticalScrollBar().setSliderPosition(0)
            # else:
            #     QMessageBox.information(self, 'Hint', 'What you are looking for is not in the table !')

# -------------------------------------------------------------------------------------------------
# 7
class EPN_Info_Table(QWidget):
    def __init__(self):
        super().__init__()
        all_header_combobox.clear()
        self.setWindowTitle("EPN Station-Info")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))
        # self.move(370 / 1920 * win_width, 100 / 1080 * win_height)
        # self.setFixedSize(1250 / 1920 * win_width, 685 / 1080 * win_height)
        self.resize(1000*win_height/1080, 600*win_height/1080)
        self.setup_ui()

    my_Signal_AreaCors = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.my_Signal_AreaCors.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.searchLab = QLineEdit(self)
        self.searchLab.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.searchLab.setPlaceholderText('e.g. ACOR:LEICA GR50')
        # self.searchLab.setGeometry(0, 0, 1010 / 1920 * win_width, 35 / 1080 * win_height)
        self.searchLab.setMinimumWidth(60)
        self.searchLab.setMinimumHeight(20)
        layout0.addWidget( self.searchLab)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(str(curdir) + r'/slib/logo/magnifier.jpg'))
        self.searchLab.addAction(station_search_icon, QLineEdit.LeadingPosition)
        station_search_icon.triggered.connect(self.showMessage)

        self.confirm_btn = QPushButton(self)
        # self.confirm_btn.setGeometry(1015 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.confirm_btn)
        self.confirm_btn.setMinimumWidth(10)
        self.confirm_btn.setMinimumHeight(15)
        self.confirm_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.confirm_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/sure.png')}")
        self.confirm_btn.clicked.connect(self.addInformationStations)

        self.add_btn = QPushButton(self)
        # self.add_btn.setGeometry(1056 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.add_btn)
        self.add_btn.setMinimumWidth(10)
        self.add_btn.setMinimumHeight(15)
        self.add_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.add_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/plus.png')}")
        self.add_btn.clicked.connect(self.add_info_links)

        self.minus_btn = QPushButton(self)
        self.minus_btn.setGeometry(1093 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.minus_btn)
        self.minus_btn.setMinimumWidth(10)
        self.minus_btn.setMinimumHeight(15)
        self.minus_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/minus.png')}")
        self.minus_btn.clicked.connect(self.minus_info_links)

        self.export_btn = QPushButton(self)
        # self.export_btn.setGeometry(1130 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.export_btn)
        self.export_btn.setMinimumWidth(10)
        self.export_btn.setMinimumHeight(15)
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.export_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/export.png')}")
        self.export_btn.clicked.connect(self.saveCheckedInformation)

        self.save_btn = QPushButton(self)
        # self.save_btn.setGeometry(1167 / 1920 * win_width, 0, 35 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.save_btn)
        self.save_btn.setMinimumWidth(10)
        self.save_btn.setMinimumHeight(15)
        self.save_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.save_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/save.png')}")
        self.save_btn.clicked.connect(self.Update_ionfo)

        self.recovery_btn = QPushButton(self)
        # self.recovery_btn.setGeometry(1205 / 1920 * win_width, 1 / 1080 * win_height, 29 / 1920 * win_width, 29 / 1080 * win_height)
        layout0.addWidget(self.recovery_btn)
        self.recovery_btn.setMinimumWidth(10)
        self.recovery_btn.setMinimumHeight(15)
        self.recovery_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.recovery_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/recovery.png')}")
        self.recovery_btn.clicked.connect(self.load_origain_file)

        json_text = json.load(open(str(curdir) + r'/slib/json/EPN_Info.json', 'r'))
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(6)
        self.main_table.setRowCount(len(json_text))
        # self.main_table.setGeometry(0, 35 / 1080 * win_height, 1250 / 1920 * win_width, 650 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set checkbox header
        header = CheckBoxHeader()
        self.main_table.setHorizontalHeader(header)
        self.main_table.setHorizontalHeaderLabels(header_field_HongKong)
        # Set column width
        # self.main_table.setColumnWidth(0, 60 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 130 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 300 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 300 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header.select_all_clicked.connect(header.change_state)

        self.main_table.setHorizontalHeaderLabels(
            ['All', 'Station', 'Longitude/(°)', 'Latitude/(°)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(json_text)), json_text):
            # Set checkbox function
            checkbox_son = QCheckBox()
            all_header_combobox.append(checkbox_son)
            # add checkbox
            self.main_table.setCellWidget(i, 0, checkbox_son)

            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j + 1, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout0)
        vlayout.addLayout(layout)
        self.setLayout(vlayout)


    def add_info_links(self):
        self.s = Add_Other_Info_Windows02()
        self.s.Add_Info_Close_Signal.connect(self.add_info_windows_close)
        global station_xyz_list
        station_xyz_list = []
        self.s.show()

    def add_info_windows_close(self):
        try:
            # print('load', station_xyz_list)
            for one_list in station_xyz_list:
                self.main_table.insertRow(0)
                # 0 Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.insert(0, checkbox_son)
                self.main_table.setCellWidget(0, 0, checkbox_son)
                # 1
                newItem = QTableWidgetItem(one_list[0])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 1, newItem)
                # 2
                text_2 = str(format(one_list[2][1], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_2)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 2, newItem)
                # 3
                text_3 = str(format(one_list[2][0], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_3)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 3, newItem)
                # 4
                newItem = QTableWidgetItem(one_list[4])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 4, newItem)
                # 5
                newItem = QTableWidgetItem(one_list[5])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 5, newItem)
        except:
            pass
        print('Close the add interface')

    def minus_info_links(self):
        choosed_row = self.main_table.selectionModel().currentIndex().row()
        self.main_table.removeRow(choosed_row)

    def load_origain_file(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        shutil.copy(str(curdir) + r'/slib/json/origin/EPN_Info.json', str(curdir) + r'/slib/json/EPN_Info.json')
        if whether_update == QMessageBox.Yes:
            origain_json_text = json.load(open(str(curdir) + r'/slib/json/EPN_Info.json', 'r'))
            self.main_table.setRowCount(len(origain_json_text))
            for i, line_text in zip(range(len(origain_json_text)), origain_json_text):
                # Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.append(checkbox_son)
                self.main_table.setCellWidget(i, 0, checkbox_son)
                for j in range(len(line_text)):
                    newItem = QTableWidgetItem(line_text[j])
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(i, j + 1, newItem)

            now_json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            origin_json_text = json.load(open(str(curdir) + r'/slib/json/origin/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            now_json_text[1] = origin_json_text[1]
            with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                json.dump(now_json_text, f, ensure_ascii=False)

    # Override keyboard events
    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.showMessage()
            # self.bt1.click()

    #  Add Stations
    def addInformationStations(self):
        checked_stations = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_station = self.main_table.item(checked_c, 1).text()
                checked_stations.append(checked_station)
        global_var.set_value('Info_table_checked_AreaCORS_stations', checked_stations)
        print(checked_stations)
        self.close()

    #  Save Info
    def saveCheckedInformation(self):
        checked_c_list = []
        checked_text = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_c_list.append(checked_c)
        for i in checked_c_list:
            checked_row_text = []
            for j in range(self.main_table.columnCount()):
                if j != 0:
                    single_text = self.main_table.item(i, j).text()
                    checked_row_text.append(single_text)
            checked_text = checked_text + [checked_row_text]
        print(checked_text)

        # Save as
        saveInformationPath, ok2 = QFileDialog.getSaveFileName(self, 'File save', "/", "Text Files(*.xls)")
        if saveInformationPath:
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet("Station-Info")
            sheet1.write(0, 0, 'Station')
            sheet1.write(0, 1, 'Longitude/(°)')
            sheet1.write(0, 2, 'Latitude/(°)')
            sheet1.write(0, 3, 'Receiver Type')
            sheet1.write(0, 4, 'Antenna Type')
            for i in range(len(checked_text)):
                for j in range(len(checked_text[0])):
                    sheet1.write(i + 1, j, checked_text[i][j])
            workbook.save(saveInformationPath)
            pass

    def Update_ionfo(self):
        whether_update = QMessageBox.question(self, 'Tips',
                                              'Update station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            all_table_list = []
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount() - 1):
                    temp_list.append(self.main_table.item(r, c + 1).text())
                all_table_list.append(temp_list)
            with open(str(curdir) + r'/slib/json/EPN_Info.json', 'w', encoding='utf-8') as f:
                json.dump(all_table_list, f, ensure_ascii=False)
            if station_xyz_list:
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios.json', 'r'))
                for one_add_info_list in station_xyz_list:
                    if one_add_info_list[0] != '':
                        json_text[8].insert(0, one_add_info_list[0])
                with open(str(curdir) + r'/slib/json/CORS_Statios.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
                add_coord_list = []
                for one_add_coord_list in station_xyz_list:
                    if one_add_coord_list[0] != '' and one_add_coord_list[3] != []:
                        add_coord_list.append(
                            [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                python_json_html(str(curdir) + r'/static/EnropeCORS.json', add_coord_list)

                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
                json_text[1].insert(0, [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
            print('Update!')

    def showMessage(self):
        for r in range(self.main_table.rowCount()):
            for c in range(self.main_table.columnCount()):
                if c != 0:
                    self.main_table.item(r, c).setBackground(QBrush(QColor(255, 255, 255)))

        wen_Text = self.searchLab.text()
        wen_list = wen_Text.split(':')
        print(wen_list)
        for wen in reversed(wen_list):
            if len(wen) == 4:
                wen = wen.upper()
            items = self.main_table.findItems(wen, Qt.MatchExactly)

            if items:
                temp_text_list = []
                temp_color_list = []
                for i in items:
                    i = i.row()
                    lie_text_list = []
                    lie_color_list = []
                    for j in range(5):
                        select_text = self.main_table.item(i, j + 1).text()
                        select_color = self.main_table.item(i, j + 1).background()
                        lie_text_list.append(select_text)
                        lie_color_list.append(select_color)
                    self.main_table.removeRow(i)
                    all_header_combobox.remove(all_header_combobox[i])
                    temp_text_list = temp_text_list + [lie_text_list]
                    temp_color_list = temp_color_list + [lie_color_list]

                # Insert the information of the search target in the first line
                # print(temp_text_list)
                for i, m in zip(reversed(temp_text_list), reversed(temp_color_list)):
                    self.main_table.insertRow(0)
                    # Set checkbox function
                    checkbox_son = QCheckBox()
                    all_header_combobox.insert(0, checkbox_son)
                    self.main_table.setCellWidget(0, 0, checkbox_son)
                    for j in range(5):
                        newItem = QTableWidgetItem(i[j])
                        newItem.setBackground(m[j])
                        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.main_table.setItem(0, j + 1, newItem)

                items = self.main_table.findItems(wen, Qt.MatchExactly)

                # Secondary search, highlight
                # Scroll to the selected table and highlight it
                print(items[0].row())
                if len(items) > 0:
                    for item in items:
                        item.setBackground(QBrush(QColor(0, 255, 0)))
                self.main_table.verticalScrollBar().setSliderPosition(0)
            # else:
            #     QMessageBox.information(self, 'Hint', 'What you are looking for is not in the table !')

# -------------------------------------------------------------------------------------------------
# 8
class NGS_Info_Table(QWidget):
    def __init__(self):
        super().__init__()
        all_header_combobox.clear()
        self.setWindowTitle("USA CORS Station-Info")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))
        # self.move(370 / 1920 * win_width, 100 / 1080 * win_height)
        # self.setFixedSize(1250 / 1920 * win_width, 685 / 1080 * win_height)
        self.resize(1000*win_height/1080, 600*win_height/1080)
        self.setup_ui()

    my_Signal_AreaCors = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.my_Signal_AreaCors.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.searchLab = QLineEdit(self)
        self.searchLab.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.searchLab.setPlaceholderText('e.g. 1LSU:TRIMBLE ALLOY')
        # self.searchLab.setGeometry(0, 0, 1010 / 1920 * win_width, 35 / 1080 * win_height)
        self.searchLab.setMinimumWidth(60)
        self.searchLab.setMinimumHeight(20)
        layout0.addWidget(self.searchLab)

        station_search_icon = QAction(self)
        station_search_icon.setIcon(QIcon(str(curdir) + r'/slib/logo/magnifier.jpg'))
        self.searchLab.addAction(station_search_icon, QLineEdit.LeadingPosition)
        station_search_icon.triggered.connect(self.showMessage)

        self.confirm_btn = QPushButton(self)
        # self.confirm_btn.setGeometry(1015 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.confirm_btn)
        self.confirm_btn.setMinimumWidth(10)
        self.confirm_btn.setMinimumHeight(15)
        self.confirm_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.confirm_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/sure.png')}")
        self.confirm_btn.clicked.connect(self.addInformationStations)

        self.add_btn = QPushButton(self)
        # self.add_btn.setGeometry(1056 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.add_btn)
        self.add_btn.setMinimumWidth(10)
        self.add_btn.setMinimumHeight(15)
        self.add_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.add_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/plus.png')}")
        self.add_btn.clicked.connect(self.add_info_links)

        self.minus_btn = QPushButton(self)
        # self.minus_btn.setGeometry(1093 / 1920 * win_width, 3 / 1080 * win_height, 27 / 1920 * win_width, 27 / 1080 * win_height)
        layout0.addWidget(self.minus_btn)
        self.minus_btn.setMinimumWidth(10)
        self.minus_btn.setMinimumHeight(15)
        self.minus_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.minus_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/minus.png')}")
        self.minus_btn.clicked.connect(self.minus_info_links)

        self.export_btn = QPushButton(self)
        # self.export_btn.setGeometry(1130 / 1920 * win_width, 0, 31 / 1920 * win_width, 31 / 1080 * win_height)
        layout0.addWidget(self.export_btn)
        self.export_btn.setMinimumWidth(10)
        self.export_btn.setMinimumHeight(15)
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.export_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/export.png')}")
        self.export_btn.clicked.connect(self.saveCheckedInformation)

        self.save_btn = QPushButton(self)
        # self.save_btn.setGeometry(1167 / 1920 * win_width, 0, 35 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.save_btn)
        self.save_btn.setMinimumWidth(10)
        self.save_btn.setMinimumHeight(15)
        self.save_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.save_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/save.png')}")
        self.save_btn.clicked.connect(self.Update_ionfo)

        self.recovery_btn = QPushButton(self)
        # self.recovery_btn.setGeometry(1205 / 1920 * win_width, 1 / 1080 * win_height, 29 / 1920 * win_width, 29 / 1080 * win_height)
        layout0.addWidget(self.recovery_btn)
        self.recovery_btn.setMinimumWidth(10)
        self.recovery_btn.setMinimumHeight(15)
        self.recovery_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.recovery_btn.setStyleSheet("QPushButton{border-image: url('./slib/logo/recovery.png')}")
        self.recovery_btn.clicked.connect(self.load_origain_file)

        json_text = json.load(open(str(curdir) + r'/slib/json/NGS_Info.json', 'r'))
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(6)
        self.main_table.setRowCount(len(json_text))
        # self.main_table.setGeometry(0, 35 / 1080 * win_height, 1250 / 1920 * win_width, 650 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set checkbox header
        header = CheckBoxHeader()
        self.main_table.setHorizontalHeader(header)
        self.main_table.setHorizontalHeaderLabels(header_field_HongKong)
        # Set column width
        # self.main_table.setColumnWidth(0, 60 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 120 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 300 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 300 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        header.select_all_clicked.connect(header.change_state)

        self.main_table.setHorizontalHeaderLabels(
            ['All', 'Station', 'Longitude/(°)', 'Latitude/(°)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(json_text)), json_text):
            # Set checkbox function
            checkbox_son = QCheckBox()
            all_header_combobox.append(checkbox_son)
            # add checkbox
            self.main_table.setCellWidget(i, 0, checkbox_son)

            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j + 1, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout0)
        vlayout.addLayout(layout)
        self.setLayout(vlayout)

    def add_info_links(self):
        self.s = Add_Other_Info_Windows02()
        self.s.Add_Info_Close_Signal.connect(self.add_info_windows_close)
        global station_xyz_list
        station_xyz_list = []
        self.s.show()

    def add_info_windows_close(self):
        try:
            # print('load', station_xyz_list)
            for one_list in station_xyz_list:
                self.main_table.insertRow(0)
                # 0 Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.insert(0, checkbox_son)
                self.main_table.setCellWidget(0, 0, checkbox_son)
                # 1
                newItem = QTableWidgetItem(one_list[0])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 1, newItem)
                # 2
                text_2 = str(format(one_list[2][1], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_2)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 2, newItem)
                # 3
                text_3 = str(format(one_list[2][0], str(curdir) + r'2f'))
                newItem = QTableWidgetItem(text_3)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 3, newItem)
                # 4
                newItem = QTableWidgetItem(one_list[4])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 4, newItem)
                # 5
                newItem = QTableWidgetItem(one_list[5])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(0, 5, newItem)
        except:
            pass
        print('Close the add interface')

    def minus_info_links(self):
        choosed_row = self.main_table.selectionModel().currentIndex().row()
        self.main_table.removeRow(choosed_row)

    def load_origain_file(self):
        whether_update = QMessageBox.question(self, 'Tips', 'Restore initial station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        shutil.copy(str(curdir) + r'/slib/json/origin/NGS_Info.json', str(curdir) + r'/slib/json/NGS_Info.json')
        if whether_update == QMessageBox.Yes:
            origain_json_text = json.load(open(str(curdir) + r'/slib/json/NGS_Info.json', 'r'))
            self.main_table.setRowCount(len(origain_json_text))
            for i, line_text in zip(range(len(origain_json_text)), origain_json_text):
                # Set check box function
                checkbox_son = QCheckBox()
                all_header_combobox.append(checkbox_son)
                self.main_table.setCellWidget(i, 0, checkbox_son)
                for j in range(len(line_text)):
                    newItem = QTableWidgetItem(line_text[j])
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(i, j + 1, newItem)

            now_json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            origin_json_text = json.load(open(str(curdir) + r'/slib/json/origin/CORS_Statios_BaiDu_Coordinate.json', 'r'))
            now_json_text[0] = origin_json_text[0]
            with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                json.dump(now_json_text, f, ensure_ascii=False)

    # Override keyboard events
    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':
            self.showMessage()
            # self.bt1.click()

    #  Add Stations
    def addInformationStations(self):
        checked_stations = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_station = self.main_table.item(checked_c, 1).text()
                checked_stations.append(checked_station)
        global_var.set_value('Info_table_checked_AreaCORS_stations', checked_stations)
        print(checked_stations)
        self.close()

    #  Save Info
    def saveCheckedInformation(self):
        checked_c_list = []
        checked_text = []
        for i in all_header_combobox:
            if i.isChecked():
                checked_c = all_header_combobox.index(i)
                checked_c_list.append(checked_c)
        for i in checked_c_list:
            checked_row_text = []
            for j in range(self.main_table.columnCount()):
                if j != 0:
                    single_text = self.main_table.item(i, j).text()
                    checked_row_text.append(single_text)
            checked_text = checked_text + [checked_row_text]
        print(checked_text)

        # Save as
        saveInformationPath, ok2 = QFileDialog.getSaveFileName(self, 'File save', "/", "Text Files(*.xls)")
        if saveInformationPath:
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet("Station-Info")
            sheet1.write(0, 0, 'Station')
            sheet1.write(0, 1, 'Longitude/(°)')
            sheet1.write(0, 2, 'Latitude/(°)')
            sheet1.write(0, 3, 'Receiver Type')
            sheet1.write(0, 4, 'Antenna Type')
            for i in range(len(checked_text)):
                for j in range(len(checked_text[0])):
                    sheet1.write(i + 1, j, checked_text[i][j])
            workbook.save(saveInformationPath)
            pass

    def Update_ionfo(self):
        whether_update = QMessageBox.question(self, 'Tips',
                                              'Update station-info? ',
                                              QMessageBox.Yes | QMessageBox.No)
        if whether_update == QMessageBox.Yes:
            all_table_list = []
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount() - 1):
                    temp_list.append(self.main_table.item(r, c + 1).text())
                all_table_list.append(temp_list)
            with open(str(curdir) + r'/slib/json/NGS_Info.json', 'w', encoding='utf-8') as f:
                json.dump(all_table_list, f, ensure_ascii=False)
            try:
                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios.json', 'r'))
                for one_add_info_list in station_xyz_list:
                    if one_add_info_list[0] != '':
                        json_text[0].insert(0, one_add_info_list[0])
                with open(str(curdir) + r'/slib/json/CORS_Statios.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
                add_coord_list = []
                for one_add_coord_list in station_xyz_list:
                    if one_add_coord_list[0] != '' and one_add_coord_list[3] != []:
                        add_coord_list.append(
                            [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                python_json_html(str(curdir) + r'/static/USACORS.json', add_coord_list)

                json_text = json.load(open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'r'))
                json_text[0].insert(0, [one_add_coord_list[0], one_add_coord_list[3][0], one_add_coord_list[3][1]])
                with open(str(curdir) + r'/slib/json/CORS_Statios_BaiDu_Coordinate.json', 'w', encoding='utf-8') as f:
                    json.dump(json_text, f, ensure_ascii=False)
            except:
                pass
            print('Update!')

    def showMessage(self):
        for r in range(self.main_table.rowCount()):
            for c in range(self.main_table.columnCount()):
                if c != 0:
                    self.main_table.item(r, c).setBackground(QBrush(QColor(255, 255, 255)))

        wen_Text = self.searchLab.text()
        wen_list = wen_Text.split(':')
        print(wen_list)
        for wen in reversed(wen_list):
            if len(wen) == 4:
                wen = wen.upper()
            items = self.main_table.findItems(wen, Qt.MatchExactly)

            if items:
                temp_text_list = []
                temp_color_list = []
                for i in items:
                    i = i.row()
                    lie_text_list = []
                    lie_color_list = []
                    for j in range(5):
                        select_text = self.main_table.item(i, j + 1).text()
                        select_color = self.main_table.item(i, j + 1).background()
                        lie_text_list.append(select_text)
                        lie_color_list.append(select_color)
                    self.main_table.removeRow(i)
                    all_header_combobox.remove(all_header_combobox[i])
                    temp_text_list = temp_text_list + [lie_text_list]
                    temp_color_list = temp_color_list + [lie_color_list]

                # Insert the information of the search target in the first line
                # print(temp_text_list)
                for i, m in zip(reversed(temp_text_list), reversed(temp_color_list)):
                    self.main_table.insertRow(0)
                    # Set checkbox function
                    checkbox_son = QCheckBox()
                    all_header_combobox.insert(0, checkbox_son)
                    self.main_table.setCellWidget(0, 0, checkbox_son)
                    for j in range(5):
                        newItem = QTableWidgetItem(i[j])
                        newItem.setBackground(m[j])
                        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.main_table.setItem(0, j + 1, newItem)

                items = self.main_table.findItems(wen, Qt.MatchExactly)

                # Secondary search, highlight
                # Scroll to the selected table and highlight it
                print(items[0].row())
                if len(items) > 0:
                    for item in items:
                        item.setBackground(QBrush(QColor(0, 255, 0)))
                self.main_table.verticalScrollBar().setSliderPosition(0)
            # else:
            #     QMessageBox.information(self, 'Hint', 'What you are looking for is not in the table !')


class Add_Other_Info_Windows01(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/2), int((screen.height() - size.height() - 60)/2))
        # self.setGeometry(420 / 1920 * win_width, 350 / 1080 * win_height, 1142 / 1920 * win_width, 210 / 1080 * win_height)
        self.resize(720*win_height/1080, 300*win_height/1080)
        self.setup_ui()

    # emit windows close singal
    Add_Info_Close_Signal = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.Add_Info_Close_Signal.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.sure_btn = QPushButton('Sure', self)
        # self.sure_btn.setGeometry(0, 175 / 1080 * win_height, 1141 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.sure_btn)
        self.sure_btn.setMinimumWidth(20)
        self.sure_btn.setMinimumHeight(20)
        self.sure_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.sure_btn.clicked.connect(self.sure_btn_link)

        input_none_text_list = [['', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', ''],
                                ['', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', ''],
                                ['', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', ''],
                                ['', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', ''],
                                ['', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '']]
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(9)
        self.main_table.setRowCount(len(input_none_text_list))
        # self.main_table.setGeometry(0, 0, 1142 / 1920 * win_width, 175 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set column width
        # self.main_table.setColumnWidth(0, 130 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(4, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(5, 200 / 1920 * win_width)
        # self.main_table.setColumnWidth(6, 400 / 1920 * win_width)
        # self.main_table.setColumnWidth(7, 280 / 1920 * win_width)
        # self.main_table.setColumnWidth(8, 280 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self.main_table.setHorizontalHeaderLabels(['Station', 'Nation', 'Area', 'Institution', 'Start Time',
                                                   'End Time', 'APPROX POSITION X/Y/Z (WGS 84)', 'Receiver Type',
                                                   'Antenna Type'])
        for i, line_text in zip(range(len(input_none_text_list)), input_none_text_list):
            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout)
        vlayout.addLayout(layout0)
        self.setLayout(vlayout)

    def sure_btn_link(self):
        all_add_table_list = []
        try:
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount()):
                    temp_list.append(self.main_table.item(r, c).text())
                all_add_table_list.append(temp_list)
        except:
            pass
        # print(all_add_table_list)
        effective_input_list = []
        for i in all_add_table_list:
            if i == ['', '', '', '', '', '', '', '', '']:
                break
            effective_input_list.append(i)
        # print('effective_input_list', effective_input_list)
        global station_xyz_list
        station_xyz_list = []
        try:
            for single_list in effective_input_list:
                extract_xyz = re.findall('\-?\d+\.?\d*', single_list[6])
                BLH_list = XYZ_to_BLH(float(extract_xyz[0]), float(extract_xyz[1]), float(extract_xyz[2]))
                BD09_list = BLH_to_BD09(float(BLH_list[0]), float(BLH_list[1]), float(BLH_list[2]))
                station_xyz_list.append([single_list[0], single_list[1], single_list[2], single_list[3], single_list[4],
                                         single_list[5], extract_xyz, BLH_list, BD09_list, single_list[7],
                                         single_list[8]])
        except:
            pass
        print(station_xyz_list)
        self.close()


class Add_Other_Info_Windows02(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        # self.setGeometry(420 / 1920 * win_width, 350 / 1080 * win_height, 1142 / 1920 * win_width, 210 / 1080 * win_height)
        self.resize(720*win_height/1080, 300*win_height/1080)
        self.setup_ui()

    # emit windows close singal
    Add_Info_Close_Signal = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.Add_Info_Close_Signal.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.sure_btn = QPushButton('Sure', self)
        # self.sure_btn.setGeometry(0, 175 / 1080 * win_height, 1141 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.sure_btn)
        self.sure_btn.setMinimumWidth(20)
        self.sure_btn.setMinimumHeight(20)
        self.sure_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.sure_btn.clicked.connect(self.sure_btn_link)

        input_none_text_list = [['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''],
                                ['', '', '', ''],
                                ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''],
                                ['', '', '', ''],
                                ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''],
                                ['', '', '', ''],
                                ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''],
                                ['', '', '', '']]
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(4)
        self.main_table.setRowCount(len(input_none_text_list))
        # self.main_table.setGeometry(0, 0, 1142 / 1920 * win_width, 175 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set column width
        # self.main_table.setColumnWidth(0, 130 / 1920 * win_width)
        # self.main_table.setColumnWidth(1, 400 / 1920 * win_width)
        # self.main_table.setColumnWidth(2, 280 / 1920 * win_width)
        # self.main_table.setColumnWidth(3, 280 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self.main_table.setHorizontalHeaderLabels(
            ['Station', 'APPROX POSITION X/Y/Z (WGS 84)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(input_none_text_list)), input_none_text_list):
            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j, newItem)
                pass
        layout.addWidget(self.main_table)

    def sure_btn_link(self):
        all_add_table_list = []
        try:
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount()):
                    temp_list.append(self.main_table.item(r, c).text())
                all_add_table_list.append(temp_list)
        except:
            pass
        # print(all_add_table_list)
        effective_input_list = []
        for i in all_add_table_list:
            if i == ['', '', '', '']:
                break
            effective_input_list.append(i)
        # print('effective_input_list', effective_input_list)
        global station_xyz_list
        station_xyz_list = []
        try:
            for single_list in effective_input_list:
                extract_xyz = re.findall('\-?\d+\.?\d*', single_list[1])
                BLH_list = XYZ_to_BLH(float(extract_xyz[0]), float(extract_xyz[1]), float(extract_xyz[2]))
                BD09_list = BLH_to_BD09(float(BLH_list[0]), float(BLH_list[1]), float(BLH_list[2]))
                station_xyz_list.append(
                    [single_list[0], extract_xyz, BLH_list, BD09_list, single_list[2], single_list[3]])
        except:
            pass
        print(station_xyz_list)
        self.close()

class Add_Other_Info_Windows03(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add")
        self.setWindowIcon(QIcon(str(curdir) + r'/slib/logo/GDDS logo.ico'))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        # self.setGeometry(420 / 1920 * win_width, 350 / 1080 * win_height, 1142 / 1920 * win_width, 210 / 1080 * win_height)
        self.resize(720*win_height/1080, 300*win_height/1080)
        self.setup_ui()

    # emit windows close singal
    Add_Info_Close_Signal = pyqtSignal(str)

    def sendEditContent(self):
        content = '1'
        self.Add_Info_Close_Signal.emit(content)

    def closeEvent(self, event):
        self.sendEditContent()

    def setup_ui(self):
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()

        vlayout = QVBoxLayout()
        layout0 = QHBoxLayout()

        self.sure_btn = QPushButton('Sure', self)
        # self.sure_btn.setGeometry(0, 175 / 1080 * win_height, 1141 / 1920 * win_width, 35 / 1080 * win_height)
        layout0.addWidget(self.sure_btn)
        self.sure_btn.setMinimumWidth(20)
        self.sure_btn.setMinimumHeight(20)
        self.sure_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.sure_btn.clicked.connect(self.sure_btn_link)

        input_none_text_list = [['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']]
        layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(5)
        self.main_table.setRowCount(len(input_none_text_list))
        # self.main_table.setGeometry(0, 0, 1142 / 1920 * win_width, 175 / 1080 * win_height)

        # Select the entire row of the table
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set column width
        # self.main_table.setColumnWidth(0, 110 / 1920 * win_width)
        #         # self.main_table.setColumnWidth(1, 100 / 1920 * win_width)
        #         # self.main_table.setColumnWidth(2, 360 / 1920 * win_width)
        #         # self.main_table.setColumnWidth(3, 260 / 1920 * win_width)
        #         # self.main_table.setColumnWidth(4, 260 / 1920 * win_width)

        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self.main_table.setHorizontalHeaderLabels(
            ['Station', 'Location', 'APPROX POSITION X/Y/Z (WGS 84)', 'Receiver Type', 'Antenna Type'])
        for i, line_text in zip(range(len(input_none_text_list)), input_none_text_list):
            for j in range(len(line_text)):
                newItem = QTableWidgetItem(line_text[j])
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.main_table.setItem(i, j, newItem)
                pass
        layout.addWidget(self.main_table)

        vlayout.addLayout(layout)
        vlayout.addLayout(layout0)
        self.setLayout(vlayout)

    def sure_btn_link(self):
        all_add_table_list = []
        try:
            for r in range(self.main_table.rowCount()):
                temp_list = []
                for c in range(self.main_table.columnCount()):
                    temp_list.append(self.main_table.item(r, c).text())
                all_add_table_list.append(temp_list)
        except:
            pass
        # print(all_add_table_list)
        effective_input_list = []
        for i in all_add_table_list:
            if i == ['', '', '', '', '']:
                break
            effective_input_list.append(i)
        # print('effective_input_list', effective_input_list)
        global station_xyz_list
        station_xyz_list = []
        try:
            for single_list in effective_input_list:
                extract_xyz = re.findall('\-?\d+\.?\d*', single_list[2])
                BLH_list = XYZ_to_BLH(float(extract_xyz[0]), float(extract_xyz[1]), float(extract_xyz[2]))
                BD09_list = BLH_to_BD09(float(BLH_list[0]), float(BLH_list[1]), float(BLH_list[2]))
                station_xyz_list.append(
                    [single_list[0], single_list[1], extract_xyz, BLH_list, BD09_list, single_list[3], single_list[4]])
        except:
            pass
        print(station_xyz_list)
        self.close()


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
    # else:
    #     font.setPointSize(pointsize - 3)
    font.setFamily("Times New Roman")
    app.setFont(font)
    win = IGS_Station_Info_Table()
    win.show()
    sys.exit(app.exec_())