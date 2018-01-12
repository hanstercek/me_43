################################################################################
#				MODROOSTER README			       #
################################################################################
The ModRooster impact tester was designed by Tufts University ME-43 students
    Daniel McGinn, Olivia Montgomery, Shea Nelson, Jacob Siegelbaum, and Hans
    Tercek under the supervision of Professor Natasha Wright for ReMaterials,
    Ahmedabad, India, during the fall of 2017.
    
    Note: vim and nano are installed on the Raspberry Pi to ease file
	  modification. To edit a file:
	  vim <filename>
	    or
	  nano <filename>

################################################################################
#				   HOW TO RUN				       #
################################################################################
    To execute, user should make sure they are SSH'ed into the Raspberry Pi
    Note: SSH is a standard method of connecting to devices that are on the same
	  WiFi network. To SSH, make sure you are connected to the following
	  network:
    WiFi Network:  'ReMaterials'
	 Password: 'rematerials'
	 Security:  WPA2

    Note: Not all consoles have built-in SSH functionality:
	  macOS:   'Terminal' app has built-in functionality.
	  Linux:   'Console' app has built-in functionality.
	  Windows: 'Putty' SSH client is a popular method of SSHing in Windows.
		    It can be found for free online. Follow online instructions
		    to set-up.

    In your preferred console, execute the following commands to run tests:
	ssh user@rematerials.local
	cd ~/Desktop
	./runTestTimed.py <iterations>

    Note: <iterations> is the desired number of tests to be run. If no value
	  is specified, the script will use the fallback base number of tests.
	  Input will be verified before progressing with the testing.

    SSH Details (for reference):
    Username:	   'user@rematerials.local'
    Password:	   'rematerials'

################################################################################
#				INCLUDED FILES				       #
################################################################################
    Navigate to Desktop directory to find ('cd ~/Desktop' when SSH'ed into Pi)

    runTestTimed.py
	Runs the impact tester with a timing and limit switch condition. If the
	upper switches are not depressed, once the lift time is met, the next
	test will be run automatically.
	**** This is the PREFERRED method to be run.
    runTestNoTimer.py
	Runs the impact tester without a timing condition. There is NO fallback
	timed loop for lifting the weight. Only use this if it is guaranteed the
	mass will depress the upper limit switches consistently and without fail.
	**** Failure to properly configure upper limits can result in COMPLETE
	     SYSTEM FAILURE.
    droptests.txt
	Logs the tests completely  run by the ModRooster. This file can be later
	accessed should tests be terminated prematurely and it is unclear how
	many tests were fully executed.

################################################################################
#				  HOW IT WORKS				       #
#				(runTestTimed.py)			       #
################################################################################
    The program features four primary steps to run the tester (as referenced as
	sections within the script):
	1. INITIALIZATION
	2. SPI READ
	3. RUNPROG
	4. TEST SETUP

    1. INITIALIZATION
	Test variables and Raspberry Pi pins can be specified by editing the
	script itself. Additionally, a debug feature can be enabled to ease
	troubleshooting.
    2. SPI READ
	This is not currently implemented (as of Fall 2017), but can be later
	integrated to allow for SPI data reading. Note: an analog to digital 
	converter will probably need to be added.
    3. RUNPROG
	This runs the tester. The motor and clutch are run in parallel, turned
	on when a 'True' value is sent to the relay pin, and are off by default.
	This loop runs until the desired number of tests are reached. It can be
	broken into the following substeps:
	a. Setup Raspberry Pi pinout based on pins specified in '1. Base setup'
	b. Engages clutch and motor
	c. Waits until lift time has elapsed or until an upper limit switch is
	   hit. 
	d. If c. is completed, logs completed test to logfile and continues with
	   testing.
    4. TEST SETUP
	Reads user input to configure and verify number of tests to be run.

