import configparser
from colorama import Fore
from configparser import ConfigParser
import pexpect

gpioInfo = ConfigParser()
gpioInfo.read("gpioConfig.ini")
gpioInfo.sections()

def AutoTerminalGetPermisssion():
    child = pexpect.spawn("sudo -i")
    child.expect([":", "#", pexpect.EOF, pexpect.TIMEOUT])
    child.sendline(gpioInfo.get("UserPassword", "rootPassword"))
    return child
    # return []

def AutoTerminal(command, child = None):
    if child is None:
        child = pexpect.spawn(command)
        return child
        # return None
    
    child.expect(["#", pexpect.EOF, pexpect.TIMEOUT])
    child.sendline(command)
    return child
    # return None

def AutoTerminalClose(child = None):
    if child is None:
        return
    child.expect("#")
    child.close(force = False)
    # return None

class NormalGPIO:
    def __init__(self):
        self.usingList = []
        self.controlPath = "/sys/class/gpio"
        self.gpioMap = gpioInfo["NumberOfNormalGPIO"]

    def __del__(self):
        for gpio in self.usingList:
            self.Value(gpio, "0")
            self.Direction(gpio, "in")
        self.UnExport("ALL")

    def Export(self, numberOfGPIO, direction = "out"):
        if numberOfGPIO not in self.gpioMap:
            print(Fore.RED + "[ERROR]" + Fore.RESET + " gpio number " + numberOfGPIO + " can't be use !!")
            return False

        if numberOfGPIO.upper() in self.usingList:
            print(Fore.RED + "[ERROR]" + Fore.RESET + " gpio number " + numberOfGPIO + " has be used !!")
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + self.gpioMap[numberOfGPIO] + " > " + self.controlPath + "/export", child)
        AutoTerminal("echo " + direction + " > " + self.controlPath + "/gpio" + self.gpioMap[numberOfGPIO] + "/direction", child)        
        AutoTerminalClose(child)
        print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " gpio number "+ numberOfGPIO + " export")
        self.usingList.append(numberOfGPIO.upper())

    def UnExport(self, numberOfGPIO = "ALL"):
        if numberOfGPIO == "ALL":
            child = AutoTerminalGetPermisssion()
            for gpio in self.usingList:
                AutoTerminal("echo " + self.gpioMap[gpio] + " > " + self.controlPath + "/unexport", child)
                print(Fore.GREEN + "[UnExport]" + Fore.RESET + " gpio number "+ gpio + " unexport")
            
            self.usingList.clear()
            AutoTerminalClose(child)         
            return True

        if numberOfGPIO.upper() not in self.usingList:
            print(Fore.RED + "[ERROR]" + Fore.RESET +" gpio number " + numberOfGPIO + " can't be unexport !!")
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + self.gpioMap[numberOfGPIO] + " > " + self.controlPath + "/unexport", child)
        AutoTerminalClose(child)
        print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " gpio number "+ numberOfGPIO + " unexport")
        self.usingList.remove(numberOfGPIO.upper())
        return True

    def Value(self, numberOfGPIO, value):
        if numberOfGPIO.upper() not in self.usingList:
            print(Fore.RED + "[ERROR]" + Fore.RESET + " gpio number " + numberOfGPIO + " is not export !!")
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + value + " > " + self.controlPath + "/gpio" + self.gpioMap[numberOfGPIO] + "/value", child)
        AutoTerminalClose(child)
        print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " gpio number "+ numberOfGPIO + " set value to " + value)
        return True

    def Direction(self, numberOfGPIO, direction):
        if numberOfGPIO.upper() not in self.usingList:
            print(Fore.RED + "[ERROR]" + Fore.RESET + " gpio number " + numberOfGPIO + " is not export !!")
            return False

        child = AutoTerminalGetPermisssion()
        AutoTerminal("echo " + direction + " > " + self.controlPath + "/gpio" + self.gpioMap[numberOfGPIO] + "/direction", child)
        AutoTerminalClose(child)
        print(Fore.GREEN + "[SUCCESS]" + Fore.RESET + " gpio number "+ numberOfGPIO + " set direction to " + direction)
        return True
        


if __name__ == "__main__":
    import time

    n = NormalGPIO()

    n.Export("1d3")
    n.Export("1")
    n.Export("12aS")
    n.Export("linux26")
    n.Export("linux25")

    n.Value("linux26", "1")

    time.sleep(2)

    n.Value("linux26", "0")

    time.sleep(2)

    n.Value("linux26", "1")

    time.sleep(2)

    print(n.usingList)
