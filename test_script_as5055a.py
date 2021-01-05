from AS5055A_Encoder import AS5055A
import statistics
import time



encoder = AS5055A()

while(True):
    print("angle: "+str(round(encoder.getAngle())))
    time.sleep(0.1)
