#include <Servo.h>

Servo CamServoX;  
Servo CamServoY;
int ServoAngleInitialize = 90;
char startByte;
char servo;
String servoAngle;

void setup() {
  CamServoX.attach(3);
  CamServoY.attach(4);
  Serial.begin(115200);
  Serial.setTimeout(10);
  CamServoX.write(ServoAngleInitialize);
  CamServoY.write(ServoAngleInitialize);
}

bool IsDigit(String string)
{
  for (int i = 0; i < string.length(); i ++)
  {
    if (!isDigit(string.charAt(i)))
      return false;
  }
  return true;  
}

void loop() {
  if(Serial.available() > 2)
  {
    startByte = Serial.read();
    if (startByte == 'S')
    {
        servo = Serial.read();
        servoAngle = Serial.readStringUntil('\r');
        if (!IsDigit(servoAngle))
          servo = 'N';
        if (servo == 'X')
          CamServoX.write(servoAngle.toInt());
        else if (servo == 'Y')
          CamServoY.write(servoAngle.toInt());
    }
  }
    //Serial.println(distanceSensor.measureDistanceCm());
    //delay(500);
}
