import sys
import os
import dlib
import glob
import numpy
import imutils
from cv2 import cv2 as cv2
import configparser
from enum import Enum
import multiprocessing
from multiprocessing import Pool
import traceback
from PetController import PetAction

#region 公用參數
config = configparser.ConfigParser()
config.read("Config.ini")
# 載入正臉檢測器 Dlib 的人臉偵測器
detector = dlib.get_frontal_face_detector()
# 載入人臉關鍵點檢測器
predictor = dlib.shape_predictor("Bat/shape_predictor_68_face_landmarks.dat")
# 載入人臉識別模型
facerec = dlib.face_recognition_model_v1("Bat/dlib_face_recognition_resnet_model_v1.dat")
# 導入correlation_tracker()
tracker = dlib.correlation_tracker()
#endregion

# region catch Master
# 取得清晰度
def getImageVar(image):

    img2gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    imageVar = cv2.Laplacian(img2gray, cv2.CV_64F).var()

    return imageVar

# 取得樣本描述子們
def Get68FaceFromImg(img):
    # 候選人臉描述子list
    descriptors = []

    # 1.人臉檢測
    dets = detector(img, 0)
    print("Number of faces detected: {}".format(len(dets)))
    for d in dets:
        # 2.關鍵點檢測
        shape = predictor(img, d)
        # 畫出人臉區域和和關鍵點
        # 3.描述子提取，128D向量
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        # 轉換為numpy array
        v = numpy.array(face_descriptor)
        descriptors.append(v)

    if(len(descriptors) == 0):
        print("Face68 predictor error!!")

    return descriptors

def ScanningMaster(img):
        catchAreaThreshol = config.getint("MasterSample", "Threshold")
        catchFileTotal = config.getint("MasterSample", "Total")
        MasterSamplePath = config.get("MasterSample", "Path")

        if not os.path.isdir(MasterSamplePath):
            os.mkdir(MasterSamplePath)

        catchFileCount = len(glob.glob(os.path.join(MasterSamplePath, "*.jpg")))

        if catchFileCount >= catchFileTotal:
            return True

        # 偵測人臉
        face_rects = detector(img, 0)
        if(len(face_rects) != 1):
            if(config.getboolean("ShowControl", "TerminalMessage_CatchFaceExist")):
                print("Can\"n catch face")
            return False

        faceImg = img[face_rects[0].top(): face_rects[0].bottom(),
                    face_rects[0].left(): face_rects[0].right()]
        imageVar = getImageVar(faceImg)

        print(imageVar)
        if(int(imageVar) > catchAreaThreshol and len(Get68FaceFromImg(faceImg)) != 0):
            cv2.imwrite(MasterSamplePath + "/MasterSample" +
                        str(catchFileCount + 1) + ".jpg",
                        faceImg)

        return False

def TrackerOverWindow(catchRec, imgRecHeight, imgRecWidth):
    midX = (catchRec.left() + catchRec.right()) / 2
    midY = (catchRec.top() + catchRec.bottom()) / 2
    if midX < 0 or midX > imgRecWidth:
        return True
    if midY < 0 or midY > imgRecHeight:
        return True
    return False
#endregion

# region multiprocessing
def TrackerAreaExistFace(q, img):
    face_rects = detector(img, 0)

    q.put(bool(len(face_rects) == 1))

def handle_error(e):
    #處理 child process 的錯誤，不然 code 寫錯時，不會回報任何錯誤
    traceback.print_exception(type(e), e, e.__traceback__)
#endregion

class MasterDetectorState(Enum):
    #Samply not ready
    SAMPLE_NO_READY = "Scanning"
    # Sample ready
    CATCHED = "Catch" # Master face is be catched
    LOST = "Lost" # Master face is lose

class MasterDetector:
    def __init__(self, pool, queue):
        self._status = MasterDetectorState.SAMPLE_NO_READY
        # 候選人臉描述子list
        self._descriptors = []
        self._catchArea = None
        self._pool = pool
        self._queue = queue
        self._faceLostFramesCount = 0

    def __del__(self):
        pass

    def GetSampleDescriptors(self):
        # 樣本目錄
        faces_folder_path = config.get("MasterSample", "Path")
        # 對資料夾下的每一個人臉進行:
        # 1.人臉檢測
        # 2.關鍵點檢測
        # 3.描述子提取
        for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
            print("Processing file: {}".format(f))
            img = cv2.imread(f)
            # 1.人臉檢測
            dets = detector(img, 0)
            print("Number of faces detected: {}".format(len(dets)))
            for d in dets:
                # 2.關鍵點檢測
                shape = predictor(img, d)
                # 畫出人臉區域和和關鍵點
                # 3.描述子提取，128D向量
                face_descriptor = facerec.compute_face_descriptor(img, shape)
                # 轉換為numpy array
                v = numpy.array(face_descriptor)
                self._descriptors.append(v)
        return self._descriptors

    def MasterCatch(self, imgTarget, descriptors):
        euclideanDistanceThreshold = config.getfloat("MasterRecognize", "EuclideanDistanceThreshold")

        # 對需識別人臉進行同樣處理
        # 提取描述子
        dets = detector(imgTarget, 0)
        dist = []
        faceInThr = []
        facerRectangle = []
        facerSimilarRectangle = []
        catch = None
        if(len(dets) < 1):
            return catch, facerSimilarRectangle, facerRectangle

        for d in dets:
            shape = predictor(imgTarget, d)
            face_descriptor = facerec.compute_face_descriptor(imgTarget, shape)
            d_test = numpy.array(face_descriptor)
            distance = 0
            # 計算歐式距離
            for i in descriptors:
                dist_ = numpy.linalg.norm(i-d_test)
                dist.append(dist_)
                print(dist_)
                distance += dist_

            distance /= len(descriptors)

            facerRectangle.append(d)

            # 如果在允許範圍之內則加入faceInThr
            if(distance < euclideanDistanceThreshold):
                facerSimilarRectangle.append(d)
                faceInThr.append([d, distance])

        if len(faceInThr) <= 1:
            return facerSimilarRectangle[0] if len(facerSimilarRectangle) == 1 else None, facerSimilarRectangle, facerRectangle

        minDisFace = faceInThr[0]
        for i, d in enumerate(faceInThr):
            if d[1] < minDisFace[1]:
                minDisFace = d

        catch = minDisFace[0]

        return catch, facerSimilarRectangle, facerRectangle

    def CatchArea(self):
        return self._catchArea

    def CheckCatchAreaIsMaster(self, img):
        if not config.getboolean('Enable', 'MultiProcessing'):
            return None

        if self._catchArea is not None:
            self._pool.apply_async(TrackerAreaExistFace,
                            args=(self._queue, img[int(self._catchArea.top()):int(self._catchArea.bottom()),
                                        int(self._catchArea.left()):int(self._catchArea.right())], ),
                            error_callback=handle_error)

        if(not self._queue.empty()):
            faceInCatch = self._queue.get()
            if(faceInCatch):
                self._faceLostFramesCount = 0
                print("get face : True")
                return True
            else:
                self._faceLostFramesCount += 1
                faceLostFrames = config.getint('Limit', 'FaceTarckingLostFrames')
                if(self._faceLostFramesCount >= faceLostFrames):
                    self._faceLostFramesCount = 0
                    self._status = MasterDetectorState.LOST
                print("get face : False")
                return False

    def Status(self, status = None):
        if status is not None:
            self._status = status
        return self._status

    def RunCatchMaster(self, img):
        if self._status is MasterDetectorState.SAMPLE_NO_READY:
            IsSampleReady = ScanningMaster(img)
            if IsSampleReady:
                self.GetSampleDescriptors()
                self._status = MasterDetectorState.LOST
            return self._status
        
        if self._status is MasterDetectorState.LOST:
            if self._descriptors is []:
                self._status = MasterDetectorState.SAMPLE_NO_READY
            catch, facerSimilarRectangle, facerRectangle = self.MasterCatch(img, self._descriptors)
            if(len(facerSimilarRectangle) >= 1):
                tracker.start_track(img, catch)
                self._catchArea = catch
                self._status = MasterDetectorState.CATCHED

        if self._status is MasterDetectorState.CATCHED:
            tracker.update(img)
            self._catchArea = tracker.get_position()
            if TrackerOverWindow(self._catchArea, img.shape[0], img.shape[1]):
                self._status = MasterDetectorState.LOST

        self.CheckCatchAreaIsMaster(img)

        return self._status

class FaceDetectorAction(PetAction):
    
    def InitalShareValue(self):
        self._cm = MasterDetector(self._shareValue._pool, self._shareValue._queue)

    def Run(self):
        self._shareValue._status = self._cm.RunCatchMaster(self._shareValue._img)
        self._shareValue._catch = self._cm.CatchArea()
        self._shareValue._imgText = self._shareValue._status.value
        pass

    def KeyDown(self):
        if self._shareValue._keyDown == ord('r'):
            for f in glob.glob(os.path.join(config.get('MasterSample', 'Path'), "*.jpg")):
                print("Delete file: {}".format(f))
                os.remove(f)
            self._cm.Status(MasterDetectorState.SAMPLE_NO_READY)
        if self._shareValue._keyDown == ord('x'):
            self._cm.Status(MasterDetectorState.LOST)
        pass
        
if __name__ == "__main__":
    pass
