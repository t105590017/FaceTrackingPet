from PetController import PetAction
from configparser import ConfigParser
# from GPIOController import Servomotor

gpioInfo = ConfigParser()
gpioInfo.read("gpioConfig.ini")

class CameraMoveAction(PetAction):
    def __init__(self):
        self._cameraHorizontalAngle = 90
        self._cameraVerticalAngle = 90
        self._horizontalServomotor = None
        self._verticalServomotor = None
        servoModel = "SG90"
        self._maxAngle = gpioInfo.getint(servoModel, "MaxAngle")
        self._minAngle = gpioInfo.getint(servoModel, "MinAngle")
        # self._horizontalServomotor = Servomotor(servoModel, "PIN32", resetAngle = 90, initAngle= self._cameraHorizontalAngle)
        # self._verticalServomotor = Servomotor(servoModel, "PIN33", resetAngle = 90, initAngle= self._cameraHorizontalAngle)

    def InitalShareValue(self):
        pass

    def Run(self):
        imgH, imgW = self._shareValue._img.shape[:2]
        if self._shareValue._catch is not None:
            catchX = (int(self._shareValue._catch.left()) + int(self._shareValue._catch.right())) / 2
            catchY = (int(self._shareValue._catch.top()) + int(self._shareValue._catch.bottom())) / 2
            self.HardwareInterface(catchX * 100 // imgW, catchY * 100 // imgH)
        else:
            self.HardwareInterface(50, 50)
        pass

    def KeyDown(self):
        pass

    def HardwareInterface(self, x, y):
        # Horizontal
        if x > 50 and self._cameraHorizontalAngle < self._maxAngle:
            self._cameraHorizontalAngle += 1
        if x < 50 and self._cameraHorizontalAngle > self._minAngle:
            self._cameraHorizontalAngle -= 1

        # Vertical
        if y > 50 and self._cameraVerticalAngle < self._maxAngle:
            self._cameraVerticalAngle += 1
        if y < 50 and self._cameraVerticalAngle > self._minAngle:
            self._cameraVerticalAngle -= 1

        print("Change Horizontal Angle To {}".format(self._cameraHorizontalAngle))
        print("Change Vertical Angle To {}".format(self._cameraVerticalAngle))

        # self._horizontalServomotor.ChangeAngle(self._cameraHorizontalAngle)
        # self._verticalServomotor.ChangeAngle(self._cameraVerticalAngle)
        