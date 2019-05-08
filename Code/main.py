from cv2 import cv2
import face as face
import configparser
import dlib
import shutil
import glob
import os

config = configparser.ConfigParser()
config.read('Config.ini')

tracker = dlib.correlation_tracker()   # 導入correlation_tracker()


def TrackerOverWindow(catchRec, imgRecHeight, imgRecWidth):
    midX = (catchRec.left() + catchRec.right()) / 2
    midY = (catchRec.top() + catchRec.bottom()) / 2
    if midX < 0 or midX > imgRecWidth:
        return False
    if midY < 0 or midY > imgRecHeight:
        return False

    return True


if __name__ == '__main__':
    # 樣本描述子們
    descriptors = face.GetSampleDescriptors()

    MasterExist = False
    IsSampleReady = False

    # 選擇預設攝影機
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("show", cv2.WINDOW_AUTOSIZE)

    while(cap.isOpened()):
        ret, img = cap.read()
        imgText = ''
        if(not ret):
            break

        facerRectangle = []
        facerSimilarRectangle = []
        catch = None

        if IsSampleReady:
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

            imgText = 'Ok'

        else:
            # 獲取樣本
            IsSampleReady = face.ScanningMaster(img)
            if IsSampleReady:
                # 重新讀取樣本描述子們
                descriptors = face.GetSampleDescriptors()
            imgText = 'Scanning'

        # face.PrintRectangleFaceWithdDetector(img, facerRectangle, (0, 255, 0))
        # face.PrintRectangleFaceWithdDetector(img, facerSimilarRectangle, (255, 0, 0))
        cv2.putText(img, imgText, (0, 30), cv2.FONT_HERSHEY_DUPLEX,
                    0.7, (255, 0, 0), 1, cv2.LINE_AA)

        cv2.imshow('show', img)

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
