import spidev
import time
import RPi.GPIO as GPIO 


class AS5055A:

    SPI_CMD_READ = 0x8000
    SPI_REG_DATA = 0x7ffe
    SPI_REG_AGC = 0x7ff0
    SPI_REG_CLRERR = 0x6700

    _bp_parity       = 1 << 0
    _bp_ef           = 1 << 1
    _bp_alarm_low    = 1 << 15
    _bp_alarm_high   = 1 << 14

    showWarnings = False

    _pin_cs = -1

    spi = spidev.SpiDev()
    
    def __init__(self, pin_cs, max_speed_hz=10000):
        print("AS5055A: Init")
        self._pin_cs = pin_cs
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin_cs, GPIO.OUT)

        self.spi.open(0,0)
        self.spi.max_speed_hz = max_speed_hz
        self.spi.mode = 0b01
        self.spi.lsbfirst = False
        
    def __del__(self):
        print("AS5055A: Deinit")
        self.spi.close()
        GPIO.cleanup()


    def set_bit(self, value, bit):
        return value | (1<<bit)

    def clear_bit(self, value, bit):
        return value & ~(1<<bit)

    def calculate_parity(self, value):
        cnt = 0
     
        for i in range(16):
            if (value & 0x1):
                cnt += 1
            value >>= 1
        return cnt & 0x1

    def spi_transfer(self, data):
        GPIO.output(self._pin_cs, 0)
        answer = spi.xfer2([data])
        GPIO.output(self._pin_cs, 1)
        return answer

    def clear_error(self):
        command = SPI_CMD_READ | SPI_REG_CLRERR
        command = command | calculate_parity(command)
        answer_agc = spi_transfer(command)

    def getAngle_bits(self):
        GPIO.output(self._pin_cs, 0)
        result1 = self.spi.xfer2([0xff])[0]
        result2 = self.spi.xfer2([0xff])[0]
        GPIO.output(self._pin_cs, 1)

        #result1 &= 0b00111111
        result1 = result1 << 8
        result = (result1 | result2)
        #data = result & 0x3FFF

        if(self.calculate_parity(result)):
            print("AS5055A: Parity Error")
            return False
        if(result & self._bp_ef and self.showWarnings):
            print("AS5055A: Error Occured")
            #return False
        if(result & self._bp_alarm_low and self.showWarnings):
            print("AS5055A: Alarm Low")
        if(result & self._bp_alarm_high and self.showWarnings):
            print("AS5055A: Alarm High")

        result &= 0x3FFF
        result = result >>2
        #print(bin(result))

        return result

    def getAngle(self):
        tries = 0
        while(True):
            tries += 1
            angleBits = self.getAngle_bits()
            if(angleBits != False):
                angle = angleBits * 360 / 4096
                return angle
            
            if(tries>=10):
                print("AS5055A: after 10 tries not valid answer. exiting")
                raise SystemExit
