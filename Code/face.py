import sys
import os
import dlib
import glob
import numpy
import imutils
from cv2 import cv2 as cv2
import configparser

config = configparser.ConfigParser()
config.read('Config.ini')

# 載入正臉檢測器 Dlib 的人臉偵測器
detector = dlib.get_frontal_face_detector()
# 載入人臉關鍵點檢測器
predictor = dlib.shape_predictor(
    "Bat\\shape_predictor_68_face_landmarks.dat")
# 載入人臉識別模型
facerec = dlib.face_recognition_model_v1(
    "Bat\\dlib_face_recognition_resnet_model_v1.dat")


def CatchFace(img):
    
    # 偵測人臉
    face_rects, scores, idx = detector.run(img, 0)

    # 取出所有偵測的結果
    for i, d in enumerate(face_rects):
        x1 = d.left()
        y1 = d.top()
        x2 = d.right()
        y2 = d.bottom()

        imageVar = getImageVar(img[y1:y2, x1:x2])

        text = "%2.2f(%d)" % (scores[i], idx[i])

        print(int(imageVar))

        # if(int(imageVar) > 100):
        #     cv2.imwrite('Photo\\MasterSample' +
        #                 str(int(imgSet)) + '.jpg', img[y1:y2, x1:x2])

        # 以方框標示偵測到的人臉
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4, cv2.LINE_AA)
        cv2.putText(img, text, (x1, y1), cv2.FONT_HERSHEY_DUPLEX,
                    0.7, (255, 255, 255), 1, cv2.LINE_AA)

    return img


def CheckSampleWithCam(imgTarget, descriptors):
    # 對需識別人臉進行同樣處理
    # 提取描述子
    # imgTarget = io.imread(img_path)
    dets = detector(imgTarget, 0)
    dist = []
    if(len(dets) < 1):
        return

    for k, d in enumerate(dets):
        shape = predictor(imgTarget, d)
        face_descriptor = facerec.compute_face_descriptor(imgTarget, shape)
        d_test = numpy.array(face_descriptor)
        # 計算歐式距離
        for i in descriptors:
            dist_ = numpy.linalg.norm(i-d_test)
            dist.append(dist_)
            print(dist_)

    print(dist)


def ScanningMaster(img):
    catchFileCountLimit = int(config.get('MasterSample', 'Threshold'))
    catchFileTotal = int(config.get('MasterSample', 'Total'))
    MasterSamplePath = str(config.get('MasterSample', 'Path'))

    if not os.path.isdir(MasterSamplePath):
        os.mkdir(MasterSamplePath)

    catchFileCount = len(glob.glob(os.path.join(MasterSamplePath, "*.jpg")))

    if catchFileCount >= catchFileTotal :
        return True

    # 偵測人臉
    face_rects = detector(img, 0)
    if(len(face_rects) != 1):
        print('Can\'n catch face')
        return False

    faceImg = img[face_rects[0].top(): face_rects[0].bottom(),
                    face_rects[0].left(): face_rects[0].right()]
    imageVar = getImageVar(faceImg)

    print(imageVar)
    if(int(imageVar) > catchFileCountLimit and len(Get68FaceFromImg(faceImg)) != 0):
        cv2.imwrite(MasterSamplePath + '\\MasterSample' +
                    str(catchFileCount + 1) + '.jpg',
                    faceImg)

    return False


def getImageVar(image):

    img2gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    imageVar = cv2.Laplacian(img2gray, cv2.CV_64F).var()

    return imageVar

# 取得樣本描述子們
def GetSampleDescriptors():
    # 樣本目錄
    faces_folder_path = str(config.get('MasterSample', 'Path'))
    # 候選人臉描述子list
    descriptors = []
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
        for k, d in enumerate(dets):
            # 2.關鍵點檢測
            shape = predictor(img, d)
            # 畫出人臉區域和和關鍵點
            # 3.描述子提取，128D向量
            face_descriptor = facerec.compute_face_descriptor(img, shape)
            # 轉換為numpy array
            v = numpy.array(face_descriptor)
            descriptors.append(v)
    return descriptors

def Get68FaceFromImg(img):
    # 候選人臉描述子list
    descriptors = []

    # 1.人臉檢測
    dets = detector(img, 0)
    print("Number of faces detected: {}".format(len(dets)))
    for k, d in enumerate(dets):
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

# 在臉上顯示方塊
def PrintRectangleFaceWithdDetector(img, face_rects=[], rgb = (0, 255, 0)):

    for i, d in enumerate(face_rects):
        x1 = d.left()
        y1 = d.top()
        x2 = d.right()
        y2 = d.bottom()

        # 以方框標示偵測到的人臉
        cv2.rectangle(img, (x1, y1), (x2, y2), rgb, 4, cv2.LINE_AA)

    return img

# 在臉上顯示68個關鍵點
def Print68Face(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # 人臉數rects
    rects = detector(img_gray, 0)
    for i in range(len(rects)):
        landmarks = numpy.matrix(
            [[p.x, p.y] for p in predictor(img, rects[i]).parts()])  # 人臉關鍵點識別
        for idx, point in enumerate(landmarks):  # enumerate函式遍歷序列中的元素及它們的下標
            # 68點的座標
            pos = (point[0, 0], point[0, 1])
            print(idx, pos)

            # 利用cv2.circle給每個特徵點畫一個圈，共68個
            cv2.circle(img, pos, 5, color=(0, 255, 0))
            # 利用cv2.putText輸出1-68
            font = cv2.FONT_HERSHEY_SIMPLEX
            # 各引數依次是：圖片，新增的文字，座標，字型，字型大小，顏色，字型粗細
            cv2.putText(img, str(idx+1), pos, font, 0.8,
                        (0, 0, 255), 1, cv2.LINE_AA)

    return img
    # cv2.namedWindow("img", 2)
    # cv2.imshow("img", img)       #顯示影象
    # cv2.waitKey(0)        #等待按鍵，隨後退出


def MasterCatch(imgTarget, descriptors):
    euclideanDistanceThreshold = float(config.get(
        'MasterRecognize', 'EuclideanDistanceThreshold'))

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

    for k, d in enumerate(dets):
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

        x1 = d.left()
        y1 = d.top()
        x2 = d.right()
        y2 = d.bottom()
        facerRectangle.append(d)
        # cv2.rectangle(imgTarget, (x1, y1), (x2, y2),
        #               (0, 255, 0), 4, cv2.LINE_AA)

        # 如果在允許範圍之內則加入faceInThr
        if(distance < euclideanDistanceThreshold):
            facerSimilarRectangle.append(d)
            # cv2.rectangle(imgTarget, (x1, y1), (x2, y2),
            #               (255, 0, 0), 4, cv2.LINE_AA)
            # faceInThr.append([d, distance])

    if len(faceInThr) <= 1:
        return catch, facerSimilarRectangle, facerRectangle

    minDisFace = faceInThr[0]
    for i, d in enumerate(faceInThr):
        if d[1] < minDisFace[1]:
            minDisFace = d

    catch = minDisFace[0]
    # cv2.rectangle(imgTarget, (catch.left(), catch.top()),
    #               (catch.right(), catch.bottom()), (0, 0, 255), 4, cv2.LINE_AA)

    return catch, facerSimilarRectangle, imgTarget

