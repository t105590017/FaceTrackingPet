from PetController import PetAction
from FaceDetectorAction import MasterDetectorState
from configparser import ConfigParser
from GPIOController import Servomotor

gpioInfo = ConfigParser()
gpioInfo.read("gpioConfig.ini")

class CameraMoveAction(PetAction):
    def __init__(self):
        self._cameraHorizontalAngle = 90
        self._cameraVerticalAngle = 90
        self._horizontalServomotor = None
        self._verticalServomotor = None
        self._horizontalServomotor = Servomotor("SG90", "PIN32", resetAngle = 90, initAngle= self._cameraHorizontalAngle)
        self._verticalServomotor = Servomotor("SG90", "PIN33", resetAngle = 90, initAngle= self._cameraHorizontalAngle)

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
        if self._shareValue._status is MasterDetectorState.LOST:
            return
            
        # Horizontal
        if x > 50 and self._cameraHorizontalAngle < gpioInfo.getint("SG90", "MaxAngle"):
            moveAngle = int((gpioInfo.getint("SG90", "MaxAngle") - self._cameraHorizontalAngle) * (x - 50)) // 100
            self._cameraHorizontalAngle += moveAngle
            if self._cameraHorizontalAngle > gpioInfo.getint("SG90", "MaxAngle"):
                self._cameraHorizontalAngle = gpioInfo.getint("SG90", "MaxAngle")
        if x < 50 and self._cameraHorizontalAngle > gpioInfo.getint("SG90", "MinAngle"):
            moveAngle = int(self._cameraHorizontalAngle * (50 - x)) // 100
            self._cameraHorizontalAngle -= moveAngle
            if self._cameraHorizontalAngle < gpioInfo.getint("SG90", "MinAngle"):
                self._cameraHorizontalAngle = gpioInfo.getint("SG90", "MinAngle")

        # Vertical
        if y > 50 and self._cameraVerticalAngle < gpioInfo.getint("SG90", "MaxAngle"):
            moveAngle = int((gpioInfo.getint("SG90", "MaxAngle") - self._cameraVerticalAngle) * (y - 50)) // 100
            self._cameraVerticalAngle += moveAngle
            if self._cameraVerticalAngle > gpioInfo.getint("SG90", "MaxAngle"):
                self._cameraVerticalAngle = gpioInfo.getint("SG90", "MaxAngle")
        if y < 50 and self._cameraVerticalAngle > gpioInfo.getint("SG90", "MinAngle"):
            moveAngle = int(self._cameraVerticalAngle * (50 - y)) // 100
            self._cameraVerticalAngle -= moveAngle
            if self._cameraVerticalAngle < gpioInfo.getint("SG90", "MinAngle"):
                self._cameraVerticalAngle = gpioInfo.getint("SG90", "MinAngle")

        print("Change Horizontal Angle To {}".format(self._cameraHorizontalAngle))
        print("Change Vertical Angle To {}".format(self._cameraVerticalAngle))

        self._horizontalServomotor.ChangeAngle(self._cameraHorizontalAngle)
        self._verticalServomotor.ChangeAngle(self._cameraVerticalAngle)
        