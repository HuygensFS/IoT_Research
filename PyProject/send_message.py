def choose_option(type):
	print()
	print(type, ':')
	for x in msgtype[type]:
		print("  ", x,"- Press", msgtype[type][x])
	
	
	while True:
		option = raw_input("Enter your option: ")
		try:
			msgtype[type].keys()[msgtype[type].values().index(int(option))]
			break
		except ValueError:
			print("Not valid option")
	return int(option)

def req_rsp():
	print()
	print("REQ or RSP?")
	listtypes = {
		"REQ": 1,
		"RSP": 2
	}

	for x in listtypes:
		print("  ", x,"- Press", listtypes[x])
	
	
	while True:
		option = raw_input("Enter your option: ")
		try:
			listtypes.keys()[listtypes.values().index(int(option))]
			break
		except ValueError:
			print("Not valid option")
	return int(option)

def read_params(frame):
	print()
	option = ""
	for x2 in range(0, len(frame)):
		print("Valor: ", x2, " e potencia: ", 2**x2)
		print(frame[x2].keys()[0], "(Max length is ", 2**x2, ")?")
		while True:
			newoption = None
			while not newoption:
				val = raw_input("  Value: ")
				try:
					newoption = int(val)
				except ValueError:
					print("Not valid option")
			if (newoption < (256*(2**x2)) and newoption > 0):
				#newoption = "%02X" % newoption
				option += convert_number(newoption)
				break
			else:
				print("Too long option")
	return option

def convert_number(number):
	if (number < 256):
		return chr(number)
	else:
		number_final = ""
		while (number > 255):
			number -= 255
			number_final = number_final + chr(255)
			#print("number grande: ", number_final)
		return chr(number) + number_final

def send_message():
	messageup("SEND MESSAGE")
	
	CmdType = choose_option("CmdType")
	Subsys = choose_option("Subsys")

	cmd0 = CmdType*10 + Subsys

	Subsys_str = msgtype["Subsys"].keys()[msgtype["Subsys"].values().index(int(Subsys))]
	cmd1 = choose_option(Subsys_str)
	
	cmd1_str = msgtype[Subsys_str].keys()[msgtype[Subsys_str].values().index(int(cmd1))]

	print("cmd1: ", convert_number(int(str(cmd1), 16)))

	temp = msgdict[Subsys_str]
	temp = temp[cmd1_str]
	temp = temp["params"]

	if(req_rsp() == 1):
		temp = temp["req"]
	else:
		temp = temp["rsp"]

	data = read_params(temp)

	message = convert_number(len(data)) + convert_number(int(str(cmd0), 16)) + convert_number(cmd1) + data
	#print("MESSAGE: ", printable_hex(message))
	send_command(message)