#!/usr/bin/env python2
from __future__ import print_function

# Standard Library
import serial
from serial import SerialException
import io
from pprint import pprint
import time
import sys
import threading
import sys
import os
import Queue as queue
import json
import paho.mqtt.client as paho
from datetime import datetime
import subprocess
from termios import tcflush, TCIOFLUSH
execfile("send_message.py")

# Import dictionary from json
with open('zpi_meta.json') as handle:
    msgdict = json.loads(handle.read())
with open('zmt_defs.json') as handle:
    msgtype = json.loads(handle.read())

#f = open("demofile.txt", "a")

# Globals
# A variable for the Serial object
ser = []
# A queue for synchronous messages (response to synchronous commands)
sync_msg_q = []
# A queue for everything else
async_msg_q = []
# A variable to tell our threads that we're stopping
stopping = False
# A queue for sensor readings to publish
# It'll contain lists of the form [device address, msg type (str), value]
value = ""
topic = ""
line = ""
first = 1
frame = {}
msg_pub_q = []
broker = "localhost"

def monitor_incoming():
	""" 
	A function to be run on a thread that constantly waits for new messages. 

	TODO: send messages back to main thread
	"""
	print("Incoming monitoring thread running.")
    # state 0 = wating, 1=len,2=cmd0,3=cmd1,4=waitforfcs
	
	state = 0

	while not stopping:
		# First four bytes are always
		# 0xFE, Length, CMD0, CMD1
		# Read response bytes
		byte = ""

		byte = ser.read()

		if not byte:
			continue
			
		elif state == 0:
			if byte != "\xfe":
				print("Received incorrect message start, discarding:", printable_hex(byte))
			else:
				line = ""
				line += byte
				state = 1

		elif state == 1: #length
			frame["length"] = ord(byte)
			length = frame["length"]
			state = 2
			line += byte

		elif state == 2: #cmd0
			cmd0 = printable_hex(byte)
			frame["type"] = decodeCmdType(int(cmd0[0]))
			frame["subsystem"] = decodeSubsys(int(cmd0[1]))
			state = 3
			line += byte

		elif state == 3: #cmd1
			frame["id"] = decodeType(frame["subsystem"], ord(byte))
			state = 4
			line += byte
			data = ""

		else:
			if length > 0:
				data += byte
				line += byte
				length -= 1
			else:
				state = 0
				if (frame["type"] == decodeCmdType(2) or frame["type"] == decodeCmdType(4)):
					req = True
				else:
					req = False
				frame["data"] = decodeData(data, frame["subsystem"], frame["id"], req)
				#print()
				f = open("demofile.txt", "a")
				global first
				if(first == 1):
					now = datetime.now()
					f.write(now.strftime("\nPROGRAM START - %d/%m/%Y, %H:%M:%S\n"))
				showmessage(line, frame, data, f, 0)
				
				sync_msg_q.put(frame)
				if(first == 1):
					first = 0
				#Processamento da mensagem da porta:
				if(frame["subsystem"] == "AF"):
					for x in frame:
						if (x == "data"):
							max = 0
							alreadyread = 0
							for x2 in range(0, len(frame[x])):
								max = alreadyread + 2**frame[x][x2].values()[0]
								if(max > len(data)):
									max = len(data)
								datafinal = ""
								for x3 in range(alreadyread, max):
									if(datafinal != ""):
										datafinal += ':'
									datafinal += printable_hex(data[x3])
									if (printable_hex(data[x3]) == "30" or printable_hex(data[x3]) == "34"):
										send_mqtt('1', "zigbee/door")
									elif (printable_hex(data[x3]) == "31" or printable_hex(data[x3]) == "35"):
										send_mqtt('0', "zigbee/door")
									alreadyread += 1
				#criar uma fila de transmissao para onde enviamos as mensagens de cada uma 
				#das filas (sinc e nao sinc) para que nao haja conflitos
	print("Stopping incoming monitoring thread!")

def send_info():
	print("Send message thread running.")
	while not stopping:
		send_message()
	print("Stopping sending message!")

def showmessage(msg, frame, data, f, send):
	message = ""			
	if(send == 0):
		if (frame["type"] == decodeCmdType(6) or frame["type"] == decodeCmdType(2)):
			#messageup("MESSAGE RECEIVED (Sync Message)")
			f.write("MESSAGE RECEIVED (Sync Message) - ")
			message = "MESSAGE RECEIVED (Sync Message) - "
		else:
			#messageup("MESSAGE RECEIVED (Async Message)")
			f.write("MESSAGE RECEIVED (Async Message) - ")
			message = "MESSAGE RECEIVED (Async Message) - "
	else:
		if (frame["type"] == decodeCmdType(6) or frame["type"] == decodeCmdType(2)):
			#messageup("MESSAGE SEND (Sync Message)")
			f.write("MESSAGE SEND (Sync Message) - ")
			message = "MESSAGE SEND (Sync Message) - "
			#send_mqtt("MESSAGE SEND (Sync Message) - ", "house/aleatorio")
		else:
			#messageup("MESSAGE SEND (Async Message)")
			f.write("MESSAGE SEND (Async Message) - ")
			message = "MESSAGE SEND (Async Message) - "
			#send_mqtt("MESSAGE SEND (Async Message) - ", "house/aleatorio")
	now = datetime.now()
	f.write(now.strftime("%d/%m/%Y, %H:%M:%S\n"))
	#send_mqtt(now.strftime("%d/%m/%Y, %H:%M:%S\n"), "house/aleatorio")
	#print()
	#print("Message: ", printable_hex(msg))
	f.write("  Message: ")
	#send_mqtt("  Message: ", "house/aleatorio")
	f.write(printable_hex(msg))
	message += printable_hex(msg)
	send_mqtt(message, "house/aleatorio")
	f.write("\n")
	#send_mqtt("\n", "house/aleatorio")
	
	#print()
	for x in frame:
		if (x != "data"):
			#print(x,"-", frame[x])
			f.write("    ")
			f.write(x)
			f.write(" - ")
			f.write(str(frame[x]))
			f.write("\n")
	for x in frame:
		if (x == "data"):
			max = 0
			alreadyread = 0
			for x2 in range(0, len(frame[x])):
				max = alreadyread + 2**frame[x][x2].values()[0]
				if(max > len(data)):
					max = len(data)
				datafinal = ""
				for x3 in range(alreadyread, max):
					if(datafinal != ""):
						datafinal += ':'
					datafinal += printable_hex(data[x3])
					alreadyread += 1
				#print(frame[x][x2].keys()[0], "-", datafinal)
				f.write("    ")
				f.write(frame[x][x2].keys()[0])
				f.write(" - ")
				f.write(datafinal)
				f.write("\n")
	#print("====================================================================")					

def decodetype(type):
	listtypes = {
		0: "0 - POLL",
		2: "2 - SREQ",
		4: "4 - AREQ",
		6: "6 - SRSP"
	}
	return listtypes[type]

def decodeCmdType(CmdType):
	temp = msgtype["CmdType"]
	#print("msgtype: ", temp)
	return temp.keys()[temp.values().index(CmdType)]

def decodeSubsys(Subsys):
	temp = msgtype["Subsys"]	
	return temp.keys()[temp.values().index(Subsys)]

def decodeParamType(ParamType):
	temp = msgtype["ParamType"]	
	return temp.keys()[temp.values().index(ParamType)]

def decodeType(Subsys, Type):
	temp = msgtype[Subsys]
	return temp.keys()[temp.values().index(Type)]

def decodeData(Data, Subsys, Type, req):
	temp = msgdict[Subsys]
	temp = temp[Type]
	temp = temp["params"]
	if(req == True):
		temp = temp["req"]
	else:
		temp = temp["rsp"]
	return temp

def process_async():
	""" 
	A function to process the messages placed in the async queue.
	(usually run on a thread)

	TODO: Use dictionaries to make this generic and indexable by the CMD field.
	"""
	print("Asynchronous message processing thread running")
	while not stopping:
		# Get message
		try:
			msg = async_msg_q.get(block=False, timeout=1)
		except queue.Empty:
			continue
		
		'''
		# Decode message type by analyzing the CMD field
		dec = decode_frame(msg, async=True)
		print("Message type:", dec["Type"], " | Message name:", dec["Name"])
		#pprint(dec)

		if dec["Name"] == "AF_INCOMING_MSG":
			dec["SrcAddr"] = decode_device(dec["SrcAddr"])
			data = dec["Remainder"]
			# If the corresponding bit is 1
			if len(data) == 10: # Door sensor
				door_open = (ord(data[3]) | ord("\xFE")) == ord("\xFF")
				if door_open:
					print("====================================================================")
					print("Device", dec["SrcAddr"] + " | Door is open!")
					print("====================================================================")
					#msg_pub_q.put([dec["SrcAddr"], "door", True])
					#send_mqtt("Open", "house/aleatorio")
				else:
					print("====================================================================")
					print("Device", dec["SrcAddr"] + " | Door is closed!")
					print("====================================================================")
					#msg_pub_q.put([dec["SrcAddr"], "door", False])
					#send_mqtt("Closed", "house/aleatorio")
			else:
				print("Device", dec["SrcAddr"] + ":", end=" ")
				print("ClusterID = ", printable_hex(dec["ClusterID"]))
		'''
	# Inform that we're stopping
	print("Stopping asynchronous message processing thread!")
	

def process_sync():
	""" 
	A function to process the messages placed in the sync queue.
	(usually run on a thread)

	TODO: Use dictionaries to make this generic and indexable by the CMD field.
	
	print("Synchronous message processing thread running")

	print("THREADS: ", printable_hex(sync_msg_q.count()))
	while not stopping:
		# Get message
		try:
			msg = sync_msg_q.get(block=False, timeout=1)
		except queue.Empty:
			continue

		# Inform
		print()
		print("Processing sync message:", printable_hex(msg))

		# Decode message type by analyzing the CMD field
		dec = decode_frame(msg, async=False)
		print("Message type:", dec["Type"], " | Message name:", dec["Name"])
		#pprint(dec)

		if dec["Name"] == "AF_INCOMING_MSG":
			data = dec["Remainder"]
			# If the corresponding bit is 1
			print("Device", printable_hex(dec["SrcAddr"]) + ":", end=" ")
			print("ClusterID = ", printable_hex(dec["ClusterID"]))
			if len(data) == 10: # Door sensor
				door_open = (ord(data[3]) | ord("\xFE")) == ord("\xFF")
				if door_open:
					print("Door is open!")
					#msg_pub_q.put([dec["SrcAddr"], "door", True])
					#send_mqtt("Open", "house/aleatorio")
				else:
					print("Door is closed!")
					#msg_pub_q.put([dec["SrcAddr"], "door", False])
					#send_mqtt("Closed", "house/aleatorio")

	# Inform that we're stopping
	print("Stopping synchronous message processing thread!")
	"""

def printable_hex(command):
	""" Converts a string of hex ints to something print-able. """
	# https://stackoverflow.com/questions/12214801/print-a-string-as-hex-bytes
	return ":".join("{:02x}".format(ord(c)) for c in command)

def calc_fcs(command):
	""" Calculates the Frame Check Sequence that must be appended to every command.

	The FCS is an xor of all of the other bytes on the command.
	"""
	# Calculate the fcs by iteratively XOR-ing the command
	fcs = ord(command[0])
	for b in command[1:]:
		fcs = fcs^ord(b)
	return fcs


def open_connection(port="/dev/serial/by-id/usb-FTDI_FT230X_Basic_UART_DN00QQN1-if00-port0"):
	""" Opens a serial connection, returns the object if everything goes well,
	otherwise throws an exception. """
	# LINUX: /dev/serial/by-id/usb-FTDI_FT230X_Basic_UART_DN00QQN1-if00-port0
	# MAC: /dev/tty.usbserial-DN00QQN1
	# Open serial port
	global ser
	ser = serial.Serial()
	ser.baudrate = 115200
	ser.port = port
	ser.timeout = 1
	ser.open()

	# Raise if connection not open
	if not ser.is_open:
		raise RuntimeError("Could not open connection on port {}!".format(port))
	else:
		print("Serial connection open!")

	# Return object
	return ser

def send_mqtt(value, topic):
	broker="localhost"
	#define callback
	def on_message(client, userdata, message):
		time.sleep(1)
		#print("received message =",str(message.payload.decode("utf-8")))

	client= paho.Client("client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) 		#establish connection client1.publish("house/bulb1","on")
	######Bind function to callback
	client.on_message=on_message
	#####
	#print("connecting to broker ",broker)
	client.connect(broker)#connect
	client.loop_start() #start loop to process received messages
	#print("subscribing ")
	client.subscribe(topic)#subscribe
	#time.sleep(2)
	#print("publishing ")
	client.publish(topic, value)#publish
	client.disconnect() #disconnect
	client.loop_stop() #stop loop

def close_connection(serial_obj):
	""" Closes the connection on a serial object received. """
	serial_obj.close()

def decode_device(device):
	listdevices = {		
		"\xf9\x65": "1",	
		"\x40\x93": "2"
	}

	try:
		return listdevices[device]
	except KeyError:
		return "Device unknown"

def decode_frame(packet, async=False):
	''' Decodes a packet according to a certain spec. 

	The spec is a list of the form
	[["name", len], ["name", len], ...], with the name of the attribute and 
	its length in bytes. The function returns a dictionary with the respective
	entries, and values as colon-separated hex strings.

	If async is true, no FCS is retrieved, since these packets don't seem to have it.

	TODO: Implement FCS checking
	
	# Create output dict
	out_dict = {}

	# Message decoding specs:
	# Desctiption string
	msg_type = {
		"\x45\xc1": "New device connected!",
		"\x67\x00": "Device Info",
		"\x45\xb6": "Permit join response",
		"\x44\x81": "New data received",
		"\x41\x80": "Reset has occurred",
		"\x45\xc0": "ZDO state change",
		"\x45\xb4": "Response to the ZDO Management Leave Request"
	}
	# Name on the docs
	msg_name = {
		"\x45\xc1": "ZDO_END_DEVICE_ANNCE_IND",
		"\x67\x00": "UTIL_GET_DEVICE_INFO",
		"\x45\xb6": "ZDO_MGMT_PERMIT_JOIN_RSP",
		"\x44\x81": "AF_INCOMING_MSG",
		"\x41\x80": "SYS_RESET_IND",
		"\x45\xc0": "ZDO_STATE_CHANGE_IND",
		"\x45\xb4": "ZDO_MGMT_LEAVE_RSP"
	}
	msg_type2 = {
		"\x00": "POLL",
		"\x20": "SREQ",
		"\x40": "AREQ",
		"\x60": "SRSP"
	}
	msg_subsystem = {		
		"\x00": "Reserved",
		"\x01": "SYS interface",
		"\x02": "MAC interface",
		"\x03": "NWK interface",
		"\x04": "AF interface",
		"\x05": "ZDO interface",
		"\x06": "SAPI interface",
		"\x07": "UTIL interface",
		"\x08": "DEBUG interface",
		"\x09": "APP interface"
	}
	# Decoding spec
	msg_specs = {
		"\x45\xc1":	[["SrcAddr", 2], ["NwkAddr", 2], ["IEEEAddr", 8], ["Capabilities", 1]],
		"\x67\x00": [["status", 1], ["IEEEAddr", 8], ["ShortAddr", 2], ["DeviceType", 1], ["DeviceState", 1], ["NumAssocDevices", 1]],
		"\x45\xb6": [["SrcAddr", 2], ["Status", 1]],
		"\x44\x81": [["GroupID", 2], ["ClusterID", 2], ["SrcAddr", 2], ["SrcEndpoint", 1], ["DestEndpoint", 1], ["WasBroadcast", 1], ["LinkQuality", 1], ["SecurityUse", 1], ["TimeStamp", 4], ["TransSeqNumber", 1], ["Data Len", 1]],
		"\x41\x80": [["Reason", 1], ["TransportRev", 1], ["ProductID", 1]],
		"\x45\xc0": [["State", 1]],
		"\x45\xb4": [["SrcAddr", 2], ["Status", 1]]
	}

	# Get info on packet
	try:
		cmd = packet[2:4]
		out_dict["Type"] = printable_hex(cmd)
		out_dict["Name"] = msg_name[cmd]
		#out_dict["Subsystem"] = msg_subsystem[cmd]
		#out_dict["Type2"] = msg_type2[cmd]
		spec = msg_specs[cmd]
	except KeyError:
		out_dict["Type"] = printable_hex(cmd)
		out_dict["Name"] = "Unknown"
		#out_dict["Subsystem"] = "Unknown"
		#out_dict["Type2"] = "Unknown"
		return out_dict
	
	try:
		cmd = packet[2]
		frame["type"] = cmd0[0]
		frame["subsystem"] = cmd0[1]
		print("CMDOIIIIasdjkdjkajknsadjnkda: ", printable_hex(cmd))
		out_dict["Subsystem"] = msg_subsystem[cmd]
		print("Subsystem: ", out_dict["Subsystem"])
	except KeyError:
		out_dict["Subsystem"] = "Unknown"
		print("Subsystem: ", out_dict["Subsystem"])
		return out_dict
	
	try:
		cmd = packet[3:4]
		print("CMD: ", printable_hex(cmd))
		out_dict["Subsystem"] = msg_subsystem[cmd]
		print("Subsystem: ", out_dict["Subsystem"])
	except KeyError:
		out_dict["Subsystem"] = "Unknown"
		print("Subsystem: ", out_dict["Subsystem"])
		return out_dict

	# Copy the packet to a local variable
	byte_string = packet[:]

	# Strip control bytes
	out_dict["Packet Start"] = byte_string[0]
	byte_string = byte_string[1:]
	out_dict["Length"] = byte_string[0]
	byte_string = byte_string[1:]
	out_dict["CMD0"] = byte_string[0]
	byte_string = byte_string[1:]
	out_dict["CMD1"] = byte_string[0]
	byte_string = byte_string[1:]
	if not async:
		out_dict["FCS"] = byte_string[-1]
		byte_string = byte_string[:-1]
	
	# Convert the remaining packet to a dictionary according to the spec
	for attr in spec:
		# Get data from byte string
		data = byte_string[0:attr[1]]
		# Remove the data we got
		byte_string = byte_string[attr[1]:]
		# Convert it to an integer
		out_dict[attr[0]] = data
	# If the spec is well-formed, there should be no remainder.
	out_dict["Remainder"] = byte_string

	# Return the dictionary
	return out_dict
	'''
def send_command(command):
	""" Sends a command through the serial port.
	
	The input is the "clean" command, all control bytes (prefix and FCS) are
	added by this function. I.e., you can input commands directly from the
	reference manual in this function.
	"""	
	# Calculate FCS
	fcs = calc_fcs(command)

	# Compose command
	prefix = "\xFE"
	command_str = prefix + command + chr(fcs)

	frame["length"] = ord(command[0])
	
	cmd0 = printable_hex(command[1])
	
	frame["type"] = decodeCmdType(int(cmd0[0]))
	frame["subsystem"] = decodeSubsys(int(cmd0[1]))
	
	frame["id"] = decodeType(frame["subsystem"], ord(command[2]))
	
	if (frame["type"] == decodeCmdType(2) or frame["type"] == decodeCmdType(4)):
		req = True
	else:
		req = False
	
	data = ""
	for x in range(3, len(command)):
		data += command[x]

	frame["data"] = decodeData(data, frame["subsystem"], frame["id"], req)
	
	#print()
	f = open("demofile.txt", "a")
	global first
	if(first == 1):
		now = datetime.now()
		f.write(now.strftime("\nPROGRAM START - %d/%m/%Y, %H:%M:%S\n"))
		first = 0

	showmessage(command_str, frame, data, f, 1)

	# Send command
	ser.write(command_str)

def sync_command(command):
	""" Sends a synchronous command and returns the decoded reply. """
	#print("Sending synchronous command:", printable_hex(command))

	send_command(command)
	resp = sync_msg_q.get()
	if resp:
		decoded_resp = decode_frame(resp)
	else:
		decoded_resp = []
	return decoded_resp

def message(message):
	print("====================================================================")
	print(message)
	print("====================================================================")

def messageup(message):
	print("====================================================================")
	print(message)

def messagedown(message):
	print(message)
	print("====================================================================")


if __name__ == "__main__":
	#TESTES FUNCAO ENVIO

	#send_message()

	# Clean the terminal
	os.system('cls' if os.name == 'nt' else 'clear')
	
	# Initialize dict for the state of the sensors
	sensors_state = {}
	messageup("WELCOME")
	message("To run this program open other terminal window and put tail -f demofile.txt")
	# Open the connection with the device
	open_connection()

	# Initialize the mesage queues
	sync_msg_q = queue.Queue()
	async_msg_q = queue.Queue()
	msg_pub_q = queue.Queue()

	# Start the threads
	m = threading.Thread(target=monitor_incoming)
	a = threading.Thread(target=process_async)
	s = threading.Thread(target=process_sync)
	e = threading.Thread(target=send_info)
	m.start()
	a.start()
	s.start()
	e.start()
	
	# Get device info
	sync_command("\x00\x27\x00")
	
	send_command("\x01\x41\x00\x00")
	time.sleep(5)
	
	# ZDO_MGMT_PERMIT_JOIN_REQ
	send_command("\x04\x25\x36\x00\x00\xFF\xFF")
	
	send_command("\x04\x24\x01\x00\x00\xFF\xFF\x04\x00\x00")
	
	send_command("\x10\x24\x00\xFF\xFF\xFF\xFF\xff\x08\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
	# TODO: Correctly bind the necessary clusters.
	# This is the final step needed to get the temp sensors working.
	# print("Requesting bind")
	# send_command("\x10\x25\x21\x22\x48\x24\x6e\xff\x08\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
	# send_command("\x10\x25\x21\x22\x48\xf5\x2b\xa5\x13\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
	# print("Comando enviado.")

	#print("Requesting bind")
	#send_command("\x10\x26\x03\x22\x48\x24\x6e\xff\x08\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
	#send_command("\x10\x26\x03\x22\x48\x24\x6e\xff\x08\x00\x4b\x12\x00\x01\x05\x01\xFF\xFF\xFF")
	#send_command("\x10\x26\x03\x22\x48\x24\x6e\xff\x08\x00\x4b\x12\x00\x01\x04\x02\xFF\xFF\xFF")
	#send_command("\x10\x25\x21\x00\x00\x64\x30\xa5\x13\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
	#send_command("\x10\x26\x03\x22\x48\x24\x6e\xff\x08\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
		
	# Spin for a while and publish ROS messages when needed
	while True:
		try:
			msg = msg_pub_q.get(timeout=1)
			print(msg)
		except queue.Empty:
			continue
		except KeyboardInterrupt:
			break

	# Stop threads
	#print()
	stopping = True
	m.join()
	a.join()
	s.join()

	# Close the connection when everything terminates
	print("Main thread terminating")
	close_connection(ser)
	
