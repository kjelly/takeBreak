#! /usr/bin/env python
import sys
from subprocess import check_output

from PySide.QtCore import *
from PySide.QtGui import *


def get_user_idle_time():
    output = check_output("xprintidle", shell=True)
    return int(output, 10)


class Timeout(object):
    def __init__(self, max_busy_time=10, break_time=10,
                 idle_callback=None, break_callback=None):
        self.max_busy_time = max_busy_time
        self.break_time = break_time
        self.idle_callback = idle_callback
        self.break_callback = break_callback

        self.busy = 0

    def __call__(self, idle_time):
        if idle_time < 1000:
            self.busy += 1

        if self.busy > self.max_busy_time:
            if self.break_callback:
                self.break_callback(self.busy)

        if idle_time > self.break_time * 1000:
            if self.idle_callback:
                self.idle_callback(self.busy)
            self.busy = 0


class Timer(QObject):
    def __init__(self):
        self.func_list = []

    def add_func(self, func):
        self.func_list.append(func)

    def action(self):
        idle_time = get_user_idle_time()
        for func in self.func_list:
            func(idle_time)

    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.action)
        self.timer.start(1000)


class Logger(object):
    def __init__(self, name='data.txt'):
        import os.path
        if os.path.exists(name):
            self.ftr = open(name, 'a')
        else:
            self.ftr = open(name, 'w')

    def write(self, data):
        self.ftr.write(str(data) + '\n')
        self.ftr.flush()


class App(object):
    def __init__(self):
        # Create a Qt application
        self.app = QApplication(sys.argv)
        self.tray_icon = 'green'

        icon = QIcon("green-led.png")
        menu = QMenu()
        exitAction = menu.addAction("exit")
        exitAction.triggered.connect(sys.exit)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setContextMenu(menu)
        self.tray.show()

        self.timer = Timer()
        self.timer.add_func(Timeout(3 * 60, 30,
                             self.idle_callback, self.short_break_callback))
        self.timer.add_func(Timeout(30 * 60, 5 * 60,
                             self.idle_callback, self.long_break_callback))
        self.timer.start()

        self.logger = Logger()

    def short_break_callback(self, busy=None):
        self.set_red_led()

    def long_break_callback(self, busy=None):
        self.set_red_cross()

    def idle_callback(self, idle=None):
        if self.tray_icon != 'green':
            self.tray.showMessage("busy",
                                  str(idle), millisecondsTimeoutHint=5000)
            self.logger.write(idle)
            self.set_green_led()

    def set_green_led(self):
        icon = QIcon("green-led.png")
        self.tray.setIcon(icon)
        self.tray_icon = 'green'

    def set_red_led(self):
        if self.tray_icon == 'green':
            icon = QIcon("red-led.png")
            self.tray.setIcon(icon)
            self.tray_icon = 'red'

    def set_red_cross(self):
        icon = QIcon("red-cross.png")
        self.tray.setIcon(icon)
        self.tray_icon = 'red-cross'

    def run(self):
        # Enter Qt application main loop
        self.app.exec_()
        sys.exit()

    def setting(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Setting Dialog")
        self.dialog.show()

if __name__ == "__main__":
    app = App()
    app.run()
