


'''
ASEBA PROTOCOL
'''

import socket
from time import *

ASEBA_PROTOCOL_VERSION                      = 0x0004

''' from bootloader control program to a specific node '''
ASEBA_MESSAGE_BOOTLOADER_RESET              = 0x8000
ASEBA_MESSAGE_BOOTLOADER_READ_PAGE          = 0x8001
ASEBA_MESSAGE_BOOTLOADER_WRITE_PAGE         = 0x8002
ASEBA_MESSAGE_BOOTLOADER_PAGE_DATA_WRITE    = 0x8003
	
''' from node to bootloader control program '''
ASEBA_MESSAGE_BOOTLOADER_DESCRIPTION        = 0x8004
ASEBA_MESSAGE_BOOTLOADER_PAGE_DATA_READ     = 0x8005
ASEBA_MESSAGE_BOOTLOADER_ACK                = 0x8006
	
''' from a specific node '''
ASEBA_MESSAGE_DESCRIPTION                   = 0x9000
ASEBA_MESSAGE_NAMED_VARIABLE_DESCRIPTION    = 0x9001
ASEBA_MESSAGE_LOCAL_EVENT_DESCRIPTION       = 0x9002
ASEBA_MESSAGE_NATIVE_FUNCTION_DESCRIPTION   = 0x9003

'''
	ASEBA_MESSAGE_DISCONNECTED,
'''
ASEBA_MESSAGE_VARIABLES                     = 0x9005
'''
	ASEBA_MESSAGE_ARRAY_ACCESS_OUT_OF_BOUNDS,
	ASEBA_MESSAGE_DIVISION_BY_ZERO,
'''
ASEBA_MESSAGE_EVENT_EXECUTION_KILLED		= 0x9008
'''
	ASEBA_MESSAGE_NODE_SPECIFIC_ERROR,
'''
ASEBA_MESSAGE_EXECUTION_STATE_CHANGED       = 0x900A
ASEBA_MESSAGE_BREAKPOINT_SET_RESULT         = 0x900B

'''from IDE to all nodes '''
ASEBA_MESSAGE_GET_DESCRIPTION               = 0xA000

'''
	/* from IDE to a specific node */
'''
ASEBA_MESSAGE_SET_BYTECODE		    		= 0xA001
ASEBA_MESSAGE_RESET                         = 0xA002
ASEBA_MESSAGE_RUN                           = 0xA003
ASEBA_MESSAGE_PAUSE                         = 0xA004
ASEBA_MESSAGE_STEP                          = 0xA005
ASEBA_MESSAGE_STOP                          = 0xA006
ASEBA_MESSAGE_GET_EXECUTION_STATE           = 0xA007
ASEBA_MESSAGE_BREAKPOINT_SET                = 0xA008
ASEBA_MESSAGE_BREAKPOINT_CLEAR 				= 0xA009
ASEBA_MESSAGE_BREAKPOINT_CLEAR_ALL          = 0xA00A
ASEBA_MESSAGE_GET_VARIABLES                 = 0xA00B
ASEBA_MESSAGE_SET_VARIABLES					= 0xA00C

'''
	ASEBA_MESSAGE_WRITE_BYTECODE,
	ASEBA_MESSAGE_REBOOT,
	ASEBA_MESSAGE_SUSPEND_TO_RAM,
'''	
ASEBA_MESSAGE_INVALID                       = 0xFFFF

def SwapEndian16(val16):
	msb = val16 & 0x0000FF00
	lsb = val16 & 0x000000FF
	result = (lsb << 8) | (msb >> 8)
	#print hex(msb) + ':' + hex(lsb) + ':' + hex(result)
	return result
	
def ExtractUInt16(string):
    # print 's0=' + hex(ord(string[0])) + ' s1=' + hex(ord(string[1]))
    val = ord(string[0]) + (ord(string[1]) << 8)
    return val

def UInt8(value):
    return chr(value & 0xFF)

def AddUInt8(string, value):
    string = string + UInt8(value)
    return string

def RecvUInt8(ClientSocket):
    donnees = ClientSocket.recv(1)
    if not donnees:
        print 'Erreur de reception.'
        return None
    result = ord(donnees[0])
    return result

def RecvUInt16(ClientSocket):
    donnees = ClientSocket.recv(2)
    if not donnees:
        print 'Erreur de reception.'
        return None
    result = ExtractUInt16(donnees)
    return result

def UInt16(value):
    return chr(value & 0x00FF) + chr((value >> 8) & 0x00FF)

def AddUInt16(string, value):
    string = string + UInt16(value)
    return string

def InsUInt16(string, value):
    string = UInt16(value) + string
    return string

def SInt16(value):
    return chr(value & 0x00FF) + chr((value >> 8) & 0x00FF)

def AddSInt16(string, value):
    string = string + SInt16(value)
    return string

def AddString(string, value):
    #print 'AddString:' + value
    string = AddUInt8(string, len(value))
    for c in value:
        string = AddUInt8(string, ord(c))
    return string

def AsebaPrintMessage(buf):
    print "len=" + str(ExtractUInt16(buf[0:2]))
    print "id=" + hex(ExtractUInt16(buf[2:4]))
    msgtype = ExtractUInt16(buf[4:6])
    print "type=" + hex(msgtype)
    for c in buf[6:]:
        if ord(c) >= 32 and ord(c) <= 126:
            a = c
        else:
            a = '*'
        s = hex(ord(c))
        if len(s) == 3:
            s = s[0:2] + '0' + s[2:]
        print s + ':' + a
    return

def AsebaSendBuffer(client, buf):
    #AsebaPrintMessage(buf)
    n = client.send(buf)
    if (n != len(buf)):
        print 'Erreur envoi.'
    #else:
    #    print 'Envoi ok.'
    return

def AsebaSendMessage(client, src, typ, data):
    print 'SendMessage(src=' + str(src) + ',type=' + hex(typ) + ')'
    header = ''
    header = AddUInt16(header, len(data))
    header = AddUInt16(header, src)
    header = AddUInt16(header, typ)
    AsebaSendBuffer(client, header + data)
    return

def AsebaSendMessageWords(client, src, typ, data16):
    print 'SendMessage(src=' + str(src) + ',type=' + hex(typ) + ')'
    data = ''
    for d in data16:
		data = AddUInt16(data, d)
    header = ''
    header = AddUInt16(header, len(data))
    header = AddUInt16(header, src)
    header = AddUInt16(header, typ)
    AsebaSendBuffer(client, header + data)
    return

def AsebaSendDescription(client, vm):
    vmDesc = vm['vm_description']
    varDesc = vm['vm_variables_description']
    evDesc = vm['vm_localevents_description']
    natDesc = vm['vm_nativefunctions_description']
    vmState = vm

    allVariablesSize = vmDesc['VM_VARIABLES_FREE_SPACE']
    for v in varDesc:
        allVariablesSize = allVariablesSize + v[0]

    buf = ''
    buf = AddString(buf, vmDesc['PRODUCT_NAME'])
    buf = AddUInt16(buf, ASEBA_PROTOCOL_VERSION)
    buf = AddUInt16(buf, vmDesc['VM_BYTECODESIZE'])
    buf = AddUInt16(buf, vmDesc['VM_STACK_SIZE'])
    buf = AddUInt16(buf, allVariablesSize)
    buf = AddUInt16(buf, len(varDesc))
    buf = AddUInt16(buf, len(evDesc))
    buf = AddUInt16(buf, len(natDesc))
    AsebaSendMessage(client, vmState['nodeId'], ASEBA_MESSAGE_DESCRIPTION, buf)

    sleep(1)
    
    for v in varDesc:
        buf = ''
        buf = AddUInt16(buf, v[0])
        buf = AddString(buf, v[1])
        AsebaSendMessage(client, vmState['nodeId'], ASEBA_MESSAGE_NAMED_VARIABLE_DESCRIPTION, buf)

    for e in evDesc:
        buf = ''
        buf = AddString(buf, e[0])
        buf = AddString(buf, e[1])
        AsebaSendMessage(client, vmState['nodeId'], ASEBA_MESSAGE_LOCAL_EVENT_DESCRIPTION, buf)

    for f in natDesc:
        buf = ''
        buf = AddString(buf, f[0])
        buf = AddString(buf, f[1])
        buf = AddUInt16(buf, len(f[2]))
        for arg in f[2]:
            buf = AddSInt16(buf, arg[0])
            buf = AddString(buf, arg[1])
        AsebaSendMessage(client, vmState['nodeId'], ASEBA_MESSAGE_NATIVE_FUNCTION_DESCRIPTION, buf)
    return

def AsebaSendVariables(client, vm, start, length):
	vmState = vm
	vmVar = vmState['variables']
	buf = ''
	buf = AddUInt16(buf, start)
	for i in range(start, start+length):
		if i < len(vmVar):
			var = vmVar[i]
		else:
			var = vmVar[0]

		buf = AddUInt16(buf, var)
	AsebaSendMessage(client, vmState['nodeId'], ASEBA_MESSAGE_VARIABLES, buf)
	return

def AsebaSendExecutionState(client, vm):
    vmState = vm
    pc = vmState['pc']
    flags = vmState['flags']
    buf = ''
    buf = AddUInt16(buf, pc)
    buf = AddUInt16(buf, flags)
    AsebaSendMessage(client, vmState['nodeId'], ASEBA_MESSAGE_EXECUTION_STATE_CHANGED, buf)
    return

def AsebaSendBreakpointSetResult(client, vm):
    vmState = vm
    pc = vmState['pc']
    success = 1
    buf = ''
    buf = AddUInt16(buf, pc)
    buf = AddUInt16(buf, success)
    AsebaSendMessage(client, vmState['nodeId'], ASEBA_MESSAGE_BREAKPOINT_SET_RESULT, buf)
    return


ADRESSE = ''
PORT = 33334

def AsebaNetworkStart(vm):
	print 'Demarrage du serveur sur port ' + str(PORT)
	serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serveur.bind((ADRESSE, PORT))
	serveur.listen(1)
	#while True:
	#try:
	print 'Attente connexion client...'
	client, adresseClient = serveur.accept()
	print 'Connexion de ', adresseClient

	vm['network'] = client

	while True:
		Length = RecvUInt16(client)
		Source = RecvUInt16(client)
		Type = RecvUInt16(client)
		print 'RECV : Len=' + str(Length) + ' Src=' + str(Source) + ' Typ=' + hex(Type)

		if Type == ASEBA_MESSAGE_GET_DESCRIPTION:
			version = RecvUInt16(client)
			print 'ASEBA_MESSAGE_GET_DESCRIPTION : Protocol version=' + str(version)
			AsebaSendDescription(client, vm)
			
		elif Type == ASEBA_MESSAGE_GET_VARIABLES:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				start = RecvUInt16(client)
				length = RecvUInt16(client)
				print 'ASEBA_MESSAGE_GET_VARIABLES : dst=' + str(destination) + ' start=' + str(start) + ' len=' + str(length)
				AsebaSendVariables(client, vm, start, length)

		elif Type == ASEBA_MESSAGE_SET_VARIABLES:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				start = RecvUInt16(client)
				length = Length - 1
				print 'ASEBA_MESSAGE_GET_VARIABLES : dst=' + str(destination) + ' start=' + str(start) + ' len=' + str(length)
				for i in range(length):
					value = RecvUInt16(client)
					vm['variables'][i] = value
					print 'var ' + str(i) + ' set to ' + hex(value)
				
		elif Type == ASEBA_MESSAGE_SET_BYTECODE:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				start = RecvUInt16(client)
				nbByteCode = (Length - 2 - 2) / 2
				print 'ASEBA_MESSAGE_SET_BYTECODE : dst=' + str(destination) + ' start=' + str(start) + ' nbbytecode=' + str(nbByteCode)
				for i in range(nbByteCode):
					bytecode = RecvUInt16(client)
					print 'bytecode=' + hex(bytecode)
					vm['bytecode'][i + start] = bytecode
				vm['flags'] = ASEBA_VM_STEP_BY_STEP_MASK
				result = AsebaVmSetupEvent(vm, ASEBA_EVENT_INIT)
				if result == 0:
					AsebaSendExecutionState(client, vm)
				
		elif Type == ASEBA_MESSAGE_RESET:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				vm['flags'] = ASEBA_VM_STEP_BY_STEP_MASK
				print 'ASEBA_MESSAGE_RESET : dst=' + str(destination) + ' flags=' + hex(vm['flags'])
				AsebaSendExecutionState(client, vm)
			
		elif Type == ASEBA_MESSAGE_RUN:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				vm['flags'] = vm['flags'] & ~ASEBA_VM_STEP_BY_STEP_MASK
				print 'ASEBA_MESSAGE_RUN : dst=' + str(destination) + ' flags=' + hex(vm['flags'])
				AsebaSendExecutionState(client, vm)

		elif Type == ASEBA_MESSAGE_PAUSE:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				print 'ASEBA_MESSAGE_PAUSE : dst=' + str(destination)
				vm['flags'] = vm['flags'] | ASEBA_VM_STEP_BY_STEP_MASK
				print 'ASEBA_MESSAGE_PAUSE : dst=' + str(destination) + ' flags=' + hex(vm['flags'])
				AsebaSendExecutionState(client, vm)

		elif Type == ASEBA_MESSAGE_STEP:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				print 'ASEBA_MESSAGE_STEP : dst=' + str(destination) + ' flags=' + hex(vm['flags'])
				if vm['flags'] & ASEBA_VM_EVENT_ACTIVE_MASK != 0:
					AsebaVmStep(vm)
					AsebaSendExecutionState(client, vm)

		elif Type == ASEBA_MESSAGE_STOP:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				vm['flags'] = ASEBA_VM_STEP_BY_STEP_MASK
				print 'ASEBA_MESSAGE_STOP : dst=' + str(destination) + ' flags=' + hex(vm['flags'])
				AsebaSendExecutionState(client, vm)

		elif Type == ASEBA_MESSAGE_GET_EXECUTION_STATE:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				print 'ASEBA_MESSAGE_GET_EXECUTION_STATE : dst=' + str(destination)
				AsebaSendExecutionState(client, vm)

		elif Type == ASEBA_MESSAGE_BREAKPOINT_SET:
			destination = RecvUInt16(client)
			pc = RecvUInt16(client)
			if destination == vm['nodeId']:
				print 'ASEBA_MESSAGE_BREAKPOINT_SET : dst=' + str(destination) + ' pc=' + hex(pc)
				AsebaSendBreakpointSetResult(client, vm)

		elif Type == ASEBA_MESSAGE_BREAKPOINT_CLEAR:
			destination = RecvUInt16(client)
			pc = RecvUInt16(client)
			if destination == vm['nodeId']:
				print 'ASEBA_MESSAGE_BREAKPOINT_CLEAR : dst=' + str(destination) + ' pc=' + hex(pc)
				AsebaSendBreakpointSetResult(client, vm)

		elif Type == ASEBA_MESSAGE_BREAKPOINT_CLEAR_ALL:
			destination = RecvUInt16(client)
			if destination == vm['nodeId']:
				print 'ASEBA_MESSAGE_BREAKPOINT_CLEAR_ALL : dst=' + str(destination)
				AsebaSendExecutionState(client, vm)
			
		else:
			print 'UNKNOWN MESSAGE, RECEIVING FOLLOWING BYTES...'
			for i in range(Length):
				val = RecvUInt8(client)
			
		sleep(0.1)

	#except Exception:
		#pass

	print 'Fermeture de la connexion avec le client.'
	client.close()

	print 'Arret du serveur.'
	serveur.close()


'''
VM
'''

import threading

ASEBA_VM_DEBUG = True

ASEBA_BYTECODE_STOP 				= 0x00
ASEBA_BYTECODE_SMALL_IMMEDIATE 		= 0x01
ASEBA_BYTECODE_LARGE_IMMEDIATE 		= 0x02
ASEBA_BYTECODE_LOAD 				= 0x03
ASEBA_BYTECODE_STORE 				= 0x04
ASEBA_BYTECODE_LOAD_INDIRECT 		= 0x05
ASEBA_BYTECODE_STORE_INDIRECT 		= 0x06
ASEBA_BYTECODE_UNARY_ARITHMETIC 	= 0x07
ASEBA_BYTECODE_BINARY_ARITHMETIC 	= 0x08
ASEBA_BYTECODE_JUMP 				= 0x09
ASEBA_BYTECODE_CONDITIONAL_BRANCH 	= 0x0A
ASEBA_BYTECODE_EMIT 				= 0x0B
ASEBA_BYTECODE_NATIVE_CALL 			= 0x0C
ASEBA_BYTECODE_SUB_CALL 			= 0x0D
ASEBA_BYTECODE_SUB_RET 				= 0x0E

ASEBA_VMSTATE_ACTIVE				= 0x00
ASEBA_VM_EVENT_ACTIVE_MASK			= 0x01
ASEBA_VM_STEP_BY_STEP_MASK			= 0x02
ASEBA_VM_EVENT_RUNNING_MASK			= 0x04

ASEBA_EVENT_INIT 					= 0xFFFF
ASEBA_EVENT_LOCAL_EVENTS_START 		= 0xFFFE

ASEBA_BINARY_OPERATOR_MASK          = 0x00FF
ASEBA_UNARY_OPERATOR_MASK           = 0x00FF
ASEBA_IF_IS_WHEN_BIT                = 8
ASEBA_IF_WAS_TRUE_BIT               = 9

VM_DESCRIPTION = {
    'PRODUCT_NAME'              : "Thymio-II",
    'PRODUCT_ID'                : 8,
    'FIRMWARE_VERSION' 			: [6,0],
    'ID'                        : 1,
    'VM_VARIABLES_FREE_SPACE'   : 512,
    'VM_BYTECODESIZE'           : 766+768,
    'VM_STACK_SIZE'             : 32,
    'VM_VARIABLES_ARG_SIZE'     : 32,
    'VM_VARIABLES_FREE_SPACE'   : 1024,
    }

'''
VARIABLES DESCRIPTIONS
First value is the number of element in the array (1 if not an array)
Second value is the name of the variable which will be displayed in aseba studio
'''

VM_VARIABLES_DESCRIPTION = [
	[1, "_id"], # Do not touch it
	[1, "event.source"], # Nor this one
	[VM_DESCRIPTION['VM_VARIABLES_ARG_SIZE'], "event.args"], # neither this one
	[2, "_fwversion"], # Do not event think about changing this one ...
	[1, "_productId"], # Robot type
        
	[5, "buttons._raw"],
	[1, "button.backward"], #variables[42]
	[1, "button.left"],
	[1, "button.center"],
	[1, "button.forward"],
	[1, "button.right"],
			
	[5, "buttons._mean"],
	[5, "buttons._noise"],
		
	[7, "prox.horizontal"],
	[2, "prox.ground.ambiant"],
	[2, "prox.ground.reflected"],
	[2, "prox.ground.delta"],
		
	[1, "motor.left.target"],
	[1, "motor.right.target"],
	[2, "_vbat"],
	[2, "_imot"],
	[1, "motor.left.speed"],
	[1, "motor.right.speed"],
	[1, "motor.left.pwm"],
	[1, "motor.right.pwm"],
		
	[3, "acc"],
		
	[1, "temperature"],
		
	[1, "rc5.address"],
	[1, "rc5.command"],
		
	[1, "mic.intensity"],
	[1, "mic.threshold"],
	[1, "mic._mean"],
		
	[2, "timer.period"],
		
	[1, "acc._tap"],

    ]

VARNUM_BUTTON_BACKWARD		= 42
VARNUM_BUTTON_LEFT			= 43
VARNUM_BUTTON_CENTER		= 44
VARNUM_BUTTON_FORWARD		= 45
VARNUM_BUTTON_RIGHT			= 46
VARNUM_PROX_H               = 57
VARNUM_MOTOR_LEFT_TARGET 	= 70
VARNUM_MOTOR_RIGHT_TARGET 	= 71

'''
EVENT DESCRIPTIONS
First value is event "name" (will be used as "onevent name" in asebastudio
Second value is the event description
'''
VM_LOCALEVENTS_DESCRIPTION = [
    [ "button.backward", "Backward button status changed"],
    [ "button.left", "Left button status changed"],
    [ "button.center", "Center button status changed"],
    [ "button.forward", "Forward button status changed"],
    [ "button.right", "Right button status changed"],	
    [ "buttons", "Buttons values updated"],
    [ "prox", "Proximity values updated"],
    [ "tap", "A tap is detected"],
    [ "acc", "Accelerometer values updated"],
    [ "mic", "Fired when microphone intensity is above threshold"],	
    [ "sound.finished", "Fired when the playback of a user initiated sound is finished"],
    [ "temperature", "Temperature value updated"],
    [ "rc5", "RC5 message received"],
    [ "motor", "Motor timer"],
    [ "timer0", "Timer 0"],
    [ "timer1", "Timer 1"],
]

EVENT_B_BACKWARD 			= 0
EVENT_B_LEFT				= 1
EVENT_B_CENTER				= 2
EVENT_B_FORWARD				= 3
EVENT_B_RIGHT				= 4
EVENT_BUTTONS				= 5
EVENT_PROX					= 6
EVENT_TAP					= 7
EVENT_ACC					= 8
EVENT_MIC					= 9
EVENT_SOUND_FINISHED		= 10
EVENT_TEMPERATURE			= 11
EVENT_RC5					= 12
EVENT_MOTOR					= 13
EVENT_TIMER0				= 14
EVENT_TIMER1				= 15
EVENT_COUNT					= 16

'''
NATIVE FUNCTIONS
'''

ASEBA_NATIVE_DEBUG = True

AsebaNativeDescription__system_reboot = [
	"_system.reboot",
	"Reboot the microcontroller",
	[
    ]
]
def AsebaNative__system_reboot(vm):
	AsebaNativeDebug('AsebaNative__system_reboot')
	

AsebaNativeDescription__system_settings_read = [
	"_system.settings.read",
	"Read a setting",
	[
		[ 1, "address"],
		[ 1, "value"],
    ]
]
def AsebaNative__system_settings_read(vm):
	AsebaNativeDebug('AsebaNative__system_settings_read')
	
AsebaNativeDescription__system_settings_write = [
	"_system.settings.write",
	"Write a setting",
	[
		[ 1, "address"],
		[ 1, "value"],
    ]
]
def AsebaNative__system_settings_write(vm):
	AsebaNativeDebug('AsebaNative__system_settings_write')
	
AsebaNativeDescription__system_settings_flash = [
	"_system.settings.flash",
	"Write the settings into flash",
	[
    ]
]
def AsebaNative__system_settings_flash(vm):
	AsebaNativeDebug('AsebaNative__system_settings_flash')
	

AsebaNativeDescription_veccopy = [
	"math.copy",
	"copies src to dest element by element",
	[
		[ -1, "dest" ],
		[ -1, "src" ],
	]
]
def AsebaNative_veccopy(vm):
	AsebaNativeDebug('AsebaNative_veccopy')
	dest = AsebaVmStackPop(vm)
	src = AsebaVmStackPop(vm)
	length = AsebaVmStackPop(vm)
	for i in range(length):
		vm['variables'][dest] = vm['variables'][src]
		dest = dest + 1
		src = src + 1
	
	
ThymioNativeDescription_set_led = [
	"_leds.set",
	"Set the led",
	[
		[1, "led"],
		[1, "brightness"],
	]
]
def ThymioNative_set_led(vm):
	AsebaNativeDebug('ThymioNative_set_led')
	led = vm['variables'][AsebaVmStackPop(vm)]
	b = vm['variables'][AsebaVmStackPop(vm)]

ThymioNativeDescription_record = [
	"sound.record",
	"Start recording of rN.wav",
	[
		[1, "N"],
	]
]
def ThymioNative_sound_record(vm):
	AsebaNativeDebug('ThymioNative_sound_record')
	number = AsebaVmStackPop(vm)

ThymioNativeDescription_play = [
	"sound.play",
	"Start playback of pN.wav",
	[
		[1, "N"],
	]
]
def ThymioNative_sound_playback(vm):
	AsebaNativeDebug('ThymioNative_sound_playback')
	number = vm['variables'][AsebaVmStackPop(vm)]

ThymioNativeDescription_replay = [
	"sound.replay",
	"Start playback of rN.wav",
	[
		[1, "N"],
	]
]
def ThymioNative_sound_replay(vm):
	AsebaNativeDebug('ThymioNative_sound_replay')
	number = vm['variables'][AsebaVmStackPop(vm)]

ThymioNativeDescription_sound_system = [
	"sound.system",
	"Start playback of system sound N",
	[
		[1,"N"],
	]
]
def ThymioNative_sound_system(vm):
	AsebaNativeDebug('ThymioNative_sound_system')
	number = vm['variables'][AsebaVmStackPop(vm)]

ThymioNativeDescription_set_led_circle = [
	"leds.circle",
	"Set circular ring leds",
	[
		[1,"led 0"],
		[1,"led 1"],
		[1,"led 2"],
		[1,"led 3"],
		[1,"led 4"],
		[1,"led 5"],
		[1,"led 6"],
		[1,"led 7"],
	]
]
def ThymioNative_set_led_circle(vm):
	AsebaNativeDebug('ThymioNative_set_led_circle')
	for i in range(8):
		varindex = AsebaVmStackPop(vm)
		val = vm['variables'][varindex]
		AsebaNativeDebug('ThymioNative_set_led_circle ' + str(i) + ' = ' + str(val))
		vm['hardware']['leds_circle'][i] = val

ThymioNativeDescription_set_led_rgb_top = [
	"leds.top",
	"Set RGB top led",
	[
		[1,"red"],
		[1,"green"],
		[1,"blue"],
	]
]
def ThymioNative_set_rgb_top(vm):
	AsebaNativeDebug('ThymioNative_set_rgb_top')
	r = vm['variables'][AsebaVmStackPop(vm)]
	g = vm['variables'][AsebaVmStackPop(vm)]
	b = vm['variables'][AsebaVmStackPop(vm)]

ThymioNativeDescription_set_led_rgb_bl = [
	"leds.bottom.left",
	"Set RGB botom left led",
	[
		[1,"red"],
		[1,"green"],
		[1,"blue"],
	]
]
def ThymioNative_set_rgb_bl(vm):
	AsebaNativeDebug('ThymioNative_set_rgb_bl')
	r = vm['variables'][AsebaVmStackPop(vm)]
	g = vm['variables'][AsebaVmStackPop(vm)]
	b = vm['variables'][AsebaVmStackPop(vm)]

ThymioNativeDescription_set_led_rgb_br = [
	"leds.bottom.right",
	"Set RGB botom right led",
	[
		[1,"red"],
		[1,"green"],
		[1,"blue"],
	]
]
def ThymioNative_set_rgb_br(vm):
	AsebaNativeDebug('ThymioNative_set_rgb_br')
	r = vm['variables'][AsebaVmStackPop(vm)]
	g = vm['variables'][AsebaVmStackPop(vm)]
	b = vm['variables'][AsebaVmStackPop(vm)]





ThymioNativeDescription_poweroff = [
	"_poweroff",
	"Poweroff",
	[
	]
]
def ThymioNative_power_off(vm):
	AsebaNativeDebug('ThymioNative_power_off')
	
	
VM_NATIVEFUNCTIONS_DESCRIPTIONS = [

	AsebaNativeDescription__system_reboot,
	AsebaNativeDescription__system_settings_read,
	AsebaNativeDescription__system_settings_write,
	AsebaNativeDescription__system_settings_flash,
	
	AsebaNativeDescription_veccopy,
	#AsebaNativeDescription_vecfill,
	#AsebaNativeDescription_vecaddscalar,
	#AsebaNativeDescription_vecadd,
	#AsebaNativeDescription_vecsub,
	#AsebaNativeDescription_vecmul,
	#AsebaNativeDescription_vecdiv,
	#AsebaNativeDescription_vecmin,
	#AsebaNativeDescription_vecmax,
	#AsebaNativeDescription_vecdot,
	#AsebaNativeDescription_vecstat,
	#AsebaNativeDescription_vecargbounds,
	#AsebaNativeDescription_vecsort,
	#AsebaNativeDescription_mathmuldiv,
	#AsebaNativeDescription_mathatan2,
	#AsebaNativeDescription_mathsin,
	#AsebaNativeDescription_mathcos,
	#AsebaNativeDescription_mathrot2,
	#AsebaNativeDescription_mathsqrt,
	#AsebaNativeDescription_rand,

	ThymioNativeDescription_set_led,
	ThymioNativeDescription_record,
	ThymioNativeDescription_play,
	ThymioNativeDescription_replay,
	ThymioNativeDescription_sound_system,
	ThymioNativeDescription_set_led_circle,
	ThymioNativeDescription_set_led_rgb_top,
	ThymioNativeDescription_set_led_rgb_bl,
	ThymioNativeDescription_set_led_rgb_br,
	#ThymioNativeDescription_play_freq,
	#ThymioNativeDescription_set_led_buttons,
	#ThymioNativeDescription_set_hprox_leds,
	#ThymioNativeDescription_set_vprox_leds,
	#ThymioNativeDescription_set_rc_leds,
	#ThymioNativeDescription_set_sound_leds,
	#ThymioNativeDescription_set_ntc_leds,
	#ThymioNativeDescription_set_wave,
		
	ThymioNativeDescription_poweroff,

]

AsebaNativeFunctions = [

	AsebaNative__system_reboot,
	AsebaNative__system_settings_read,
	AsebaNative__system_settings_write,
	AsebaNative__system_settings_flash,

	AsebaNative_veccopy,
	#AsebaNative_vecfill,
	#AsebaNative_vecaddscalar,
	#AsebaNative_vecadd,
	#AsebaNative_vecsub,
	#AsebaNative_vecmul,
	#AsebaNative_vecdiv,
	#AsebaNative_vecmin,
	#AsebaNative_vecmax,
	#AsebaNative_vecdot,
	#AsebaNative_vecstat,
	#AsebaNative_vecargbounds,
	#AsebaNative_vecsort,
	#AsebaNative_mathmuldiv,
	#AsebaNative_mathatan2,
	#AsebaNative_mathsin,
	#AsebaNative_mathcos,
	#AsebaNative_mathrot2,
	#AsebaNative_mathsqrt,
	#AsebaNative_rand,  
	
	ThymioNative_set_led,
	ThymioNative_sound_record,
	ThymioNative_sound_playback,
	ThymioNative_sound_replay,
	ThymioNative_sound_system,
	ThymioNative_set_led_circle,
	ThymioNative_set_rgb_top,
	ThymioNative_set_rgb_bl,
	ThymioNative_set_rgb_br,
	#ThymioNative_play_freq,
	#ThymioNative_set_buttons_leds,
	#ThymioNative_set_hprox_leds,
	#ThymioNative_set_vprox_leds,
	#ThymioNative_set_rc_leds,
	#ThymioNative_set_sound_leds,
	#ThymioNative_set_ntc_leds,
	#ThymioNative_set_wave,
	
	ThymioNative_power_off,
]



'''
 
'''
	

HARDWARE = {
	'leds_prox_h' 			: [0,0,0,0,0,0,0,0],
	'leds_prox_v' 			: [0,0],
	'leds_circle' 			: [0,0,0,0,0,0,0,0],
	'leds_buttons' 		    : [0,0,0,0,0],
	'motor_targets'			: [0, 0],
	'buttons'               : [0,0,0,0,0],
	'prox_h'                : [0,0,0,0,0,0,0],
}

HW_BUTTONS_BACKWARD		= 0
HW_BUTTONS_LEFT			= 1
HW_BUTTONS_CENTER		= 2
HW_BUTTONS_FORWARD		= 3
HW_BUTTONS_RIGHT		= 4
HW_MOTOR_LEFT_TARGET	= 0
HW_MOTOR_RIGHT_TARGET	= 1

VM_STATE = {
    'nodeId'        : 1,
    'bytecode'      : [0] * VM_DESCRIPTION['VM_BYTECODESIZE'],
    'bytecodeSize'  : VM_DESCRIPTION['VM_BYTECODESIZE'],
    'stack'         : [0] * VM_DESCRIPTION['VM_STACK_SIZE'],
    'stackSize'     : VM_DESCRIPTION['VM_STACK_SIZE'],
    'variables'     : [],
    'variablesSize' : 0,
    'flags'         : ASEBA_VMSTATE_ACTIVE,
    'pc'            : 0,
    'sp'            : -1,
    'network'       : None,
    'hardware'      : HARDWARE,
    'vm_description'             : VM_DESCRIPTION,
    'vm_variables_description'   : VM_VARIABLES_DESCRIPTION,
    'vm_localevents_description' : VM_LOCALEVENTS_DESCRIPTION,
    'vm_nativefunctions_description' : VM_NATIVEFUNCTIONS_DESCRIPTIONS,
    'pending_local_events' : [0] * EVENT_COUNT,
    }

def AsebaVmGetEventAddress(vm, event):
	eventAddress = 0
	eventVectorSize = vm['bytecode'][0]
	for i in range(1,eventVectorSize,2):
		if vm['bytecode'][i] == event:
			eventAddress = vm['bytecode'][i+1]
	return eventAddress
	
def AsebaVmSetupEvent(vm, event):
	eventAddress = AsebaVmGetEventAddress(vm, event)
	if eventAddress != 0:
		if vm['flags'] & ASEBA_VM_EVENT_ACTIVE_MASK != 0:
			AsebaSendMessageWords(vm['network'], vm['nodeId'], ASEBA_MESSAGE_EVENT_EXECUTION_KILLED, [vm['pc'],])
		vm['pc'] = eventAddress
		vm['sp'] = -1
		vm['flags'] = vm['flags'] | ASEBA_VM_EVENT_ACTIVE_MASK
		if vm['flags'] & ASEBA_VM_STEP_BY_STEP_MASK != 0:
			AsebaSendExecutionState(vm['network'], vm)
	return eventAddress

def AsebaVmClrPendingLocalEvent(vm, eventNum):
	vm['pending_local_events'][eventNum] = 0
	
def AsebaVmSetPendingLocalEvent(vm, eventNum):
	vm['pending_local_events'][eventNum] = 1
	
def AsebaVmGetPendingLocalEvent(vm):
	result = None
	for i in range(EVENT_COUNT):
		if vm['pending_local_events'][i] == 1:
			result = i
			break
	return result

lock_hw = threading.Lock()
def AsebaVmLockHardware():
	lock_hw.acquire()

def AsebaVmUnlockHardware():
	lock_hw.release()
	
def AsebaVmCheckAONSensor(vm, varNum, sensorVal, eventNum):
	result = 0
	v = vm['variables']
	if v[varNum] != sensorVal:
		v[varNum] = sensorVal
		AsebaVmSetPendingLocalEvent(vm, eventNum)
		result = 1
	return result	

ASEBA_VM_SENSORS_PROX_POLL_FREQUENCY = 1

def AsebaVmReadSensors(vm):
	AsebaVmLockHardware()
	v = vm['variables']
	hw = vm['hardware']
	
	# EVENT_BUTTON:
	r = 0
	r = r + AsebaVmCheckAONSensor(vm, VARNUM_BUTTON_BACKWARD, 	hw['buttons'][HW_BUTTONS_BACKWARD], EVENT_B_BACKWARD)
	r = r + AsebaVmCheckAONSensor(vm, VARNUM_BUTTON_CENTER, 	hw['buttons'][HW_BUTTONS_CENTER], 	EVENT_B_CENTER)
	r = r + AsebaVmCheckAONSensor(vm, VARNUM_BUTTON_FORWARD, 	hw['buttons'][HW_BUTTONS_FORWARD], 	EVENT_B_FORWARD)
	r = r + AsebaVmCheckAONSensor(vm, VARNUM_BUTTON_LEFT, 		hw['buttons'][HW_BUTTONS_LEFT], 	EVENT_B_LEFT)
	r = r + AsebaVmCheckAONSensor(vm, VARNUM_BUTTON_RIGHT, 		hw['buttons'][HW_BUTTONS_RIGHT], 	EVENT_B_RIGHT)
	if r > 0:
		AsebaVmSetPendingLocalEvent(vm, EVENT_BUTTONS)
	
	# PROX VARIABLES <- hw(prox)
	for i in range(7):
		val = hw['prox_h'][i]
		if val < 0:
			val = 0
		if val > 4300:
			val = 4300
		v[VARNUM_PROX_H + i] = val
		
	# EVENT_PROX sometimes automatically fired:
	if ASEBA_VM_CLOCK_COUNTER % int(ASEBA_VM_SENSORS_PROX_POLL_FREQUENCY // ASEBA_VM_CLOCK_FREQUENCY) == 0:
		AsebaVmSetPendingLocalEvent(vm, EVENT_PROX)
	
	AsebaVmUnlockHardware()

def AsebaVmWriteActuators(vm):
	AsebaVmLockHardware()
	v = vm['variables']
	hw = vm['hardware']
	hw['motor_targets'][HW_MOTOR_LEFT_TARGET] = v[VARNUM_MOTOR_LEFT_TARGET]
	hw['motor_targets'][HW_MOTOR_RIGHT_TARGET] = v[VARNUM_MOTOR_RIGHT_TARGET]
	AsebaVmUnlockHardware()

def AsebaVmDebug(msg):
	if ASEBA_VM_DEBUG == True:
		print "ASEBA_VM_DEBUG: " + msg

ASEBA_UNARY_OP_SUB 			= 0
ASEBA_UNARY_OP_ABS			= 1
ASEBA_UNARY_OP_BIT_NOT		= 2

def AsebaVmDoUnaryOperation(operand, operation):
	result = 0
	if operation == ASEBA_UNARY_OP_SUB:
		result = -operand
	elif operation == ASEBA_UNARY_OP_ABS:
		if operand < 0:
			operand = -operand
		result = operand
	elif operation == ASEBA_UNARY_OP_BIT_NOT:
		result = ~operand
	return result

ASEBA_OP_SHIFT_LEFT 		= 0
ASEBA_OP_SHIFT_RIGHT		= 1
ASEBA_OP_ADD				= 2
ASEBA_OP_SUB				= 3
ASEBA_OP_MULT				= 4
ASEBA_OP_DIV				= 5
ASEBA_OP_MOD				= 6
ASEBA_OP_BIT_OR				= 7
ASEBA_OP_BIT_XOR			= 8
ASEBA_OP_BIT_AND			= 9
ASEBA_OP_EQUAL				= 10
ASEBA_OP_NOT_EQUAL			= 11
ASEBA_OP_BIGGER_THAN		= 12
ASEBA_OP_BIGGER_EQUAL_THAN	= 13
ASEBA_OP_SMALLER_THAN		= 14
ASEBA_OP_SMALLER_EQUAL_THAN = 15
ASEBA_OP_OR					= 16
ASEBA_OP_AND				= 17
	
def AsebaVmDoBinaryOperation(operand1, operand2, operation):
	AsebaVmDebug('AsebaVmDoBinaryOperation: ' + 'op1=' + str(operand1) + ' op2=' + str(operand2) + ' opnum=' + str(operation))
	result = 0
	if operation == ASEBA_OP_SHIFT_LEFT:
		result = operand1 << operand2
	elif operation == ASEBA_OP_SHIFT_RIGHT:
		result = operand1 >> operand2
	elif operation == ASEBA_OP_ADD:
		result = operand1 + operand2
	elif operation == ASEBA_OP_SUB:
		result = operand1 - operand2
	elif operation == ASEBA_OP_MULT:
		result = operand1 * operand2
	elif operation == ASEBA_OP_DIV:
		result = operand1 // operand2
	elif operation == ASEBA_OP_MOD:
		result = operand1 % operand2
	elif operation == ASEBA_OP_BIT_OR:
		result = operand1 | operand2
	elif operation == ASEBA_OP_BIT_XOR:
		result = operand1 ^ operand2
	elif operation == ASEBA_OP_BIT_AND:
		result = operand1 & operand2
	elif operation == ASEBA_OP_EQUAL:
		if operand1 == operand2:
			result = 1
		else:
			result = 0
	elif operation == ASEBA_OP_NOT_EQUAL:
		if operand1 != operand2:
			result = 1
		else:
			result = 0
	elif operation == ASEBA_OP_BIGGER_THAN:
		if operand1 > operand2:
			result = 1
		else:
			result = 0
	elif operation == ASEBA_OP_BIGGER_EQUAL_THAN:
		if operand1 >= operand2:
			result = 1
		else:
			result = 0
	elif operation == ASEBA_OP_SMALLER_THAN:
		if operand1 < operand2:
			result = 1
		else:
			result = 0
	elif operation == ASEBA_OP_SMALLER_EQUAL_THAN:
		if operand1 <= operand2:
			result = 1
		else:
			result = 0
	elif operation == ASEBA_OP_OR:
		if operand1 or operand2:
			result = 1
		else:
			result = 0
	elif operation == ASEBA_OP_AND:
		if operand1 and operand2:
			result = 1
		else:
			result = 0
		
	return result

def AsebaNativeDebug(msg):
	if ASEBA_NATIVE_DEBUG == True:
		print "ASEBA_NATIVE_DEBUG: " + msg


def AsebaVmNativeFunctionCall(vm, function):
	AsebaNativeDebug('Call function number ' + str(function))
	if function >= 0 and function < len(AsebaNativeFunctions):
		AsebaNativeFunctions[function](vm)

def AsebaVmStackPop(vm):
	value = vm['stack'][vm['sp']]
	vm['sp'] = vm['sp'] - 1
	return value

def AsebaVmStackPush(vm, value):
	vm['sp'] = vm['sp'] + 1	
	vm['stack'][vm['sp']] = value

def AsebaVmInit():
	vm = VM_STATE
	vm['network'] = None
	vm['hardware'] = HARDWARE
	vm['pc'] = 0
	vm['sp'] = -1
	vm['flags'] = ASEBA_VMSTATE_ACTIVE
	vm['variablesSize'] = 0
	for vdesc in VM_VARIABLES_DESCRIPTION:
		vm['variablesSize'] = vm['variablesSize'] + vdesc[0] 
		if vdesc[0] == 1:
			if vdesc[1] == "_id":
				val = VM_DESCRIPTION['ID']
			elif vdesc[1] == "_productId":
				val = VM_DESCRIPTION['PRODUCT_ID']
			else:
				val = 0
			vm['variables'].append(val)
		else:
			if vdesc[1] == "_fwversion":
				val = VM_DESCRIPTION['FIRMWARE_VERSION'][0]
				vm['variables'].append(val)
				val = VM_DESCRIPTION['FIRMWARE_VERSION'][1]
				vm['variables'].append(val)
			else:
				for i in range(vdesc[0]):
					vm['variables'].append(0)
	for i in range(VM_DESCRIPTION['VM_VARIABLES_FREE_SPACE']):
		vm['variables'].append(0)
		
	thread_network = threading.Thread(group=None, target=AsebaNetworkStart, args=(vm,))
	thread_network.start()

	return vm

def AsebaVmStep(vm):

	bytecode = vm['bytecode'][vm['pc']]
	opcode = (bytecode & 0x0000F000) >> 12
	value =   bytecode & 0x00000FFF;

	AsebaVmDebug('AsebaVmStep: pc[' + hex(vm['pc']) + ']=' + hex(bytecode) + '=' + hex(opcode) + ':' + hex(value))
	
	if opcode == ASEBA_BYTECODE_STOP:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_STOP')
		vm['flags'] = vm['flags'] & ~ASEBA_VM_EVENT_ACTIVE_MASK
		
	elif opcode == ASEBA_BYTECODE_SMALL_IMMEDIATE:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_SMALL_IMMEDIATE')
		AsebaVmStackPush(vm, value)
		vm['pc'] = vm['pc'] + 1
		
	elif opcode == ASEBA_BYTECODE_LARGE_IMMEDIATE:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_LARGE_IMMEDIATE')
		value = vm['bytecode'][vm['pc'] + 1]
		AsebaVmStackPush(vm, value)
		vm['pc'] = vm['pc'] + 2
		
	elif opcode == ASEBA_BYTECODE_LOAD:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_LOAD')
		varindex = value
		varvalue = vm['variables'][varindex]
		AsebaVmStackPush(vm, varvalue)
		vm['pc'] = vm['pc'] + 1

	elif opcode == ASEBA_BYTECODE_STORE:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_STORE')
		varvalue = AsebaVmStackPop(vm)
		varindex = value
		vm['variables'][varindex] = varvalue
		vm['pc'] = vm['pc'] + 1

	elif opcode == ASEBA_BYTECODE_LOAD_INDIRECT:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_LOAD_INDIRECT')
		arrayindex = value
		arraysize = vm['bytecode'][vm['pc'] + 1]
		varindex = AsebaVmStackPop(vm)
		varvalue = vm['variables'][arrayindex + varindex]
		AsebaVmStackPush(vm, varvalue)
		vm['pc'] = vm['pc'] + 2
	
	elif opcode == ASEBA_BYTECODE_STORE_INDIRECT:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_STORE_INDIRECT')
		arrayindex = value
		arraysize = vm['bytecode'][vm['pc'] + 1]
		varindex = AsebaVmStackPop(vm)
		varvalue = AsebaVmStackPop(vm)
		vm['variables'][arrayindex + varindex] = varvalue
		vm['pc'] = vm['pc'] + 2
		
	elif opcode == ASEBA_BYTECODE_UNARY_ARITHMETIC:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_UNARY_ARITHMETIC')
		operand = AsebaVmStackPop(vm)
		result = AsebaVmDoUnaryOperation(operand, bytecode & ASEBA_UNARY_OPERATOR_MASK)
		AsebaVmStackPush(vm, result)
		vm['pc'] = vm['pc'] + 1
		
	elif opcode == ASEBA_BYTECODE_BINARY_ARITHMETIC:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_BINARY_ARITHMETIC')
		operand2 = AsebaVmStackPop(vm)
		operand1 = AsebaVmStackPop(vm)
		result = AsebaVmDoBinaryOperation(operand1, operand2, bytecode & ASEBA_BINARY_OPERATOR_MASK)
		AsebaVmStackPush(vm, result)
		vm['pc'] = vm['pc'] + 1
		
	elif opcode == ASEBA_BYTECODE_JUMP:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_JUMP')
		vm['pc'] = vm['pc'] + value
	
	elif opcode == ASEBA_BYTECODE_CONDITIONAL_BRANCH:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_CONDITIONAL_BRANCH')
		operand2 = AsebaVmStackPop(vm)
		operand1 = AsebaVmStackPop(vm)
		result = AsebaVmDoBinaryOperation(operand1, operand2, bytecode & ASEBA_BINARY_OPERATOR_MASK)
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_CONDITIONAL_BRANCH: result=' + str(result))
		mask1 = 1 << ASEBA_IF_IS_WHEN_BIT
		mask2 = 1 << ASEBA_IF_WAS_TRUE_BIT
		if result and not((bytecode & mask1) and (bytecode & mask2)):
			disp = 2
		else:
			disp = vm['bytecode'][vm['pc'] + 1]
		if result != 0:
			vm['bytecode'][vm['pc']] = vm['bytecode'][vm['pc']] | mask2
		else:
			vm['bytecode'][vm['pc']] = vm['bytecode'][vm['pc']] & ~mask2
		vm['pc'] = vm['pc'] + disp
	
	elif opcode == ASEBA_BYTECODE_EMIT:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_EMIT')
		start = vm['bytecode'][vm['pc'] + 1]
		length = vm['bytecode'][vm['pc'] + 2]
		data16 = []
		for i in range(start, start + length):
			data16.append(vm['variables'][i])
		AsebaSendMessageWords(vm['network'], vm['nodeId'], value, data16)
		vm['pc'] = vm['pc'] + 3
	
	elif opcode == ASEBA_BYTECODE_NATIVE_CALL:
		AsebaVmDebug('AsebaVmStep: ASEBA_BYTECODE_NATIVE_CALL')
		AsebaVmNativeFunctionCall(vm, value)
		vm['pc'] = vm['pc'] + 1
		
def AsebaVmRun(vm):
	if vm['flags'] & ASEBA_VM_EVENT_ACTIVE_MASK == 0:
		#print 'asebavmrun : no event active'
		return
	if vm['flags'] & ASEBA_VM_STEP_BY_STEP_MASK != 0:
		#print 'asebavmrun : no step by step'
		return
	vm['flags'] = vm['flags'] | ASEBA_VM_EVENT_RUNNING_MASK
	AsebaVmStep(vm)
	vm['flags'] = vm['flags'] & ~ASEBA_VM_EVENT_RUNNING_MASK

ASEBA_VM_CLOCK_FREQUENCY = 0.01
ASEBA_VM_CLOCK_COUNTER = 0

def AsebaVmMainLoop(vm):
	global ASEBA_VM_CLOCK_COUNTER
	while True:
		AsebaVmReadSensors(vm)
		if vm['flags'] & ASEBA_VM_EVENT_ACTIVE_MASK == 0 or vm['flags'] & ASEBA_VM_STEP_BY_STEP_MASK == 0:
			eventNum = AsebaVmGetPendingLocalEvent(vm)
			if eventNum != None:
				#if eventNum != EVENT_PROX:
				AsebaVmDebug('Pending event ' + str(eventNum))
				AsebaVmClrPendingLocalEvent(vm, eventNum)
				AsebaVmSetupEvent(vm, ASEBA_EVENT_LOCAL_EVENTS_START - eventNum)
		AsebaVmRun(vm)
		AsebaVmWriteActuators(vm)
		
		ASEBA_VM_CLOCK_COUNTER = ASEBA_VM_CLOCK_COUNTER + 1		
		sleep(ASEBA_VM_CLOCK_FREQUENCY)

