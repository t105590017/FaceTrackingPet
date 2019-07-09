import serial
import configparser
from enum import Enum
from PetController import PetAction
from FaceDetectorAction import MasterDetectorState

#region 公用參數
config = configparser.ConfigParser()
config.read("Config.ini")
#endregion

#Serial訊號列舉
class SerialSignalEnum(Enum):
    GET = 'G'
    FACE = 'F'
    HAND = 'H'

#Serial溝通Action
class SerialAction(PetAction):
    def __init__(self):
        #region Serial Initialization
        COM_PORT = str(config.get('Arduino', 'COM_PORT'))
        BAUD_RATE = int(config.get('Arduino', 'BAUD_RATES'))
        self._serial = serial.Serial(COM_PORT, BAUD_RATE)
        #endregion
        pass
    def InitialShareValue(self):
        pass

    def Run(self):
        #如果抓到臉就傳送訊號
        if (self._shareValue._faceDetectorStatus == MasterDetectorState.CATCHED.value):
            self._serial.write(SerialSignalEnum.GET.value.encode())
            self._serial.write(SerialSignalEnum.FACE.value.encode())
            print("Get face and send serial signal")
        else:
            self._serial.write(SerialSignalEnum.GET.value.encode())
            self._serial.write(SerialSignalEnum.HAND.value.encode())
        pass

    def KeyDown(self):
        pass