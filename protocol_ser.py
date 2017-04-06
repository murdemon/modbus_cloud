#!/usr/bin/env python

#---------------------------------------------------------------------------# 
# import the modbus libraries we need
#---------------------------------------------------------------------------# 
class Protocol:

  def frame_reader(self,frame):
    frame_data = frame.split('*')

    if frame_data[0]   == "10" and len(frame_data) == 5:
	print "Get System Status: 10"
        print "SV = Status Value: "+str(frame_data[1]);
	if frame_data[1] == "00":
		print "System OK"
	if frame_data[1] == "01":
		print "PLC Hardware Fault"
	if frame_data[1] == "02":
		print "Low Flow or Valve Failure"
	if frame_data[1] == "03":
		print "Pump / Motor Overload"
	if frame_data[1] == "04":
		print "Low or no flow at Sensor"
	if frame_data[1] == "05":
		print "Analog Sensor Out of Range (Analog IO Problem)"
	if frame_data[1] == "06":
		print "Command Could not be Completed, Prompt Operator"
	print "Module # "+str(frame_data[2])
	print "Channel # "+str(frame_data[3])


    elif frame_data[0] == "11" and len(frame_data) == 8:
	print "Get RTC (Real Time Clock): 11"
	print "Year:"+str(frame_data[1])
	print "Month:"+str(frame_data[2])
	print "Day:"+str(frame_data[3])
	print "Hour:"+str(frame_data[4])
	print "Minute:"+str(frame_data[5])
	print "Second:"+str(frame_data[6])

    elif frame_data[0] == "12" and len(frame_data) == 5:
	print "Get System Analog / Digital Sensor Input: 12"
	print "Sensor Number, Module:"+str(frame_data[1])
	print "Sensor Number, Channel:"+str(frame_data[2])
	print "Sensor Value:"+str(frame_data[3])

    elif frame_data[0] == "13" and len(frame_data) == 6:
	print "Get System Analog / Digital Output Value: 13"
#	print "Output Number, Module:"+str(frame_data[1])
#	print "Output Number, Channel:"+str(frame_data[2])
#	print "Output Value:"+str(frame_data[3])
	if frame_data[4] == "00":
			print "Forced State:Unforced"
	if frame_data[4] == "01":
			print "Forced State:Forced"

    elif frame_data[0] == "14" and len(frame_data) == 6:
	print "Force System Analog / Digital Output Value: 14"
#	print "Output Number, Module:"+str(frame_data[1])
#	print "Output Number, Channel:"+str(frame_data[2])
#	print "Output Value:"+str(frame_data[3])
	if frame_data[4] == "00":
			print "Forced State:Unforced"
	if frame_data[4] == "01":
			print "Forced State:Forced"

    elif frame_data[0] == "02" and len(frame_data) == 6:
	print "Get Subsystem Mode / Sequence Status: 02"
#	print "Subsystem Number:"+str(frame_data[1])
#	print "Run / Stop Mode:"+str(frame_data[2])
#	print "Current Sequence Step Running:"+str(frame_data[3])
#	print "Last Sequence Step Completed:"+str(frame_data[4])

    elif frame_data[0] == "03" and len(frame_data) == 5:
	print "Get Subsystem Set point: 03"
#	print "Subsystem Number:"+str(frame_data[1])
#	print "Set point Number:"+str(frame_data[2])
#	print "Set point Value:"+str(frame_data[3])

    elif frame_data[0] == "04" and len(frame_data) == 4:
	print "Set Subsystem Mode & Sequence: 04"
#	print "Subsystem Number:"+str(frame_data[1])
#	print "Mode / Sequence Command:"+str(frame_data[2])

    elif frame_data[0] == "05" and len(frame_data) == 5:
	print "Set Subsystem Set point: 05"
#	print "Subsystem Number"+str(frame_data[1])
#	print "Set point Number:"+str(frame_data[2])
#	print "Set point Value:"+str(frame_data[3])
    elif len(frame) > 0:
	print "----Unknown frame---:"+str(frame)
        return ["00","00","00"]
    return frame_data

  def Get_System_Status(self):
	return "10*\r"
  def Get_RTC(self):
	return "11*\r"

  def Get_System_Input_Value(self, MD, CH):
	if MD > 99 or MD < 0:
		print "Error MD format"
		return ""
	if CH > 99 or CH < 0:
		print "Error CH format"
		return ""	
	return "12*"+str('%02d' % MD)+"*"+str('%02d' % CH)+"*\r"

  def Get_System_Output_Value(self, MD, CH):
	if MD > 99 or MD < 0:
		print "Error MD format"
		return ""
	if CH > 99 or CH < 0:
		print "Error CH format"
		return ""	
	return "13*"+str('%02d' % MD)+"*"+str('%02d' % CH)+"*\r"

  def Force_System_Output_Value(self, MD, CH, FV):
	if MD > 99 or MD < 0:
		print "Error MD format"
		return ""
	if CH > 99 or CH < 0:
		print "Error CH format"
		return ""	
	if FV == True:
		FV = "01"
	if FV == False:
		FV = "00"
	return "14*"+str('%02d' % MD)+"*"+str('%02d' % CH)+"*"+str(FV)+"*\r"

  def Get_Subsystem_Mode(self, SN):
	if SN > 99 or SN < 0:
		print "Error SN format"
		return ""
	return "02*"+str('%02d' % SN)+"*\r"

  def Get_Subsystem_Setpoint(self, SN, SP):
	if SN > 99 or SN < 0:
		print "Error SN format"
		return ""
	if SP > 99 or SP < 0:
		print "Error SP format"
		return ""
	return "03*"+str('%02d' % SN)+"*" +str('%02d' % SP)+ "*\r"

  def Set_Subsystem_Mode(self, SN, MS):
	if SN > 99 or SN < 0:
		print "Error SN format"
		return ""
	if MS > 99 or MS < 0:
		print "Error MS format"
		return ""
	return "04*"+str('%02d' % SN)+"*" +str('%02d' % MS)+ "*\r"

  def Set_Subsystem_Setpoint(self, SN, SP, SV):
	if SN > 99 or SN < 0:
		print "Error SN format"
		return ""
	if SP > 99 or SP < 0:
		print "Error SP format"
		return ""
	return "05*"+str('%02d' % SN)+"*" +str('%02d' % SP)+"*" +str(SV)+ "*\r"


