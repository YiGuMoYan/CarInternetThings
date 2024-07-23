from threading import Thread

import serial
import time

from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QMessageBox, QApplication

# 打开串口
# ser = serial.Serial('/dev/ttyUSB0', 115200)  # 请根据实际情况修改串口号和波特率
ser = serial.Serial('COM7', 115200)  # 请根据实际情况修改串口号和波特率
# 用于存储最近接收到的运动参数的列表
recent_motion_params = []
tmp_motion_params = []
recent_heart_params = []
recent_aveheart_params = []

ap = QApplication([])

def show_message(text, title):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.NoButton)

    # QTimer to close the message box after 2 seconds
    QTimer.singleShot(2000, msg.close)

    msg.exec_()

def serial_main():
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            hex_num = data.strip().hex()[4:-6]
            control_code = hex_num[:2]
            command_code = hex_num[2:4]
            len_code = hex_num[4:8]
            data_code = hex_num[8:]
            if control_code == "80":
                if command_code == "01":
                    if data_code == "01":
                        print("人体存在")
                    elif data_code == "00":
                        print("人体不存在")
                elif command_code == "02":
                    if data_code == "01":
                        print("运动信息:静止")
                    elif data_code == "02":
                        print("运动信息:活跃")
                elif command_code == "03":
                    motion_param = int(data_code, 16)
                    print("运动参数:", motion_param)
                    # 将新的运动参数添加到列表中，并限制列表长度为3
                    recent_motion_params.append(motion_param)
                    tmp_motion_params.append(motion_param)
                    if len(tmp_motion_params) > 3:
                        tmp_motion_params.pop(0)
                        # 检查列表中是否有三个连续的值大于50
                        if all(param > 50 for param in tmp_motion_params):
                            print("请问您是否需要帮助")
                            # QTimer.singleShot(0, show_message)
                            # show_message("请问您是否需要帮助", "询问")
                            # show_message("请问您是否需要帮助", "询问")
                            QCoreApplication.postEvent(app, lambda: show_message("请问您是否需要帮助", "询问"))
                elif command_code == "04":
                    print("人体距离(单位：cm):", int(data_code, 16))
                elif command_code == "05":
                    print("运动方位(单位：cm):", 'x方向:', int(data.strip().hex()[14:16], 16), 'y方向:',
                          int(data.strip().hex()[18:20], 16), 'z方向:', int(data.strip().hex()[22:24], 16))
            if control_code == "81":
                if command_code == "01":
                    if data_code == "01":
                        print("呼吸正常")
                    elif data_code == "02":
                        print("呼吸过高")
                    elif data_code == "03":
                        print("呼吸过低")
                    elif data_code == "04":
                        print("没有呼吸")
                elif command_code == "02":
                    print("呼吸数值为(次/分):", int(data_code, 16))
            if control_code == "85":
                if command_code == "02":
                    heart_param = int(data_code, 16)
                    recent_heart_params.append(heart_param)
                    total = sum(recent_heart_params)
                    count = len(recent_heart_params)
                    if count > 0:
                        average = total / count
                        recent_aveheart_params.append(int(average))
                        print("心率平均值为", int(average))
                        if len(recent_aveheart_params) > 60:
                            recent_aveheart_params.pop(0)
                            if all(param < 65 for param in recent_aveheart_params):
                                print("请注意不要疲劳驾驶，您的心率平均值已超标")
                    if int(data_code, 16) > 110:
                        print("心率数值为(次/分):", int(data_code, 16), "心率过快")
                    elif 60 <= int(data_code, 16) <= 110:
                        print("心率数值为(次/分):", int(data_code, 16), "心率正常")
                    elif int(data_code, 16) < 60:
                        print("心率数值为(次/分):", int(data_code, 16), "心率过慢")
    # 关闭串口
    ser.close()
