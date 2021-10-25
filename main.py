import sys
import os
import serial
import glob
import requests
from threading import Thread, Event
import string
from ctypes import windll
import websocket
import datetime
import _thread
import time


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QComboBox, QRadioButton, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

port_name = ""
disk_name = ""
ex = None
ws = None
th = None

class StoppableThread(Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  target_):
        super(StoppableThread, self).__init__(target=target_)
        self._stop_event = Event()

    def starting(self):
        self.start()

    def stop(self):
        print("stop")
        self._stop_event.set()

    def stopped(self):
        print("stoped")
        return self._stop_event.is_set()

def serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Samsung IoT'
        self.left = 600
        self.top = 400
        self.width = 320
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # self.comboBox = QComboBox(self)
        # self.comboBox.addItems(["COM666"])
        # self.comboBox.activated.connect(self.handleActivated)
        self.radio = QRadioButton(self)

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setText("Empty")

        self.comboBox2 = QComboBox(self)
        self.comboBox2.addItems(['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)][::-1])
        self.comboBox2.activated.connect(self.handleActivated2)

        self.text = QLabel(self)
        self.text.setText(['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)][-1])
        self.text.move(100, 50)

        global disk_name
        disk_name = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)][-1]

        button = QPushButton('Refresh', self)
        button.setToolTip('This is an example button')
        button.move(100, 70)
        button.clicked.connect(self.on_click)

        button1 = QPushButton("Reconect", self)
        button1.clicked.connect(self.on_click_update)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.label)
        lay.addWidget(self.text)
        # lay.addWidget(self.comboBox)
        lay.addWidget(self.comboBox2)
        lay.addWidget(button)
        lay.addWidget(self.radio)
        lay.addWidget(button1)
        lay.addStretch()

        self.show()

    @pyqtSlot()
    def on_click(self):
        # self.comboBox.clear()
        self.comboBox2.clear()
        # self.comboBox.addItems(serial_ports())
        self.comboBox2.addItems(['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)][::-1])
        print('PyQt5 button click')

    @pyqtSlot()
    def on_click_update(self):
        print("")
        global th
        th.stop()
        th.stopped()

    def handleActivated(self, index):
        global port_name
        # port_name = self.comboBox.itemText(index)
        # self.text.setText(self.comboBox.itemText(index))
        # print(self.comboBox.itemText(index))

    def handleActivated2(self, index):
        global disk_name
        disk_name = self.comboBox2.itemText(index)
        self.text.setText(self.comboBox2.itemText(index))
        print(self.comboBox2.itemText(index))

    def changeText(self, text):
        self.label.setText(text)

    def changeState(self, boo):
        if boo:
            self.radio.setChecked(True)
            self.radio.setText("Подключение активно")
        else:
            self.radio.setChecked(False)
            self.radio.setText("Подключение разорвано")

    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        ws.close()
        event.accept()

def on_message(ws, message):
    print(message)
    global disk_name
    if message == "getFile":
        myfile = requests.get("https://levandrovskiy.ru/iot/getFile")
        print(myfile.headers)
        try:
            name = myfile.headers["content-disposition"].split("filename=")[1].split("\"")[1]
            print(name)
            open(f'{disk_name}/{name}', 'wb').write(myfile.content)
            ws.send("Ready")
            ex.changeText(datetime.datetime.today().strftime("%H:%M:%S") + " - "+name)
        except Exception as e:
            print("Error:",e)
            ex.changeText(datetime.datetime.today().strftime("%H:%M:%S") +" - " + myfile.headers["content-disposition"])
            open(f'{disk_name}/stm32code.bin', 'wb').write(myfile.content)
            ws.send("Ready")


def on_error(ws, error):
    ex.changeState(False)
    print("Error", error)

def on_close(ws, close_status_code, close_msg):
    ex.changeState(False)
    print("### closed ###")

def on_open(ws):
    ex.changeState(True)
    ws.send("Hello")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://levandrovskiy.ru/iot/ws",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    th = StoppableThread(ws.run_forever)
    th.starting()


    sys.exit(app.exec_())