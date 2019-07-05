from cv2 import cv2
import configparser
import os
import glob
import multiprocessing
from multiprocessing import Pool
from MasterDetector import MasterDetector, MasterDetectorState

config = configparser.ConfigParser()
config.read("Config.ini")

class PetAction:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def Run(self):
        raise RuntimeError()

class PetController(PetAction):
    def __init__(self):
        CAMERA_INDEX = config.getint("Camera", "Index")
        self._catch = None
        self._imgText = ""
        self._cap = cv2.VideoCapture(CAMERA_INDEX)
        if (config.getboolean("ShowControl", "CameraImgToWindow")):
            cv2.namedWindow(config.get("ShowControl", "CameraImgToWindow_WindowName"), cv2.WINDOW_AUTOSIZE)
        self._queue = multiprocessing.Manager().Queue()
        multiprocessing.freeze_support()
        self._actionList = []
        pass

    def __del__(self):
        pass

    def AddNowAction(self, action):
        self._actionList.append(action)

    def Run(self):
        cpus = multiprocessing.cpu_count()
        with Pool(processes=cpus) as p:
            cm = MasterDetector(p, self._queue)
            while(self._cap.isOpened()):
                # region cap read
                ret, img = self._cap.read()
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
                if (config.getboolean("ShowControl", "CameraImgToWindow")):
                    cv2.imshow(config.get("ShowControl", "CameraImgToWindow_WindowName"), img)
                    
                # endregion

                # region Hardware
                # imgH, imgW = img.shape[:2]
                # if catch is not None:
                #     catchX = (int(catch.left()) + int(catch.right())) / 2
                #     catchY = (int(catch.top()) + int(catch.bottom())) / 2
                #     HardwareInterface(catchX * 100 // imgW, catchY * 100 // imgH)
                # else:
                #     HardwareInterface(50, 50)
                # endregion

                # region keyCode
                keyCode = cv2.waitKey(1)
                if keyCode & 0xFF == ord('q'):
                    break
                if keyCode & 0xFF == ord('r'):
                    for f in glob.glob(os.path.join(config.get('MasterSample', 'Path'), "*.jpg")):
                        print("Delete file: {}".format(f))
                        os.remove(f)
                    cm.Status(MasterDetectorState.SAMPLE_NO_READY)
                if keyCode & 0xFF == ord('x'):
                    cm.Status(MasterDetectorState.LOST)
                # endregion
                
                # region else action
                for act in self._actionList:
                    act.Run()
                # endregion

            p.terminate()
            p.join()

        # 釋放攝影機
        self._cap.release()
        cv2.destroyAllWindows()
        pass
    
    
if __name__ == "__main__":
    p = PetController()
    p.Run()

    pass