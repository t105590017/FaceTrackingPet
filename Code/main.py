from PetController import PetController
from FaceDetectorAction import FaceDetectorAction
from CameraMoveAction import CameraMoveAction
 
if __name__ == '__main__':
    pc = PetController()

    fda = FaceDetectorAction()
    pc.AddNewAction(fda)

    cma = CameraMoveAction()
    pc.AddNewAction(cma)

    pc.Run()
    