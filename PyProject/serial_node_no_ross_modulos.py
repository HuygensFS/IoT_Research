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
#import queue
#from queue import Queue
import json
#import paho.mqtt.client as paho

# Globals (I really need them)
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
msg_pub_q = []
broker="localhost"

def monitor_incoming():
	""" 
	A function to be run on a thread that constantly waits for new messages. 

	TODO: send messages back to main thread
	"""
	print("Incoming monitoring thread running.")
	while not stopping:
		# First four bytes are always
		# 0xFE, Length, CMD0, CMD1
		# Read response bytes
		line = ""
		byte = ""
		remaining = 10000
		
		# Try to read first byte. If it fails, we re-start the loop
		byte = ser.read()
		if not byte:
			continue

		if byte != "\xfe":
			print("Received incorrect message start, discarding:", printable_hex(byte))
			continue

		# Add first byte to the message
		line += byte

		# Get remaining bytes
		while remaining > 0:
			byte = ser.read()
			line += byte
			# When we have a length, we adjust how many bytes we're expecting
			if len(line) == 2:
				remaining = ord(line[-1])+4
			remaining -= 1
		
		# Filter out the mysterious message we always get on the first command
		if line == "\xfe\x02\x61\x01\xdd\x01":
			print("Got the mysterious message:", printable_hex(line))
			continue
		else:
			print("Received from serial port:", printable_hex(line) + ". ", end="")

		# Place the message in the appropriate queue
		if ord(line[2]) | ord("\x0F") == ord("\x6F"):
			print("Writing to synchronous queue.")
			sync_msg_q.put(line)
		else:
			print("Writing to asynchronous queue.")
			async_msg_q.put(line)

	# Inform that we're stopping
	print("Stopping incoming monitoring thread!")

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

		# Inform
		print("Processing async message:", printable_hex(msg))

		# Decode message type by analyzing the CMD field
		dec = decode_frame(msg, async=True)
		print("Message type:", dec["Type"])
		#pprint(dec)

		if dec["Name"] == "AF_INCOMING_MSG":
			data = dec["Remainder"]
			# If the corresponding bit is 1
			print("Device", printable_hex(dec["SrcAddr"]) + ":", end=" ")
			if len(data) == 10: # Door sensor
				door_open = (ord(data[3]) | ord("\xFE")) == ord("\xFF")
				if door_open:
					print("Door is open!")
					msg_pub_q.put([dec["SrcAddr"], "door", True])
					#send_mqtt("Open", "house/door")
				else:
					print("Door is closed!")
					msg_pub_q.put([dec["SrcAddr"], "door", False])
					#send_mqtt("Closed", "house/door")

	# Inform that we're stopping
	print("Stopping asynchronous message processing thread!")

"""
def process_sync():
	 
	A function to process the messages placed in the async queue.
	(usually run on a thread)

	TODO: Use dictionaries to make this generic and indexable by the CMD field.
	
	print("Asynchronous message processing thread running")
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
		dec = decode_frame(msg, async=True)
		print("Message type:", dec["Type"], " | Message name:", dec["Name"])
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

'''
def send_mqtt(value, topic):
	broker="localhost"
	#define callback
	def on_message(client, userdata, message):
		time.sleep(1)
		print("received message =",str(message.payload.decode("utf-8")))

	client= paho.Client("client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) 		#establish connection client1.publish("house/bulb1","on")
	######Bind function to callback
	client.on_message=on_message
	#####
	print("connecting to broker ",broker)
	client.connect(broker)#connect
	client.loop_start() #start loop to process received messages
	print("subscribing ")
	client.subscribe(topic)#subscribe
	#time.sleep(2)
	print("publishing ")
	client.publish(topic, value)#publish
	client.disconnect() #disconnect
	client.loop_stop() #stop loop
'''

def close_connection(serial_obj):
	""" Closes the connection on a serial object received. """
	serial_obj.close()

def decode_frame(packet, async=False):
	""" Decodes a packet according to a certain spec. 

	The spec is a list of the form
	[["name", len], ["name", len], ...], with the name of the attribute and 
	its length in bytes. The function returns a dictionary with the respective
	entries, and values as colon-separated hex strings.

	If async is true, no FCS is retrieved, since these packets don't seem to have it.

	TODO: Implement FCS checking
	"""
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
		"\x45\xb4": "Response to the ZDO Management Leave Request",
		"\x45\xb2": "Response to the ZDO Management Routing Table Request",
		"\x46\x85": "Find Device Operation Completes",
		"\x46\x83": "Acknowledgement of data indication",
		"\x45\x85": "Response to the ZDO Active Endpoint Request"
	}
	# Name on the docs
	msg_name = {
		"\x45\xc1": "ZDO_END_DEVICE_ANNCE_IND",
		"\x67\x00": "UTIL_GET_DEVICE_INFO",
		"\x45\xb6": "ZDO_MGMT_PERMIT_JOIN_RSP",
		"\x44\x81": "AF_INCOMING_MSG",
		"\x41\x80": "SYS_RESET_IND",
		"\x45\xc0": "ZDO_STATE_CHANGE_IND",
		"\x45\xb4": "ZDO_MGMT_LEAVE_RSP",
		"\x45\xb2": "ZDO_MGMT_RTG_RSP",
		"\x46\x85": "ZB_FIND_DEVICE_CONFIRM",
		"\x46\x83": "ZB_RECEIVE_DATA_INDICATION",
		"\x45\x85": "ZDO_ACTIVE_EP_RSP"
	}
	# Decoding spec
	msg_specs = {
		"\x45\xc1":	[["SrcAddr", 2], ["NwkAddr", 2], ["IEEEAddr", 8], ["Capabilities", 1]],
		"\x67\x00": [["status", 1], ["IEEEAddr", 8], ["ShortAddr", 2], ["DeviceType", 1], ["DeviceState", 1], ["NumAssocDevices", 1]],
		"\x45\xb6": [["SrcAddr", 2], ["Status", 1]],
		"\x44\x81": [["GroupID", 2], ["ClusterID", 2], ["SrcAddr", 2], ["SrcEndpoint", 1], ["DestEndpoint", 1], ["WasBroadcast", 1], ["LinkQuality", 1], ["SecurityUse", 1], ["TimeStamp", 4], ["TransSeqNumber", 1], ["Data Len", 1]],
		"\x41\x80": [["Reason", 1], ["TransportRev", 1], ["ProductID", 1]],
		"\x45\xc0": [["State", 1]],
		"\x45\xb4": [["SrcAddr", 2], ["Status", 1]],
		"\x45\xb2": [["SrcAddr", 2], ["Status", 1], ["RoutingTableEntries", 1], ["StartIndex", 1], ["RoutingTableListCount", 1], ["RoutingTableListRecords",0-75]],
		"\x46\x85": [["SearchType", 1], ["SearchKey", 2], ["Result", 8]],
		"\x46\x83": [["Source", 2], ["Command", 2], ["Len", 2], ["data", 7]],
		"\x45\x85": [["SrcAddr", 2], ["Status", 1], ["NwkAddr", 2], ["ActiveEPCount", 1], ["ActiveEPList", 0-77]]
	}

	# Get info on packet
	try:
		cmd = packet[2:4]
		out_dict["Type"] = printable_hex(cmd)
		out_dict["Name"] = msg_name[cmd]
		spec = msg_specs[cmd]
	except KeyError:
		out_dict["Type"] = printable_hex(cmd)
		out_dict["Name"] = "Unknown"
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

	# DEBUG: Print the command
	print("Writing to serial port:", printable_hex(command_str))

	# Send command
	ser.write(command_str)

def sync_command(command):
	""" Sends a synchronous command and returns the decoded reply. """
	print("Sending synchronous command:", printable_hex(command))
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
	# Clean the terminal
	os.system('cls' if os.name == 'nt' else 'clear')
	
	# Initialize dict for the state of the sensors
	sensors_state = {}
	message("Welcome")

	# Open the connection with the device
	open_connection()

	# Initialize the mesage queues
	sync_msg_q = queue.Queue()
	async_msg_q = queue.Queue()
	msg_pub_q = queue.Queue()

	# Start the threads
	m = threading.Thread(target=monitor_incoming)
	a = threading.Thread(target=process_async)
	#s = threading.Thread(target=process_sync)
	m.start()
	a.start()
	send_command("\x04\x21\x09\x01\x87\x00\x01\x00")	

	# # Get device info
	# UTIL_GET_DEVICE_INFO
	print("Getting device info")
	resp = sync_command("\x00\x27\x00")
	#pprint(resp)
	print()
	print("IEEEAddr:", printable_hex(resp['IEEEAddr']))
	print("ShortAddr:", printable_hex(resp['ShortAddr']))
	print()

	print("Resetting:")
	send_command("\x01\x41\x00\x00")
	#time.sleep(5)
	print()
	#send_command("\x04\x21\x09\x01\x87\x00\x01\x00")

	# ZDO_MGMT_PERMIT_JOIN_REQ
	print("Activating joining:")
	send_command("\x04\x25\x36\x00\x00\xFF\xFF")

	# TODO: Correctly bind the necessary clusters.
	# This is the final step needed to get the temp sensors working.
	# print("Requesting bind")
	#send_command("\x10\x25\x21\x22\x48\x24\x6e\xff\x08\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
	#send_command("\x10\x25\x21\x22\x48\xf5\x2b\xa5\x13\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
	# print("Comando enviado.")

	print()
	print("Requesting bind")
	print()
	#send_command("\x10\x25\x21\x22\x48\x64\x30\xa5\x13\x00\x4b\x12\x00\x01\x04\x00\xFF\xFF\xFF")
	#send_command("\x17\x25\x21\x95\x05\x64\x30\xa5\x13\x00\x4b\x12\x00\xFF\x01\x06\xFF\x24\x6e\xff\x08\x00\x4b\x12\x00\x01")
	#x64\x30\xa5\x13\x00\x4b\x12\x00
	
	#print("SCAN")
	#send_command("\x13\x22\x0c\x07\xFF\xF8\x00\x01\x05\x00\x24\x6e\xff\x08\x00\x4b\x12\x00\x00\x00\x00")
	#print("ZB_FIND_DEVICE_REQUEST")
	#send_command("\x08\x26\x07\x00\x00\x00\x00\x00\x00\x00\x00")
	#print("ZDO_ACTIVE_EP_REQ")
	#send_command("\x04\x25\x05\x00\x00\x01\x06")

	# Spin for a while and publish ROS messages when needed
	
	time.sleep(5)
	#print("UTIL_ADDRMGR_NWK_ADDR_LOOKUP")
	#send_command("\x02\x27\x41\xc8\xf2")
	#print("UTIL_ADDRMGR_NWK_ADDR_LOOKUP")
	#send_command("\x02\x27\x41\x95\x05")
	#send_command("\x05\x25\x04\x00\x00\x95\x05\x01")
	#FAILING send_command("\x0e\x24\x01\x95\x05\x01\x00\x01\x06\xf0\x10\xff\x02\x00\x00")
	#send_command("\x08\x27\x45\x76\xa5\xe9\x0e\x00\x4b\x12\x00")
	#send_command("\x04\x25\x02\x95\x05\x95\x05")
	#send_command("\x0b\x25\x37\x95\x05\x02\x07\xff\xf8\x00\xff\xff\x00\x00")

	#ZB_SEND_DATA_REQUEST
	send_command("\x17\x25\x21\x95\x05\x64\x30\xa5\x13\x00\x4b\x12\x00\x01\x01\x06\x03\x24\x6e\xff\x08\x00\x4b\x12\x00\x01")
	#send_command("\x17\x25\x21\xc8\xf2\x76\xa5\xe9\x0e\x00\x4b\x12\x00\xFF\x04\x02\xFF\x24\x6e\xff\x08\x00\x4b\x12\x00\x01")
	#x64\x30\xa5\x13\x00\x4b\x12\x00
	while True:
		try:
			#send_command("\x16\x24\x02\x02\x95\x05\xa5\x13\x00\x4b\x95\x05\x01\x01\x06\x01\x01\x06\x22\x10\xff\x02\x00\x00")
			#send_command("\x0c\x24\x01\x95\x05\x01\x01\x01\x06\x22\x10\xff\x02\x00\x24")

			#AF_REGISTER
			#send_command("\x09\x24\x00\x01\x95\x05\x01\x06\x00\x00\x00\x00\x00\x00")

			#send_command("\x0c\x24\x01\x95\x05\x01\x01\x01\x06\x22\x10\xff\x02\x00\x00")
			#send_command("\x0a\x24\x01\x95\x05\x01\x01\x01\x06\x22\x10\xff\x00")

			#TEST
			#send_command("\x0f\x24\x01\x95\x05\x01\x01\x01\x06\x22\x10\xff\x05\x00\x02\x00\x00\x00")

			#send_command("\x00\x21\x01")
			cmd = input("Command:")
			send_command(cmd)
			#print("Command sent")
			msg = msg_pub_q.get(timeout=1)
			print(msg)
			# msg is of structure [device address, msg type (str), value]
			print(sensors_state)
		except queue.Empty:
			continue
		except KeyboardInterrupt:
			break

	# Stop threads
	print()
	stopping = True
	m.join()
	a.join()

	# Close the connection when everything terminates
	print("Main thread terminating")
	close_connection(ser)
