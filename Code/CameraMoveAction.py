from PetController import PetAction
from FaceDetectorAction import MasterDetectorState
from configparser import ConfigParser
from GPIOController import Servomotor

gpioInfo = ConfigParser()
gpioInfo.read("gpioConfig.ini")
SG90MaxAngle = gpioInfo.getint("SG90", "MaxAngle")
SG90MinAngle = gpioInfo.getint("SG90", "MinAngle")

class CameraMoveAction(PetAction):
    def __init__(self):
        self._cameraHorizontalAngle = 90
        self._cameraVerticalAngle = 90
        self._horizontalServomotor = Servomotor("SG90", "PIN32", resetAngle = 90, initAngle= self._cameraHorizontalAngle)
        self._verticalServomotor = Servomotor("SG90", "PIN33", resetAngle = 90, initAngle= self._cameraHorizontalAngle)
        self._cameraMoveCount = 0

    def InitialShareValue(self):
        pass

    def Run(self):
        imgH, imgW = self._shareValue.SourceImage.shape[:2]
        if self._cameraMoveCount is 2:
            if self._shareValue.FaceCatchArea is not None:
                catchX = (int(self._shareValue.FaceCatchArea.left()) + int(self._shareValue.FaceCatchArea.right())) / 2
                catchY = (int(self._shareValue.FaceCatchArea.top()) + int(self._shareValue.FaceCatchArea.bottom())) / 2
                self.HardwareInterface(catchX * 100 // imgW, catchY * 100 // imgH)
            else:
                self.HardwareInterface(50, 50)
            self._cameraMoveCount = 0

        self._cameraMoveCount += 1
        pass

    def KeyDown(self):
        pass

    def HardwareInterface(self, x, y):
        cameraMoveAngle = 1

        if(x < 40 and x > 60 ):
            return
        if(y < 40 and y > 60):
            return

        if self._shareValue.FaceDetectorStatus is MasterDetectorState.LOST:
            return
            
        # Horizontal
        if x > 50 and self._cameraHorizontalAngle < SG90MaxAngle:
            self._cameraHorizontalAngle += cameraMoveAngle
            if self._cameraHorizontalAngle > SG90MaxAngle:
                self._cameraHorizontalAngle = SG90MaxAngle
        if x < 50 and self._cameraHorizontalAngle > SG90MinAngle:
            self._cameraHorizontalAngle -= cameraMoveAngle
            if self._cameraHorizontalAngle < SG90MinAngle:
                self._cameraHorizontalAngle = SG90MinAngle

        # Vertical
        if y > 50 and self._cameraVerticalAngle < SG90MaxAngle:
            self._cameraVerticalAngle += cameraMoveAngle
            if self._cameraVerticalAngle > SG90MaxAngle:
                self._cameraVerticalAngle = SG90MaxAngle
        if y < 50 and self._cameraVerticalAngle > SG90MinAngle:
            self._cameraVerticalAngle -= cameraMoveAngle
            if self._cameraVerticalAngle < SG90MinAngle:
                self._cameraVerticalAngle = SG90MinAngle

        print("Change Horizontal Angle To {}".format(self._cameraHorizontalAngle))
        print("Change Vertical Angle To {}".format(self._cameraVerticalAngle))

        self._horizontalServomotor.ChangeAngle(self._cameraHorizontalAngle)
        self._verticalServomotor.ChangeAngle(self._cameraVerticalAngle)
        
if __name__ =="__main__":
    hServomotor = Servomotor("SG90", "PIN32", resetAngle = 90, initAngle= 90)
    vServomotor = Servomotor("SG90", "PIN33", resetAngle = 90, initAngle= 90)

