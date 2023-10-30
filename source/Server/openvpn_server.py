import subprocess
import sys
import os
import threading

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton,QLabel,QWidget,QGridLayout,QFileDialog,QDialog,QDialogButtonBox,QVBoxLayout,QScrollArea

# def capture_output(process, label):
#    output = ""
#    for line in process.stdout:
#       output = output + line.decode()
#       label.setText(output)


# class for scrollable label
class ScrollLabel(QScrollArea):
   def __init__(self, *args, **kwargs):
      QScrollArea.__init__(self, *args, **kwargs)

      # making widget resizable
      self.setWidgetResizable(True)

      # making qwidget object
      content = QWidget(self)
      self.setWidget(content)

      # vertical box layout
      lay = QVBoxLayout(content)

      # creating label
      self.label = QLabel(content)

      # setting alignment to the text
      self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

      # making label multi-line
      self.label.setWordWrap(True)

      # adding label to the layout
      lay.addWidget(self.label)

   # the setText method
   def setText(self, text):
      # setting text to the label
      self.label.setText(text)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):


   class CustomDialog(QDialog):
    def __init__(self,title:str,msg:str):
        super().__init__()

        self.setWindowTitle(title)

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(msg)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

   def __init__(self):
      super().__init__()

      self.setWindowTitle("Open VPN Server")

      self.setMinimumSize(QSize(700, 500))
      self.openvpn_config=""
      self.terminal_output=""
      self.openvpn_config_payload=""

      self.button = QPushButton("Start Server")
      self.button.setFixedSize(QSize(100, 30))
      self.button.setCheckable(True)
      self.button.setEnabled(False)
      self.button.clicked.connect(self.the_button_was_toggled)

      self.view_confs_button = QPushButton('View Conf')
      self.view_confs_button.setFixedSize(QSize(100,30))
      self.view_confs_button.setCheckable(True)
      self.view_confs_button.setEnabled(False)
      self.view_confs_button.clicked.connect(self.toggle_view_file)


      self.conf_file_label = QLabel('',alignment=Qt.AlignmentFlag.AlignCenter)
      self.conf_file_label.setFixedSize(QSize(500, 350))

      self.conf_file_label_data = QLabel('',alignment=Qt.AlignmentFlag.AlignCenter)
      self.conf_file_label_data.setFixedSize(QSize(500, 350))
      self.scroll_area = QScrollArea(self.conf_file_label)
      self.scroll_area.setWidgetResizable(True)
      self.scroll_area.setWidget(self.conf_file_label_data)

      self.label = QLabel('Inactive',alignment=Qt.AlignmentFlag.AlignCenter)
      self.label.setFixedSize(QSize(100, 30))

      self.load_conf_file_button = QPushButton('Load Confs')
      self.load_conf_file_button.clicked.connect(self.select_configurations_file)

      self.loaded_conf_path_label_mkp = QLabel('conf file path: ',alignment=Qt.AlignmentFlag.AlignCenter)
      self.loaded_conf_path_label_mkp.setFixedSize(QSize(100, 30))
      self.loaded_conf_path_label = QLabel(self.openvpn_config,alignment=Qt.AlignmentFlag.AlignCenter)
      self.loaded_conf_path_label.setFixedSize(QSize(300, 30))
      # self.vpn_log_label_mkp = QLabel('terminal output: ',alignment=Qt.AlignmentFlag.AlignCenter)
      # self.vpn_log_label = ScrollLabel(self,alignment=Qt.AlignmentFlag.AlignLeft)


      self.mainLayout = QGridLayout()

      self.offsetLabel = QLabel()
      self.mainLayout.addWidget(self.load_conf_file_button,0,0)
      self.mainLayout.addWidget(self.button,0,1)
      self.mainLayout.addWidget(self.label,1,1)
      self.mainLayout.addWidget(self.loaded_conf_path_label,2,1)
      self.mainLayout.addWidget(self.loaded_conf_path_label_mkp,2,0)
      # self.mainLayout.addWidget(self.vpn_log_label_mkp,3,0)
      # self.mainLayout.addWidget(self.vpn_log_label,3,1)
      # self.mainLayout.addWidget(self.view_confs_button,3,0)
      # self.mainLayout.addWidget(self.conf_file_label,4,0)
      self.mainLayout.addWidget(self.offsetLabel,15,15)

      self.container = QWidget()
      self.container.setLayout(self.mainLayout)

      self.setCentralWidget(self.container)


   def the_button_was_toggled(self, checked):
        if checked is True:
            self.label.setText("Starting Server ...")
            # self.vpn_log_label.setText("hello there")
            self.button.setEnabled(False)
            self.start_client()
        else:
            self.label.setText("Stopping Server ...")
            self.button.setEnabled(False)
            self.stop_client()

   def toggle_view_file(self, checked):
        if checked is True:
            self.view_conf_file()
        else:
            self.close_conf_file()





   def start_client(self):
      # self.openvpn_process = subprocess.Popen(["openvpn", "--config", self.openvpn_config],user='root')
      # self.openvpn_process = subprocess.Popen(["/opt/custum_openvpn/sbin/openvpn", "--config", self.openvpn_config],user='root', stdout=subprocess.PIPE)
      self.openvpn_process = subprocess.Popen(["/opt/oqs-vpn/sbin/openvpn", "--config", self.openvpn_config],user='root')
      # threading.Thread(target=capture_output, args=(self.openvpn_process, self.vpn_log_label)).start()
      self.label.setText("Active")
      self.button.setText("Stop Server")
      self.button.setEnabled(True)


   def stop_client(self):

      self.openvpn_process.kill()
      self.openvpn_process.terminate()
      print('Connection closed')
      self.label.setText("Inactive")
      self.button.setText("Start Server")
      self.button.setEnabled(True)

   def select_configurations_file(self):

      file_dialog = QFileDialog(self)
      file_dialog.setWindowTitle('Select conf file')
      file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
      file_dialog.setNameFilter('conf file (*.conf);;')

      if file_dialog.exec():
         selected_file = file_dialog.selectedFiles()[0]
         _,file_ext = os.path.splitext(selected_file)
         if (file_ext=='.conf'):
            with open(selected_file,'+r') as ovpn_file:
              self.openvpn_config_payload=ovpn_file.read()
            self.openvpn_config=selected_file
            self.loaded_conf_path_label.setText(selected_file)
            self.button.setEnabled(True)
            self.view_confs_button.setEnabled(True)
         else:
            select_file_error_dialogue = self.CustomDialog(title='Incorrect file type',msg='Select the proper File type')

   def view_conf_file(self):
      self.conf_file_label_data.setText(self.openvpn_config_payload)

   def close_conf_file(self):
      self.conf_file_label_data.setText('')

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
