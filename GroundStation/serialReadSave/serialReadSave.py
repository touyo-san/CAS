# python3 -m pip install pyserial
from serial.tools import list_ports
import serial
import time
import csv

# list ports
ports = list_ports.comports()
for port in ports: print(port)

serialCom = serial.Serial('COM3', 115200, timeout=1)

# create data file
f = open("data.csv","w", newline='')
writer = csv.writer(f, delimiter=",")

# Reset the Arduino
serialCom.rts = False  # RTS信号をオフ
time.sleep(0.5)
serialCom.flushInput()
serialCom.rts = True   # RTS信号をオン
time.sleep(2)          # Arduinoの初期化を待機

# Read setup data
# for _ in range(3):  # 必要に応じて行数を調整
#     if serialCom.in_waiting > 0:
#         setup_data = serialCom.readline().decode("utf-8", errors="ignore").strip('\r\n')
#         print(f"Setup Data: {setup_data}")

kmax = 60*1    # number of data points to record
for k in range(kmax):
    try:
        # Read a line of data
        s_bytes = serialCom.readline()
        # print(f"Raw data: {s_bytes}")  # デバッグ用
        # Decode binary
        decoded_bytes = s_bytes.decode("utf-8", errors="ignore").strip('\r\n')
        # print(f"Decoded bytes: {decoded_bytes}")  # デバッグ用

        # Parse Lines
        if k == 0:
            values = decoded_bytes.split(",")
        else:
             # データをカンマで分割し、数値に変換
            values = [float(x.strip()) for x in decoded_bytes.split(",")]
        print(f"Parsed values: {values}")

        writer.writerow(values)

    except ValueError as e:
        print(f"Data parsing error: {e}")
    except Exception as e:
        print(f"ERROR. Line was not recorded: {e}")

f.close()
serialCom.close()