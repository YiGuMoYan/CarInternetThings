import os
import sys
import random
from queue import Queue
from threading import Thread

import cv2
import serial
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QTimer, QSize, QCoreApplication, QObject, QMetaObject, Q_ARG, \
    pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QLabel, QPushButton, \
    QGridLayout, QMessageBox
from CarLaneDetection.src.lane_detection import LaneDetection, lane
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from coco import real_time_inference

# 用于存储最近接收到的运动参数的列表
recent_motion_params = []
tmp_motion_params = []
recent_heart_params = []
recent_aveheart_params = []
recent_breath_params = []

styleSheet = """
QPushButton {
    border: none;
    background-color: #e0e0e0;
    color: #333333;
    font-size: 16px;
    padding: 10px;
    border-radius: 5px;
}

QPushButton:hover {
    background-color: #d0d0d0;
}

QPushButton:pressed {
    background-color: #c0c0c0;
}

QLabel {
    color: #333333;
    font-size: 18px;
}


QSplitter::handle:vertical {
    height: 1px;
}
"""


# MplCanvas 类用于在 PyQt5 中嵌入 matplotlib 图形
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


# 更新图表的函数
def update_plot(canvas, data):
    canvas.axes.clear()  # 清除之前的图形
    canvas.axes.plot(data)  # 绘制新的数据
    canvas.draw()  # 更新画布


def get_current_temperature():
    # 获取传入的温度
    # return round(random.uniform(20, 30), 1)
    return 29.3


# 假设这是你的硬件数据模拟器
def simulate_hardware_data():
    return np.random.rand(100)  # 返回随机数据作为模拟数据


def process_frame(self, frame):
    frame_resized = cv2.resize(frame, (512, 512))
    frame_normalized = frame_resized.astype(np.float32) / 255.0
    frame_transposed = np.transpose(frame_normalized, [2, 0, 1])
    frame_batched = np.expand_dims(frame_transposed, axis=0)
    return frame_batched


class MainWindow(QMainWindow):
    def __init__(self, win_width=800, win_height=600):
        super().__init__()
        self.win_width = win_width
        self.win_height = win_height
        self.setStyleSheet(styleSheet)
        self.presence_data = np.zeros(100)
        self.breath_data = np.zeros(100)
        self.heart_rate_data = np.zeros(100)

        self.lane_detector = LaneDetection()

        self.setWindowTitle("人体车载")
        self.resize(self.win_width, self.win_height)

        # 创建主部件
        self.main_widget = QWidget()
        self.main_widget.resize(self.win_width, self.win_height)
        self.setCentralWidget(self.main_widget)

        # 创建垂直布局
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)  # 确保布局填充满整个窗口

        # 创建Splitter
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setHandleWidth(0)
        self.layout.addWidget(self.splitter)

        # 主页
        self.widget_home = QWidget()
        self.widget_home.resize(self.win_width, self.win_height - 150)
        self.welcome_label = QLabel("欢迎使用人体车载系统", self.widget_home)
        self.light_button = QPushButton()
        self.light_button.setIconSize(QSize(256, 256))
        # 设置按钮样式为圆形
        self.light_button.setStyleSheet("""
            QPushButton {
                border-image: none;
                padding: 0px; /* 取消默认边距 */
                border: none;
                background-color: rgba(0, 0, 0, 0); /* 透明背景 */
                border-radius: 128px; /* 边框半径为一半的宽度，以形成圆形 */
            }
            QPushButton::icon {
                subcontrol-position: center;
                subcontrol-origin: content;
            }
        """)
        # self.light_button.setFixedSize(128, 128)
        self.light_button.clicked.connect(self.light_button_clicked)
        self.is_light_on = False
        self.light_button.setIcon(QIcon('./static/off.png'))
        self.temperature_label = QLabel()
        self.update_temperature_qtimer = QTimer(self)
        self.update_temperature_qtimer.timeout.connect(self.update_temperature)
        self.update_temperature_qtimer.start(1000)
        self.home_grid_layout = QGridLayout(self.widget_home)
        self.home_grid_layout.addWidget(self.welcome_label, 0, 1, Qt.AlignHCenter)
        self.home_grid_layout.addWidget(self.temperature_label, 1, 0)
        self.home_grid_layout.addWidget(self.light_button, 1, 2)

        # 人体信息
        self.widget_body_info = QWidget()
        self.widget_body_info.resize(self.win_width, self.win_height - 150)
        # 创建三个 MplCanvas 实例
        self.canvas_presence = MplCanvas(self.widget_body_info, width=5, height=3, dpi=100)
        self.canvas_presence.axes.set_title('人体存在')
        self.canvas_breath = MplCanvas(self.widget_body_info, width=5, height=3, dpi=100)
        self.canvas_breath.axes.set_title('呼吸')
        self.canvas_heart_rate = MplCanvas(self.widget_body_info, width=5, height=3, dpi=100)
        self.canvas_heart_rate.axes.set_title('心率')
        self.label_presence = QLabel('人体存在')
        self.label_breath = QLabel('呼吸')
        self.label_heart_rate = QLabel('心率')
        # 创建定时器来更新图表
        self.timer_plot = QTimer(self)
        self.timer_plot.timeout.connect(self.update_plots)
        self.timer_plot.start(1000)  # 每秒更新一次
        self.body_info_grid_layout = QGridLayout(self.widget_body_info)
        # 在网格布局中放置 QLabel 标题
        self.body_info_grid_layout.addWidget(self.label_presence, 0, 0)
        self.body_info_grid_layout.addWidget(self.label_breath, 0, 1)
        # 在网格布局中放置 MplCanvas 实例，确保它们在标题下方
        self.body_info_grid_layout.addWidget(self.canvas_presence, 1, 0)  # 放置在 label_presence 下方
        self.body_info_grid_layout.addWidget(self.canvas_breath, 1, 1)  # 放置在 label_breath 下方
        # 将 label_heart_rate 和 canvas_heart_rate 放置在新的一行中
        self.body_info_grid_layout.addWidget(self.label_heart_rate, 2, 0, 1, 2, Qt.AlignHCenter)
        self.body_info_grid_layout.addWidget(self.canvas_heart_rate, 3, 0, 1, 2)
        # 调整行高和列宽
        self.body_info_grid_layout.setRowMinimumHeight(0, 30)  # 标签行
        self.body_info_grid_layout.setRowMinimumHeight(1, 200)  # 图表行
        self.body_info_grid_layout.setRowMinimumHeight(2, 30)  # label_heart_rate 的行
        self.body_info_grid_layout.setRowMinimumHeight(3, 200)  # canvas_heart_rate 的行
        self.body_info_grid_layout.setColumnMinimumWidth(0, 300)
        self.body_info_grid_layout.setColumnMinimumWidth(1, 300)
        # 设置 grid 布局
        self.widget_body_info.setLayout(self.body_info_grid_layout)
        # 设置 widget_body_info 的固定高度
        self.widget_body_info.setFixedHeight(450)

        # 车底情况
        self.widget_bottom_info = QWidget()
        self.widget_bottom_info.resize(self.win_width, self.win_height - 150)
        self.widget_bottom_info_layout = QVBoxLayout(self.widget_bottom_info)
        self.video_label_bottom = QLabel(self.widget_bottom_info)
        self.widget_bottom_info_layout.addWidget(self.video_label_bottom)
        # 添加一个 QLabel 用于显示检测提示信息
        self.detection_label_bottom = QLabel(self.widget_bottom_info)
        self.detection_label_bottom.setStyleSheet("color: red; font-size: 18px;")
        self.widget_bottom_info_layout.addWidget(self.detection_label_bottom)
        # 打开摄像头
        self.cap_bottom = cv2.VideoCapture(0)
        self.timer_bottom = QTimer(self)
        self.timer_bottom.timeout.connect(self.update_bottom_video_label)
        self.timer_bottom.start(30)

        # 车况分析
        self.widget_lane = QWidget()
        self.video_label = QLabel(self)
        self.widget_lane.resize(self.win_width, self.win_height - 150)
        self.video_label.setFixedSize(self.win_width, self.win_height - 180)
        self.widget_lane_layout = QVBoxLayout(self.widget_lane)
        self.widget_lane_layout.addWidget(self.video_label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_label)
        self.timer.start(30)

        # 初始状态
        self.current_top_widget = self.widget_home
        self.splitter.addWidget(self.current_top_widget)

        # 下部分
        self.bottom_widget = QWidget()
        self.bottom_widget.resize(self.win_width, 150)
        self.main_button_width = 120
        self.other_button_width = 100
        self.space = (self.win_width - self.other_button_width * 4 - self.main_button_width) / 4

        # 创建按钮
        self.buttons = {}
        self.active_button_name = "主页"
        self.button_names = ["人体信息", "车底情况", "主页", "车况分析"]
        for i, name in enumerate(self.button_names):
            button = QPushButton(name, self.bottom_widget)
            if name == "主页":
                button.resize(self.main_button_width, self.main_button_width)
                button.move(int(self.space + i * (self.other_button_width + self.space)),
                            int(150 / 2 - self.main_button_width / 2))
            else:
                button.resize(self.other_button_width, self.other_button_width)
                button.move(int(self.space + i * (self.other_button_width + self.space) + (
                    self.main_button_width - self.other_button_width if i > 2 else 0)),
                            int(150 / 2 - self.other_button_width / 2))
            button.clicked.connect(self.animate_button)
            self.buttons[name] = button
            self.buttons[name].clicked.connect(self.button_action)

        self.splitter.addWidget(self.bottom_widget)
        self.animations = []

    def animate_button(self):
        sender = self.sender()
        button_name = sender.text()
        if button_name == self.active_button_name:
            return
        button_index = self.button_names.index(button_name)
        diff = self.button_names.index(self.active_button_name) - button_index
        raw_names = self.button_names
        self.active_button_name = button_name
        self.button_names = self.button_names[-diff:] + self.button_names[:-diff]
        for i, name in enumerate(raw_names):
            new_index = i + diff
            if new_index < 0:
                new_index += len(self.button_names)
                self.buttons[name].move(int(self.space + (new_index - diff) * (self.other_button_width + self.space)
                                            + (self.main_button_width - self.other_button_width if (
                                                                                                           new_index - diff) > 2 else 0)),
                                        int(150 / 2 - self.other_button_width / 2))
            if new_index > len(self.button_names) - 1:
                new_index -= len(self.button_names)
                self.buttons[name].move(int(self.space + (new_index - diff) * (self.other_button_width + self.space)
                                            + (self.main_button_width - self.other_button_width if (
                                                                                                           new_index - diff) > 2 else 0)),
                                        int(150 / 2 - self.other_button_width / 2))
            animation = QPropertyAnimation(self.buttons[name], b"geometry")
            animation.setDuration(300)
            button_width = self.main_button_width if new_index == 2 else self.other_button_width
            if new_index == 2:
                x = int(self.space + new_index * (self.other_button_width + self.space))
                y = int(150 / 2 - self.main_button_width / 2)
            else:
                x = int(self.space + new_index * (self.other_button_width + self.space) + (
                    self.main_button_width - self.other_button_width if new_index > 2 else 0))
                y = int(150 / 2 - self.other_button_width / 2)
            animation.setEndValue(QRect(x, y, button_width, button_width))
            animation.start()
            self.animations.append(animation)

    def button_action(self):
        sender = self.sender().text()
        widget_dict = {
            '主页': self.widget_home,
            '人体信息': self.widget_body_info,
            '车底情况': self.widget_bottom_info,
            # '语音助手': self.widget_assistant,
            '车况分析': self.widget_lane
        }
        if self.current_top_widget != widget_dict[sender]:
            self.current_top_widget.hide()
            self.current_top_widget = widget_dict[sender]
            self.splitter.replaceWidget(0, self.current_top_widget)  # 替换splitter中的第一个部件
            self.current_top_widget.show()

    def update_video_label(self):
        ret, frame = self.cap_bottom.read()
        if ret:
            frame, is_person = lane.process_an_image(frame)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(q_image)
            self.video_label_bottom.setPixmap(pixmap)

    def update_plots(self):
        self.presence_data = recent_motion_params[-50:]
        if len(recent_motion_params) > 50:
            recent_motion_params.pop(0)

        self.breath_data = recent_breath_params[-50:]
        if len(recent_breath_params) > 50:
            recent_breath_params.pop(0)

        self.heart_rate_data = recent_heart_params[-50:]
        if len(recent_heart_params) > 50:
            recent_heart_params.pop(0)

        # 更新图表
        update_plot(self.canvas_presence, self.presence_data)
        update_plot(self.canvas_breath, self.breath_data)
        update_plot(self.canvas_heart_rate, self.heart_rate_data)

    def update_temperature(self):
        current_temp = get_current_temperature()  # 获取当前温度
        self.temperature_label.setText(f"当前温度: {current_temp}°C")  # 更新标签内容

    def light_button_clicked(self):
        if not self.is_light_on:
            self.is_light_on = True
            self.light_button.setIcon(QIcon('./static/open.png'))
        else:
            self.is_light_on = False
            self.light_button.setIcon(QIcon('./static/off.png'))

    def update_bottom_video_label(self):
        ret, frame = self.cap_bottom.read()
        if ret:
            frame, is_person = real_time_inference(frame)
            if is_person:
                # 更新 QLabel 文本以显示提示信息
                self.detection_label_bottom.setText("检测到人体！")
            else:
                # 清除提示信息
                self.detection_label_bottom.setText("")

            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(q_image)
            self.video_label_bottom.setPixmap(pixmap)


ser = serial.Serial('/dev/ttyUSB0', 115200)  # 请根据实际情况修改串口号和波特率


class MessageHelper(QObject):
    show_message_signal = pyqtSignal(str, str)  # 定义一个信号

    def __init__(self):
        super().__init__()
        self.show_message_signal.connect(self.show_message)

    def show_message(self, text, title):
        self.current_msg = QMessageBox()
        self.current_msg.setIcon(QMessageBox.Information)
        self.current_msg.setText(text)
        self.current_msg.setWindowTitle(title)
        self.current_msg.setStandardButtons(QMessageBox.Ok)
        self.current_msg.button(QMessageBox.Ok).animateClick(1000)  # t时间后自动关闭(t单位为毫秒)
        self.current_msg.exec_()  # 如果使用.show(),会导致QMessageBox框一闪而逝


message_helper = MessageHelper()


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
                        if all(param > 20 for param in tmp_motion_params):
                            print("请问您是否需要帮助")
                            message_helper.show_message_signal.emit("请问您是否需要帮助", "询问")
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
                        message_helper.show_message_signal.emit("呼吸过高", "注意")
                    elif data_code == "03":
                        message_helper.show_message_signal.emit("呼吸过低", "注意")
                        print("呼吸过低")
                    elif data_code == "04":
                        print("没有呼吸")
                elif command_code == "02":
                    print("呼吸数值为(次/分):", int(data_code, 16))
                    recent_breath_params.append(int(data_code, 16))
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
                        message_helper.show_message_signal.emit("心率过快", "注意")
                    elif 60 <= int(data_code, 16) <= 110:
                        print("心率数值为(次/分):", int(data_code, 16), "心率正常")
                    elif int(data_code, 16) < 60:
                        print("心率数值为(次/分):", int(data_code, 16), "心率过慢")
                        message_helper.show_message_signal.emit("心率过慢", "注意")
    # 关闭串口
    ser.close()


if __name__ == "__main__":
    app = QApplication([])

    Thread(target=serial_main).start()

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
