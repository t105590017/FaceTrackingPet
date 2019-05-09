from cv2 import cv2
import face as face
import configparser
import dlib
import shutil
import glob
import os
import multiprocessing
from multiprocessing import Pool
import time
import traceback

config = configparser.ConfigParser()
config.read('Config.ini')

tracker = dlib.correlation_tracker()            # 導入correlation_tracker()
detector = dlib.get_frontal_face_detector()     # 載入正臉檢測器 Dlib 的人臉偵測器


def handle_error(e):
    '''處理 child process 的錯誤，不然 code 寫錯時，不會回報任何錯誤'''
    traceback.print_exception(type(e), e, e.__traceback__)


def TrackerOverWindow(catchRec, imgRecHeight, imgRecWidth):
    midX = (catchRec.left() + catchRec.right()) / 2
    midY = (catchRec.top() + catchRec.bottom()) / 2
    if midX < 0 or midX > imgRecWidth:
        return False
    if midY < 0 or midY > imgRecHeight:
        return False

    return True


def TrackerAreaExistFace(q, img):
    global detector

    face_rects, scores, idx = detector.run(img, 0)

    # print("face Number :", len(face_rects))
    q.put(len(face_rects))
    return len(face_rects) == 1


if __name__ == '__main__':

    # region 變數
    # 樣本描述子們
    descriptors = face.GetSampleDescriptors()

    MasterExist = False
    IsSampleReady = False

    facerRectangle = []
    facerSimilarRectangle = []
    catch = None
    # endregion

    def SampleReady(img):
        global MasterExist, catch, facerSimilarRectangle, facerRectangle, descriptors, tracker

        if not MasterExist:
            catch, facerSimilarRectangle, facerRectangle = face.MasterCatch(
                img, descriptors)
            if(len(facerSimilarRectangle) == 1):
                catch = facerSimilarRectangle[0]
                tracker.start_track(img, catch)
                MasterExist = True

        else:
            tracker.update(img)
            catch = tracker.get_position()
            MasterExist = TrackerOverWindow(catch, img.shape[0], img.shape[1])

        if catch is not None:
            cv2.rectangle(img, (int(catch.left()), int(catch.top())), (int(
                catch.right()), int(catch.bottom())), (0, 0, 255), 4, cv2.LINE_AA)

        return 'Ok'

    def ImageProcessing(img):
        global IsSampleReady, descriptors

        imgText = ''

        if IsSampleReady:
            imgText = SampleReady(img)
        else:
            IsSampleReady = face.ScanningMaster(img)
            if IsSampleReady:
                descriptors = face.GetSampleDescriptors()
            imgText = 'Scanning'

        cv2.putText(img, imgText, (0, 30), cv2.FONT_HERSHEY_DUPLEX,
                    0.7, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.imshow('show', img)

    # 選擇預設攝影機
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("show", cv2.WINDOW_AUTOSIZE)

    q = multiprocessing.Manager().Queue()
    multiprocessing.freeze_support()
    with Pool(processes=3) as p:
        while(cap.isOpened()):
            ret, img = cap.read()
            if(not ret):
                break

            ImageProcessing(img)

            p.apply_async(TrackerAreaExistFace,
                          args=(q, img,),
                          error_callback=handle_error)

            if(not q.empty()):
                print("get face :", q.get())

            # region keyCode
            keyCode = cv2.waitKey(1)
            if keyCode & 0xFF == ord('q'):
                break
            if keyCode & 0xFF == ord('r'):
                for f in glob.glob(os.path.join(config.get('MasterSample', 'Path'), "*.jpg")):
                    print("Delete file: {}".format(f))
                    os.remove(f)
                IsSampleReady = False
            if keyCode & 0xFF == ord('x'):
                MasterExist = False
            # endregion

        p.terminate()
        p.join()

    # while(cap.isOpened()):
    #     ret, img = cap.read()
    #     if(not ret):
    #         break

    #     ImageProcessing(img)

    #     #region keyCode
    #     keyCode = cv2.waitKey(1)
    #     if keyCode & 0xFF == ord('q'):
    #         break
    #     if keyCode & 0xFF == ord('r'):
    #         for f in glob.glob(os.path.join(config.get('MasterSample', 'Path'), "*.jpg")):
    #             print("Delete file: {}".format(f))
    #             os.remove(f)
    #         IsSampleReady = False
    #     if keyCode & 0xFF == ord('x'):
    #         MasterExist = False
    #     #endregion

    # 釋放攝影機
    cap.release()
    cv2.destroyAllWindows()
