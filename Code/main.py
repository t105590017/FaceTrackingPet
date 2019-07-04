from cv2 import cv2
# import face as face
import configparser
import dlib
import shutil
import glob
import os
import multiprocessing
from multiprocessing import Pool
import traceback
from MasterDetector import MasterDetector, MasterDetectorState

# import serial

config = configparser.ConfigParser()
config.read('Config.ini')

##Servo連接參數
ser = None
servoAngleX = 90
servoAngleY = 90
#Servo停止允許的範圍 (50+-Interval)%
servoXInterval = 5
servoYInterval = 12
#Servo最大角度
MAX_ANGLE = 160
MIN_ANGLE = 20

def HardwareInterface(x, y):
    # global servoAngleX, servoAngleY, servoXInterval, servoYInterval
    # servoAngleX = RotateServo(x, 'X', servoAngleX, servoXInterval)
    # servoAngleY = RotateServo(y,'Y',servoAngleY, servoYInterval)
    pass

def RotateServo(position, xy, angle, interval):
    global ser, MAX_ANGLE, MIN_ANGLE
    # if (position < 50 - interval):
    #     if (angle < MAX_ANGLE):
    #         angle = angle - 1
    #     ser.write('S'.encode())
    #     ser.write(xy.encode())
    #     ser.write((str(angle) + '\r').encode())
    # elif (position > 50 + interval):
    #     if (angle > MIN_ANGLE):
    #         angle = angle + 1
    #     ser.write('S'.encode())
    #     ser.write(xy.encode())
    #     ser.write((str(angle) + '\r').encode())
    return angle
 
if __name__ == '__main__':
    CAMERA_INDEX = int(config.get('Camera', 'Index'))
    # region 變數
    catch = None
    imgText = ''
    # endregion

    # 選擇預設攝影機
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cv2.namedWindow('show', cv2.WINDOW_AUTOSIZE)

    q = multiprocessing.Manager().Queue()
    multiprocessing.freeze_support()
    cpus = multiprocessing.cpu_count()
    with Pool(processes=cpus) as p:
        cm = MasterDetector(p, q)
        while(cap.isOpened()):
            # region cap read
            ret, img = cap.read()
            if(not ret):
                break
            # endregion

            # region catch
            st = cm.RunCatchMaster(img)
            catch = cm.CatchArea()
            imgText = st.value
            # endregion

            # region show
            if catch is not None:
                cv2.rectangle(img,
                                (int(catch.left()), int(catch.top())),
                                (int(catch.right()), int(catch.bottom())),
                                (0, 0, 255), 4, cv2.LINE_AA)

            cv2.putText(img, imgText, (0, 30), cv2.FONT_HERSHEY_DUPLEX,
                        0.7, (255, 0, 0), 1, cv2.LINE_AA)
            cv2.imshow('show', img)
            # endregion

            # region Hardware
            imgH, imgW = img.shape[:2]
            if catch is not None:
                catchX = (int(catch.left()) + int(catch.right())) / 2
                catchY = (int(catch.top()) + int(catch.bottom())) / 2
                HardwareInterface(catchX * 100 // imgW, catchY * 100 // imgH)
            else:
                HardwareInterface(50, 50)
            # endregion

            # region keyCode
            keyCode = cv2.waitKey(1)
            if keyCode & 0xFF == ord('q'):
                break
            if keyCode & 0xFF == ord('r'):
                for f in glob.glob(os.path.join(config.get('MasterSample', 'Path'), "*.jpg")):
                    print("Delete file: {}".format(f))
                    os.remove(f)
                cm.ChangeStatus(MasterDetectorState.SAMPLE_NO_READY)
            if keyCode & 0xFF == ord('x'):
                cm.ChangeStatus(MasterDetectorState.LOST)
            # endregion

        p.terminate()
        p.join()

    # 釋放攝影機
    cap.release()
    cv2.destroyAllWindows()