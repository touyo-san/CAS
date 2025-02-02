#include <Arduino_LSM6DS3.h> // IMU用ライブラリ

void setup() {
  Serial.begin(9600);
  
  // シリアル通信の初期化待ちにタイムアウトを設定
  unsigned long startTime = millis();
  while (!Serial && (millis() - startTime < 5000)) {
    ; // 最大5秒間待機
  }
  
  // IMUの初期化
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  
  // 初期化完了メッセージ
  Serial.println("Initialization complete!");
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

        // データ出力（時間を含む）
        Serial.print(millis() / 1000.0, 3); Serial.print(",");
        Serial.print(ax, 2); Serial.print(",");
        Serial.print(ay, 2); Serial.print(",");
        Serial.print(az, 2); Serial.print(",");
        Serial.print(gx, 2); Serial.print(",");
        Serial.print(gy, 2); Serial.print(",");
        Serial.println(gz, 2);
      }
    }
  }
}