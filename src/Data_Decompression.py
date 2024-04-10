import os
import gzip
import unlzw3
from pathlib import Path
import subprocess
from station_info_table import *
import platform
import global_var
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QProgressDialog
global curdir
curdir = os.getcwd()

'''
-----------------------------------------------------------------------------------------------------------------------
Function: Unzip the GNSS data file
Principle: 1. Determine whether the selected file contains compressed files with gz and Z as suffixes, and decompress them if so
2. Determine whether the selected file contains a CRINEX compressed file, and decompress it if soe is a jump of the interface. Only after the program execution completes the jump of the interface can valid cookie information be generated)
   ——>Loop total URL list - > execute URL web address - > write file (multithreading)
-----------------------------------------------------------------------------------------------------------------------
'''

# -------------------------------------------------------------------------------------------------
""" file decompression """
def file_decompression(self):
    desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
    desktop_path = desktop_path.replace("\\", "/")
    unzip_default_download_path = desktop_path + '/Download'
    if os.path.exists(unzip_default_download_path):
        zip_complute_route, unused_suffix = QFileDialog.getOpenFileNames(self, 'Select Unzip Files', unzip_default_download_path, 'All(*.*);;Zip(*.Z *.gz);;CRINEX(*.*d *.crx)')
    else:
        zip_complute_route, unused_suffix = QFileDialog.getOpenFileNames(self, 'Select Unzip Files', desktop_path, 'All(*.*);;Zip(*.Z *.gz);;CRINEX(*.*d *.crx)')
    # -------------------------------------------------------------------------------------------------
    # file path
    if zip_complute_route != []:
        zip_file_route = zip_complute_route[0].rsplit("/", 1)[0]
        global_var.set_value('zip_file_route', zip_file_route)
        #  Select the file
        all_chose_file_name_list = []
        for i in zip_complute_route:
            all_chose_file_name = i.split("/")[-1]
            all_chose_file_name_list = all_chose_file_name_list + [all_chose_file_name]
            pass
        # -------------------------------------------------------------------------------------------------
        # Popup progress bar
        unzip_process_all_num = len(all_chose_file_name_list) * 2
        progress = QProgressDialog(self)
        progress.setWindowTitle("Decompression")
        progress.setLabelText("decompressing...")
        progress.setCancelButtonText("Cancel")
        progress.setMinimumDuration(4)
        progress.setWindowModality(Qt.WindowModal)
        progress.setRange(0, unzip_process_all_num)
        unzip_process_step = 0
        # -------------------------------------------------------------------------------------------------
        #  file classification
        gz_file_list = []
        Z_file_list = []
        for file_name in all_chose_file_name_list:
            suffix = file_name.split('.')[-1]
            if suffix == 'gz':
                gz_file_list = gz_file_list + [file_name]
            elif suffix == 'Z':
                Z_file_list = Z_file_list + [file_name]
            if progress.wasCanceled():
                QMessageBox.warning(self, 'Tips', "Cancel decompression !")
                return
        # -------------------------------------------------------------------------------------------------
        #  File decompression
        for gz_file in gz_file_list:
            try:
                gz_file_path = zip_file_route + '/' + gz_file
                unzip_gz_file_name = gz_file_path.replace(".gz", "")
                unzip_gz_file_name_name = gz_file.replace(".gz", "")
                all_chose_file_name_list = all_chose_file_name_list + [unzip_gz_file_name_name]
                unzip_gz_text = gzip.GzipFile(gz_file_path)
                open(unzip_gz_file_name, "wb+").write(unzip_gz_text.read())
                unzip_gz_text.close()
                os.remove(gz_file_path)
                unzip_process_step += 1
                progress.setValue(unzip_process_step)
                if progress.wasCanceled():
                    QMessageBox.warning(self, 'Tips', "Cancel decompression !")
                    return
                QApplication.processEvents()
                pass
            except:
                progress.close()
                QMessageBox.information(self, 'Error', "Decompression failed !")
                return
        # -------------------------------------------------------------------------------------------------
        for Z_file in Z_file_list:
            try:
                Z_file_path = zip_file_route + '/' + Z_file
                unzip_Z_file_name = Z_file_path.replace(".Z", "")
                unzip_Z_file_name_name = Z_file.replace(".Z", "")
                all_chose_file_name_list = all_chose_file_name_list + [unzip_Z_file_name_name]
                unzip_Z_text = unlzw3.unlzw(Path(Z_file_path))
                with open(unzip_Z_file_name, 'wb+') as new_file:
                    new_file.write(unzip_Z_text)
                os.remove(Z_file_path)
                unzip_process_step += 1
                progress.setValue(unzip_process_step)
                if progress.wasCanceled():
                    QMessageBox.warning(self, 'Tips', "Cancel decompression !")
                    return
                QApplication.processEvents()
            except:
                Z_file_path = zip_file_route + '/' + Z_file
                unzip_Z_file_name = Z_file_path.replace(".Z", "")
                unzip_Z_text = gzip.GzipFile(Z_file_path)
                open(unzip_Z_file_name, "wb+").write(unzip_Z_text.read())
                unzip_Z_text.close()
                os.remove(Z_file_path)
                unzip_process_step += 1
                progress.setValue(unzip_process_step)
                if progress.wasCanceled():
                    QMessageBox.warning(self, 'Tips', "Cancel decompression !")
                    return
                QApplication.processEvents()
        # -------------------------------------------------------------------------------------------------
        single_all_chose_file_name_list = []
        for i in all_chose_file_name_list:
            if i not in single_all_chose_file_name_list:
                single_all_chose_file_name_list.append(i)
        d_file_list = []
        for file_name in single_all_chose_file_name_list:
            suffix = file_name.split('.')[-1]
            if suffix == 'crx':
                d_file_list = d_file_list + [file_name]
            else:
                if suffix[-1] == 'd':
                    d_file_list = d_file_list + [file_name]
        # -------------------------------------------------------------------------------------------------
        # crinex to rinex
        if d_file_list:
            if platform.system() == 'Linux':
                shutil.copy(str(curdir) + r'/slib/third party/Linux/crx2rnx', zip_file_route + '/' + 'crx2rnx')
            elif platform.system() == 'Windows':
                shutil.copy(str(curdir) + r'/slib/third party/Win/crx2rnx.exe', zip_file_route + '/' + 'crx2rnx.exe')
            os.chdir(zip_file_route)
            for i in d_file_list:
                if platform.system() == 'Linux':
                    cmd_input_code = './crx2rnx -f ' + i
                    subprocess.run('chmod +x crx2rnx', shell=True)
                elif platform.system() == 'Windows':
                    cmd_input_code = 'crx2rnx.exe -f ' + i
                completed = subprocess.run(cmd_input_code, shell=True)
                # print('state', completed.returncode)
                os.remove(i)
                unzip_process_step += 1
                progress.setValue(unzip_process_step)
                QApplication.processEvents()
                if progress.wasCanceled():
                    QMessageBox.warning(self, 'Tips', "Cancel decompression !")
                    return
            if platform.system() == 'Linux':
                os.remove('./crx2rnx')
            elif platform.system() == 'Windows':
                os.remove('crx2rnx.exe')
        progress.setValue(unzip_process_all_num)
        QMessageBox.information(self, 'Tips', "Decompression completed !")