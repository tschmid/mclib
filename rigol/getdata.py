import rigol
import time

rs = rigol.RigolScope("/dev/usbtmc0")

print rs.getName()
rs.stop()

#print "CH1"
#print rs.getDataCh1()
#print "CH2"
#print rs.getDataCh2()
print "MATH"
print rs.getDataMath()

rs.run()
rs.local()
