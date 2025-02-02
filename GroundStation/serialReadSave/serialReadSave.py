# python3 -m pip install pyserial
from serial.tools import list_ports
import serial
import time
import csv
from datetime import datetime  # 追加

# list ports
ports = list_ports.comports()
for port in ports: print(port)

serialCom = serial.Serial('COM3', 115200, timeout=1)

# Get current date and time
current_time = datetime.now().strftime('%y%m%d%H%M%S')
filename = f"data_{current_time}.csv"

# create data file with timestamp
f = open(filename, "w", newline='')
writer = csv.writer(f, delimiter=",")

print("Press Ctrl+C to stop recording data...")
print("Recording will start in:")
for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)
print("Recording started!")

try:
    k = 0
    while True:  # 無限ループ
        # Read a line of data
        serialCom.write(b'g')     # Transmit the char 'g' to receive the Arduino data point
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
        k = k + 1
except KeyboardInterrupt:  # Ctrl+C で終了
    print("\nStopping data collection...")
except Exception as e:
    print(f"ERROR.y Line was not recorded: {e}")
except ValueError as e:
    print(f"Data parsing error: {e}")
finally:
    f.close()
    serialCom.close()
    print("Data collection completed.")