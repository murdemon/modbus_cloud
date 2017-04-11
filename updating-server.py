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

frame_PLC = ""
Sens_1_takt = 0

st1_soil_temp = 0
st1_soil_moist = 0
st1_air_temp = 0
st1_air_humid = 0

st2_soil_temp = 0
st2_soil_moist = 0
st2_air_temp = 0
st2_air_humid = 0

st3_soil_temp = 0
st3_soil_moist = 0
st3_air_temp = 0
st3_air_humid = 0

st4_soil_temp = 0
st4_soil_moist = 0
st4_air_temp = 0
st4_air_humid = 0

def xbee_data(frames):
	global one_send_only
	global new_data
        global frame_PLC
	global Sens_1_takt
	global st1_soil_temp
	global st1_soil_moist
	global st1_air_temp
	global st1_air_humid
        global st2_soil_temp
        global st2_soil_moist
        global st2_air_temp
        global st2_air_humid
        global st3_soil_temp
        global st3_soil_moist
        global st3_air_temp
        global st3_air_humid
        global st4_soil_temp
        global st4_soil_moist
        global st4_air_temp
        global st4_air_humid


	print frames

	addr = frames['source_addr']

	if addr ==  "0013a2004124f8d4":
		print "Get Data from XBee PLC"
		frame_PLC = frames['data'].decode("hex")

        if len(frames['data']) == 32 and  addr ==  "0013a200415b7ea4":
                print "Get Data from Sensor station 2"

                sensor = frames['source_addr']
                st2_soil_temp = struct.unpack('!f', frames['data'][0:8].decode('hex'))[0]
                st2_soil_moist = struct.unpack('!f', frames['data'][8:16].decode('hex'))[0]
                st2_air_temp = struct.unpack('!f', frames['data'][16:24].decode('hex'))[0]*1.8 + 32
                st2_air_humid = struct.unpack('!f', frames['data'][24:32].decode('hex'))[0]

                print "We get data from sensor station: "+ sensor
                print "Soil Temperature: " + str(st2_soil_temp)
                print "Soil Moisture: "      + str(st2_soil_moist)
                print "Air Temperature: "    + str(st2_air_temp)
                log.info("Air Humidity: "  + str(st2_air_humid))			

        if len(frames['data']) == 32 and  addr ==  "0013a2004154d773":
                print "Get Data from Sensor station 1"

                sensor = frames['source_addr']
                st1_soil_temp = struct.unpack('!f', frames['data'][0:8].decode('hex'))[0]
                st1_soil_moist = struct.unpack('!f', frames['data'][8:16].decode('hex'))[0]
                st1_air_temp = struct.unpack('!f', frames['data'][16:24].decode('hex'))[0]*1.8 + 32
                st1_air_humid = struct.unpack('!f', frames['data'][24:32].decode('hex'))[0]

                print "We get data from sensor station: "+ sensor
                print "Soil Temperature: " + str(st1_soil_temp)
                print "Soil Moisture: "      + str(st1_soil_moist)
                print "Air Temperature: "    + str(st1_air_temp)
                print "Air Humidity: "  + str(st1_air_humid)

        if len(frames['data']) == 32 and  addr ==  "0013a200415b7e9c":
                print "Get Data from Sensor station 3"

                sensor = frames['source_addr']
                st3_soil_temp = struct.unpack('!f', frames['data'][0:8].decode('hex'))[0]
                st3_soil_moist = struct.unpack('!f', frames['data'][8:16].decode('hex'))[0]
                st3_air_temp = struct.unpack('!f', frames['data'][16:24].decode('hex'))[0]*1.8 + 32
                st3_air_humid = struct.unpack('!f', frames['data'][24:32].decode('hex'))[0]

                print "We get data from sensor station: "+ sensor
                print "Soil Temperature: " + str(st3_soil_temp)
                print "Soil Moisture: "      + str(st3_soil_moist)
                print "Air Temperature: "    + str(st3_air_temp)
                print "Air Humidity: "  + str(st3_air_humid)

def electron_read(a):
#	  log.info("Electron read")
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

                if RecordID == "1177247":
                        Mode_from_Cloud = cloud_data[1]
                        print Mode_from_Cloud

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
	serial_PLC = serial.Serial('/dev/ttyUSB1', 9600, timeout=0.1)
except Exception:
        print ("PLC not connected")
	serial_PLC = serial.Serial('/dev/tty22', 9600, timeout=0.1)


try:
	serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
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
SerPipe_PLC = Protocol()

#Set MASTER name on master station
#xbee.send('at', id='\x08', frame_id='\x01',  command='NI', parameter='MASTER')
#xbee.send('at', id='\x09', frame_id='\x02',  command='AO', parameter='\x00')
#xbee.send('tx', id='\x10', frame_id='\x03',  dest_addr='\x00\x13\xa2\x00\x41\x24\xf8\xd4', reserved = '\xFF\xFE' , broadcast_radius = '\x00', options = '\x00', data = '02*00*')
print "Startting..."
xbee.send('at', id='\x08', frame_id='\x01',  command='NI', parameter='MASTER')
xbee.send('at', id='\x08', frame_id='\x02',  command='AO', parameter='\x00')
xbee.send('at', id='\x08', frame_id='\x03',  command='ID', parameter='\x1F\xF7')
xbee.send('at', id='\x08', frame_id='\x04',  command='SH', parameter='')
xbee.send('at', id='\x08', frame_id='\x05',  command='SL', parameter='')
xbee.send('at', id='\x08', frame_id='\x06',  command='ID', parameter='')
xbee.send('at', id='\x08', frame_id='\x07',  command='SM', parameter='')

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
#dt_now_PLC =  ""

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
	print "Check val:"+str(old_1) + "," + str(new_1)
#    	if old_1 <> new_1:
	if 1 == 1:
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
   global Get_sample
    
   if answer_was == 1:
#    answer_was = 0
#    log.info("Send data to PLC step:" + str(ix))
#    print(".")
    if ix == 0:
	    xbee.send('tx', id='\x10', frame_id='\x03',  dest_addr='\x00\x13\xa2\x00\x41\x24\xf8\xd4', reserved = '\xFF\xFE' , broadcast_radius = '\x00', options = '\x00', data = '02*00*')
	    if Get_sample == 1:
		    serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,0))
		    serial_PLC.flush()
		    answer_was = 0
	    ix = 1
    elif ix == 1:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,1))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 2
    elif ix == 2:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,2))
                    answer_was = 0
 	            serial_PLC.flush()
            ix = 3
    elif ix == 3:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,3))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 4    
    elif ix == 4:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,4))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 5
    elif ix == 5:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,5))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 6
    elif ix == 6:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,6))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 7
    elif ix == 7:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,7))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 8
    elif ix == 8:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,10))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 9
    elif ix == 9:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,11))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 10
    elif ix == 10:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,12))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 11
    elif ix == 11:
            if Get_sample == 1:
	            serial_PLC.write(SerPipe.Get_Subsystem_Setpoint(0,13))
	            serial_PLC.flush()
                    answer_was = 0
            ix = 12
    elif ix == 12:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,21,Y[1]))
            serial_PLC.flush() 
            answer_was = 0
            ix = 13
    elif ix == 13:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,22,Y[2]))
            serial_PLC.flush()
            answer_was = 0
            ix = 14
    elif ix == 14:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,23,Y[3]))
            serial_PLC.flush()
            answer_was = 0
            ix = 15
    elif ix == 15:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,24,Y[4]))
            serial_PLC.flush()
            answer_was = 0
            ix = 16
    elif ix == 16:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,25,Y[5]))
            serial_PLC.flush()
            answer_was = 0
            ix = 17
    elif ix == 17:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,26,Y[6]))
            serial_PLC.flush()
            answer_was = 0
            ix = 18
    elif ix == 18:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,27,Y[7]))
            serial_PLC.flush()
            answer_was = 0
            ix = 19
    elif ix == 19:
            serial_PLC.write(SerPipe.Set_Subsystem_Setpoint(0,28,Y[8]))
            serial_PLC.flush()
            answer_was = 0
            ix = 20
    elif ix == 20:
            serial_PLC.write(SerPipe.Get_RTC())
            serial_PLC.flush()
            answer_was = 0
            ix = 21
    elif ix == 21:
            serial_PLC.write(SerPipe.Get_System_Status())
            serial_PLC.flush()
            answer_was = 0
            ix = 22
    elif ix == 22:
            serial_PLC.write(SerPipe.Get_Subsystem_Mode(0))
            serial_PLC.flush()
            answer_was = 0
            ix = 0
#    Get_sample = 0
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
 global st1_soil_temp
 global st1_soil_moist
 global st1_air_temp
 global st1_air_humid

 print "Check vals.............."
 for i in [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]:
    check_val_change(old[i],new[i],i+1)

 sensor = "0013a20040e3abd5"
 serial_port_electron.write(str(sensor) + "_1,1800,"+ str('%.2f' % st2_soil_temp)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_2,1800,"+ str('%.2f' % st2_soil_moist)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_3,1800,"+ str('%.2f' % st2_air_temp)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_4,1800,"+ str('%.2f' % st2_air_humid)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)

 sensor = "0013a20040e3abca"
 serial_port_electron.write(str(sensor) + "_1,1800,"+ str('%.2f' % st1_soil_temp)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_2,1800,"+ str('%.2f' % st1_soil_moist)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_3,1800,"+ str('%.2f' % st1_air_temp)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_4,1800,"+ str('%.2f' % st1_air_humid)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)

 sensor = "0013a20040e3abea"
 serial_port_electron.write(str(sensor) + "_1,1800,"+ str('%.2f' % st1_soil_temp)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_2,1800,"+ str('%.2f' % st1_soil_moist)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_3,1800,"+ str('%.2f' % st1_air_temp)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 serial_port_electron.write(str(sensor) + "_4,1800,"+ str('%.2f' % st1_air_humid)+"\r");
 serial_port_electron.flushOutput()
 sleep(10)
 
 sensor = "MasterStatus"
 serial_port_electron.write(str(sensor) + ",1800,"+ ErrorStatus +"\r");
 serial_port_electron.flushOutput()
 sleep(10)



iter = 0
ErrorStatus = "00000000000000000000000000000000"
was_ErrorStatus = "00000000000000000000000000000000"
Mode = "00";
was_Mode = "00";

def loop_data_PLC(a):
    global new
    global ErrorStatus
    global was_ErrorStatus
    global answer_was
    global iter
    global frame_PLC 
    global dt_now_PLC
    global Mode
    global was_Mode
    frame = serial_PLC.readline()
    frame_data = SerPipe.frame_reader(frame)

#    if 1==1:
#	print "Parse PLC frame" + frame
#	frame_data_PLC = SerPipe_PLC.frame_reader(frame)
#        frame_PLC = "";

    iter = iter + 1

    if iter > 5 and answer_was == 0:
	    answer_was = 1
	    iter = 0

    if frame_data[0] == "10":
	 was_ErrorStatus =  ErrorStatus
         answer_was = 1
	 print frame_data
	 if frame_data[1] == "00" and frame_data[2] == "00" and frame_data[3] == "00":
		print "No error"
		ErrorStatus = "00000000000000000000000000000000"
	 if frame_data[1] == "01":
		print "Error 1"
		new = list(ErrorStatus)
		new[31] = '1'
		ErrorStatus = ''.join(new)
		print ErrorStatus

         if frame_data[1] == "02":
                print "Error 2"
                new = list(ErrorStatus)
                new[30] = '1'
                ErrorStatus = ''.join(new)
                print ErrorStatus

         if frame_data[1] == "03":
                print "Error 3"
                new = list(ErrorStatus)
                new[29] = '1'
                ErrorStatus = ''.join(new)
                print ErrorStatus

         if frame_data[1] == "04":
                print "Error 4"
                new = list(ErrorStatus)
                new[28] = '1'
                ErrorStatus = ''.join(new)
                print ErrorStatus
         if frame_data[1] == "05":
                print "Error 5"
                new = list(ErrorStatus)
                new[27] = '1'
                ErrorStatus = ''.join(new)
                print ErrorStatus
         if frame_data[1] == "06":
                print "Error 6"
                new = list(ErrorStatus)
                new[26] = '1'
                ErrorStatus = ''.join(new)
                print ErrorStatus
         if frame_data[1] == "07":
                print "Error 7"
                new = list(ErrorStatus)
                new[25] = '1'
                ErrorStatus = ''.join(new)
                print ErrorStatus
		
    if frame_data[0] == "11":
	 print frame_data
         answer_was = 1
         Year = frame_data[1]
	 Month = frame_data[2]
	 Day = frame_data[3]
	 Hour = frame_data[4]
	 Min = frame_data[5]
	 Sec = frame_data[6]
         new_datetime = (int(Year), int(Month), int(Day), int(Hour), int(Min), int(Sec),int(0))
	 dt_now_PLC = datetime( *new_datetime[:6])
	 print dt_now_PLC

    if frame_data[0] == "02":
         answer_was = 1
	 was_Mode = Mode
	 if frame_data[2] == "00":
		 Mode = "00"
	         print "Get subsystem mode: STOP"
	 if frame_data[2] == "01":
		 Mode = "01"
                 print "Get subsystem mode: RUN"

    if frame_data[0] == "03":
	 answer_was = 1
	 if frame_data[1] == "00":
	  print "Get data from PLC:" + str(frame_data[3])
	  print "Sensor num:" + str(frame_data[2])
	  new[int(frame_data[2])] = float(frame_data[3])

Get_sample = 1

def SampleTime(a):
    global Get_sample    
    global was_ErrorStatus
    global ErrorStatus
    global was_Mode
    global Mode
    if was_ErrorStatus <>  ErrorStatus:
         sensor = "MasterStatus"
         serial_port_electron.write(str(sensor) + ",1800,"+ ErrorStatus +"\r");
         serial_port_electron.flushOutput()
         sleep(10)

    if was_Mode <> Mode:
         sensor = "MasterMode"
         serial_port_electron.write(str(sensor) + ",1800,"+ Mode +"\r");
         serial_port_electron.flushOutput()
         sleep(10)

    Get_sample = 1

def customHandler():
        log.info("Bye")
	reactor.sigTerm()
	xbee.halt()
	serial_PLC.close()
	serial_port.close()
	serial_port_electron.close()
	reactor.removeAll()
	reactor.stop	

#signal.signal(signal.SIGINT, customHandler)
#signal.signal(signal.SIGTERM, customHandler)

print("Starting.... service")

serial_port_electron.write("Electron starting\r");
serial_port_electron.flushOutput()

loop1 = LoopingCall(f=loop_30min, a=(context,))
loop1.start(1800, now=False).addErrback(fail) # initially delay by time

loop_s = LoopingCall(f=SampleTime, a=(context,))
loop_s.start(10, now=False).addErrback(fail) # initially delay by time

loop2 = LoopingCall(f=updating_writer, a=(context,))
loop2.start(0.01, now=False).addErrback(fail) # initially delay by time

loop3 = LoopingCall(f=loop_data_PLC, a=(context,))
loop3.start(0.01, now=False).addErrback(fail) # initially delay by time

loop_Electron_read = LoopingCall(f=electron_read, a=(context,))
loop_Electron_read.start(0.01, now=False).addErrback(fail) # initially delay by time

loop_cloud = LoopingCall(f=updating_cloud, a=(context,))
loop_cloud.start(0.01, now=False).addErrback(fail) # initially delay by time

reactor.addSystemEventTrigger('before', 'shutdown', customHandler)
reactor.run()
