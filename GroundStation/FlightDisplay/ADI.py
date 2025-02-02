# IN BETA, INACCURATE PITCH INDICATION ON ROLL

import tkinter as tk
from PIL import Image, ImageTk
import math
import serial
import time

class AttitudeIndicator(tk.Canvas):
    def __init__(self, parent, bg_image_path, fg_image_path, serial_port='COM3', baud_rate=115200, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        try:
            self.bg_image_path = bg_image_path
            self.fg_image_path = fg_image_path

            print(f"Attempting to load background image from: {bg_image_path}")
            self.bg_image = Image.open(bg_image_path)
            print("Background image loaded successfully")
            
            print(f"Attempting to load foreground image from: {fg_image_path}")
            self.fg_image = Image.open(fg_image_path)
            print("Foreground image loaded successfully")
            
            self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
            self.fg_image_tk = ImageTk.PhotoImage(self.fg_image)

            self.bg_item = self.create_image(350, 350, anchor="center", image=self.bg_image_tk)
            self.fg_item = self.create_image(350, 350, anchor="center", image=self.fg_image_tk)
            
            self.pitch_text = self.create_text(350, 15, anchor="n", font=("Chakra Petch", 16), fill="white", text="Pitch: 0°")
            self.roll_text = self.create_text(350, 45, anchor="n", font=("Chakra Petch", 16), fill="white", text="Roll: 0°")

            # Initialize serial connection
            print(f"Attempting to connect to {serial_port} at {baud_rate} baud")
            self.serial_port = serial.Serial(
                serial_port,
                baud_rate,
                timeout=0,  # ノンブロッキングモード
                writeTimeout=0
            )
            time.sleep(2)  # Arduinoのリセット待ち
            
            # 初期化時にバッファをクリア
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            print("Serial connection established")
            self.update_from_arduino()
            
        except serial.SerialException as e:
            print(f"Serial port error: {str(e)}")
            raise
        except Exception as e:
            print(f"General error: {str(e)}")
            raise

        self.pack(fill="both", expand=True)

    def pitch_to_pixels(self, pitch):
        # ピッチ角を±85度に制限
        limited_pitch = max(min(pitch, 85), -85)
        # 1度あたり3ピクセルに調整（感度を下げる）
        return limited_pitch * 3

    def update_attitude(self, pitch, roll):
        try:
            # ピッチオフセットの計算
            pitch_offset = self.pitch_to_pixels(pitch)
            
            # 背景画像の位置を更新（中心位置は350）
            self.coords(self.bg_item, 350, 350 + pitch_offset)
            
            # ロール角の更新（±180度は許容）
            self.bg_image = Image.open(self.bg_image_path).rotate(roll)
            self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
            self.itemconfig(self.bg_item, image=self.bg_image_tk)
            
            # デバッグ出力
            print(f"Applied values - Pitch: {pitch}° (limited: {max(min(pitch, 85), -85)}°, offset: {pitch_offset}px), Roll: {roll}°")
            
            # 表示テキストを更新
            self.itemconfig(self.pitch_text, text=f"Pitch: {pitch:.1f}°")
            self.itemconfig(self.roll_text, text=f"Roll: {roll:.1f}°")
            
        except Exception as e:
            print(f"Error in update_attitude: {str(e)}")

    def demo(self):
        def animate_pitch(pitch_sequence, roll=0, next_animation=None):
            def animate():
                try:
                    pitch = next(pitches)
                    if abs(pitch) > 88:
                        self.quick_flip(pitch, roll, next_animation)
                        return
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            pitches = iter(pitch_sequence)
            animate()

        def animate_roll(roll_sequence, pitch=0, next_animation=None):
            def animate():
                try:
                    roll = next(rolls)
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            rolls = iter(roll_sequence)
            animate()

        def animate_pitch_and_roll(pitch_sequence, roll_sequence, next_animation=None):
            def animate():
                try:
                    pitch = next(pitches)
                    roll = next(rolls)
                    if abs(pitch) > 88:
                        self.quick_flip(pitch, roll, next_animation)
                        return
                    self.update_attitude(pitch, roll)
                    self.update()
                    self.after(50, animate)
                except StopIteration:
                    if next_animation:
                        next_animation()
            pitches = iter(pitch_sequence)
            rolls = iter(roll_sequence)
            animate()

        pitch_sequence_full_up = list(range(-6, 6, 2))
        pitch_sequence_full_down = list(range(6, -6, -2))
        pitch_sequence_flip_over = list(range(0, 120, 2)) + list(range(120, 0, -2))
        pitch_sequence_level = [0] * 36
        roll_sequence_full_right = list(range(0, 6, 2))
        roll_sequence_full_left = list(range(6, -6, -2))
        roll_sequence_level = [0] * 36

        animate_pitch(
            pitch_sequence_full_up,
            next_animation=lambda: animate_pitch(
                pitch_sequence_full_down,
                next_animation=lambda: animate_pitch(
                    pitch_sequence_level,
                    next_animation=lambda: animate_roll(
                        roll_sequence_full_right,
                        next_animation=lambda: animate_roll(
                            roll_sequence_full_left,
                            next_animation=lambda: animate_roll(
                                roll_sequence_level,
                                next_animation=lambda: animate_pitch_and_roll(
                                    pitch_sequence_full_up + pitch_sequence_full_down + pitch_sequence_level,
                                    roll_sequence_full_right + roll_sequence_full_left + roll_sequence_level,
                                    next_animation=lambda: self.quick_flip(
                                        pitch_sequence_flip_over[0], 0, animate_pitch_and_roll(
                                            pitch_sequence_flip_over, [0]*len(pitch_sequence_flip_over)
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )

    def quick_flip(self, pitch, roll, next_animation=None):
        def animate():
            if pitch > 90 or pitch < -90:
                self.bg_image = Image.open(self.bg_image_path).rotate(180 if pitch > 90 else -180)
                self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
                self.itemconfig(self.bg_item, image=self.bg_image_tk)
                self.update()
                new_pitch = 180 - pitch if pitch > 90 else -180 - pitch
                self.update_attitude(new_pitch, roll)
                self.update()
                if next_animation:
                    next_animation()
        self.after(10, animate)

    def update_from_arduino(self):
        try:
            # バッファに溜まっているデータをすべて読み取り、最新のデータのみを使用
            latest_data = None
            while self.serial_port.in_waiting:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:  # 空行でない場合
                    latest_data = data
            
            # 最新のデータがある場合のみ処理
            if latest_data:
                try:
                    values = latest_data.split(',')
                    if len(values) == 2:
                        pitch = float(values[0])
                        roll = float(values[1])
                        self.update_attitude(pitch, roll)
                except ValueError as e:
                    print(f"Data parsing error: {str(e)}, Raw data: {latest_data}")
            
        except Exception as e:
            print(f"Error in update_from_arduino: {str(e)}")
        
        # より高頻度で更新（2ms = 500Hz）
        self.after(2, self.update_from_arduino)

    def __del__(self):
        if hasattr(self, 'serial_port') and self.serial_port.is_open:
            self.serial_port.close()
            print("Serial port closed")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Attitude Indicator")
    root.geometry("700x700")

    bg_image_path = "assets/attitudebg1.png"
    fg_image_path = "assets/attitudefg.png"

    # Specify your Arduino's COM port here
    SERIAL_PORT = 'COM3'  # Windows example, might be '/dev/ttyUSB0' on Linux
    BAUD_RATE = 115200

    try:
        ai = AttitudeIndicator(root, bg_image_path, fg_image_path, 
                              serial_port=SERIAL_PORT, baud_rate=BAUD_RATE,
                              width=700, height=700)
        ai.pack(fill="both", expand=True)

        # Start the demo
        root.after(1000, ai.demo)
        
        root.mainloop()
    except Exception as e:
        print(f"Application error: {str(e)}")