import serial

ser = serial.Serial('COM7', 9600)
try:
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting) # 读取一行数据并解码
            data = data.strip().hex()
            print(data)
            if data.startswith("36"):
                print("Light On")
            elif data.startswith("39"):
                print("Light Off")
            elif data.startswith("31"):
                print("灯光已调暗")
            elif data.startswith("32"):
                print("灯光已调亮")
            elif data.startswith("33"):
                print("灯光已调到最亮")
except KeyboardInterrupt:
    print("程序被用户中断")
finally:
    ser.close()  # 关闭串口连接
