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


#----------------------------------------#
#making config parser
#----------------------------------------#
config = ConfigParser.RawConfigParser()
config.read('/etc/updating-server.conf')
post_url = config.get('post_conf','post_url')

#---------------------------------------------------------------------------# 
# import the twisted libraries we need
#---------------------------------------------------------------------------# 
from twisted.internet.task import LoopingCall

#---------------------------------------------------------------------------# 
# configure the service logging
#---------------------------------------------------------------------------# 
import logging
#logging.basicConfig(filename='/var/log/modbussrv.log',level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)


from ctypes import *
from datetime import datetime
import time as _time

#-----------------------------------------#
#Intilize CSV file header
#-----------------------------------------#
csvfile = open('setSensorData.csv', 'ab')
fieldnames = ["Operation","Flag","ObjectId","ObjectType","MobileRecordId","Functional Group Name","Organization Name","Organization Number","Value","Datetime","Grower","GrowerRecordId",\
                      "Ranch","RanchRecordId","Field","FieldRecordId","Row","Latitude","Longitude","Elevation","Sensor Name","SensorRecordId","SensorType","Sensor High Limit",\
                      "Sensor Low Limit","Sensor Alert","Alert SMS Carrier","Alert SMS Message","Alert SMS PhoneNumber","Alert Email Address","Alert Email Message"]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
#writer.writeheader()

#------------------------------------------#
#Save data to CSV file
#------------------------------------------#
def save_csv(val, sensor_num):
		now = datetime.now()
		dt = datetime.now()
		timestamp = _time.mktime(dt.timetuple())
		datetime_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
		writer.writerow({"Operation": config.get('Sensor_'+str(sensor_num),'Operation'),\
				 "Flag": config.get('Sensor_'+str(sensor_num),'Flag'),\
				 "ObjectId": config.get('Sensor_'+str(sensor_num),'ObjectId'),\
                                 "ObjectType": config.get('Sensor_'+str(sensor_num),'ObjectType'),\
                                 "MobileRecordId": "SensorData"+str(sensor_num)+"-"+str(timestamp),\
                                 "Functional Group Name": config.get('Sensor_'+str(sensor_num),'Functional Group Name'),\
                                 "Organization Name": config.get('Sensor_'+str(sensor_num),'Organization Name'),\
                                 "Organization Number": config.get('Sensor_'+str(sensor_num),'Organization Number'),\
                                 "Value": 0 if val == -9999 else str('%.2f' % val),\
                                 "Datetime": datetime_now,\
                                 "Grower": config.get('Sensor_'+str(sensor_num),'Grower'),\
                                 "GrowerRecordId": config.get('Sensor_'+str(sensor_num),'GrowerRecordId'),\
                                 "Ranch": config.get('Sensor_'+str(sensor_num),'Ranch'),\
                                 "RanchRecordId": config.get('Sensor_'+str(sensor_num),'RanchRecordId'),\
                                 "Field": config.get('Sensor_'+str(sensor_num),'Field'),\
                                 "FieldRecordId": config.get('Sensor_'+str(sensor_num),'FieldRecordId'),\
                                 "Row": config.get('Sensor_'+str(sensor_num),'Row'),\
                                 "Latitude": config.get('Sensor_'+str(sensor_num),'Latitude'),\
                                 "Longitude": config.get('Sensor_'+str(sensor_num),'Longitude'),\
                                 "Elevation": config.get('Sensor_'+str(sensor_num),'Elevation'),\
                                 "Sensor Name": config.get('Sensor_'+str(sensor_num),'Sensor Name'),\
                                 "SensorRecordId": config.get('Sensor_'+str(sensor_num),'SensorRecordId'),\
                                 "SensorType": config.get('Sensor_'+str(sensor_num),'SensorType'),\
                                 "Sensor High Limit": config.get('Sensor_'+str(sensor_num),'Sensor High Limit'),\
                                 "Sensor Low Limit": config.get('Sensor_'+str(sensor_num),'Sensor Low Limit'),\
                                 "Sensor Alert": str('yes' if val == -9999 else 'no'),\
						# config.get('Sensor_'+str(sensor_num),'Sensor Alert'),\
				 "Alert SMS Carrier": config.get('Sensor_'+str(sensor_num),'Alert SMS Carrier'),\
                                 "Alert SMS Message": config.get('Sensor_'+str(sensor_num),'Alert SMS Message'),\
                                 "Alert SMS PhoneNumber": config.get('Sensor_'+str(sensor_num),'Alert SMS PhoneNumber'),\
                                 "Alert Email Address": config.get('Sensor_'+str(sensor_num),'Alert Email Address'),\
                                 "Alert Email Message": config.get('Sensor_'+str(sensor_num),'Alert Email Message')\
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
old_values = [0]*8192
new_data = 0

def updating_cloud(a):
    global csvfile
    global writer
    global new_data
    data_was_updated = 1

    if new_data == 1:
        csvfile.close()
	#-----------------------------------------------#
	# if have ne data make API setSensorData
	#-----------------------------------------------#
        try:
                multiple_files = [
                        ('text', ('setSensorData.csv', open('setSensorData.csv', 'rb'), 'text/plain'))]
                r = requests.post(post_url, files=multiple_files, timeout=5)

                log.info('Upload data to Cloud')
                log.info('Status: '+str(r.status_code))

                if r.status_code == 200:
                        csvfile = open('setSensorData.csv', 'wb')
			new_data = 0
			data_was_updated = 1
                elif r.status_code == 404:
                        csvfile = open('setSensorData.csv', 'ab')
			new_data = 0
		else: 
		        csvfile = open('setSensorData.csv', 'ab') 
			new_data = 0

        except requests.exceptions.Timeout:
                log.info("Timeout POST Sensor 1 data to Cloud")
                csvfile = open('setSensorData.csv', 'ab')
		new_data = 0
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)


    if data_was_updated == 1:
	#----------------------------------------------------------------#
	# Ask command for devices (first getState then if ok resetState)
	#----------------------------------------------------------------#
	   context  = a[0]
	   register = 3
    	   slave_id = 0x00
    	   address  = 0x1000
    	   values_w   = context[slave_id].getValues(register, address, count=40)

	   for i in range(0, 20):

	   	b = values_w[i*2]*65536+values_w[i*2+1]
	   	newval = convert(b)
	   	newval = newval + 1
	   	bi = convert_i(newval)
	   	values_w[i*2] = bi/65536
	   	values_w[i*2+1] = bi - 65536*values_w[i*2]
	

	   context[slave_id].setValues(register, address, values_w)
	   
	   data_was_updating = 0

	
#---------------------------------------------------------------------#
#Check that dat changed and save to CSV and set command send in Cloud
#---------------------------------------------------------------------#
def check_val_change(old_1, new_1, old_2, new_2,sensor_num):
	global new_data

    	if old_1 <> new_1 or old_2 <> new_2:
	        b = new_1*65536+new_2
	        newval = convert(b)
	        log.info("We get new sensor "+str(sensor_num)+" data: " + str('%.2f' % newval))
	        save_csv(newval,1)
	        new_data = 1


#-----------------------------------------#
#Check if we have new data on Modbus
#-----------------------------------------#
def updating_writer(a):

    global old_values
    global csvfile
    global writer
    global new_data
    context  = a[0]
    register = 3
    slave_id = 0x00
    address  = 0x0
    values   = context[slave_id].getValues(register, address, count=40)

#-------------------------------------------------------------#
# if we have savi it to CSV and give command to send in Cloud
#-------------------------------------------------------------#
    for i in range(0, 20):
	check_val_change(old_values[i*2],values[i*2],old_values[i*2+1],values[i*2+1],i+1)

    old_values = values

#---------------------------------------------------------------------------# 
# initialize your data store
#---------------------------------------------------------------------------# 
store = ModbusSlaveContext(
    di = ModbusSequentialDataBlock(0, [0]*8192),
    co = ModbusSequentialDataBlock(0, [0]*8192),
    hr = ModbusSequentialDataBlock(0, [0]*8192),
    ir = ModbusSequentialDataBlock(0, [0]*8192))
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


#---------------------------------------------------------------------------# 
# run the server you want
#---------------------------------------------------------------------------# 
time = 3 # 5 seconds delay

loop = LoopingCall(f=updating_writer, a=(context,))
loop.start(time, now=False) # initially delay by time

loop_cloud = LoopingCall(f=updating_cloud, a=(context,))
loop_cloud.start(time, now=False) # initially delay by time

StartTcpServer(context, identity=identity, address=("0.0.0.0", 502))
