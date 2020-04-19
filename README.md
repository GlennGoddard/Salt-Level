# Salt-Level
Checks level of salt in water softner brine tank.

Utilizes utrasonic sensor attached to a Raspberry Pi to comunicate level via email or MQTT.

Python 2.7; not currently python 3 syntaxed.
Utilizes paho mqtt client (not needed if not utilizing MQTT); just comment out import of mqtt if not using.
Utilizes smtplib library for email communication.
Currently no LCD display setup in script.

Email sent on a custumizable day of the week to an email address; one additional cc is setup.
Default is Friday for standard email status of salt tank.
Email is sent regardless of day of week if tank is empty.

Email contains: percentage full, distance of salt from sensor, level of salt in tank, bags of salt needed to fill tank, date and time of email

MQTT is intergrated with customizable time interval.  Default is 10 mins.
Built in error handling for MQTT broker communication failure.

Debugging has been pre-worked with the used of a single variable at the begining of the script.
Debugging screen color codes are not all used; this is just a section that I put in all my scripts so I have the colors available without having to recreate it everytime.

Once script is working for your situation, just add to a cron job to start at boot-up.

## MQTT
Bags - How many 40lb bags of salt to fill tank  
DebugEnabled - True or False  
Count - # of MQTT Topics  
MQTT_Finish - Ture or False  
Email - True or False  
MailDay - Day of Week email sent  
MailDayInfo - Defines values for MailDay  
Time - Time of last MQTT post  
Level - Level of salt in inches from bottom of tank  
Percent - Percentage full of salt  
BottomLv - Just above water level  
lvBag - Inches per bag  
lvEmpty - Inches from top considered empty  
lvFull - level considered full  
lvTop - Top of tank from bottom  

## Change Log
4/8/2020  
Added a pause between MQTT Publish Topics, due to dropped topics on some MQTT Brokers  
Expanded MQTT Debug  

4/17/2020 1430  
Added MQTT Topics  
Added decimal to PercentFull and Bags  

4/18/2020 2130  
Added MQTT QoS and Retain  
