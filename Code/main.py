from PetController import PetController
from FaceDetectorAction import FaceDetectorAction
from CameraMoveAction import CameraMoveAction
from SerialAction import SerialAction
 
if __name__ == '__main__':
    print("Begin")
    
    pc = PetController()

    fda = FaceDetectorAction()
    pc.AddNewAction(fda)

    serialAction = SerialAction()
    pc.AddNewAction(serialAction)

    cma = CameraMoveAction()
    pc.AddNewAction(cma)

    pc.Run()
    