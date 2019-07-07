import configparser
from colorama import Fore
from configparser import ConfigParser
import pexpect
import time
import os

config = configparser.ConfigParser()
config.read("Config.ini")

gpioInfo = ConfigParser()
gpioInfo.read("gpioConfig.ini")

class NormalGPIO:
    def __init__(self):
        self.usingList = []
        self._gpioMap = gpioInfo["NumberOfNormalGPIO"]

    def __del__(self):
        for gpio in self.usingList:
            self.Value(gpio, "0")
            self.Direction(gpio, "in")
        self.UnExport("ALL")

    def Export(self, pinNumber, direction = "out"):
        if pinNumber not in self._gpioMap:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} can't be use !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        if pinNumber.upper() in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} has be used !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo " + self._gpioMap[pinNumber] + " > /sys/class/gpio/export")
        os.system("echo " + direction + " > /sys/class/gpio/gpio" + self._gpioMap[pinNumber] + "/direction")        
        
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print("{0}[SUCCESS]{1} pin number {2} export".format(Fore.GREEN, Fore.RESET, pinNumber))
        self.usingList.append(pinNumber.upper())
        return True

    def UnExport(self, pinNumber = "ALL"):
        if pinNumber == "ALL":
            
            for gpio in self.usingList:
                os.system("echo " + self._gpioMap[gpio] + " > /sys/class/gpio/unexport")
                if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                    print("{0}[SUCCESS]{1} pin number {2} unexport".format(Fore.GREEN, Fore.RESET, pinNumber))
            
            self.usingList.clear()
                     
            return True

        if pinNumber.upper() not in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} can't be unexport !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo " + self._gpioMap[pinNumber] + " > /sys/class/gpio/unexport")
        
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " pin number "+ pinNumber + " unexport")
        self.usingList.remove(pinNumber.upper())
        return True

    def Value(self, pinNumber, value):
        if pinNumber.upper() not in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo " + value + " > /sys/class/gpio/gpio" + self._gpioMap[pinNumber] + "/value")
        
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print("{0}[SUCCESS]{1} pin number {2} set value to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, value))
        return True

    def Direction(self, pinNumber, direction):
        if pinNumber.upper() not in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo " + direction + " > /sys/class/gpio/gpio" + self._gpioMap[pinNumber] + "/direction")
        
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print("{0}[SUCCESS]{1} pin number {2} set direction to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, direction))
        return True
        
class PwmGPIO:
    def __init__(self):
        self.usingList = []
        self._gpioMap = gpioInfo["NumberOfPwmGPIO"]
        self._period = -1

    def __del__(self):
        for gpio in self.usingList:
            self.Enable(gpio, False)
        self.UnExport("ALL")

    def Export(self, pinNumber):
        if pinNumber not in self._gpioMap:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} can't be use !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        if pinNumber.upper() in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} has be used !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo 0 > /sys/class/pwm/" + self._gpioMap[pinNumber] + "/export")      
        
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print("{0}[SUCCESS]{1} pin number {2} export".format(Fore.GREEN, Fore.RESET, pinNumber))
        self.usingList.append(pinNumber.upper())

    def UnExport(self, pinNumber = "ALL"):
        if pinNumber == "ALL":
            
            for gpio in self.usingList:
                os.system("echo " + self._gpioMap[gpio] + " > /sys/class/pwm/unexport")
                print("{0}[SUCCESS]{1} pin number {2} unexport".format(Fore.GREEN, Fore.RESET, pinNumber))
            
            self.usingList.clear()
                     
            return True

        if pinNumber.upper() not in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} can't be unexport !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo 0 > /sys/class/pwm/" + self._gpioMap[pinNumber] + "/unexport")
        
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " pin number "+ pinNumber + " unexport")
        self.usingList.remove(pinNumber.upper())
        return True

    def Period(self, pinNumber, period):
        if pinNumber.upper() not in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False
        
        if period < 0:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} must > 1 !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo " + str(period) + " > /sys/class/pwm/" + self._gpioMap[pinNumber] + "/pwm0/period")      
        
        self._period = period
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print("{0}[SUCCESS]{1} pin number {2} set period to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, period))
        return True

    def DutyCycle(self, pinNumber, dutyCycle):
        dutyCycle = int(dutyCycle)
        if pinNumber.upper() not in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        if dutyCycle > self._period:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} period must larger than dutyCycle !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo " + str(int(dutyCycle)) + " > /sys/class/pwm/" + self._gpioMap[pinNumber] + "/pwm0/duty_cycle")      
        
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print("{0}[SUCCESS]{1} pin number {2} set dutyCycle to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, int(dutyCycle)))
        return True

    def Enable(self, pinNumber, enable = True):
        if pinNumber.upper() not in self.usingList:
            if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
                print("{0}[ERROR]{1} pin number {2} is not export !!".format(Fore.RED, Fore.RESET, pinNumber))
            return False

        
        os.system("echo " + str(1 if enable else 0) + " > /sys/class/pwm/" + self._gpioMap[pinNumber] + "/pwm0/enable")      
        
        if config.getboolean("ShowControl","TerminalMessage_GPIOResult") :
            print("{0}[SUCCESS]{1} pin number {2} set enable to {3}".format(Fore.GREEN, Fore.RESET, pinNumber, 1 if enable else 0))
        return True

class Servomotor:
    def __init__(self, servoModel, pin, resetAngle = None, initAngle = 0):
        self._pin = pin
        self._resetAngle = resetAngle
        self._servoModel = servoModel
        self._pwmGPIO = PwmGPIO()
        self._pwmGPIO.Export(pin)
        self._pwmGPIO.Period(pin, 3413333)
        self._pwmGPIO.Enable(pin, True)
        self.ChangeAngle(initAngle)
    
    def __del__(self):
        if self._resetAngle is not None:
            self.ChangeAngle(self._resetAngle)
        
        self._pwmGPIO.Enable(self._pin, False)
        self._pwmGPIO.UnExport(self._pin)
        # pass

    def ChangeAngle(self, angle):
        angle = int(angle) % 360

        if angle > gpioInfo.getint(self._servoModel, "MaxAngle"):
            print("{0}[ERROR]{1} the angle is too large !!".format(Fore.RED, Fore.RESET))
            return False

        if angle < gpioInfo.getint(self._servoModel, "MinAngle"):
            print("{0}[ERROR]{1} the angle is too small !!".format(Fore.RED, Fore.RESET))
            return False

        dutyCycle = (gpioInfo.getint(self._servoModel, "MaxDutyCycle") - gpioInfo.getint(self._servoModel, "MinDutyCycle")) * angle / gpioInfo.getint(self._servoModel, "MaxAngle") + gpioInfo.getint(self._servoModel, "MinDutyCycle")

        self._pwmGPIO.DutyCycle(self._pin, dutyCycle)
        print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " Servomotor change angle to " + str(angle) +" in pin number "+ self._pin)
        return True


if __name__ == "__main__":
    #region NormalGPIO
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
    #endregion

    #region PwmGPIO
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
    #endregion
    
    #region Servomotor
    s1 = Servomotor("SG90", "PIN32", resetAngle = 90, initAngle= 90)
    s2 = Servomotor("SG90", "PIN33", resetAngle = 90, initAngle= 90)

    # s1.ChangeAngle(90)
    # # time.sleep(2)

    # s2.ChangeAngle(45)
    # # time.sleep(2)

    # s1.ChangeAngle(135)
    # # time.sleep(2)

    # s2.ChangeAngle(180)
    # # time.sleep(2)

    # s1.ChangeAngle(0)
    # # time.sleep(2)

    # s2.ChangeAngle(135)
    # # time.sleep(2)


    for i in range(0, 10):
        if(i%2 == 0):
            s1.ChangeAngle(180)
        else:
            s1.ChangeAngle(0)
    #endregion