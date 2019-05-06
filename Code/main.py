from cv2 import cv2
import face as face
import configparser
import dlib
import shutil
import glob, os

config = configparser.ConfigParser()
config.read('Config.ini')

# 選擇預設攝影機
cap = cv2.VideoCapture(0)

cv2.namedWindow("show", cv2.WINDOW_AUTOSIZE)

# 獲取樣本
# scanningSuccess = face.ScanningMaster(img)

# 樣本描述子們
descriptors = face.GetSampleDescriptors()

IsSampleReady = False

while(cap.isOpened()):
    ret, result = cap.read()
    resultText = ''
    if(not ret):
        break

    facerRectangle = []
    facerSimilarRectangle = []
    catch = []

    if IsSampleReady:
        catch, facerSimilarRectangle, facerRectangle = face.MasterCatch(result, descriptors)
        resultText = 'Ok'
    else:
        # 獲取樣本
        IsSampleReady = face.ScanningMaster(result)
        if IsSampleReady :
            # 重新讀取樣本描述子們
            descriptors = face.GetSampleDescriptors()
        resultText = 'Scanning'

    face.PrintRectangleFaceWithdDetector(result, facerRectangle, (0, 255, 0))
    face.PrintRectangleFaceWithdDetector(result, facerSimilarRectangle, (255, 0, 0))
    face.PrintRectangleFaceWithdDetector(result, catch, (0, 0, 255))
    cv2.putText(result, resultText, (0, 30), cv2.FONT_HERSHEY_DUPLEX,
                0.7, (255, 0, 0), 1, cv2.LINE_AA)

    cv2.imshow('show', result)

    keyCode = cv2.waitKey(1)
    # 若按下 q 鍵則離開迴圈
    if keyCode & 0xFF == ord('q'):
        break
    if keyCode & 0xFF == ord('r'):
        for f in glob.glob(os.path.join(config.get('MasterSample', 'Path'), "*.jpg")):
            print("Delete file: {}".format(f))
            os.remove(f)
        IsSampleReady = False

# 釋放攝影機
cap.release()
cv2.destroyAllWindows()