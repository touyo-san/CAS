import time
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
from datetime import datetime
import threading
from queue import Queue

class DataLogger:
    def __init__(self, serial_port="COM3", baud_rate=9600):
        # データ保存用の設定
        current_time = datetime.now().strftime('%y%m%d%H%M%S')
        self.filename = f"data_{current_time}.csv"
        self.csv_file = open(self.filename, "w", newline='')
        self.csv_writer = csv.writer(self.csv_file)
        
        # プロット用のデータリストを初期化（時間は含めない）
        self.dataLists = [[] for _ in range(6)]  # センサデータ用の6つのリスト
        
        # キューの初期化
        self.data_queue = Queue(maxsize=100)  # キューサイズを制限
        
        try:
            self.ser = serial.Serial(serial_port, baud_rate, timeout=1)
            print(f"シリアルポート {serial_port} に接続成功")
            time.sleep(2)
        except serial.SerialException as e:
            print(f"シリアルポート接続エラー: {e}")
            raise

        # プロット用の設定
        plt.ion()
        self.fig = plt.figure(figsize=(12, 5))
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        
        # アニメーションの設定
        self.ani = animation.FuncAnimation(
            self.fig, self.update_plot, 
            interval=100,
            blit=False
        )
        
        plt.show(block=False)
        
        # データ記録用スレッドの開始
        self.recording = True
        self.record_thread = threading.Thread(target=self.record_data)
        self.record_thread.daemon = True  # メインスレッド終了時に終了
        self.record_thread.start()

    def record_data(self):
        """データを記録するスレッド"""
        print("データ記録開始")
        while self.recording:
            try:
                self.ser.write(b'g')
                data_string = self.ser.readline().decode('ascii').strip()
                if data_string:
                    data_values = [float(x) for x in data_string.split(',')]
                    if len(data_values) == 7:  # 時間 + 6つのセンサデータ
                        print(f"受信データ: {data_string}")
                        self.csv_writer.writerow(data_values)  # 全データを保存
                        # キューには時間以外のデータを送信
                        self.data_queue.put(data_values[1:])  # インデックス1以降のデータ
                    else:
                        print(f"不正なデータ形式: {data_string}")
            except Exception as e:
                print(f"データ読み取りエラー: {e}")
                time.sleep(0.1)

    def update_plot(self, frame):
        """プロットを更新する関数"""
        try:
            if not self.data_queue.empty():
                data_values = self.data_queue.get()  # センサデータのみ（時間は含まない）
                
                # データの追加
                for idx, value in enumerate(data_values):
                    self.dataLists[idx].append(value)
                    if len(self.dataLists[idx]) > 50:  # 最新の50点を保持
                        self.dataLists[idx].pop(0)
                
                # プロットの更新
                self.ax1.clear()
                self.ax2.clear()
                
                # 加速度データのプロット（インデックス0-2）
                self.ax1.plot(self.dataLists[0], 'r-', label='Accel_x')
                self.ax1.plot(self.dataLists[1], 'g-', label='Accel_y')
                self.ax1.plot(self.dataLists[2], 'b-', label='Accel_z')
                self.ax1.set_ylim([-5, 5])
                self.ax1.set_title("Acceleration")
                self.ax1.set_ylabel("g")
                self.ax1.legend()
                
                # ジャイロデータのプロット（インデックス3-5）
                self.ax2.plot(self.dataLists[3], 'c-', label='Gyro_x')
                self.ax2.plot(self.dataLists[4], 'm-', label='Gyro_y')
                self.ax2.plot(self.dataLists[5], 'y-', label='Gyro_z')
                self.ax2.set_ylim([-2500, 2500])
                self.ax2.set_title("Angular Velocity")
                self.ax2.set_ylabel("dps")
                self.ax2.legend()
                
                self.fig.tight_layout()
                
        except Exception as e:
            print(f"プロット更新エラー: {e}")

    def close(self):
        """プログラムの終了処理"""
        self.recording = False
        self.record_thread.join()
        self.csv_file.close()
        self.ser.close()
        plt.close()

def main():
    # 利用可能なシリアルポートを表示
    print("利用可能なシリアルポート:")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"- {port.device}")

    port = input("使用するシリアルポートを入力してください (デフォルト: COM3): ") or "COM3"
    
    print("Press Ctrl+C to stop recording data...")
    print("Recording will start in:")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print("Recording started!")
    
    try:
        logger = DataLogger(serial_port=port)
        print("プロットウィンドウを表示中...")
        
        # プログラムの実行状態を表示
        while True:
            plt.pause(0.1)  # プロット更新のための短い待機
            
    except KeyboardInterrupt:
        print("\nプログラムを終了します...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'logger' in locals():
            logger.close()
        print("Data collection completed.")

if __name__ == "__main__":
    main()