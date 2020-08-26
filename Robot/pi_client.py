#!/usr/bin/env python

import rospy
import socket
import struct
import paho.mqtt.publish as publish

#mqtt server ip
mqtt_host = '10.231.234.184'
#raspberry pi ip
host = '10.42.0.92'
#mqtt server port
mqtt_port = 1883
#raspberry pi port of ssh
port = 8889

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

while True:
	word = s.recv(100)
	if not word:
		break
	print("receiving")
	print(word)

	#Get word without empty chars
	word_aux = []
	for i in range(100):
		if(word[i] is not  '\x00'):
			word_aux.append(word[i])

	str_mqtt = ""
        str_mqtt = ''.join(word_aux)

	#Choices for each word spelled
	if(str_mqtt  == "ONE"):
		publish.single("paho/devices","Lights", hostname = "10.231.234.184")
	elif(str_mqtt == "TWO"):
		publish.single("paho/devices","Coffee", hostname = "10.231.234.184")

	#Only for testing
	#publish.single("paho/devices",word,hostname = "10.231.234.184")
s.close()



