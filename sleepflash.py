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
#value = spicmd(0xAB, 8, 64, 0.5)

#if((value & 0xff) != ((value >> 8)& 0xff)):
#        print "Chip ID read didn't go well"

#id = value & 0xff
#print "ID ", format(id, '02x')

#if((id < 0x01) or (id > 0x20)):
#    print "ID is suspect, perhaps comms not working?" 

time.sleep(0.5)

# read the status register
jdec1 = spicmd(0x9F, 8, 24)  
print "JDEC ID ", format(jdec1, '06x')

#send power down cmd
#8 bits instruction
result = spicmd(0xB9, 8, 0)

#wait for the flash to nod off
time.sleep(1)

#verify the write
jdec2 = spicmd(0x9F, 8, 24)  
print "JDEC ID Now ", format(jdec2, '06x')

if(0xffffff == jdec2 or 0x000000 == jdec2):
    print "Flash looks asleep."
else:
    print "Flash doesnt look asleep"

# hang out and do nothing for a half second
time.sleep(0.5)
GPIO.cleanup()
print "Done!"
