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
import datetime
from ftplib import FTP
from requests_twisted import TwistedRequestsSession
import json
from flask import jsonify

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from flask import Flask
from flask import request
from flask import abort
from twisted.internet import ssl
from twisted.internet import reactor
reactor.suggestThreadPoolSize(10)

app = Flask(__name__)

@app.route('/rest/jesse/jesse8/setvalve', methods=['POST'])
def setvalve():
    global context
    if not request.json or not 'PowerOn' or not 'Item Number' in request.json:
        abort(400)

    register = 3
    slave_id = 0x00
    address  = 0x1000
    values_w   = context[slave_id].getValues(register, address, count=40)
    data = request.json
#    log.info(json(data))
    Item = data['Item Number']
    Command = data['PowerOn']
    log.info("Item " + str(Item))
    log.info("Command " + str(Command))

    if str(Command).find('manualon') > -1:
                values_w[4+(int(Item)-1)*4] = int(values_w[4+(int(Item)-1)*4]/256)*256+int(60)

    if str(Command).find('manualoff') > -1:
                values_w[4+(int(Item)-1)*4] = int(values_w[4+(int(Item)-1)*4]/256)*256+int(61)

    context[slave_id].setValues(register, address, values_w)
   
    return jsonify(request.json),200

@app.route('/')
def index():
    return "API 1.0"

if __name__ == '__main__':
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
#    reactor.listenTCP(80, site)
    reactor.listenSSL(443, site, ssl.DefaultOpenSSLContextFactory('/etc/server_unencrypted.key', '/etc/server.crt'))
#    reactor.run()

DurationInMinutes = ['0']*10
Days = ['']*10
StartTime = ['0:0']*10
PowerOn = ['']*10




session = TwistedRequestsSession()

#----------------------------------------#
#making config parser
#----------------------------------------#
config = ConfigParser.RawConfigParser()
config.read('/etc/updating-server.conf')
post_url = config.get('post_conf','post_url')
valve_url = config.get('post_conf','valve_url')

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
from datetime import timedelta
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
requestdone = 0
new_data1 = 0
data_was_updated1 = 0
sending_in_progress1 = 0
requestdone1 = 0

def handleFailure1(f):
         global csvfile
         global writer
         global new_data
         global data_was_updated
         global sending_in_progress
	 global requestdone
	 global session 

	 requestdone = 1
	 sending_in_progress = 0 
	 log.info("Timeout POST Sensor data to Cloud ")
         csvfile = open('/home/pi/setSensorData.csv', 'ab')
         data_was_updated = 1 
	 new_data = 0
	 session.close()
         writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

def print_status1(r):
 		global csvfile
    		global writer
    		global new_data
		global data_was_updated
		global sending_in_progress
		global DurationInMinutes
		global Days
		global StartTime
		global PowerOn
		global requestdone
		global session

		requestdone = 1
		sending_in_progress = 0
		log.info('Status POST CSV file: '+str(r.status_code))

                if r.status_code == 200:
                         csvfile = open('/home/pi/setSensorData.csv', 'wb')
                         new_data = 0
                         data_was_updated = 1

 	                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

                elif r.status_code == 404:
                        csvfile = open('/home/pi/setSensorData.csv', 'ab')
                        new_data = 0
                	data_was_updated = 1
		else:
                        csvfile = open('/home/pi/setSensorData.csv', 'ab')
                        new_data = 0
			data_was_updated = 1
	        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

                session.close()

def handleFailure(f):
         global csvfile
         global writer
         global new_data1
         global data_was_updated1
         global sending_in_progress1
	 global requestdone1
	 global session 

	 requestdone1 = 1
	 sending_in_progress1 = 0 
	 log.info("Timeout POST Sensor data to Cloud ")
         data_was_updated1 = 1 
	 new_data1 = 0
	 session.close()

def print_status(r):
 		global csvfile
    		global writer
    		global new_data1
		global data_was_updated1
		global sending_in_progress1
		global DurationInMinutes
		global Days
		global StartTime
		global PowerOn
		global requestdone1
		global session

		requestdone1 = 1
		sending_in_progress1 = 0
		log.info('Status GET Valves: '+str(r.status_code))

                if r.status_code == 200:
                        new_data1 = 0
                        data_was_updated1 = 1
                        data = r.json()
			for i in [1, 2, 3, 4, 5, 6, 7, 8]:
				DurationInMinutes[i] = data[i-1]['mapCodingInfo']['DurationInMinutes']
                        	Days[i] = data[i-1]['mapCodingInfo']['Days']
                        	StartTime[i] = data[i-1]['mapCodingInfo']['Start Time']
                                PowerOn[i] = data[i-1]['mapCodingInfo']['PowerOn']
				
				log.info('Data JSON '+str(Days[i])+' '+str(StartTime[i])+' '+str(DurationInMinutes[i]))

                elif r.status_code == 404:
                        new_data1 = 0
                	data_was_updated1 = 1
		else:
                        new_data1 = 0
			data_was_updated1 = 1
                session.close()

def setBit(int_type, offset):
     mask = 1 << offset
     return(int_type | mask)

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
    global DurationInMinutes
    global Days
    global StartTime
    global new_data
    global one_send_only
    global UpdateTime
    global old_values
    global Year
    global Month
    global Day
    global Hour
    global Min
    global Sec
    global PowerOn
    global requestdone
    global session
    global dt_now_PLC

    global new_data1
    global data_was_updated1
    global sending_in_progress1
    global requestdone1

    log.info("new data: "+str(new_data))
    log.info("sending_in_progress: "+str(sending_in_progress))

    if new_data == 1 and sending_in_progress == 0 and requestdone == 0:
       csvfile.close()
       sending_in_progress = 1
       log.info('Upload data to Cloud')
       multiple_files = [('text', ('setSensorData.csv', open('/home/pi/setSensorData.csv', 'rb'), 'text/plain'))]
       r1 = session.post(post_url, files=multiple_files, timeout=60, stream=True)
       r1.addCallback(print_status1)
       r1.addErrback(handleFailure1)

    if data_was_updated == 1:
        #----------------------------------------------------------------#
        # Ask command for devices (first getState then if ok resetState)
        #----------------------------------------------------------------#
     	log.info('Data was updatet')
	if requestdone == 1:
          delay = delay + 1


          if delay > 4:
           requestdone = 0

           context  = a[0]
           register = 3
           slave_id = 0x00
           address  = 0x0

           values_zer = [65535]*100
           context[slave_id].setValues(register, address, values_zer)
           log.info("Clear all input registers")


           context  = a[0]
           register = 3
           slave_id = 0x00
           address  = 0x1000

           values_zer = [65535]*2
           context[slave_id].setValues(register, address, values_zer)
           log.info("Clear all output registers")

           Year = 0
           Month = 0
           Day = 0
           Hour = -1
           Min = -1
           Sec = -1

           old_values_zer = [65535]*8192
           old_values = old_values_zer

           new_data = 0
           one_send_only = 0
           UpdateTime = 1
           delay = 0
           data_was_updated = 0

        

    if sending_in_progress1 == 0 and requestdone1 == 0:

       sending_in_progress1 = 1
	#-----------------------------------------------#
	# if have ne data make API setSensorData
	#-----------------------------------------------#
       log.info('Get data from Cloud')
       
       r = session.get(valve_url, timeout=(3, 500), stream=False)
       r.addCallback(print_status)
       r.addErrback(handleFailure)
   

    if data_was_updated1 == 1:   
	#----------------------------------------------------------------#
	# Ask command for devices (first getState then if ok resetState)
	#----------------------------------------------------------------#
	if requestdone1 == 1:

	   context  = a[0]
	   register = 3
     	   slave_id = 0x00
    	   address  = 0x1000
    	   values_w   = context[slave_id].getValues(register, address, count=40)

	   bi = convert_i(1.0)
           values_w[0] = bi/65536
           values_w[1] = bi - 65536*values_w[0]


	   for i in [1, 2, 3, 4, 5, 6, 7, 8]:

	    values_w[2+(i-1)*4] = 0
            values_w[3+(i-1)*4] = 0

	    AllDays = Days[i].split(",")
	    AllStartTime = StartTime[i].split(",")
	    AllDurations = DurationInMinutes[i].split(",")

	    for j in range(len(AllDays)):
#		log.info("Vavel " + str(i) + " Day to work "+ AllDays[j])
	    	TimeFrom = datetime.strptime(AllStartTime[j],"%H:%M")
#		log.info("Vavel " + str(i) + " Time from "+ datetime.strftime(TimeFrom,"%H:%M"))
		TimeTo = TimeFrom + timedelta(minutes=int(AllDurations[j]))
#                log.info("Vavel " + str(i) + " Time to "+ datetime.strftime(TimeTo,"%H:%M"))
#		log.info("Day now " + dt_now_PLC.strftime("%a"))

		TimeNow = datetime.strptime(dt_now_PLC.strftime("%H:%M"),"%H:%M")
#		log.info("Time now " + TimeNow.strftime("%H:%M"))

		if dt_now_PLC.strftime("%a").find(AllDays[j]) > -1 and TimeNow > TimeFrom and TimeNow < TimeTo:
			values_w[4+(i-1)*4] = int(0)*256+int(60)
                	log.info("Shudler on valve N" + str(i))
		else:
			values_w[4+(i-1)*4] = int(0)*256+int(0)


            log.info("Hour Manual status:" + str(PowerOn[i]))
	    if str(PowerOn[i]).find('manualon') > -1:
		values_w[4+(i-1)*4] = int(0)*256+int(60)
#		log.info("Manual on valve N" + str(i))
            if str(PowerOn[i]).find('manualoff') > -1:
                values_w[4+(i-1)*4] = int(0)*256+int(61)

	   context[slave_id].setValues(register, address, values_w)

	   requestdone1 = 0
           data_was_updated1 = 0
	
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
     for i in [0, 1, 2, 3, 4, 5, 6, 12, 13, 18]:
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
time = 3600
time_cloud = 10

loop = LoopingCall(f=updating_writer, a=(context,))
loop.start(time, now=False).addErrback(fail) # initially delay by time

loop_cloud = LoopingCall(f=updating_cloud, a=(context,))
loop_cloud.start(time_cloud, now=False).addErrback(fail) # initially delay by time

StartTcpServer(context, identity=identity, address=("0.0.0.0", 502))

