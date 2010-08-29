import os
import sys
import numpy
import time

class usbtmc:
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""

    DEBUG = False

    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)

        # TODO: Test that the file opened

    def write(self, command):
        if self.DEBUG:
            print "DEBUG(write): *%s*"%command
        os.write(self.FILE, command)
        #time.sleep(0.25)

    def read(self, length = 4000):
        s = os.read(self.FILE, length)
        if self.DEBUG:
            print "DEBUG(read): *%s*"%s
        return s

    def readline(self):
        """ To read one command, just read a lot. the read command will only
        return as much as can be read from the device. """
        return self.read(2097152)

class RigolScope:
    """Class to control a Rigol DS1000 series oscilloscope"""

    CHANNELS = ["CHAN1", "CHAN2", "MATH"]

    def __init__(self, device):
        self.meas = usbtmc(device)

    def reset(self):
        """Reset the instrument"""
        self.meas.write("*RST")

    def getName(self):
        self.meas.write("*IDN?")
        return self.meas.readline()

    def stop(self):
        self.meas.write(":STOP")

    def run(self):
        self.meas.write(":RUN")

    def triggerSingleEdge(self):
        self.meas.write(":TRIG:EDGE:SWE SING")

    def validChannel(self, channel):
        if channel in self.CHANNELS:
            return True
        else:
            return False

    def isChannelOn(self, channel):
        if not self.validChannel(channel):
            # not a valid channel
            return False
        self.meas.write(":%s:DISP?"%channel)
        r = self.meas.readline()
        if r == "ON" or r == "1":
            return True
        else:
            return False

    def getData(self, channel, maximum=False):
        if not self.validChannel(channel):
            # not a valid channel
            return ""
        if self.isChannelOn(channel):
            # get the data
            if maximum:
                self.meas.write(":WAV:POIN:MODE RAW")
                self.meas.write(":WAV:DATA? %s"%channel)
                r = self.meas.read(10)
                # find out how many datapoints we have to read
                l = int(r[2:]) # first character is #, then number of bits (8) then number of samples
                r = ""
                i = 0
                while i < l:
                    c = self.meas.read(1024)
                    #print i
                    #sys.stdout.flush()
                    i += 1024
                    r += "%s"%c
            else:
                self.meas.write(":WAV:POIN:MODE NOR")
                self.meas.write(":WAV:DATA? %s"%channel)
                r = self.meas.readline()
                # the first 10 bytes are something I don't know... maybe
                r = r[10:]
            # #bitresnumsamples?
            data = numpy.frombuffer(r, 'B')


            # if the channel is the MATH channel, we can't get offset nor
            # scale. Assume Math uses the same thing as channel 1
            if channel == "MATH":
                channel = "CHAN1"
            #get the voltage scale
            self.meas.write(":%s:SCAL?"%channel)
            voltscale = float(self.meas.readline())

            # get the voltage offset
            self.meas.write(":%s:OFFS?"%channel)
            voltoffset = float(self.meas.readline())

            # Walk through the data, and map it to actual voltages
            # First invert the data (ya rly)
            data = data * -1 + 255

            # Now, we know from experimentation that the scope display range
            # is actually
            # 30-229.  So shift by 130 - the voltage offset in counts, then
            # scale to
            # get the actual voltage.
            data = (data - 130.0 - voltoffset/voltscale*25) / 25 * voltscale
            #data *= voltscale

            # get the timescale
            self.meas.write(":TIM:SCAL?")
            timescale = float(self.meas.readline())

            # get the timescale offset
            self.meas.write(":TIM:OFFS?")
            r = (self.meas.readline())
            rate = float(r)

            # Now, generate a time axis.  The scope display range is 0-600,
            # with 300 being
            # time zero.
            #time = numpy.arange(-300.0/50*timescale, 300.0/50*timescale,
            #        timescale/50.0)
            # there are 50 points per division
            time = numpy.arange(-l/2*timescale/50, l/2*timescale/50,
                    timescale/50)

            # get the sampling rate
            self.meas.write(":ACQ:SAMP? %s"%channel)
            r = (self.meas.readline())
            rate = float(r)
            time = numpy.arange(-l/2*1/rate, l/2*1/rate, 1/rate)

            # If we generated too many points due to overflow, crop the length
            # of time.
            if (time.size > data.size):
                time = time[0:data.size]
            # See if we should use a different time axis
            #if (time[599] < 1e-3):
            #    time = time * 1e6
            #    tUnit = "uS"
            #elif (time[599] < 1):
            #    time = time * 1e3
            #    tUnit = "mS"
            #else:
            #    tUnit = "S"

            numpy.set_printoptions(threshold=numpy.nan)
            return numpy.column_stack((time,data))
        else:
            return ""

    def getDataCh1(self):
        return self.getData("CHAN1")

    def getDataCh2(self):
        return self.getData("CHAN2")

    def getDataMath(self):
        return self.getData("MATH")

    def getCounter(self):
        """ Returns the value of the counter in Hz. """
        self.meas.write(":COUNTER:VALUE?")
        r = self.meas.readline()
        return float(r)

    def getFrequency(self, channel):
        """ Measures the frequency of the given channel. The return value is
        in Hz."""
        if not self.validChannel(channel):
            return None
        if self.isChannelOn(channel):
            self.meas.write(":MEAS:FREQ? %s"%channel)
            r = self.meas.readline()
            return float(r)

    def local(self):
        self.meas.write(":KEY:FORC")


if __name__ == "__main__":
    rs = RigolScope("/dev/usbtmc0")
    print "Device Name: ", rs.getName()
    print "Resetting Device"
    rs.reset()
    print "Stop"
    rs.stop()
    print "Configure for single acquisition"
    rs.triggerSingleEdge()
    print "Start"
    rs.run()



