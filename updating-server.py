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
from requests_twisted import TwistedRequestsSession

session = TwistedRequestsSession()

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
from twisted.internet import reactor
#---------------------------------------------------------------------------# 
# configure the service logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig(filename='/var/log/modbussrv.log',level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)
#log.setLevel(logging.INFO)


from ctypes import *
from datetime import datetime
import time as _time

#-----------------------------------------#
#Intilize CSV file header
#-----------------------------------------#
csvfile = open('/home/pi/setSensorData.csv', 'ab')
fieldnames = ["Operation","Flag","ObjectId","ObjectType","MobileRecordId","Functional Group Name","Organization Name","Organization Number","Value","Datetime",\
#"Grower","GrowerRecordId",\
#                      "Ranch","RanchRecordId","Field","FieldRecordId","Row","Latitude","Longitude","Elevation",\
"Sensor Name","SensorRecordId"]
#"SensorType","Sensor High Limit",\
#                      "Sensor Low Limit","Sensor Alert","Alert SMS Carrier","Alert SMS Message","Alert SMS PhoneNumber","Alert Email Address","Alert Email Message",\
#			"Alert Count","OrgLevel1Description","OrgLevel1Value","OrgLevel1RecordId","OrgLevel2Description",\
#			"OrgLevel2Value","OrgLevel2RecordId","OrgLevel3Description","OrgLevel3Value","OrgLevel3RecordId",\
#			"OrgLevel4Description","OrgLevel4Value","OrgLevel4RecordId","OrgLevel5Description","OrgLevel5Value",\
#			"OrgLevel5RecordId","SpatialLevel1Description","SpatialLevel1Value","SpatialLevel1RecordId","SpatialLevel2Description",\
#			"SpatialLevel2Value","SpatialLevel2RecordId","SpatialLevel3Description","SpatialLevel3Value","SpatialLevel3RecordId",\
#			"SpatialLevel4Description","SpatialLevel4Value","SpatialLevel4RecordId","SpatialLevel5Description",\
#			"SpatialLevel5Value","SpatialLevel5RecordId"]
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
		OutLim = val >  float(config.get('Sensor_'+str(sensor_num),'Sensor High Limit')) or val < float(config.get('Sensor_'+str(sensor_num),'Sensor Low Limit'))
		log.info("write to CSV for "+str(sensor_num)+" Value:"+str(val))                                    
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
#                                 "Grower": config.get('Sensor_'+str(sensor_num),'Grower'),\
#                                 "GrowerRecordId": config.get('Sensor_'+str(sensor_num),'GrowerRecordId'),\
#                                 "Ranch": config.get('Sensor_'+str(sensor_num),'Ranch'),\
#                                 "RanchRecordId": config.get('Sensor_'+str(sensor_num),'RanchRecordId'),\
#                                 "Field": config.get('Sensor_'+str(sensor_num),'Field'),\
#                                 "FieldRecordId": config.get('Sensor_'+str(sensor_num),'FieldRecordId'),\
#                                 "Row": config.get('Sensor_'+str(sensor_num),'Row'),\
#                                 "Latitude": config.get('Sensor_'+str(sensor_num),'Latitude'),\
#                                 "Longitude": config.get('Sensor_'+str(sensor_num),'Longitude'),\
#                                 "Elevation": config.get('Sensor_'+str(sensor_num),'Elevation'),\
                                 "Sensor Name": config.get('Sensor_'+str(sensor_num),'Sensor Name'),\
                                 "SensorRecordId": config.get('Sensor_'+str(sensor_num),'SensorRecordId'),\
#                                 "SensorType": config.get('Sensor_'+str(sensor_num),'SensorType'),\
#                                 "Sensor High Limit": config.get('Sensor_'+str(sensor_num),'Sensor High Limit'),\
#                                 "Sensor Low Limit": config.get('Sensor_'+str(sensor_num),'Sensor Low Limit'),\
#                                 "Sensor Alert": str('yes' if OutLim == True or val == -9999 else 'no'),\
		                                #"Sensor Alert": str('yes' if val == -9999 else 'no'),\
						# config.get('Sensor_'+str(sensor_num),'Sensor Alert'),\
#				 "Alert SMS Carrier": config.get('Sensor_'+str(sensor_num),'Alert SMS Carrier'),\
#                                 "Alert SMS Message": config.get('Sensor_'+str(sensor_num),'Alert SMS Message'),\
#                                 "Alert SMS PhoneNumber": config.get('Sensor_'+str(sensor_num),'Alert SMS PhoneNumber'),\
#                                 "Alert Email Address": config.get('Sensor_'+str(sensor_num),'Alert Email Address'),\
#                                 "Alert Email Message": config.get('Sensor_'+str(sensor_num),'Alert Email Message'),\
#				 "Alert Count":  config.get('Sensor_'+str(sensor_num),'Alert Count'),\
#                                 "OrgLevel1Description":  config.get('Sensor_'+str(sensor_num),'OrgLevel1Description'),\
#                                 "OrgLevel1RecordId":  config.get('Sensor_'+str(sensor_num),'OrgLevel1RecordId'),\
#                                 "OrgLevel1Value":  config.get('Sensor_'+str(sensor_num),'OrgLevel1Value'),\
#                                 "OrgLevel2Description":  config.get('Sensor_'+str(sensor_num),'OrgLevel2Description'),\
#                                 "OrgLevel2RecordId":  config.get('Sensor_'+str(sensor_num),'OrgLevel2RecordId'),\
#                                 "OrgLevel2Value":  config.get('Sensor_'+str(sensor_num),'OrgLevel2Value'),\
#                                 "OrgLevel3Description":  config.get('Sensor_'+str(sensor_num),'OrgLevel3Description'),\
#                                 "OrgLevel3RecordId":  config.get('Sensor_'+str(sensor_num),'OrgLevel3RecordId'),\
#                                 "OrgLevel3Value":  config.get('Sensor_'+str(sensor_num),'OrgLevel3Value'),\
#                                 "OrgLevel4Description":  config.get('Sensor_'+str(sensor_num),'OrgLevel4Description'),\
#                                 "OrgLevel4RecordId":  config.get('Sensor_'+str(sensor_num),'OrgLevel4RecordId'),\
#                                 "OrgLevel4Value":  config.get('Sensor_'+str(sensor_num),'OrgLevel4Value'),\
#                                 "OrgLevel5Description":  config.get('Sensor_'+str(sensor_num),'OrgLevel5Description'),\
#                                 "OrgLevel5RecordId":  config.get('Sensor_'+str(sensor_num),'OrgLevel5RecordId'),\
#                                 "OrgLevel5Value":  config.get('Sensor_'+str(sensor_num),'OrgLevel5Value'),\
#                                 "SpatialLevel1Description":  config.get('Sensor_'+str(sensor_num),'SpatialLevel1Description'),\
#                                 "SpatialLevel1RecordId":  config.get('Sensor_'+str(sensor_num),'SpatialLevel1RecordId'),\
#                                 "SpatialLevel1Value":  config.get('Sensor_'+str(sensor_num),'SpatialLevel1Value'),\
#                                 "SpatialLevel2Description":  config.get('Sensor_'+str(sensor_num),'SpatialLevel2Description'),\
#                                 "SpatialLevel2RecordId":  config.get('Sensor_'+str(sensor_num),'SpatialLevel2RecordId'),\
#                                 "SpatialLevel2Value":  config.get('Sensor_'+str(sensor_num),'SpatialLevel2Value'),\
#                                 "SpatialLevel3Description":  config.get('Sensor_'+str(sensor_num),'SpatialLevel3Description'),\
#                                 "SpatialLevel3RecordId":  config.get('Sensor_'+str(sensor_num),'SpatialLevel3RecordId'),\
#                                 "SpatialLevel3Value":  config.get('Sensor_'+str(sensor_num),'SpatialLevel3Value'),\
#                                 "SpatialLevel4Description":  config.get('Sensor_'+str(sensor_num),'SpatialLevel4Description'),\
#                                 "SpatialLevel4RecordId":  config.get('Sensor_'+str(sensor_num),'SpatialLevel4RecordId'),\
#                                 "SpatialLevel4Value":  config.get('Sensor_'+str(sensor_num),'SpatialLevel4Value'),\
#                                 "SpatialLevel5Description":  config.get('Sensor_'+str(sensor_num),'SpatialLevel5Description'),\
#                                 "SpatialLevel5RecordId":  config.get('Sensor_'+str(sensor_num),'SpatialLevel5RecordId'),\
#                                 "SpatialLevel5Value":  config.get('Sensor_'+str(sensor_num),'SpatialLevel5Value')\
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
#+str(f.getTraceback()))
         csvfile = open('/home/pi/setSensorData.csv', 'ab')
         new_data = 0
         writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

def print_status(r):
#    print(response.url, response.status_code)
 		global csvfile
    		global writer
    		global new_data
		global data_was_updated
		global sending_in_progress

		sending_in_progress = 0
		log.info('Status: '+str(r.status_code))
#+' Text: '+str(r.text))

                if r.status_code == 200:
                        csvfile = open('/home/pi/setSensorData.csv', 'wb')
                        new_data = 0
                        data_was_updated = 1
                elif r.status_code == 404:
                        csvfile = open('/home/pi/setSensorData.csv', 'ab')
                        new_data = 0
                else:
                        csvfile = open('/home/pi/setSensorData.csv', 'ab')
                        new_data = 0
	        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

def updating_cloud(a):
    global csvfile
    global writer
    global new_data
    global session
    global data_was_updated
    global sending_in_progress

    if new_data == 1 and sending_in_progress == 0:
        csvfile.close()
	sending_in_progress = 1
	#-----------------------------------------------#
	# if have ne data make API setSensorData
	#-----------------------------------------------#
        try:
                multiple_files = [
                        ('text', ('setSensorData.csv', open('/home/pi/setSensorData.csv', 'rb'), 'text/plain'))]
                r = session.post(post_url, files=multiple_files, timeout=60, stream=True)
		r.addCallback(print_status)
		r.addErrback(handleFailure) 
                log.info('Upload data to Cloud')
#                log.info('Status: '+str(r.status_code))

#                if r.status_code == 200:
#                        csvfile = open('setSensorData.csv', 'wb')
#			new_data = 0
#			data_was_updated = 1
#                elif r.status_code == 404:
#                        csvfile = open('setSensorData.csv', 'ab')
#			new_data = 0
#		else: 
#		        csvfile = open('setSensorData.csv', 'ab') 
#			new_data = 0

#        except requests.exceptions.Timeout:
        except requests.exceptions.ReadTimeout:
                log.info("Timeout POST Sensor 1 data to Cloud")
                csvfile = open('/home/pi/setSensorData.csv', 'ab')
		new_data = 0
#        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)


    if data_was_updated == 1:
	#----------------------------------------------------------------#
	# Ask command for devices (first getState then if ok resetState)
	#----------------------------------------------------------------#
	   context  = a[0]
	   register = 3
    	   slave_id = 0x00
    	   address  = 0x1000
    	   values_w   = context[slave_id].getValues(register, address, count=40)

	#   for i in range(0, 20):

	#   	b = values_w[i*2]*65536+values_w[i*2+1]
	#   	newval = convert(b)
	#   	newval = newval + 1
	#   	bi = convert_i(newval)
	#   	values_w[i*2] = bi/65536
	#   	values_w[i*2+1] = bi - 65536*values_w[i*2]
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

    context  = a[0]
    register = 3
    slave_id = 0x00
    address  = 0x0
    values   = context[slave_id].getValues(register, address, count=40)
    if new_data == 0 and one_send_only == 0:
#-------------------------------------------------------------#
# if we have savi it to CSV and give command to send in Cloud
#-------------------------------------------------------------#
#    for i in range(0, 20):
     for i in [0, 1, 2, 3, 4, 12, 13, 18]:
	check_val_change(old_values[i*2],values[i*2],old_values[i*2+1],values[i*2+1],i+1)
     if new_data == 1:
        one_send_only = 1
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
time = 10 # 5 seconds delay
#time_cloud = 10

loop = LoopingCall(f=updating_writer, a=(context,))
loop.start(time, now=False) # initially delay by time

loop_cloud = LoopingCall(f=updating_cloud, a=(context,))
loop_cloud.start(time, now=False) # initially delay by time

#reactor.run()
StartTcpServer(context, identity=identity, address=("0.0.0.0", 502))
