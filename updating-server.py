#!/usr/bin/env python

#---------------------------------------------------------------------------# 
# import the modbus libraries we need
#---------------------------------------------------------------------------# 
from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
import struct
import requests
import ConfigParser
import io
import csv
import grequests
import sys
import twisted
from ftplib import FTP
from requests_twisted import TwistedRequestsSession

session = TwistedRequestsSession()

#----------------------------------------#
#making config parser
#----------------------------------------#
config = ConfigParser.RawConfigParser()
config.read('/etc/updating-server.conf')
post_url = config.get('post_conf','post_url')

USER = config.get('post_conf','ftp_user')
PASS = config.get('post_conf','ftp_pass')

########### MODIFY IF YOU WANT ############

SERVER = config.get('post_conf','ftp_url')
PORT = 21
BINARY_STORE = True
#---------------------------------------------------------------------------# 
# import the twisted libraries we need
#---------------------------------------------------------------------------# 
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
#---------------------------------------------------------------------------# 
# configure the service logging
#---------------------------------------------------------------------------# 
import logging
#logging.basicConfig(filename='/var/log/modbussrv.log',level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


#---------------------------------------------------------------------------#
#  Get time from PLC registers
#---------------------------------------------------------------------------#
def linux_set_time(time_tuple):
    import ctypes
    import ctypes.util
    import time

    CLOCK_REALTIME = 0

    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]

    librt = ctypes.CDLL(ctypes.util.find_library("rt"))

    ts = timespec()
    ts.tv_sec = int( time.mktime( datetime( *time_tuple[:6]).timetuple())  )
    ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond

    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

TimeFromPLC = 0
UpdateTime = 0

if len(sys.argv) > 1:
	if (sys.argv[1:])[0] == "Time_from_PLC":
		log.info("Get time from PLC")
		UpdateTime = 0
	else:
		log.info("Get time from NTP")
		UpdateTime = 1
else:
	log.info("Get time from NTP")
	UpdateTime = 1


from ctypes import *
from datetime import datetime
import time as _time

#-----------------------------------------#
#Intilize CSV file header
#-----------------------------------------#
csvfile = open('/home/pi/setSensorData.csv', 'ab')
fieldnames = ["Operation","Flag","ObjectId","ObjectType","MobileRecordId","Functional Group Name","Organization Name","Organization Number","Value","Datetime",\
"Sensor Name","SensorRecordId"]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

dt_now_PLC =  datetime.now()

#------------------------------------------#
#Save data to CSV file
#------------------------------------------#
def save_csv(val, sensor_num):
		global dt_now_PLC
#		now = datetime.now()
#		dt = datetime.now()
		userrecordid = config.get('post_conf','ftp_userrecordid')
		weatherstationrecordid = config.get('post_conf','ftp_weatherstationrecordid')
		now = dt_now_PLC
		dt = dt_now_PLC
		timestamp = _time.mktime(dt.timetuple())
		datetime_now = datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")
		OutLim = val >  float(config.get('Sensor_'+str(sensor_num),'Sensor High Limit')) or val < float(config.get('Sensor_'+str(sensor_num),'Sensor Low Limit'))
		log.info("write to CSV for "+str(sensor_num)+" Value:"+str(val))                                    
		writer.writerow({"Operation": config.get('Sensor_'+str(sensor_num),'Operation'),\
				 "Flag": config.get('Sensor_'+str(sensor_num),'Flag'),\
				 "ObjectId": config.get('Sensor_'+str(sensor_num),'ObjectId'),\
                                 "ObjectType": config.get('Sensor_'+str(sensor_num),'ObjectType'),\
                                 "MobileRecordId": "SensorData"+str(sensor_num)+"-"+str(timestamp)+"-"+weatherstationrecordid+"-"+userrecordid,\
                                 "Functional Group Name": config.get('Sensor_'+str(sensor_num),'Functional Group Name'),\
                                 "Organization Name": config.get('Sensor_'+str(sensor_num),'Organization Name'),\
                                 "Organization Number": config.get('Sensor_'+str(sensor_num),'Organization Number'),\
                                 "Value": 0 if val == -9999 else str('%.2f' % val),\
                                 "Datetime": datetime_now,\
                                 "Sensor Name": config.get('Sensor_'+str(sensor_num),'Sensor Name'),\
                                 "SensorRecordId": config.get('Sensor_'+str(sensor_num),'SensorRecordId'),\
				})

#-------------------------------------#
#Convert two int16 to float
#-------------------------------------#
def convert(i):
    cp = pointer(c_int(i))           # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
    return fp.contents.value         # dereference the pointer, get the float

#-------------------------------------#
#Convert float to in16
#-------------------------------------#
def convert_i(i):   
    cp = pointer(c_float(i))         # make this into a c float
    fp = cast(cp, POINTER(c_int))    # cast the int pointer to a int pointer
    return fp.contents.value         # dereference the pointer, get the int


#---------------------------------------------------------------------------# 
# define your callback process
#---------------------------------------------------------------------------# 
old_values = [65535]*8192
new_data = 0
data_was_updated = 0
sending_in_progress = 0

def handleFailure(f):
         global csvfile
         global writer
         global new_data
         global data_was_updated
         global sending_in_progress

	 sending_in_progress = 0 
	 log.info("Timeout POST Sensor data to Cloud ")
#         csvfile = open('/home/pi/setSensorData.csv', 'ab')
         data_was_updated = 1 
	 new_data = 0
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

def print_status(r):
 		global csvfile
    		global writer
    		global new_data
		global data_was_updated
		global sending_in_progress

		sending_in_progress = 0
		log.info('Status: '+str(r.status_code))

                if r.status_code == 200:
                        csvfile = open('/home/pi/setSensorData.csv', 'wb')
                        new_data = 0
                        data_was_updated = 1
	                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                elif r.status_code == 404:
#                        csvfile = open('/home/pi/setSensorData.csv', 'ab')
                        new_data = 0
                	data_was_updated = 1
		else:
#                        csvfile = open('/home/pi/setSensorData.csv', 'ab')
                        new_data = 0
			data_was_updated = 1
#	        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
delay = 0
def updating_cloud(a):
    global csvfile
    global writer
    global new_data
    global session
    global data_was_updated
    global sending_in_progress
    global delay
    global Year
    global Month
    global Day
    global Hour
    global Min

    log.info("new data: "+str(new_data))
    log.info("sending_in_progress: "+str(sending_in_progress))
    if new_data == 1 and sending_in_progress == 0:
       csvfile.close()
       sending_in_progress = 1
	#-----------------------------------------------#
	# if have ne data make API setSensorData
	#-----------------------------------------------#
       log.info('Upload data to Cloud')
        #multiple_files = [('text', ('setSensorData.csv', open('/home/pi/setSensorData.csv', 'rb'), 'text/plain'))]
        #r = session.post(post_url, files=multiple_files, timeout=60, stream=True)
	#r.addCallback(print_status)
	#r.addErrback(handleFailure)
       try:	
	ftp = FTP()
    	ftp.connect(SERVER, PORT)
    	ftp.login(USER, PASS) 
	upload_file =  open('/home/pi/setSensorData.csv', 'r')
	userrecordid = config.get('post_conf','ftp_userrecordid')
        orgnum = config.get('Sensor_1','Organization Number')
        final_file_name = '/weather/'+str(int(Year)).zfill(4)+str(int(Month)).zfill(2)+str(int(Day)).zfill(2)+'-'+str(int(Hour)).zfill(2)+str(int(Min)).zfill(2)+'-1-'+orgnum+'-'+userrecordid+'.csv'
	result = ftp.storbinary('STOR '+ final_file_name, upload_file)
        log.info('Result =' + str(result))				
        sending_in_progress = 0

	if result[0:3] == '226':
		log.info('Uploading good')
                csvfile = open('/home/pi/setSensorData.csv', 'wb')
                new_data = 0
                data_was_updated = 1
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
 	else:
		log.info('Uploading bed')
                new_data = 0
                data_was_updated = 1
       except:
                log.info('Uploading bed')
                new_data = 0
                data_was_updated = 1

    if data_was_updated == 1:   
	#----------------------------------------------------------------#
	# Ask command for devices (first getState then if ok resetState)
	#----------------------------------------------------------------#
	delay = delay + 1
	if delay > 5:
	   csvfile.close()
	   context  = a[0]
	   register = 3
     	   slave_id = 0x00
    	   address  = 0x1000
    	   values_w   = context[slave_id].getValues(register, address, count=40)

	   bi = convert_i(1.0)
           values_w[0] = bi/65536
           values_w[1] = bi - 65536*values_w[0]

           log.info("Set 1 reg to one")
	   context[slave_id].setValues(register, address, values_w)
	   
	   data_was_updated = 0

	
#---------------------------------------------------------------------#
#Check that dat changed and save to CSV and set command send in Cloud
#---------------------------------------------------------------------#
def check_val_change(old_1, new_1, old_2, new_2,sensor_num):
	global new_data

    	if old_1 <> new_1 or old_2 <> new_2:
	        b = new_1*65536+new_2
	        newval = convert(b)
	        log.info("We get new sensor "+str(sensor_num)+" data: " + str('%.2f' % newval))
	        save_csv(newval,sensor_num)
	        new_data = 1

#---------------------------------------------------------------------#
#Check that dat changed and set Date and Time from PLC
#---------------------------------------------------------------------#
Year = 0
Month = 0
Day = 0
Hour = -1
Min = -1
Sec = -1
def check_val_change_RTC(old_1, new_1, old_2, new_2,sensor_num):
        global new_data
	global Year
	global Month
	global Day
	global Hour
	global Min
	global Sec
	global UpdateTime
	global loop_cloud
	global time_cloud
	global loop
	global time
	global dt_now_PLC

        if old_1 <> new_1 or old_2 <> new_2:
                b = new_1*65536+new_2
                newval = convert(b)
                log.info("We get new Date Time "+str(sensor_num)+" data: " + str('%.0f' % newval))
		if sensor_num == 41:
			Year = newval
                if sensor_num == 42:
                        Month = newval
                if sensor_num == 43:
                        Day = newval
                if sensor_num == 44:
                        Hour = newval
                if sensor_num == 45:
                        Min = newval
                if sensor_num == 46:
                        Sec = newval
	if Year > 0 and Month > 0 and Day > 0 and Hour > -1 and Min > -1 and Sec > -1:
		UpdateTime = 1
		new_datetime = (int(Year), int(Month), int(Day), int(Hour), int(Min), int(Sec),int(0))
		dt_now_PLC = datetime( *new_datetime[:6])
		log.info("Set time " + datetime.strftime(dt_now_PLC, "%Y-%m-%d %H:%M:%S"))

one_send_only = 0

#-----------------------------------------#
#Check if we have new data on Modbus
#-----------------------------------------#
def updating_writer(a):

    global old_values
    global csvfile
    global writer
    global new_data
    global one_send_only
    global UpdateTime

    log.info("Update Time is:" + str(UpdateTime))

    context  = a[0]
    register = 3
    slave_id = 0x00
    address  = 0x0
    values   = context[slave_id].getValues(register, address, count=100)

    if new_data == 0 and one_send_only == 0 and UpdateTime == 1:
#--------------------------------#
#Test 1
#--------------------------------#
     for i in [40, 41, 42, 43, 44, 45]:
        check_val_change_RTC(old_values[i*2],values[i*2],old_values[i*2+1],values[i*2+1],i+1)
     for i in [0, 1, 2, 3, 4, 12, 13, 18]:
	check_val_change(old_values[i*2],values[i*2],old_values[i*2+1],values[i*2+1],i+1)
     if new_data == 1:
        one_send_only = 1
     old_values = values

    if UpdateTime == 0:
     for i in [40, 41, 42, 43, 44, 45]:
        check_val_change_RTC(65535,values[i*2],65535,values[i*2+1],i+1)
 
#---------------------------------------------------------------------------# 
# initialize your data store
#---------------------------------------------------------------------------# 
store = ModbusSlaveContext(
    di = ModbusSequentialDataBlock(0, [65535]*8192),
    co = ModbusSequentialDataBlock(0, [65535]*8192),
    hr = ModbusSequentialDataBlock(0, [65535]*8192),
    ir = ModbusSequentialDataBlock(0, [65535]*8192))
context = ModbusServerContext(slaves=store, single=True)

#---------------------------------------------------------------------------# 
# initialize the server information
#---------------------------------------------------------------------------# 
identity = ModbusDeviceIdentification()
identity.VendorName  = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName   = 'pymodbus Server'
identity.MajorMinorRevision = '1.0'


def fail(f):
    log.info("we got an exception: %s" % (f.getTraceback(),))

#---------------------------------------------------------------------------# 
# run the server you want
#---------------------------------------------------------------------------# 
time = 10
time_cloud = 10

loop = LoopingCall(f=updating_writer, a=(context,))
loop.start(time, now=False).addErrback(fail) # initially delay by time

loop_cloud = LoopingCall(f=updating_cloud, a=(context,))
loop_cloud.start(time_cloud, now=False).addErrback(fail) # initially delay by time

StartTcpServer(context, identity=identity, address=("0.0.0.0", 502))

