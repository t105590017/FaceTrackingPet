#####################################################################
# 新增共用變數(self._shareValue)                                     
#   SourceImage         => 原始相機影像(唯獨)
#   ShowImage           => 將顯示在視窗中的影像
#   FacrCatchArea       => 臉部追蹤範圍()
#   KeyDown             => 鍵盤按下的按鍵
#   MultiprocessingPool => 由Controller統一管理的進程池
# PetAction =>> PetController內執行的基本單位
#   InitialShareValue() => 需實做
#   Run()               => 需實作
#   KeyDown()           => 需實作
#   ShowTextInWindow()  => 將文字顯示在畫面上
#       text : 文字
#       org : 座標
#       fontFace : 字型
#       fontScale : 大小
#       color : 顏色
#       thickness : 線條寬度
#       lineType : 線條種類 
#####################################################################
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
    
    def ShowTextInWindow(self, text=None, org=(0, 30), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.7, color=(255, 0, 0), thickness=1, lineType=cv2.LINE_AA):
        if self._shareValue is None:
            raise RuntimeError("ShowTextInWindow() Only Execute In Run()")
        if text is None:
            return
        cv2.putText(self._shareValue.ShowImage, text, org, fontFace, fontScale, color, thickness, lineType)
        pass

class PetController(PetAction):
    def __init__(self):
        CAMERA_INDEX = config.getint("Camera", "Index")
        self._cap = cv2.VideoCapture(CAMERA_INDEX)
        if (config.getboolean("ShowControl", "CameraImgToWindow")):
            cv2.namedWindow(config.get("ShowControl", "CameraImgToWindow_WindowName"), cv2.WINDOW_AUTOSIZE)
        self._shareValue = ShareValue()
        self._shareValue.SourceImage = None
        self._shareValue.ShowImage = None
        self._shareValue.FaceCatchArea = None
        self._shareValue.KeyDown = ""
        self._shareValue.MultiprocessingPool = None
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
        with Pool(processes=cpus) as self._shareValue.MultiprocessingPool:
            for actInitialShareValue in self._actionList:
                actInitialShareValue.InitialShareValue()
            while(self._cap.isOpened()):
                # region cap read
                ret, self._shareValue.SourceImage = self._cap.read()
                if(not ret):
                    break
                self._shareValue.ShowImage = self._shareValue.SourceImage.copy()
                # endregion

                # region Action Run
                for actRun in self._actionList:
                    actRun.Run()
                # endregion

                # region show
                if self._shareValue.FaceCatchArea is not None:
                    cv2.rectangle(self._shareValue.ShowImage,
                                    (int(self._shareValue.FaceCatchArea.left()), int(self._shareValue.FaceCatchArea.top())),
                                    (int(self._shareValue.FaceCatchArea.right()), int(self._shareValue.FaceCatchArea.bottom())),
                                    (0, 0, 255), 4, cv2.LINE_AA)

                if (config.getboolean("ShowControl", "CameraImgToWindow")):
                    cv2.imshow(config.get("ShowControl", "CameraImgToWindow_WindowName"), self._shareValue.ShowImage)

                # endregion

                # region keyCode
                keyCode = cv2.waitKey(1)
                self._shareValue.KeyDown = keyCode & 0xFF
                if keyCode & 0xFF == ord('q'):
                    break  
                for actKeyDown in self._actionList:
                    actKeyDown.KeyDown()
                # endregion

            self._shareValue.MultiprocessingPool.terminate()
            self._shareValue.MultiprocessingPool.join()

        return
        # 釋放攝影機
        self._cap.release()
        # cv2.destroyAllWindows()
        pass

class ShareValue:
    pass

if __name__ == "__main__":
    pass