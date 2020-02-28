# Salt-Level
Checks level of salt in water softner brine tank

Utilizes utrasonic sensor attached to a Raspberry Pi to comunicate level via email or MQTT.

Python 2.7; not currently python 3 syntaxed
Utilizes paho mqtt client (not needed if not utilizing MQTT); just comment out import of mqtt if not using
Utilizes smtplib library for email communication.
Currently no LCD display setup in script.

Email sent on a custumizable day of the week to an email address; one additional cc is setup.
Default is Friday for standard email status of salt tank.
Email is sent regardless of day of week if tank is empty.

Email contains: percentage full, distance of salt from sensor, level of salt in tank, bags of salt needed to fill tank, date and time of email

MQTT is intergrated with customizable time interval.  Default is 10 mins.
Built in error handling for MQTT broker communication failure.

Debugging has been preworked with the used of a single varable at the begining of the script.
Debugging screen color codes are not all used; this is just a section that I put in all my scripts so I have the colors available without having to recreate it everytime.

Once script is working for your situation, just add to a cron job to start at boot-up.
