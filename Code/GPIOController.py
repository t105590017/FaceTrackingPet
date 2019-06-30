import configparser
from colorama import Fore
from configparser import ConfigParser
import pexpect

gpioInfo = ConfigParser()
gpioInfo.read("gpioConfig.ini")

AutoTerminalEnable = False

def AutoTerminalGetPermisssion():
    if not AutoTerminalEnable:
        return []

    child = pexpect.spawn("sudo -i")
    child.expect([":", "#", pexpect.EOF, pexpect.TIMEOUT])
    child.sendline(gpioInfo.get("UserPassword", "rootPassword"))
    return child

def AutoTerminal(command, child = None):
    if not AutoTerminalEnable:
        return None

    if child is None:
        child = pexpect.spawn(command)
        return child
    
    child.expect(["#", pexpect.EOF, pexpect.TIMEOUT])
    child.sendline(command)
    return child

def AutoTerminalClose(child = None):
    if child is None or not AutoTerminalEnable:
        return
    child.expect("#")
    child.close(force = False)
    # return None

class NormalGPIO:
    def __init__(self):
        self.usingList = []
        self._controlPath = "/sys/class/gpio"
        self._gpioMap = gpioInfo["NumberOfNormalGPIO"]

    def __del__(self):
        for gpio in self.usingList:
            self.Value(gpio, "0")
            self.Direction(gpio, "in")
        self.UnExport("ALL")

    def Export(self, pinNumber, direction = "out"):
        if pinNumber not in self._gpioMap:
            print("{0}[ERROR]{1} pin number {2} can't be use !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        if pinNumber.upper() in self.usingList:
            print("{0}[ERROR]{1} pin number {2} has be used !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + self._gpioMap[pinNumber] + " > " + self._controlPath + "/export", child)
        AutoTerminal("echo " + direction + " > " + self._controlPath + "/gpio" + self._gpioMap[pinNumber] + "/direction", child)        
        AutoTerminalClose(child)
        print("{0}[SUCCESS]{1} pin number {2} export".format(Fore.GREEN, Fore.RESET, pinNumber))
        self.usingList.append(pinNumber.upper())
        return True

    def UnExport(self, pinNumber = "ALL"):
        if pinNumber == "ALL":
            child = AutoTerminalGetPermisssion()
            for gpio in self.usingList:
                AutoTerminal("echo " + self._gpioMap[gpio] + " > " + self._controlPath + "/unexport", child)
                print("{0}[SUCCESS]{1} pin number {2} unexport".format(Fore.GREEN, Fore.RESET, pinNumber))
            
            self.usingList.clear()
            AutoTerminalClose(child)         
            return True

        if pinNumber.upper() not in self.usingList:
            print("{0}[ERROR]{1} pin number {2} can't be unexport !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + self._gpioMap[pinNumber] + " > " + self._controlPath + "/unexport", child)
        AutoTerminalClose(child)
        print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " pin number "+ pinNumber + " unexport")
        self.usingList.remove(pinNumber.upper())
        return True

    def Value(self, pinNumber, value):
        if pinNumber.upper() not in self.usingList:
            print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + value + " > " + self._controlPath + "/gpio" + self._gpioMap[pinNumber] + "/value", child)
        AutoTerminalClose(child)
        print("{0}[SUCCESS]{1} pin number {2} set value to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, value))
        return True

    def Direction(self, pinNumber, direction):
        if pinNumber.upper() not in self.usingList:
            print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + direction + " > " + self._controlPath + "/gpio" + self._gpioMap[pinNumber] + "/direction", child)
        AutoTerminalClose(child)
        print("{0}[SUCCESS]{1} pin number {2} set direction to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, direction))
        return True
        
class PwmGPIO:
    def __init__(self):
        self.usingList = []
        self._controlPath = "/sys/class/pwm"
        self._gpioMap = gpioInfo["NumberOfPwmGPIO"]
        self._period = -1

    def __del__(self):
        # for gpio in self.usingList:
        #     pass
        self.UnExport("ALL")

    def Export(self, pinNumber):
        if pinNumber not in self._gpioMap:
            print("{0}[ERROR]{1} pin number {2} can't be use !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        if pinNumber.upper() in self.usingList:
            print("{0}[ERROR]{1} pin number {2} has be used !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo 0 > " + self._controlPath + "/" + self._gpioMap[pinNumber] + "/export", child)      
        AutoTerminalClose(child)
        print("{0}[SUCCESS]{1} pin number {2} export".format(Fore.GREEN, Fore.RESET, pinNumber))
        self.usingList.append(pinNumber.upper())

    def UnExport(self, pinNumber = "ALL"):
        # if pinNumber == "ALL":
        #     child = AutoTerminalGetPermisssion()
        #     for gpio in self.usingList:
        #         AutoTerminal("echo " + self._gpioMap[gpio] + " > " + self._controlPath + "/unexport", child)
        #         print("{0}[SUCCESS]{1} pin number {2} unexport".format(Fore.GREEN, Fore.RESET, pinNumber))
            
        #     self.usingList.clear()
        #     AutoTerminalClose(child)         
        #     return True

        # if pinNumber.upper() not in self.usingList:
        #     print("{0}[ERROR]{1} pin number {2} can't be unexport !!".format(Fore.RED, Fore.RESET, pinNumber))
        #     return False

        # child = AutoTerminalGetPermisssion()
        # AutoTerminal("echo " + self._gpioMap[pinNumber] + " > " + self._controlPath + "/unexport", child)
        # AutoTerminalClose(child)
        # print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " pin number "+ pinNumber + " unexport")
        # self.usingList.remove(pinNumber.upper())
        # return True
        pass

    def Period(self, pinNumber, period):
        if pinNumber.upper() not in self.usingList:
            print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + str(period) + " > " + self._controlPath + "/" + self._gpioMap[pinNumber] + "/pwm0/period", child)      
        AutoTerminalClose(child)
        self._period = period
        print("{0}[SUCCESS]{1} pin number {2} set period to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, period))
        return True

    def DutyCycle(self, pinNumber, dutyCycle):
        if pinNumber.upper() not in self.usingList:
            print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        if self._period is -1:
            print("{0}[ERROR]{1} pin number {2} need set period first !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + str(int(self._period * dutyCycle)) + " > " + self._controlPath + "/" + self._gpioMap[pinNumber] + "/pwm0/duty_cycle", child)      
        AutoTerminalClose(child)
        print("{0}[SUCCESS]{1} pin number {2} set dutyCycle to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, int(self._period * dutyCycle)))
        return True

    def Enable(self, pinNumber, enable = True):
        if pinNumber.upper() not in self.usingList:
            print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + str(1 if enable else 0) + " > " + self._controlPath + "/" + self._gpioMap[pinNumber] + "/pwm0/enable", child)      
        AutoTerminalClose(child)
        print("{0}[SUCCESS]{1} pin number {2} set enable to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, 1 if enable else 0))
        return True




if __name__ == "__main__":
    import time

    # n = NormalGPIO()

    # n.Export("1d3")
    # n.Export("1")
    # n.Export("12aS")
    # n.Export("pIn37")
    # n.Export("linux25")

    # n.Value("pin37", "1")

    # time.sleep(2)

    # n.Value("pin37", "0")

    # time.sleep(2)

    # n.Value("Pin37", "1")

    # time.sleep(2)

    p = PwmGPIO()

    p.Export("dsa")
    p.Export("PIN33")
    p.Export("pin33")

    p.DutyCycle("pin33", 0.5)
    p.Period("pin33", 3413333)
    p.DutyCycle("pin33", 0.5)

    p.Enable("pin33", True)
    p.Enable("pin26", True)

    print(p.usingList)
