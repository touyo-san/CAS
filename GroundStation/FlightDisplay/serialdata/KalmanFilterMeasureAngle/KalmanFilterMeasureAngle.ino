#include <Arduino_LSM6DS3.h>
#include <Wire.h>  // Include the Wire library for I2C communication.
// #include <PulsePosition.h>  // Need to use "Teensy" H/W
float GyroX, GyroY, GyroZ;
float AccX, AccY, AccZ;
float AngleRoll, AnglePitch;
float RateRoll, RatePitch, RateYaw;
float RateCaliRoll, RateCaliPitch, RateCaliYaw; // Calibrate the rotation rate
int RateCaliNum;
uint32_t LoopTimer; // Define the parameter containing the length of each control loop

float KalmanAngleRoll=0, KalmanUncertaintyAngleRoll=2*2;  // Define the predicted of the initial angles and the uncertainties (std dev) on the initial angle
float KalmanAnglePitch=0, KalmanUncertaintyAnglePitch=2*2;
float Kalman1DOutput[]={0,0}; //Initialize the output of the filter (angle prediction, uncertainty of the prediction)

float AccZInertial;
float VelocityVertical;

void setup() {
  Serial.begin(115200);   // ボーレートを115200に上げる
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  Rate_calibration();
  LoopTimer = micros();
}

void loop() {  
  read_accel();
  angle_by_accel();
  calibrated_rate();
  
  // カルマンフィルタの更新
  kalman_1d(KalmanAngleRoll, KalmanUncertaintyAngleRoll, RateRoll, AngleRoll);
  KalmanAngleRoll = Kalman1DOutput[0];
  KalmanUncertaintyAngleRoll = Kalman1DOutput[1];
  
  kalman_1d(KalmanAnglePitch, KalmanUncertaintyAnglePitch, RatePitch, AnglePitch);
  KalmanAnglePitch = Kalman1DOutput[0];
  KalmanUncertaintyAnglePitch = Kalman1DOutput[1];

  // シリアル通信
  Serial.print(KalmanAnglePitch);
  Serial.print(",");
  Serial.println(KalmanAngleRoll);

  // タイミング制御の改善
  while(micros() - LoopTimer < 5000); // 200Hz (5ms) に更新レートを上げる
  LoopTimer = micros();
}
