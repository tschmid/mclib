import struct
import socket
import time


# VICP Headers:
#        Byte    Description
#       ------------------------------------------------
#        0      Operation
#        1      Version     1 = version 1
#        2      Sequence Number { 1..255 }, (was unused until June 2003)
#        3      Unused
#        4      Block size, MSB  (not including this header)
#        5      Block size
#        6      Block size
#        7      Block size, LSB

class VICP:
    PORT = 1861

    def __init__(self, host, port=PORT):
        self.host = host
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

        pass

    def operation(self, data=True, remote= False, lockout=False, clear=False, sqr=False, serialPoll=False, EOI=True):
        operation = 0
        if data:
            operation += 0x80
        if remote:
            operation += 0x40
        if lockout:
            operation += 0x20
        if clear:
            operation += 0x10
        if sqr:
            operation += 0x08
        if serialPoll:
            operation += 0x04
        if EOI:
            operation += 0x01

        return operation


    def header(self, data, seq=1):
        return struct.pack(">4BL", self.operation(), 1, seq, 0, len(data))

    def command(self, command):
        self.s.send(self.header(command))
        self.s.send(command)

    def query(self, command):
        self.s.send(self.header(command))
        self.s.send(command)
        (operation, version, seq, reserved, msgLength) = struct.unpack(">4BL", self.s.recv(8))
        data = self.s.recv(msgLength)
        return data



if __name__ == "__main__":
    import sys
    vicp = VICP("172.17.5.122")
    s = vicp.query("*IDN?")
    print s
    s = vicp.query("DATE?")
    print s
    lastMeasurement = 0
    n = 0
    while 1:
        s = vicp.query("PARAMETER_STATISTICS? CUST, P1\n")
        try:
            measurement = float(s.strip().split(',')[9].split()[0])
        except:
            continue
        if measurement == lastMeasurement:
            continue
        if measurement < 2e-6 or measurement > 4e-6:
            continue
        lastMeasurement = measurement
        s = vicp.query("PARAMETER_STATISTICS? CUST, P2\n")
        try:
            measurement2 = float(s.strip().split(',')[9].split()[0])
        except:
            continue
        s = vicp.query("PARAMETER_STATISTICS? CUST, P3\n")
        try:
            measurement3 = float(s.strip().split(',')[9].split()[0])
        except:
            continue
        n += 1
        sys.stderr.write("n=%6d "%(n,))
        sys.stdout.write("%.12f %.12f %.12f\n"%(measurement, measurement2,
            measurement3))
        sys.stdout.flush()
        time.sleep(0.1)

        #s = vicp.query("PARAMETER_STATISTICS? CUST, P2\n")
        #print s
