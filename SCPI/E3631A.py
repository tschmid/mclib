import serial
import sys
import os
import time
#import Numeric

import struct

class E3631A:
    lf = "\r\n"

    def __init__(self, device):
        self.ser = serial.Serial(device, 9600, timeout=0.5, rtscts=0)
        print self.ser
        self.send("*IDN?")
        print "DEVICE: " + self.ser.readline()

        self.send(":SYST:REM")
        self.send("*RST")
        self.send("*CLS")

    def send(self, command):
        self.ser.write(command + self.lf)

    def setVoltageP25(self, volt):
        self.send("INST P25V")
        self.send("VOLT %.1f"%(volt))

    def setVoltageN25(self, volt):
        self.send("INST N25V")
        self.send("VOLT -%.1f"%(volt))

    def setVoltageCurrentP25(self, volt, current):
        self.send("APPL P25V, %.2f, %.3f;"%(volt,current))

    def setVoltageCurrentP6(self, volt, current):
        self.send("APPL P6V, %.3f, %.3f;"%(volt,current))

    def setVoltageCurrentN25(self, volt, current):
        self.send("APPL N25V, -%.3f, %.3f;"%(volt,current))

    def outputOn(self):
        self.send("OUTP ON")

    def outputOff(self):
        self.send("OUTP OFF")

if __name__ == "__main__":
    ea = E3631A(sys.argv[1])
