from cv2 import cv2
import configparser
import os
import glob
import multiprocessing
from multiprocessing import Pool

config = configparser.ConfigParser()
config.read("Config.ini")

class PetAction:
    def __init__(self):
        self._shareValue = None
        pass

    def __del__(self):
        pass

    def InitialShareValue(self):
        raise RuntimeError()

    def Run(self):
        raise RuntimeError()

    def KeyDown(self):
        raise RuntimeError()

class PetController(PetAction):
    def __init__(self):
        CAMERA_INDEX = config.getint("Camera", "Index")
        self._catch = None
        self._imgText = ""
        self._cap = cv2.VideoCapture(CAMERA_INDEX)
        if (config.getboolean("ShowControl", "CameraImgToWindow")):
            cv2.namedWindow(config.get("ShowControl", "CameraImgToWindow_WindowName"), cv2.WINDOW_AUTOSIZE)
        self._shareValue = ShareValue()
        self._shareValue._img = None
        self._shareValue._faceDetectorStatus = None
        self._shareValue._catch = None
        self._shareValue._imgText = ""
        self._shareValue._keyDown = ""
        self._shareValue._pool = None
        self._shareValue._queue = multiprocessing.Manager().Queue()
        multiprocessing.freeze_support()
        self._actionList = []
        pass

    def __del__(self):
        pass

    def AddNewAction(self, action):
        action._shareValue = self._shareValue
        # action.InitialShareValue()
        self._actionList.append(action)

    def Run(self):
        cpus = multiprocessing.cpu_count()
        with Pool(processes=cpus) as self._shareValue._pool:
            for actInitialShareValue in self._actionList:
                actInitialShareValue.InitialShareValue()
            while(self._cap.isOpened()):
                # region cap read
                ret, self._shareValue._img = self._cap.read()
                if(not ret):
                    break
                # endregion

                # region Action Run
                for actRun in self._actionList:
                    actRun.Run()
                # endregion

                # region show
                if self._shareValue._catch is not None:
                    cv2.rectangle(self._shareValue._img,
                                    (int(self._shareValue._catch.left()), int(self._shareValue._catch.top())),
                                    (int(self._shareValue._catch.right()), int(self._shareValue._catch.bottom())),
                                    (0, 0, 255), 4, cv2.LINE_AA)

                if (config.getboolean("ShowControl", "CameraImgToWindow")):
                    cv2.putText(self._shareValue._img, self._shareValue._imgText, (0, 30), cv2.FONT_HERSHEY_DUPLEX,
                                0.7, (255, 0, 0), 1, cv2.LINE_AA)
                    cv2.imshow(config.get("ShowControl", "CameraImgToWindow_WindowName"), self._shareValue._img)

                # endregion

                # region keyCode
                keyCode = cv2.waitKey(1)
                self._shareValue._keyDown = keyCode & 0xFF
                if keyCode & 0xFF == ord('q'):
                    break  
                for actKeyDown in self._actionList:
                    actKeyDown.KeyDown()
                # endregion

            self._shareValue._pool.terminate()
            self._shareValue._pool.join()

        return
        # 釋放攝影機
        self._cap.release()
        # cv2.destroyAllWindows()
        pass

class ShareValue:
    pass

if __name__ == "__main__":
    pass