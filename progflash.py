#!/usr/bin/env python
# Written by Liam Jackson based on code by  Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain
import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# change these as desired
clockpin = 22
misopin = 24
mosipin = 25
cspin = 23
holdpin = 27
wppin = 26


# read SPI data from chip
# cmd hex command to send
# cmdlen number of bits in cmd
# readlen number of bits to read back
# sleeptime time to sleep between write & read
def spicmd(cmd, cmdlen, readlen, sleeptime=0):
    GPIO.output(cspin, True)
    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    if(cmdlen != 0):
        commandout = cmd
        for i in range(cmdlen):
            if (commandout & (1 << (cmdlen - 1))):
                GPIO.output(mosipin, True)
            else:
                GPIO.output(mosipin, False)

            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
    #end if cmdlen != 0

    if(sleeptime != 0):
        time.sleep(sleeptime)

    chipout = 0
    if(readlen != 0):
        # read in bits on clk high
        for i in range(readlen):
            GPIO.output(clockpin, True)
            chipout <<= 1
            if (GPIO.input(misopin)):
                chipout |= 0x1
            GPIO.output(clockpin, False)
    #end if readlen != 0

    GPIO.output(cspin, True) # bring CS high to end
    return chipout
#end function

# set up the SPI interface pins
GPIO.setup(mosipin, GPIO.OUT)
GPIO.setup(misopin, GPIO.IN)
GPIO.setup(clockpin, GPIO.OUT)
GPIO.setup(cspin, GPIO.OUT)

#Shouldn't need to set these up for now.
#GPIO.setup(SPIHOLD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(SPIWP, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#Read the ID/wakeup register
value = spicmd(0xAB, 8, 64, 0.5)

if((value & 0xff) != ((value >> 8)& 0xff)):
        print "Chip ID read didn't go well"

id = value & 0xff
print "ID ", format(id, '02x')

if((id < 0x01) or (id > 0x20)):
    print "ID is suspect, perhaps comms not working?" 

time.sleep(0.5)

#write enable
result = spicmd(0x06, 8, 0)

# read the status register
sreg1 = spicmd(0x05, 8, 8)  
print "Status 1 ", format(sreg1, '02x')

if((sreg1 & 0x02) == 0):
    print "Write enable didn't work"

sreg2 = spicmd(0x35, 8, 8)  
print "Status 2 ", format(sreg2, '02x')

#verify
sreg2b = spicmd(0x35, 8, 8)  
if(sreg2 != sreg2b):
    print "Veritication of status2 register failed!"
    print "Status 2 ", format(sreg2b, '02x')


#send cmd
#8 bits instruction
#next 8 bits sreg 1
#then 8 bits sreg2 with QE masked out
cmd = (0x01 << 16) | (sreg1 << 8) | (sreg2 & 0xFD)
result = spicmd(cmd, 24, 0)

#wait for the flash write to happen
time.sleep(0.5)

#verify the write
verify = spicmd(0x35, 8, 8)
print "Status 2 now ", format(verify, '02x')

if(verify & 0x02):
    print "Readback of status2 register failed! If you have HOLD connected to CS this is normal."


# hang out and do nothing for a half second
time.sleep(0.5)
GPIO.cleanup()
print "Done!"
