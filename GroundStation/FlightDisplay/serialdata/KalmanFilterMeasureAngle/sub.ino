// キャリブレーション処理の最適化
void Rate_calibration() {
  const int CALI_SAMPLES = 2000;  // サンプル数を少し減らして起動を早く
  RateCaliRoll = RateCaliPitch = RateCaliYaw = 0;  // 初期化

  Serial.println("Calibrating gyroscope...");
  for(RateCaliNum = 0; RateCaliNum < CALI_SAMPLES; RateCaliNum++) {
    if (IMU.gyroscopeAvailable()) {
      IMU.readGyroscope(RateRoll, RatePitch, RateYaw);
      RateCaliRoll += RateRoll;
      RateCaliPitch += RatePitch;
      RateCaliYaw += RateYaw;
    }
    delayMicroseconds(500);  // delay(1)の代わりに0.5msに短縮
  }
  
  RateCaliRoll /= CALI_SAMPLES;
  RateCaliPitch /= CALI_SAMPLES;
  RateCaliYaw /= CALI_SAMPLES;
  
  Serial.println("Calibration complete!");
}

// カルマンフィルタの定数を定義
const float dt = 0.005;  // 200Hz用のタイムステップ
const float Q_angle = 0.001;    // プロセスノイズの分散
const float R_angle = 0.03;     // 測定ノイズの分散

void kalman_1d(float &KalmanState, float &KalmanUncertainty, float KalmanInput, float KalmanMeasurement) {
  // 状態予測
  KalmanState = KalmanState + dt * KalmanInput;
  
  // 誤差共分散の予測
  KalmanUncertainty = KalmanUncertainty + dt * dt * Q_angle;
  
  // カルマンゲインの計算
  float KalmanGain = KalmanUncertainty / (KalmanUncertainty + R_angle);
  
  // 状態の更新
  KalmanState = KalmanState + KalmanGain * (KalmanMeasurement - KalmanState);
  
  // 誤差共分散の更新
  KalmanUncertainty = (1 - KalmanGain) * KalmanUncertainty;
  
  Kalman1DOutput[0] = KalmanState;
  Kalman1DOutput[1] = KalmanUncertainty;
}

void read_accel() {
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(AccX, AccY, AccZ);
    // キャリブレーション値の適用
    AccX += 0.02;
    AccY = -AccY - 0.01;  // 右手系への変換
    AccZ -= 0.02;
  }
}

void angle_by_accel(){
  AngleRoll = atan(AccY/sqrt(AccX*AccX+AccZ*AccZ))*180/3.142;
  AnglePitch = -atan(AccX/sqrt(AccY*AccY+AccZ*AccZ))*180/3.142; 
}

void calibrated_rate() {
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(RateRoll, RatePitch, RateYaw);
    // キャリブレーション値の適用
    RateRoll = -(RateRoll - RateCaliRoll);
    RatePitch -= RateCaliPitch;
    RateYaw = -(RateYaw - RateCaliYaw);
  }
}