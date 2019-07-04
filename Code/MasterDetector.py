import sys
import os
import dlib
import glob
import numpy
import imutils
from cv2 import cv2 as cv2
import configparser
from enum import Enum

config = configparser.ConfigParser()
config.read('Config.ini')

class MasterDetectorState(Enum):
    INITIAL = "initial"
    READY = "Ready" # Master face sample ready
    CATCHED = "Catch" # Master face is be catched
    LOST = "Lost" # Master face is lose


class MasterDetector:
    def __init__(self, cap):
        # 載入正臉檢測器 Dlib 的人臉偵測器
        self._detector = dlib.get_frontal_face_detector()
        # 載入人臉關鍵點檢測器
        self._predictor = dlib.shape_predictor("Bat/shape_predictor_68_face_landmarks.dat")
        # 載入人臉識別模型
        self._facerec = dlib.face_recognition_model_v1("Bat/dlib_face_recognition_resnet_model_v1.dat")
        # VideoCapture
        self._cap = cap

    def __del__(self):
        pass

    def RunCatchMaster(self):
        while(self._cap.isOpened()):
            pass
    

if __name__ == "__main__":
    pass
