#!/usr/bin/env python

#---------------------------------------------------------------------------# 
# import the modbus libraries we need
#---------------------------------------------------------------------------# 
from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from protocol_ser import Protocol
from xbee import XBee,DigiMesh
import serial
import time
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
from time import sleep
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from flask import Flask
from flask import request
from flask import abort
from twisted.internet import ssl
from twisted.internet import reactor
import signal
import struct
import pickle


def xbee_data(frames):
	global one_send_only
	global new_data
	print frames
	if len(frames['data']) == 32:

#		print frames['data']
		sensor = frames['source_addr']
		value1 = struct.unpack('!f', frames['data'][0:8].decode('hex'))[0]
		value2 = struct.unpack('!f', frames['data'][8:16].decode('hex'))[0]
		value3 = struct.unpack('!f', frames['data'][16:24].decode('hex'))[0]
		value4 = struct.unpack('!f', frames['data'][24:32].decode('hex'))[0]
		
#		if sensor == "0013a20041461027":
		if 1 == 1:
			log.info("We get data from sensor station: "+ sensor)
			log.info("Soil Temperature: " + str(value1))
			log.info("Soil Moisture: " 	+ str(value2))
			log.info("Air Temperature: " 	+ str(value3))
			log.info("Air Humidity: "  + str(value4))
		
	
#			serial_port_electron.write(str(sensor) + "_1,1800,"+ str('%.2f' % value1)+"\r");
#			serial_port_electron.flushOutput()
#			sleep(10)
#			serial_port_electron.write(str(sensor) + "_2,1800,"+ str('%.2f' % value2)+"\r");
#			serial_port_electron.flushOutput()
#			sleep(10)
#			serial_port_electron.write(str(sensor) + "_3,1800,"+ str('%.2f' % value3)+"\r");
#			serial_port_electron.flushOutput()
#			sleep(10)
#			serial_port_electron.write(str(sensor) + "_4,1800,"+ str('%.2f' % value4)+"\r");
#			serial_port_electron.flushOutput()
#			sleep(10)

def electron_read(a):
	  log.info("Electron read")
	  data = serial_port_electron.readline()
	  print data
	  if data <> "":
	     try:
		data = data.replace("\r\n", "")
	 
		cloud_data = data.split(';')		
		RecordID = cloud_data[0]
		if RecordID == "655475":
			DurationInMinutes[1] = cloud_data[4]
			Days[1] = cloud_data[2]
			StartTime[1] = cloud_data[3]
			PowerOn[1] = cloud_data[1]
			print cloud_data
                if RecordID == "655476":
                        DurationInMinutes[2] = cloud_data[4]
                        Days[2] = cloud_data[2]
                        StartTime[2] = cloud_data[3]
                        PowerOn[2] = cloud_data[1]
                        print cloud_data
                if RecordID == "733616":
                        DurationInMinutes[3] = cloud_data[4]
                        Days[3] = cloud_data[2]
                        StartTime[3] = cloud_data[3]
                        PowerOn[3] = cloud_data[1]
                        print cloud_data
                if RecordID == "655478":
                        DurationInMinutes[4] = cloud_data[4]
                        Days[4] = cloud_data[2]
                        StartTime[4] = cloud_data[3]
                        PowerOn[4] = cloud_data[1]
                        print cloud_data
                if RecordID == "655479":
                        DurationInMinutes[5] = cloud_data[4]
                        Days[5] = cloud_data[2]
                        StartTime[5] = cloud_data[3]
                        PowerOn[5] = cloud_data[1]
                        print cloud_data
                if RecordID == "655480":
                        DurationInMinutes[6] = cloud_data[4]
                        Days[6] = cloud_data[2]
                        StartTime[6] = cloud_data[3]
                        PowerOn[6] = cloud_data[1]
                        print cloud_data
                if RecordID == "655481":
                        DurationInMinutes[7] = cloud_data[4]
                        Days[7] = cloud_data[2]
                        StartTime[7] = cloud_data[3]
                        PowerOn[7] = cloud_data[1]
                        print cloud_data
                if RecordID == "655482":
                        DurationInMinutes[8] = cloud_data[4]
                        Days[8] = cloud_data[2]
                        StartTime[8] = cloud_data[3]
                        PowerOn[8] = cloud_data[1]
                        print cloud_data
             except Exception:
                log.info("Bed data in")

	     f = open('/home/pi/DurationInMinutes.pckl', 'wb')
	     object = pickle.dump(DurationInMinutes,f)
	     f.close()

	     f = open('/home/pi/Days.pckl', 'wb')
	     object = pickle.dump(Days,f)
	     f.close()

	     f = open('/home/pi/StartTime.pckl', 'wb')
	     object = pickle.dump(StartTime,f)
	     f.close()

	     f = open('/home/pi/PowerOn.pckl', 'wb')
             object = pickle.dump(PowerOn,f)
	     f.close()
		

try:
	serial_PLC = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)
except Exception:
        print ("PLC not connected")
	serial_PLC = serial.Serial('/dev/tty22', 9600, timeout=0.1)


try:
	serial_port = serial.Serial('/dev/ttyUSB1', 9600, timeout=0.1)
except Exception:
        print ("Xbee not connected")
	serial_port = serial.Serial('/dev/tty21', 9600)


try:
	serial_port_electron = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
except Exception:
	print ("Modem not connected")
	serial_port_electron = serial.Serial('/dev/tty20', 9600, timeout=1)

xbee = DigiMesh(serial_port,  callback=xbee_data)

SerPipe = Protocol()

#Set MASTER name on master station
xbee.send('at', id='\x08', frame_id='\x00',  command='NI', parameter='MASTER')
xbee.send('at', id='\x09', frame_id='\x00',  command='AO', parameter='\x00')
xbee.send('at', id='\x08', frame_id='\x00',  command='NI', parameter='MASTER')
xbee.send('at', id='\x09', frame_id='\x00',  command='AO', parameter='\x00')
xbee.send('at', id='\x08', frame_id='\x00',  command='NI', parameter='MASTER')
xbee.send('at', id='\x09', frame_id='\x00',  command='AO', parameter='\x00')
xbee.send('at', id='\x08', frame_id='\x00',  command='NI', parameter='MASTER')
xbee.send('at', id='\x09', frame_id='\x00',  command='AO', parameter='\x00')

reactor.suggestThreadPoolSize(10)

DurationInMinutes = ['0']*10
Days = ['']*10
StartTime = ['0:0']*10
PowerOn = ['']*10

try:
	f = open('/home/pi/DurationInMinutes.pckl', 'rb')
	DurationInMinutes = pickle.load(f)
	f.close()

	f = open('/home/pi/Days.pckl', 'rb')
	Days = pickle.load(f)
	f.close()

	f = open('/home/pi/StartTime.pckl', 'rb')
	StartTime = pickle.load(f)
	f.close()

	f = open('/home/pi/PowerOn.pckl', 'rb')
	PowerOn = pickle.load(f)
	f.close()
except:
    print "Can't load saved data"


session = TwistedRequestsSession()

from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import logging

#logging.basicConfig(filename='/var/log/modbussrv.log',level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)



TimeFromPLC = 0
UpdateTime = 0

from ctypes import *
from datetime import datetime
from datetime import timedelta
import time as _time

dt_now_PLC =  datetime.now()


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
	   global Y

	   for i in [1, 2, 3, 4, 5, 6, 7, 8]:
		
	    Y[i] = 0

	    AllDays = Days[i].split(",")
	    AllStartTime = StartTime[i].split(",")
	    AllDurations = DurationInMinutes[i].split(",")

	    for j in range(len(AllDays)):
	    	TimeFrom = datetime.strptime(AllStartTime[j],"%H:%M")
		TimeTo = TimeFrom + timedelta(minutes=int(AllDurations[j]))
		TimeNow = datetime.strptime(dt_now_PLC.strftime("%H:%M"),"%H:%M")

		if dt_now_PLC.strftime("%a").find(AllDays[j]) > -1 and TimeNow > TimeFrom and TimeNow < TimeTo:
			Y[i] = 1
                	log.info("Shudler on valve N" + str(i))
		else:
			Y[i] = 0

	    if str(PowerOn[i]).lower().find('manualon') > -1:
		log.info("Manual on valve N" + str(i))
		Y[i] = 1
            if str(PowerOn[i]).lower().find('manualoff') > -1:
		Y[i] = 0

	
#---------------------------------------------------------------------#
#Check that dat changed and save to CSV and set command send in Cloud
#---------------------------------------------------------------------#
def check_val_change(old_1, new_1,sensor_num):
	global new_data

    	if old_1 <> new_1:
	        newval = new_1
	        log.info("We get new sensor "+str(sensor_num)+" data: " + str('%.2f' % newval))
		serial_port_electron.write("1_"+str(sensor_num) + ",1800,"+ str('%.2f' % newval)+"\r");
		log.info("1_"+str(sensor_num) + ",1800,"+ str('%.2f' % newval)+"\r");
		serial_port_electron.flushOutput()
	        sleep(10)		

#---------------------------------------------------------------------#
#Check that dat changed and set Date and Time from PLC
#---------------------------------------------------------------------#
Year = 0
Month = 0
Day = 0
Hour = -1
Min = -1
Sec = -1
one_send_only = 0

#-----------------------------------------#
#Check if we have new data on Modbus
#-----------------------------------------#
ix = 0
Y = [0]*10
answer_was = 1

def updating_writer(a):

   global old_values
   global csvfile
   global writer
   global new_data
   global one_send_only
   global UpdateTime
   global ix
   global answer_was
    
   if answer_was == 1:
    answer_was = 0
#    log.info("Send data to PLC step:" + str(ix))
    print(".")
    if ix == 0:
	    serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,0))
	    serial_PLC.flush()
	    ix = 1
    elif ix == 1:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,1))
            serial_PLC.flush()
            ix = 2
    elif ix == 2:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,2))
            serial_PLC.flush()
            ix = 3
    elif ix == 3:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,3))
            serial_PLC.flush()
            ix = 4    
    elif ix == 4:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,4))
            serial_PLC.flush()
            ix = 5
    elif ix == 5:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,5))
            serial_PLC.flush()
            ix = 6
    elif ix == 6:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,6))
            serial_PLC.flush()
            ix = 7
    elif ix == 7:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,7))
            serial_PLC.flush()
            ix = 8
    elif ix == 8:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,10))
            serial_PLC.flush()
            ix = 9
    elif ix == 9:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,11))
            serial_PLC.flush()
            ix = 10
    elif ix == 10:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,12))
            serial_PLC.flush()
            ix = 11
    elif ix == 11:
            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,13))
            serial_PLC.flush()
            ix = 12
    elif ix == 12:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,21,Y[1]))
            serial_PLC.flush()
            ix = 13
    elif ix == 13:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,22,Y[2]))
            serial_PLC.flush()
            ix = 14
    elif ix == 14:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,23,Y[3]))
            serial_PLC.flush()
            ix = 15
    elif ix == 15:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,24,Y[4]))
            serial_PLC.flush()
            ix = 16
    elif ix == 16:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,25,Y[5]))
            serial_PLC.flush()
            ix = 17
    elif ix == 17:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,26,Y[6]))
            serial_PLC.flush()
            ix = 18
    elif ix == 18:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,27,Y[7]))
            serial_PLC.flush()
            ix = 19
    elif ix == 19:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,28,Y[8]))
            serial_PLC.flush()
            ix = 0

def fail(f):
    log.info("we got an exception: %s" % (f.getTraceback(),))

#---------------------------------------------------------------------------# 
# run the server you want
#---------------------------------------------------------------------------# 
time = 1
time_cloud = 1
context = ""

old = [0]*200
new = [0]*200

def loop_30min(a):
 global new
 global old
 for i in [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]:
    check_val_change(old[i],new[i],i+1)
 old = new


iter = 0
def loop_data_PLC(a):
    global new
    global answer_was
    global iter
    frame = serial_PLC.readline()
    frame_data = SerPipe.frame_reader(frame)

    iter = iter + 1

    if iter > 5 and answer_was == 0:
	    answer_was = 1
	    iter = 0

    if frame_data[0] == "03":
	 answer_was = 1
	 if frame_data[1] == "00":
	  new[int(frame_data[2])] = float(frame_data[3])
    


def customHandler(signum, stackframe):
        log.info("Bye")
	xbee.halt()
	serial_PLC.close()
	serial_port.close()
	serial_port_electron.close()
	reactor.callFromThread(reactor.stop)	

signal.signal(signal.SIGINT, customHandler)

loop1 = LoopingCall(f=loop_30min, a=(context,))
loop1.start(1800, now=False).addErrback(fail) # initially delay by time


loop2 = LoopingCall(f=updating_writer, a=(context,))
loop2.start(1, now=False).addErrback(fail) # initially delay by time

loop3 = LoopingCall(f=loop_data_PLC, a=(context,))
loop3.start(1, now=False).addErrback(fail) # initially delay by time

loop_Electron_read = LoopingCall(f=electron_read, a=(context,))
loop_Electron_read.start(1, now=False).addErrback(fail) # initially delay by time

loop_cloud = LoopingCall(f=updating_cloud, a=(context,))
loop_cloud.start(1, now=False).addErrback(fail) # initially delay by time


reactor.run()




