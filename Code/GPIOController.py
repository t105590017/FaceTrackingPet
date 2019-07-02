import configparser
from colorama import Fore
from configparser import ConfigParser
import pexpect
import time

gpioInfo = ConfigParser()
gpioInfo.read("gpioConfig.ini")

AutoTerminalEnable = True

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
        for gpio in self.usingList:
            self.Enable(gpio, False)
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
        AutoTerminal("echo 0 > " + self._controlPath + "/" + self._gpioMap[pinNumber] + "/unexport", child)
        AutoTerminalClose(child)
        print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " pin number "+ pinNumber + " unexport")
        self.usingList.remove(pinNumber.upper())
        return True

    def Period(self, pinNumber, period):
        if pinNumber.upper() not in self.usingList:
            print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False
        
        if period < 0:
            print("{0}[ERROR]{1} pin number {2} must > 1 !!".format(Fore.RED, Fore.RESET, pinNumber))
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

        if dutyCycle > self._period:
            print("{0}[ERROR]{1} pin number {2} period must larger than dutyCycle !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + str(int(dutyCycle)) + " > " + self._controlPath + "/" + self._gpioMap[pinNumber] + "/pwm0/duty_cycle", child)      
        AutoTerminalClose(child)
        print("{0}[SUCCESS]{1} pin number {2} set dutyCycle to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, int(dutyCycle)))
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

class Servomotor:
    def __init__(self, servoModel, pin, resetAngle = None, initAngle = 0):
        self._pin = pin
        self._resetAngle = resetAngle
        self._minDutyCycle = gpioInfo.getint(servoModel, "MinDutyCycle")
        self._maxDutyCycle = gpioInfo.getint(servoModel, "MaxDutyCycle")
        self._maxAngle = gpioInfo.getint(servoModel, "MaxAngle")
        self._pwmGPIO = PwmGPIO()
        self._pwmGPIO.Export(pin)
        self._pwmGPIO.Period(pin, 3413333)
        self._pwmGPIO.Enable(pin, True)
    
    def __del__(self):
        if self._resetAngle is not None:
            self.ChangAngle(self._resetAngle)
        
        self._pwmGPIO.Enable(self._pin, False)
        self._pwmGPIO.UnExport(self._pin)

    def ChangAngle(self, angle):
        angle = angle % 360

        if angle > self._maxAngle:
            print("{0}[ERROR]{1} the angle is too large !!".format(Fore.RED, Fore.RESET))
            return False

        dutyCycle = (self._maxDutyCycle - self._minDutyCycle) * angle / self._maxAngle + self._minDutyCycle

        self._pwmGPIO.DutyCycle(self._pin, dutyCycle)
        print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " Servomotor change angle to " + str(angle) +" in pin number "+ self._pin)
        return True


if __name__ == "__main__":
    ##NormalGPIO
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

    # print(n.usingList)

    ##PwmGPIO
    # p = PwmGPIO()

    # p.Export("pin32")
    # p.Enable("pin32")

    # p.Period("pin32", 3413333)

    # p.DutyCycle("pin32", 1450000)
    # time.sleep(2)

    # p.DutyCycle("pin32", 1925000)
    # time.sleep(2)

    # p.DutyCycle("pin32", 975000)
    # time.sleep(2)

    # p.DutyCycle("pin32", 2400000)
    # time.sleep(2)

    # p.DutyCycle("pin32", 500000)
    # time.sleep(2)

    # p.UnExport("pin32")

    ## Servomotor
    s1 = Servomotor("SG90", "PIN32", resetAngle = 0)
    s2 = Servomotor("SG90", "PIN33", resetAngle = 0)

    s1.ChangAngle(90)
    time.sleep(2)

    s2.ChangAngle(45)
    time.sleep(2)

    s1.ChangAngle(135)
    time.sleep(2)

    s2.ChangAngle(180)
    time.sleep(2)

    s1.ChangAngle(0)
    time.sleep(2)

    s2.ChangAngle(135)
    time.sleep(2)
