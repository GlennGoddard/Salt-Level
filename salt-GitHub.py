#!/usr/bin/python2.7

# Salt Tank Level Program

# Last Change 2/28/2020 1150

import time						# Sleep Function
import RPi.GPIO as GPIO			# GPIO Controls
from datetime import datetime	# Now Fuction
import smtplib					# Email Library
from decimal import Decimal		# Convert float to Decimal
import paho.mqtt.client as mqtt	# Allow publishing to MQTT Server

# sudo python2.7 -m pip install paho-mqtt

''' Use BCM GPIO references instead of physical pin numbers   '''
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

'''  Define Variables   '''
Trigger	= 8				# Set Trigger to GPIO 8
Echo	= 25			# Set Echo to GPIO 25
Wait	= 2				# Set time between pulses in seconds
Pulse	= 0.00001		# Set ultrasonic pulse length in seconds
PWait	= 60			# Wait time for testing
#PWait	= 600			# Time between readings in seconds (24*60*60)
Debug	= True			# Print to screen if True; do not comment out
Debug	= False			# Do not Print to screen if False; comment out to be True
Email	= False			# False to not send emails; do not comment out
Email	= True			# True to send emails; comment out to be False
Samples	= 11			# Number of samples to take for average
lvTop	= 5				# Top of Tank from Sensor
lvBag	= 4				# Level of inces of Salt per 40lb bag (4" per bag leveled)
lvFull	= lvTop	+ lvBag	# Full Tank level
TopLv	= 35			# Tank top level from bottom (33.3")
BottomLv= 11			# Top of water level from absolute bottom (lowest measureable level)
lvEmpty	= TopLv-BottomLv# Water level in tank is empty from Sensor, Sensor is at 35" from bottom

''' GMail variables '''
gmail_user = 'YourSendingEmail@gmail.com'	# Gmail account
gmail_password = 'SendingEmailPassword'				# Gmail Password
sent_from = gmail_user					# Email Sender
to = ['YourEmail@gmail.com']			# Email Recipient
cc = ['YourOtherEmail@gmail.com']		# 2nd Email Recipient
subject = 'Salt Tank Status'			# Email Subject can be updated
body = 'Body of email'					# Email Body can be updated

mail_sent = False						# Allow only one email on the designated day.

''' Debug print to screen colors '''
POff		= '\033[0m'		# Color Effects Off
PBold		= '\033[1m'		# Bold
PUnderline	= '\033[4m'		# Underline single
PBoldOff	= '\033[21m'	# Bold Off
PBlinkOff	= '\033[25m'	# Blink Off
PBlack		= '\033[90m'	# Black
PRed		= '\033[91m'	# Red
PGreen		= '\033[92m'	# Green
PYellow		= '\033[93m'	# Yellow
PBlue		= '\033[94m'	# Blue
PPurple		= '\033[95m'	# Purple
PCyan		= '\033[96m'	# Cyan
PWhite		= '\033[97m'	# White


''' Set pins as output and input   '''
GPIO.setup(Trigger, GPIO.OUT)	# Trigger
GPIO.setup(Echo, GPIO.IN)		# Echo

''' Set trigger to False (Low)   '''
GPIO.output(Trigger, False)

''' Define functions'''

def measure():
 	# This function measures a distance
	GPIO.output(Trigger, True)
	time.sleep(Pulse)
	GPIO.output(Trigger, False)
	start = time.time()
	while GPIO.input(Echo)==0:
		start = time.time()
	while GPIO.input(Echo)==1:
		stop = time.time()
	elapsed = stop-start
	distance = Decimal(elapsed * 6744.166310046,2) - lvTop
	# 34300 is speed of sound in cm/sec or 13488.332620092 in/sec
	# Divide by 2 to account for sound there and echo back
	# Divide by 2.54 to convert to inches from cm
	# Conversion = 6751.95 in/sec or 6744.166310046
	# v = 331m/s + 0.6m/s/C * T  speed of sound in m/s compensated for temperature or speed = 331 + 0.6 * Temp in C
	# Velocity = 331.4 + 0.6*Temperature + 0.0124*Relative_Humidity ... Temperature is in Celsius Degrees ... Relative Humidity can be measured by sensors in %age ... Velocity in m/sec
	return distance

def measure_average():
	# This function takes measurements and returns the average.
	distance = 0	# Ensure distance zeroed out
	for i in range (1, Samples, 1):
		time.sleep(Wait)
		distance = distance + measure()
		if Debug is True:
			print (Samples - i),
			print "\t",
			print (round(distance/i,2))
	distance = distance / (Samples - 1)
	return distance

def Message():
	# This function sends the email
	# Indents affect email formating
	toAll = to + cc
	if Debug is True:
		# Removed cc for testing
		toAll = to
	email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	server.ehlo()
	server.login(gmail_user, gmail_password)
	server.sendmail(sent_from, toAll, email_text)
	server.close()

	if Debug is True:
		print (PCyan)
		print "sent_from:\t",
		print (sent_from)
		print "to:\t\t",
		print (to)
		print "subject:\t",
		print (subject)
		print "body:\t\t",
		print (body)
		print (PPurple)
		print "email_text:"
		print (email_text)
		print (POff)

def MQTT():
	# Send to the MQTT Broker
	try:
		mqttc = mqtt.Client("python_pub")
		mqttc.connect("10.74.1.224", 1883)
		mqttc.publish("salt/Level (in)", SaltLv)
		mqttc.publish("salt/Percent (%)", PercentFull)
		mqttc.publish("salt/BagsNeeded", Bags)
		mqttc.publish("salt/LastReadTime", ETime)
		if Debug is True:
			print "MQTT updated"
	except:
		# Prevent crashing if Broker is disconnected
		if Debug is True:
			print "MQTT Failed"

''' Main Script '''
''' Wrap main content in a try block so we can catch the user pressing CTRL-C and run the GPIO cleanup function. '''
''' This will also prevent the user seeing lots of unnecessary error messages.   '''

try:

	if Debug is True:
		now = datetime.now()
		current_time = "Starting Salt Tank Measurement at: " + str(now.strftime("%H:%M:%S"))
		print (PRed)
		print (current_time)
		print ("Debug is On")
		if Email is True:
			print ("Email will be sent")
		else:
			print ("Email will NOT be sent")
		Temp = (Samples*Wait)
		print (str(Temp)) + " seconds per Average; ",
		print (str(Samples-1)) + " Samples per Average"
		print (str(PWait)) + " second(s) or " + str(PWait/60) + " minute(s) or " + str(PWait/60/60) + " hour(s); between Reading"
		print "Inches to max possible salt level from sensor: " + str(lvTop)
		print "Inches of salt per 40lb bag: " + str(lvBag)
		print "Inches from sensor considered full of salt: " + str(lvFull)
		print "Inches from sensor considered empty of salt: " + str(lvEmpty)
		print (POff)

	while True:
		distance = measure_average()
		Dist = str(round(distance,2))
		Bags = str((int(distance))/lvBag)
		#PercentFull = str(int((TopLv - lvTop - distance)/(TopLv-lvTop)*100))
		PercentFull = str(int((lvEmpty - distance)/(lvEmpty)*100))
		SaltLv = str(round(TopLv - distance,2))
		now = datetime.now()
		ETime = str(now.strftime("at %H:%M:%S on %m-%d-%Y"))
		MQTT()

		if Debug is True:
			print (PYellow)
			#now = datetime.now()
			Dist_Time = "Average Distance = " + Dist + " " + ETime
			print (Dist_Time),
			print " / " + Bags + " bags of salt needed. / ",
			print (PercentFull),
			print "% Full / Salt Level is ",
			print (SaltLv),
			print "inces."
			print (POff)

		if distance <= lvFull:
			subject = 'Salt Tank is FULL'
			body = "Tank Full at " + PercentFull + "%, " + SaltLv + " inches of Salt, " + Dist + " inches from top " + ETime
		elif distance >= lvEmpty:
			subject = 'Salt Tank is EMPTY'
			body = "Tank Empty at " + PercentFull + "%, " + SaltLv + " inches of Salt, " + Dist + " inches from top, " + Bags + " Bags of Salt to Fill " + ETime
		else:
			subject = 'Salt Tank Status'
			body = "Tank Level is " + PercentFull + "%, " + SaltLv + " inches of Salt, " + Dist + " inches from top, " + Bags + " Bags of Salt to Fill " + ETime

		if Email is True:
			today = datetime.today()
			Weekday = today.weekday()
			# Monday = 0, Tuesday = 1, Wensday = 2, Thursday = 3, Friday = 4, Saturday = 5, Sunday = 6
			if Debug is True:
				# Send Email during Debug regardless of day or send schedule
				print "Day of week is " + str(Weekday)
				print "Monday = 0, Tuesday = 1, Wensday = 2, Thursday = 3, Friday = 4, Saturday = 5, Sunday = 6"
				Message()
			else:
				if distance >= lvEmpty:
					# Send email if empty regardless of day of week
					subject = 'Salt Tank is EMPTY'
					body = "Tank Empty at " + PercentFull + "%, " + SaltLv + " inches of Salt, " + Dist + " inches from top, " + Bags + " Bags of Salt to Fill " + ETime
					Message()
				else:
					if Weekday == 4 and mail_sent is False:
						# Send email for tank status
						subject = 'Salt Tank Status'
						body = "Tank Level is " + PercentFull + "%, " + SaltLv + " inches of Salt, " + Dist + " inches from top, " + Bags + " Bags of Salt to Fill " + ETime
						Message()
						mail_sent = True # Allow only this email on sending day
					if Weekday == 5:
						mail_sent = False # Reset to allow email next time

		time.sleep(PWait)	# Sleep between readings

except KeyboardInterrupt:
	''' User pressed CTRL-C / Reset GPIO settings   '''
	GPIO.cleanup()
