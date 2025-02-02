// https://github.com/WaveShapePlay/Arduino_RealTimePlot
#include <Arduino_LSM6DS3.h> // IMU用ライブラリ
char userInput;

void setup(){

  Serial.begin(9600);                        //  setup serial
  while (!Serial); // シリアル通信が準備完了するまで待機
  // IMUの初期化
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1); // 初期化に失敗した場合は停止
  }
}

void loop(){
  float ax, ay, az; // 加速度 (m/s^2)
  float gx, gy, gz; // 角速度 (deg/s)

if(Serial.available()> 0){ 
    
    userInput = Serial.read();               // read user input
      
      if(userInput == 'g'){                  // if we get expected value 
            // IMUデータの取得
            if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
              IMU.readAcceleration(ax, ay, az); // 加速度データを取得
              IMU.readGyroscope(gx, gy, gz);    // ジャイロデータを取得

              // シリアルモニターにデータを出力
              // Serial.print(millis() / 1000.0, 2); // 経過時間 (秒)
              // Serial.print(", ");
              Serial.print(ax, 2); Serial.print(", ");
              Serial.print(ay, 2); Serial.print(", ");
              Serial.print(az, 2); Serial.print(", ");
              Serial.print(gx, 2); Serial.print(", ");
              Serial.print(gy, 2); Serial.print(", ");
              Serial.println(az, 2);
            }
      } // if user input 'g' 
  } // Serial.available
} // Void Loop