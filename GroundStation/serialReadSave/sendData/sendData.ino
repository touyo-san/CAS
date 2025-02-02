#include <Arduino_LSM6DS3.h> // IMU用ライブラリ
char userInput;

void setup() {
  Serial.begin(115200);
  while (!Serial); // シリアル通信が準備完了するまで待機
  
  // gが入力されるまで待機
  while (true) {
    if (Serial.available() > 0) {
      userInput = Serial.read();
      if (userInput == 'g') {
        Serial.println("Time(s), Ax(m/s^2), Ay(m/s^2), Az(m/s^2), Gx(deg/s), Gy(deg/s), Gz(deg/s)");
        break;
      }
    }
  }

  // IMUの初期化
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1); // 初期化に失敗した場合は停止
  }
}

void loop() {
  float ax, ay, az; // 加速度 (m/s^2)
  float gx, gy, gz; // 角速度 (deg/s)
  userInput = Serial.read();               // read user input      
      if(userInput == 'g'){                  // if we get expected value 
            // IMUデータの取得
            if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
              IMU.readAcceleration(ax, ay, az); // 加速度データを取得
              IMU.readGyroscope(gx, gy, gz);    // ジャイロデータを取得

              // シリアルモニターにデータを出力
              Serial.print(millis() / 1000.0, 2); // プログラム開始からの経過時間 (秒)
              Serial.print(", ");
              Serial.print(ax, 2); Serial.print(", ");
              Serial.print(ay, 2); Serial.print(", ");
              Serial.print(az, 2); Serial.print(", ");
              Serial.print(gx, 2); Serial.print(", ");
              Serial.print(gy, 2); Serial.print(", ");
              Serial.println(az, 2);
              delay(100); // 測定間隔 (100ms)
            }
      } // if user input 'g' 
} // Serial.available
