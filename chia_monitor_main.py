# 农田数量监控
import sys

from requests.adapters import HTTPAdapter

import chia_monitor_ui
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *

# 从PyQt库导入QtWidget通用窗口类,基本的窗口集在PyQt5.QtWidgets模块里.
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QAction, QMenu, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt

from playsound import playsound

from PyQt5.QtCore import QThread, pyqtSignal

import json
import time
import os
import requests


class My_Gui(chia_monitor_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()

        # Custom output stream.

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        splitter = QSplitter(Qt.Horizontal)
        # self.splitter.setMinimumHeight(800)
        # self.tableWidget_2.setMinimumHeight(200)
        splitter.addWidget(self.widget)
        splitter.addWidget(self.widget_2)
        self.gridLayout_2.addWidget(splitter)

        font_0 = QtGui.QFont()
        font_0.setFamily("微软雅黑")
        font_0.setPointSize(9)
        self.textBrowser.setFont(font_0)


def signal_accept_ping(i):
    print(i)
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    MainWindow.setStatusTip("%s 掉线！！！ %s" % (i, str(t)))
    MainWindow.show()


class ping_Thread(QThread):
    _signal = pyqtSignal(str)  # 定义信号类型为整型

    def __init__(self):
        super(ping_Thread, self).__init__()
        self.run_flg = False

    def run(self):
        while True:
            if self.run_flg:
                config_path = 'prometheus.yml'
                f = open(config_path, 'r', encoding='utf-8')
                conf = yaml.safe_load(f)
                for k in range(0, len(conf['scrape_configs'][1]['static_configs'])):
                    ip = (conf['scrape_configs'][1]['static_configs'][k]['targets'][0])
                    name = (conf['scrape_configs'][1]['static_configs'][k]['labels']['host'])
                    print(name)
                    i = str(ip).find(':')
                    ip = ip[0:i]
                    s = run_cmd('ping %s -n 1' % (ip))
                    i = s.find('ms')
                    if i == -1:
                        self._signal.emit(str(name))  # 发射信号
                        try:
                            playsound('g1.mp3')
                        finally:
                            pass
                    else:
                        print('链接成功')
            time.sleep(60)


def signal_accept(i):
    print(i)
    global ini_dict
    global file_dict
    global mydict
    if (i in mydict) and (mydict[i].isdigit()):
        if (i in file_dict) and (file_dict[i].isdigit()):
            if int(mydict[i]) > int(file_dict[i]):
                file_dict[i] = mydict[i]
                FindLb = ui.centralwidget.findChild(QtWidgets.QLabel, 'num_%s' % (i))
                FindLb.setText(mydict[i])
                del FindLb
                FindLb_name = ui.centralwidget.findChild(QtWidgets.QLabel, 'user_%s' % (i))
                FindLb_name.setText(i)
                del FindLb_name
            FindLE = ui.centralwidget.findChild(QtWidgets.QProgressBar, 'p_%s' % (i))
            print(FindLE.value())
            FindLE.setRange(0, int(file_dict[i]))

            FindLE.setValue(int(mydict[i]))  # 将线程的参数传入进度条
            FindLE.setFormat(mydict[i])
            del FindLE
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        s = "%s 变化 %s-->%s   %s" % (i, ini_dict[i], mydict[i], str(t))
        # MainWindow.setStatusTip(s)
        # ui.textBrowser.append(s)

        ini_dict[i] = mydict[i]
    else:
        FindLE = ui.centralwidget.findChild(QtWidgets.QProgressBar, 'p_%s' % (i))
        FindLE.setValue(0)  # 将线程的参数传入进度条
        FindLE.setFormat('0 掉线')
        del FindLE

        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        s = "%s 掉线！！！ %s" % (i, str(t))
        # MainWindow.setStatusTip(s)
        # ui.textBrowser.append(s)
        ini_dict[i] = '掉线 0'

    MainWindow.setStatusTip(s)
    ui.textBrowser.append(s)
    f =open("log.txt","a+")
    f.write("%s \n"%s)
    f.close()
    MainWindow.showNormal()
    # MainWindow.show()


class myThread(QThread):
    _signal = pyqtSignal(str)  # 定义信号类型为整型

    def __init__(self):
        super(myThread, self).__init__()
        self.run_flg = False

    def run(self):
        global ini_dict
        try:
            if os.path.exists('start.mp3'):
                playsound('start.mp3')
        finally:
            pass
        while True:
            time.sleep(3)
            if self.run_flg:
                # print('ok')
                Html_message()
                # print(ini_dict)
                for i in ini_dict:
                    try:
                        if i in mydict:
                            if (mydict[i] != ini_dict[i]) and (mydict[i].isdigit()):
                                print('变化-------%s >%s' % (mydict[i], ini_dict[i]))
                                self._signal.emit(i)  # 发射信号
                                try:
                                    if os.path.exists('g.mp3'):
                                        playsound('g.mp3')
                                finally:
                                    pass

                        else:
                            self._signal.emit(i)  # 发射信号

                            try:
                                if os.path.exists('g1.mp3'):
                                    playsound('g1.mp3')
                                    time.sleep(10)
                            finally:
                                pass
                    finally:
                        pass
                        # print('%s:%s'%(i,mydict[i]))
                # self.run_flg = False


def add_progress():
    global User_name

    # JSON到字典转化
    f2 = open('info.json', 'r')
    progress = json.load(f2)
    f2.close()
    # print(mydict)
    # print(progress)

    wi = []
    horizontalLayout = []
    p = []
    lb_name = []
    lb_num = []
    font = QtGui.QFont()
    font.setFamily("微软雅黑")
    font.setPointSize(12)

    font_0 = QtGui.QFont()
    font_0.setFamily("微软雅黑")
    font_0.setPointSize(9)
    for i in range(0, len(User_name)):
        # print(User_name[i])
        # print(progress[User_name[i]])
        wi.append(User_name[i])
        horizontalLayout.append(User_name[i])
        lb_name.append(User_name[i])
        lb_num.append(User_name[i])
        p.append(User_name[i])

        wi[i] = QtWidgets.QWidget()
        horizontalLayout[i] = QtWidgets.QHBoxLayout(wi[i])

        lb_name[i] = MyLabel(wi[i])
        lb_name[i].setText(User_name[i])
        lb_name[i].setObjectName('user_%s' % (User_name[i]))
        lb_name[i].setFont(font_0)
        horizontalLayout[i].addWidget(lb_name[i])

        p[i] = QtWidgets.QProgressBar(wi[i])
        if int(progress[User_name[i]]) == 0:
            p[i].setRange(0, 100)
            # p[i].setRange(0, int(progress[User_name[i]]))
            p[i].setValue(0)
        else:
            p[i].setRange(0, int(progress[User_name[i]]))
            p[i].setValue(int(mydict[User_name[i]]))
        p[i].setAlignment(Qt.AlignCenter)
        p[i].setFormat(mydict[User_name[i]])
        p[i].setObjectName('p_%s' % (User_name[i]))
        p[i].setFont(font_0)
        # p[i].setAlignment(Qt.AlignTop | Qt.AlignLeft)
        horizontalLayout[i].addWidget(p[i])

        lb_num[i] = QtWidgets.QLabel(wi[i])
        lb_num[i].setText(progress[User_name[i]])
        lb_num[i].setObjectName('num_%s' % (User_name[i]))
        lb_num[i].setFont(font)

        horizontalLayout[i].addWidget(lb_num[i])

        # wi[i].clicked.connect(set_num)
        ui.gridLayout.addWidget(wi[i], int(i / 2), i % 2)


class MyLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(MyLabel, self).__init__(parent)

    def mouseDoubleClickEvent(self, e):
        print(self.text())
        ui.lineEdit_num.setText(self.text())


def set_num():
    ui.lineEdit_num.setText('ok')


def get_message():
    global User_name
    global mydict
    global file_dict

    # JSON到字典转化
    file_dict = {}
    if os.path.isfile("info.json"):
        size = os.path.getsize('info.json')
        # print(size)
        if size != 0:
            with open("info.json", 'r') as f:
                file_dict = json.loads(f.read())
        # print("ok %s"%file_dict)
    if file_dict != {}:
        for i in range(0, len(User_name)):
            if User_name[i] not in file_dict:  # 修改文件最大值
                file_dict[User_name[i]] = mydict[User_name[i]]
            elif int(file_dict[User_name[i]]) < int(mydict[User_name[i]]):
                file_dict[User_name[i]] = mydict[User_name[i]]
        info_json = json.dumps(file_dict, indent=4)
    else:
        info_json = json.dumps(mydict, indent=4)
    f = open('info.json', 'w')
    f.write(info_json)
    f.close()

    add_progress()


def Html_Login():
    global session
    userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"

    header = {
        # "origin": "https://passport.mafengwo.cn",
        "Referer": user_json['postUrl'],
        'User-Agent': userAgent,
    }

    # postUrl = 'http://192.168.77.126:3000/login'
    postUrl = '%slogin' % user_json['postUrl']
    print(postUrl)
    postData = {'user': user_json['user'], 'password': user_json['password']}
    try:
        res = session.post(postUrl, data=postData, headers=header, timeout=5)
        MainWindow.setStatusTip('服务器链接成功！')
        ui.textBrowser.setText('服务器链接成功！')
        print(res.content)
    except:
        print('服务器链接错误！')
        ui.textBrowser.setText('服务器链接出错！')
        MainWindow.setStatusTip('服务器链接出错！')


def Html_message():
    global session
    global User_name
    global mydict
    userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    header = {
        # "origin": "https://passport.mafengwo.cn",
        "Referer": user_json['postUrl'],
        'User-Agent': userAgent,
    }
    postUrl = '%s%s' % (user_json['postUrl'], 'api/datasources/proxy/1/api/v1/query_range')
    postData = {
        'query': 'total_plots',
        'start': int(time.time()),
        'end': int(time.time()),
        'step': '5',
    }
    try:
        res_message = session.post(url=postUrl, data=postData, headers=header, timeout=10)
        s = res_message.content.decode('UTF-8')
        if s != None:
            # JSON到字典转化
            progress = json.loads(s)
            # print(progress)
            if 'data' in progress:
                if 'result' in progress['data']:
                    User_name = []
                    mydict = {}
                    for i in range(0, len(progress['data']['result'])):
                        User_name.append(progress['data']['result'][i]['metric']['host'])
                        mydict[User_name[i]] = progress['data']['result'][i]['values'][0][1]
                    # print(User_name)
            # print(mydict)
    except:
        MainWindow.setStatusTip('服务器弹出！')


def monitor_init():
    global User_name
    global ini_dict
    ini_dict = {}
    Html_Login()
    Html_message()
    for i in User_name:
        ini_dict[i] = mydict[i]
    get_message()
    ui.pushButton.setEnabled(False)


def begin_Thread():
    if thread1.run_flg == False:
        thread1.run_flg = True
        thread1.start()
        # thread2.run_flg = True
        # thread2.start()
        ui.progressBar.setMinimum(0)
        ui.progressBar.setMaximum(0)
        ui.pushButton_2.setText("暂 停")
    else:
        thread1.run_flg = not (thread1.run_flg)
        # thread2.run_flg =not(thread2.run_flg)
        ui.progressBar.setMaximum(1)
        ui.pushButton_2.setText("开始检测")


import subprocess


def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    try:
        # while process.poll() is None:
        #     line = process.stdout.readline()
        #     line = line.strip()
        #     if line:
        #         log = line.decode("936", 'ignore')
        #         print(log)
        log = process.stdout.read().decode("936", 'ignore')
        # print(log)
        return log
    except:
        return 'error'


import yaml


def ping_host():
    config_path = 'prometheus.yml'
    f = open(config_path, 'r', encoding='utf-8')
    conf = yaml.safe_load(f)
    print(conf)
    print(conf['scrape_configs'])
    print(conf['scrape_configs'][1]['static_configs'][0])
    print(conf['scrape_configs'][1]['static_configs'][0]['targets'][0])
    for k in range(0, len(conf['scrape_configs'][1]['static_configs'])):
        ip = (conf['scrape_configs'][1]['static_configs'][k]['targets'][0])
        name = (conf['scrape_configs'][1]['static_configs'][k]['labels']['host'])
        print(name)
        i = str(ip).find(':')
        ip = ip[0:i]
        s = run_cmd('ping %s' % (ip))
        i = s.find('丢失')
        if i != -1:
            if os.path.exists('g1.mp3'):
                playsound('g1.mp3')


def setMax():
    global mydict
    num = ui.lineEdit_num.text()
    max = ui.lineEdit_max.text()
    if (os.path.exists('info.json')) and (max.isdigit()):
        f = open('info.json', 'r')
        my_json = json.load(f)
        f.close()
        print(my_json)
        for i in my_json:
            if (i == num) and (i in mydict):
                my_json[i] = max
                if int(max) >= int(mydict[i]):
                    file_dict[i] = mydict[i]
                    FindLb = ui.centralwidget.findChild(QtWidgets.QLabel, 'num_%s' % (i))
                    FindLb.setText(max)
                    del FindLb
                    FindLb_name = ui.centralwidget.findChild(QtWidgets.QLabel, 'user_%s' % (i))
                    FindLb_name.setText(i)
                    del FindLb_name

                    FindLE = ui.centralwidget.findChild(QtWidgets.QProgressBar, 'p_%s' % (i))
                    print(FindLE.value())
                    FindLE.setRange(0, int(max))
                    FindLE.setValue(int(mydict[i]))  # 将线程的参数传入进度条
                    FindLE.setFormat(mydict[i])
                    del FindLE

                    f = open('info.json', 'w')
                    info_json = json.dumps(my_json, indent=4)
                    f.write(info_json)
                    f.close()
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = My_Gui()
    ui.setupUi(MainWindow)
    MainWindow.show()

    # t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # MainWindow.setStatusTip("%s 变化 %s   %s" % ('a2', '232', str(t)))

    global User_name
    global mydict
    global ini_dict
    global file_dict
    global session

    User_name = []
    mydict = {}
    ini_dict = {}
    file_dict = {}
    session = requests.session()
    session.mount('http://', HTTPAdapter(max_retries=3))  # 设置重试次数为3次
    session.mount('https://', HTTPAdapter(max_retries=3))

    global user_json
    f = open('user.json', 'r')
    user_json = json.load(f)
    print(user_json)

    # Html_Login()
    # Html_message()
    # get_message()

    thread1 = myThread()  # 开启线程
    # thread1.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
    thread1._signal.connect(signal_accept)
    thread1.run_flg = False

    # thread2 = ping_Thread()  # 开启线程
    # # thread1.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
    # thread2._signal.connect(signal_accept_ping)
    # thread2.run_flg = False

    ui.pushButton.clicked.connect(monitor_init)
    ui.pushButton_2.clicked.connect(begin_Thread)
    ui.pushButton_max.clicked.connect(setMax)

    # 关闭所有窗口,也不关闭应用程序
    QApplication.setQuitOnLastWindowClosed(False)

    # 在系统托盘处显示图标
    tp = QSystemTrayIcon()
    tp.setIcon(QIcon('g.ico'))
    # 设置系统托盘图标的菜单
    a1 = QAction('&显示(Show)', triggered=MainWindow.show)


    def quitApp():
        MainWindow.show()  # w.hide() #隐藏
        re = QMessageBox.question(MainWindow, "提示", "退出系统", QMessageBox.Yes |
                                  QMessageBox.No, QMessageBox.No)
        if re == QMessageBox.Yes:
            # 关闭窗体程序
            QCoreApplication.instance().quit()
            # 在应用程序全部关闭后，TrayIcon其实还不会自动消失，
            # 直到你的鼠标移动到上面去后，才会消失，
            # 这是个问题，（如同你terminate一些带TrayIcon的应用程序时出现的状况），
            # 这种问题的解决我是通过在程序退出前将其setVisible(False)来完成的。
            tp.setVisible(False)


    a2 = QAction('&退出(Exit)', triggered=quitApp)  # 直接退出可以用qApp.quit

    tpMenu = QMenu()
    tpMenu.addAction(a1)
    tpMenu.addAction(a2)
    tp.setContextMenu(tpMenu)
    # 不调用show不会显示系统托盘
    tp.show()

    # 信息提示
    # 参数1：标题
    # 参数2：内容
    # 参数3：图标（0没有图标 1信息图标 2警告图标 3错误图标），0还是有一个小图标
    tp.showMessage('农田检测', '农田检测器', icon=0)


    def message():
        print("弹出的信息被点击了")


    tp.messageClicked.connect(message)


    def act(reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 3 or reason == 2:
            # MainWindow.setWindowFlags(Qt.WindowStaysOnTopHint)
            MainWindow.showNormal()
            # MainWindow.show()
        # print("系统托盘的图标被点击了")


    tp.activated.connect(act)

    sys.exit(app.exec_())
