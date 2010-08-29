import rigol
import time

rs = rigol.RigolScope("/dev/usbtmc0")

print rs.getName()
rs.stop()

#print "CH1"
#print rs.getDataCh1()
#print "CH2"
#print rs.getDataCh2()
#print "MATH"
#print rs.getDataMath()
THRESH = 1.5
c1 = rs.getData("CHAN1", maximum=True)
c2 = rs.getData("CHAN2", maximum=True)
print c1
for (t, x) in c1:
    if x > THRESH:
        print t
        break;
for (t, x) in c2:
    if x > THRESH:
        print t
        break;


rs.run()
rs.local()
