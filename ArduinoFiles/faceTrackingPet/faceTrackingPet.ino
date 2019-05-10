#include <Servo.h>

Servo CamServoX;  
Servo CamServoY;
int ServoAngleInitialize = 90;
String startByte;
String servo;
String servoAngle;

void setup() {
  CamServoX.attach(3);
  CamServoY.attach(4);
  Serial.begin(9600);
  CamServoX.write(ServoAngleInitialize);
  CamServoY.write(ServoAngleInitialize);
}


void loop() {
  if(Serial.available() > 1)
  {
    startByte = Serial.readStringUntil('\r');
    if (startByte == "servo")
    {
        servo = Serial.readStringUntil('\r');
        servoAngle = Serial.readStringUntil('\r');
        if (servo == "X")
          CamServoX.write(servoAngle.toInt());
        if (servo == "Y")
          CamServoY.write(servoAngle.toInt()); 
    }
  }
    //Serial.println(distanceSensor.measureDistanceCm());
    //delay(500);
}
