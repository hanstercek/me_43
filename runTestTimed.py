#!/usr/bin/env python
## Written by Hans Tercek for Tufts ME-43: Wright on behalf of ReMaterials
##   Code produced 12/11/2017
##
##   SPI code is based on Limor "Ladyada" Fried's for Adafruit Industries,
##       (c) 2015 licensed under the public domain

## NOTE: This code runs the clutch and motor in parallel. It is expected that
##       both the motor and the 12V clutch PSU are connected to the same
##       "Normally OFF" output on the relay
##       Edit TEST VARIABLES to change timing and test limits.

#******************************************************************************#
#******************************* INITIALIZATION *******************************#
#******************************************************************************#
##### TEST VARIABLES #####
NUM_TESTS       = 10                # Baseline number of tests (if no input specified)
MAX_TESTS       = 500               # Max number of tests than can be run
LIFT_TIME       = 30                # Time to lift load in seconds
DROP_TIME       = 1                 # Time to drop load in seconds
DEBUG           = 0                 # Set DEBUG to 1 to print debug messages
                                    #   Note: will require user input to continue test cycles
LOGFILE         = 'droptests.txt'   # File to log test results to

##### Pin setup #####
LIMIT_INPUTS    = [38,40]           # Upper limit switches
RELAY_OUTPUT    = 15                # Relay output for motor/clutch control
# SPI Control (for later implementation)
SPICLK          = 12
SPIMISO         = 16
SPIMOSI         = 18
SPICS           = 22
MAX_RANGE       = 600           # IR Max
MIN_RANGE       = 170           # IR Min

if DEBUG:
    print('*****DEBUG MODE ENABLED*****')
    print('PINOUT:')
    print('    LIMIT SWITCHES: ' + str(LIMIT_INPUTS[0]) + 
          ' ' + str(LIMIT_INPUTS[1]))
    print('    RELAY OUTPUT:   ' + str(RELAY_OUTPUT))
    print('    LOG FILE:       ' + LOGFILE)

##### Import packages #####
import RPi.GPIO as GPIO
import time
import sys

#******************************************************************************#
#****************************** RUNNING PROGRAM *******************************#
#******************************************************************************#

#********************************** SPI READ **********************************#
##### Code for SPI read. Currently not implemented, but included here should
#####   SPI reading become necessary.
#####   Syntax: v_read = readadc(IR_ADC, SPICLK, SPIMOSI, SPIMISO, SPICS)
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
##### Executes the main loop that runs the program. Takes int NUM_TESTS as 
#####   desired number of tests to run.
#####   Outputs iterations to console and logs completed tests to LOGFILE.
def runProgram(NUM_TESTS, DROP_TIME, LIFT_TIME):
    print('RUNNING: ' + str(NUM_TESTS) + ' TESTS......\n')

    ##### Configure GPIO pins on Raspberry Pi
    print('    Configuring pins.....')

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(LIMIT_INPUTS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(RELAY_OUTPUT, GPIO.OUT)

    # SPI setup
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    # set up interface pins
    GPIO.setup(SPICS, GPIO.OUT)

    print('     Pins configured.\n')
    print('Initiating motor in: 3...')
    time.sleep(1)
    print('                         2...')
    time.sleep(1)
    print('                             1...\n')
    time.sleep(1)

    ##### MAIN LOOP
    #####   Main loop start conditions and base configurations
    counter = 1 
    start_time = time.time()        # Establish base time to measure time elapsed

    print('     Engaging clutch and motor')
    print('TEST ' + str(counter) + '/' + str(NUM_TESTS) + '...')
    GPIO.output(RELAY_OUTPUT, True)

    LOG = open(LOGFILE, 'w')
    LOG.write('Tests run:\n')

    ##### Loop until desired number of tests are run
    while (counter <= NUM_TESTS):

        if DEBUG:
            print('     Lift time:    ' + str(LIFT_TIME))
            print('     Elapsed time: ' + str(time.time() - start_time))

        # Determine if full time elapsed or limit switches are depressed
        if (LIFT_TIME <= (time.time() - start_time) or
            GPIO.input(LIMIT_INPUTS[0]) or GPIO.input(LIMIT_INPUTS[1])):

            start_time = time.time()    # Reset start_time

            # Write to log file
            LOG.write(str(counter) + '\n')

            if DEBUG:
                print('LIMIT 1: ' + str(GPIO.input(LIMIT_INPUTS[0])))
                print('LIMIT 2: ' + str(GPIO.input(LIMIT_INPUTS[1])))

            print('     Disengaging clutch and motor\n')
            GPIO.output(RELAY_OUTPUT, False)

            if DEBUG:
                # Requires console input to continue running tests
                cont = raw_input('PRESS "enter" TO CONTINUE')
            else:
                # Deactivate motor and clutch for time to drop load
                time.sleep(DROP_TIME)

            counter += 1    # Increment count

            # Output testing to console
            if counter <= NUM_TESTS:
                print('TEST ' + str(counter) + '/' + str(NUM_TESTS) + '...')
                print('     Engaging clutch and motor')
                GPIO.output(RELAY_OUTPUT, True)

        time.sleep(0.25)    # Sleep between iterations. Reduce CPU load
        

    print('TESTING COMPLETED. CLEANING UP...')
    LOG.close()
    GPIO.output(RELAY_OUTPUT, False)
    GPIO.cleanup()
    print('     Cleanup complete. Closing program.')


#******************************************************************************#
#********************************* TEST SETUP *********************************#
#******************************************************************************#
##### Initialize number of tests 
#####   Outputs and reads user input to configure and verify tests.

# Configure number of tests to run
print('***** CLUTCH AND MOTOR RUNNING IN PARALLEL *****\n' +
             'Please verify 12V PSU and motor are plugged into "Normally off"')
if (len(sys.argv) < 2):
    verify = raw_input('UNSPECIFIED INPUT: Would you like to run base number ' +
                       'of tests (y/n) [' + str(NUM_TESTS) + ']?: ')
    while (verify != 'n' or verify != 'no' or verify != 'y' or verify != 'yes'):
        print('stuck in loop')
        if (verify == 'y' or verify == 'yes'):
            NUM_TESTS = 10
            break
        elif (verify == 'n' or verify == 'no'):
            print('Please specify number of iterations (max: ' + 
                   str(MAX_TESTS) + '):\n' + '    "runTest <iterations>"\n')
            sys.exit()
        else:
            verify = raw_input('IMPROPER INPUT: Would you like to run base number ' +
                               'of tests (y/n) [' + str(NUM_TESTS) + ']?: ')
else:
    NUM_TESTS = int(sys.argv[1])

print('NUMBER TESTS: ' + str(NUM_TESTS))

# Validate desired number of tests
if (NUM_TESTS > MAX_TESTS or NUM_TESTS < 0):
    print('ERROR: Invalid number of tests. Max tests: ' + str(MAX_TESTS) + '\n')
    sys.exit()

# Confirm testing
verify = raw_input('ENTER "y" TO CONTINUE, "n" TO ABORT: ')
while (verify != 'n' or verify != 'no' or verify != 'y' or verify != 'yes'):
    if (verify == 'n' or verify == 'no'):
        print('ABORTING\n')
        sys.exit()
    elif (verify == 'y' or verify == 'yes'):
        runProgram(NUM_TESTS, DROP_TIME, LIFT_TIME)       # RUN PROGRAM
        sys.exit()
    verify = raw_input('Please enter "y" or "n": ')
