#include <Arduino_LSM6DS3.h> // IMU用ライブラリ

void setup() {
  Serial.begin(9600);
  while (!Serial); // シリアル通信が準備完了するまで待機
  
  // IMUの初期化
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
}

void loop() {
  float ax, ay, az; // 加速度 (m/s^2)
  float gx, gy, gz; // 角速度 (deg/s)

  if (Serial.available() > 0) {
    char userInput = Serial.read();
    
    // 入力バッファをクリア
    while(Serial.available()) {
      Serial.read();
    }
    
    if (userInput == 'g') {
      // IMUデータの取得
      if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
        IMU.readAcceleration(ax, ay, az);
        IMU.readGyroscope(gx, gy, gz);

        // データ出力（最後の値を gz に修正）
        Serial.print(ax, 2); Serial.print(",");
        Serial.print(ay, 2); Serial.print(",");
        Serial.print(az, 2); Serial.print(",");
        Serial.print(gx, 2); Serial.print(",");
        Serial.print(gy, 2); Serial.print(",");
        Serial.println(gz, 2);  // ここを gz に修正
      }
    }
  }
}