#!/usr/bin/env python
## Written by Hans Tercek for Tufts ME-43: Wright on behalf of ReMaterials
##   Code produced 12/11/2017
##
##   SPI code is based on Limor "Ladyada" Fried's for Adafruit Industries,
##       (c) 2015 licensed under the public domain

## NOTE: This code runs the clutch and motor in parallel. It is expected that
##       both the motor and the 12V clutch PSU are connected to the same
##       "Normally OFF" output on the relay

#******************************************************************************#
#******************************* INITIALIZATION *******************************#
#******************************************************************************#
##### Import packages #####
import RPi.GPIO as GPIO
import time
import sys

DEBUG = 0
if DEBUG:
    print('****DEBUG MODE ENABLED*****')

##### Test variables #####
numTest = 10
maxTests = 100

##### Pin setup #####
LIMIT_INPUTS    = [38,40]   # Upper limit switches
RELAY_OUTPUT    = 15        # Relay for motor control
CLUTCH_OUTPUT   = 13        # Clutch control
# SPI Control
SPICLK      = 12
SPIMISO     = 16
SPIMOSI     = 18
SPICS       = 22
MAX_RANGE   = 600           # IR Max
MIN_RANGE   = 170           # IR Min

LOGFILE     = 'droptests.txt'

if DEBUG:
    print('PINOUT:')
    print('    LIMIT SWITCHES: ' + str(LIMIT_INPUTS[0]) + 
          ' ' + str(LIMIT_INPUTS[1]))
    print('    RELAY OUTPUT:   ' + str(RELAY_OUTPUT))
    print('    CLUTCH OUTPUT:  ' + str(CLUTCH_OUTPUT))
    print('    LOG FILE:       ' + LOGFILE)


#******************************************************************************#
#****************************** RUNNING PROGRAM *******************************#
#******************************************************************************#

#********************************** SPI READ **********************************#
# v_read = readadc(IR_ADC, SPICLK, SPIMOSI, SPIMISO, SPICS)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum > 7) or (adcnum < 0)):
            return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
            if (commandout & 0x80):
                    GPIO.output(mosipin, True)
            else:
                    GPIO.output(mosipin, False)
            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if (GPIO.input(misopin)):
                    adcout |= 0x1

    GPIO.output(cspin, True)
    
    adcout >>= 1       # first bit is 'null' so drop it
    return adcout

#********************************** RUNPROG  **********************************#
# LIMIT_INPUTS    = [29,31]   # Upper limit switches
# RELAY_OUTPUT    = 15        # Relay
# CLUTCH_OUTPUT   = 13        # Clutch control
# # SPI Control
# SPICLK      = 12
# SPIMISO     = 16
# SPIMOSI     = 18
# SPICS       = 22
# MAX_RANGE   = 600           # IR Max
# MIN_RANGE   = 170           # IR Min
def runProgram(numTest):

    ##### Configure GPIO
    print('RUNNING: ' + str(numTest) + ' TESTS......\n')
    print('    Configuring pins.....')

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(LIMIT_INPUTS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(RELAY_OUTPUT, GPIO.OUT)
    GPIO.setup(CLUTCH_OUTPUT, GPIO.OUT)

    # SPI
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    # set up interface pins
    GPIO.setup(SPICS, GPIO.OUT)

    print('     Pins configured.\n')

    ##### Run loop
    counter = 1

    print('Initiating motor in: 3...')
    time.sleep(1)
    print('                         2...')
    time.sleep(1)
    print('                             1...\n')
    time.sleep(1)


    print('     Engaging clutch and motor')
    print('TEST ' + str(counter) + '/' + str(numTest) + '...')
    GPIO.output(RELAY_OUTPUT, True)

    LOG = open(LOGFILE, 'w')
    LOG.write('Tests run:\n')

    # Main loop
    while (counter <= numTest):
        if (GPIO.input(LIMIT_INPUTS[0]) or GPIO.input(LIMIT_INPUTS[1])):

            # Write to log file
            LOG.write(str(counter) + '\n')

            if DEBUG:
                print('LIMIT 1: ' + GPIO.input(LIMIT_INPUTS[0]))
                print('LIMIT 2: ' + GPIO.input(LIMIT_INPUTS[1]))

            print('     Disengaging clutch and motor\n')
            GPIO.output(RELAY_OUTPUT, False)

            if DEBUG:
                # Wait for input to continue
                cont = raw_input('PRESS "enter" TO CONTINUE')
            else:
                time.sleep(1)

            counter += 1
            if counter <= numTest:
                print('TEST ' + str(counter) + '/' + str(numTest) + '...')
                print('     Engaging clutch and motor')
                GPIO.output(RELAY_OUTPUT, True)

        time.sleep(0.25)
        

    print('TESTING COMPLETED. CLEANING UP...')
    LOG.close()
    GPIO.output(RELAY_OUTPUT, False)
    GPIO.output(CLUTCH_OUTPUT, False)
    GPIO.cleanup()
    print('     Cleanup complete. Closing program.')


#******************************************************************************#
#********************************* TEST SETUP *********************************#
#******************************************************************************#
##### Initialize number of tests #####
# Obtain number of tests
print('***** CLUTCH AND MOTOR RUNNING IN PARALLEL *****\n' +
             'Please verify 12V PSU and motor are plugged into "Normally off"')
if (len(sys.argv) < 2):
    verify = raw_input('UNSPECIFIED INPUT: Would you like to run base number ' +
                       'of tests [' + str(numTest) + ']?: ')
    if (verify == 'y' or verify == 'yes'):
        numTest = 10
    elif (verify == 'n' or verify == 'no'):
        print('Please specify number of iterations (max: ' + 
               str(maxTests) + '):\n' + '    "runTest <iterations>"\n')
        sys.exit()
else:
    numTest = int(sys.argv[1])

print('NUMBER TESTS: ' + str(numTest))

# Validate test number
if (numTest > maxTests or numTest < 0):
    print('ERROR: Invalid number of tests. Max tests: ' + str(maxTests) + '\n')
    sys.exit()

# Verify run
verify = raw_input('ENTER "y" TO CONTINUE, "n" TO ABORT: ')
while (verify != 'n' or verify != 'no' or verify != 'y' or verify != 'yes'):
    if (verify == 'n' or verify == 'no'):
        print('ABORTING\n')
        sys.exit()
    elif (verify == 'y' or verify == 'yes'):
        runProgram(numTest)
        sys.exit()
    verify = raw_input('Please enter "y" or "n": ')
