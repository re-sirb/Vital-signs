#!/usr/bin/python
# -*- coding: utf-8 -*-

#new Revision: Testbench 0.3

import socket
import sys
import struct
import time 
import datetime

import threading 
#import multiprocessing 

class ipv_data_source:
	
	def __init__(self, ip):
		#self.n=0
		self.ip=ip
		#debug_flag
		self.debug_info=False
		self.debug_error=True
		
		#start/stop mainloop
		self.run_loop=False
		#check if connection is ok
		self.is_active=False
		#run watchdog
		self.run_con_watchdog=True
		
		# patient data
		self.p_id=""
		self.p_pre_name=""
		self.p_name=""
		self.p_gender=""
		self.p_birth=""
		self.p_age=""
		self.p_hight=""
		self.p_weight=""
		self.p_bsa=""
		
		#vital signs
		self.p_nbp_sys=0
		self.p_nbp_dias=0
		self.p_nbp_mean=0
		self.p_nbp_pulse=0
		self.p_nbp_time=["",""]
		
		self.p_spo2=0
		self.p_spo2_pulse=0
		
		self.p_ecg_pulse=0
		
		self.p_press_art=0
		self.p_temp=0
		
		self.p_timestamp=0.0
		
		#client time, not used
		self.p_pollingtime=""
		
		
		
		#time base
		self.monitor_rel_time=0.0
		self.monitor_abs_time=["",""]
		
		#handle management
		self.vital_timestamps=[]
		self.nbp_handle=""
		
		#poll type
		self.metric_demographic=2
	
	def __del__(self):
		self.halt_client()
	
	def start_client(self):
		self.run_loop=True
		#process = multiprocessing.Process(target=do_events, args=(self,)) 
		#self.process = multiprocessing.Process(target=self.do_events) 
		self.process = threading.Thread(target=self.do_events) 
		self.process.start() 
	
	def start_watchdog(self):
		self.run_con_watchdog=True
		#self.watchdog_thread = multiprocessing.Process(target=self.con_watchdog)
		self.watchdog_thread = threading.Thread(target=self.con_watchdog)
		self.watchdog_thread.start()
	
	def con_watchdog(self):
		#mainloop should be running
		while(self.run_con_watchdog==True):
			#check if it has ended prematurely
			if(self.check_client_is_working_correctly==False):
				# wait 5 sec
				time.sleep(5)
				# check again
				if(self.check_client_is_working_correctly==False):
					self.run_loop=False
					time.sleep(30)
					if(self.process.is_alive()==False):
						self.start_client()
					else:
						#self.process.terminate()
						time.sleep(30)
						self.start_client()
			time.sleep(5)
	
	def check_client_is_working_correctly(self):
		#returns false if client does not work
		if (self.is_active==self.run_loop):
			return True
		else:
			return False
	
	def halt_client(self):
		self.run_con_watchdog=False
		self.run_loop=False
	
	def debug_p(self):
		print(self.p_name)
	
	def refresh_patient_data(self):
		self.metric_demographic=2
	
	def get_patient_data(self):
		ret_val=[]
		
		# patient data
		ret_val.append(["ID", self.p_id])
		ret_val.append(["prename", self.p_pre_name])
		ret_val.append(["name", self.p_name])
		ret_val.append(["gender", self.p_gender])
		ret_val.append(["birth", self.p_birth])
		ret_val.append(["age", self.p_age])
		ret_val.append(["hight", self.p_hight])
		ret_val.append(["weight", self.p_weight])
		ret_val.append(["bsa", self.p_bsa])
		
		return ret_val
	
	def get_vital_signs(self):
		ret_val=[]
		#vital signs
		ret_val.append(["NBP_sys", self.p_nbp_sys])
		ret_val.append(["NBP_dias", self.p_nbp_dias])
		ret_val.append(["NBP_mean", self.p_nbp_mean])
		ret_val.append(["NBP_pulse", self.p_nbp_pulse])
		
		if(self.p_nbp_time[0]!="")and(self.p_nbp_time[1]!=""):
			temp_time=datetime.datetime.strptime(str(self.p_nbp_time[0]) + " " + str(self.p_nbp_time[1]),'%d.%m.%Y %H:%M:%S')
		else:
			temp_time=datetime.datetime.strptime("01.01.1990 00:00:00",'%d.%m.%Y %H:%M:%S')
		
		ret_val.append(["NBP_time", temp_time])
		
		ret_val.append(["SPO2", self.p_spo2])
		ret_val.append(["SPO2_pulse", self.p_spo2_pulse])
		
		ret_val.append(["ECG_pulse", self.p_ecg_pulse])
		
		ret_val.append(["Time rel. since connection start: measurement", self.p_timestamp])
		ret_val.append(["Time rel. since power-on to connection start", self.monitor_rel_time])
		
		if(self.monitor_abs_time[0]!="")and(self.monitor_abs_time[1]!=""):
			temp_time=datetime.datetime.strptime(str(self.monitor_abs_time[0]) + " " + str(self.monitor_abs_time[1]),'%d.%m.%Y %H:%M:%S')
		else:
			temp_time=datetime.datetime.strptime("01.01.1990 00:00:00",'%d.%m.%Y %H:%M:%S')
		
		ret_val.append(["Connection start: time", temp_time])
		
		#ret_val.append(["ART_press", self.p_press_art])
		#ret_val.append(["Temp", self.p_temp])
		
		return ret_val
		
	# Requests
	def create_release_request(self):
		release_request=bytearray(b'\x09\x18\xC1\x16\x61\x80\x30\x80\x02\x01\x01\xA0\x80\x62\x80\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		return release_request
	
	def create_assoc_request(self):
		#default Association request
		b=bytearray(b'\x0d\xff\x01\x28\x05\x08\x13\x01\x00\x16\x01\x02\x80\x00\x14\x02\x00\x02\xc1\xff\x01\x16\x31\x80\xa0\x80\x80\x01\x01\x00\x00\xa2\x80\xa0\x03\x00\x00\x01\xa4\x80\x30\x80\x02\x01\x01\x06\x04\x52\x01\x00\x01\x30\x80\x06\x02\x51\x01\x00\x00\x00\x00\x30\x80\x02\x01\x02\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x30\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x61\x80\x30\x80\x02\x01\x01\xa0\x80\x60\x80\xa1\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x03\x01\x00\x00\xbe\x80\x28\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x02\x01\x02\x81\x82\x00\x80\x80\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x64\x00\x01\x00\x28\x80\x00\x00\x00\x00\x00\x0f\xa0\x00\x00\x05\xb0\x00\x00\x05\xb0\xff\xff\xff\xff\x60\x00\x00\x00\x00\x01\x00\x0c\xf0\x01\x00\x08\x8e\x00\x00\x00\x00\x00\x00\x00\x01\x02\x00\x34\x00\x06\x00\x30\x00\x01\x00\x21\x00\x00\x00\x01\x00\x01\x00\x06\x00\x00\x00\xc9\x00\x01\x00\x09\x00\x00\x00\x3c\x00\x01\x00\x05\x00\x00\x00\x10\x00\x01\x00\x2a\x00\x00\x00\x01\x00\x01\x00\x36\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		#alternativ 4e
		#b=bytearray(b'\x0d\xff\x01\x28\x05\x08\x13\x01\x00\x16\x01\x02\x80\x00\x14\x02\x00\x02\xc1\xff\x01\x16\x31\x80\xa0\x80\x80\x01\x01\x00\x00\xa2\x80\xa0\x03\x00\x00\x01\xa4\x80\x30\x80\x02\x01\x01\x06\x04\x52\x01\x00\x01\x30\x80\x06\x02\x51\x01\x00\x00\x00\x00\x30\x80\x02\x01\x02\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x30\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x61\x80\x30\x80\x02\x01\x01\xa0\x80\x60\x80\xa1\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x03\x01\x00\x00\xbe\x80\x28\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x02\x01\x02\x81\x82\x00\x80\x80\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x64\x00\x01\x00\x28\x80\x00\x00\x00\x00\x00\x0f\xa0\x00\x00\x05\xb0\x00\x00\x05\xb0\xff\xff\xff\xff\x60\x00\x00\x00\x00\x01\x00\x0c\xf0\x01\x00\x08\x4e\x00\x00\x00\x00\x00\x00\x00\x01\x02\x00\x34\x00\x06\x00\x30\x00\x01\x00\x21\x00\x00\x00\x01\x00\x01\x00\x06\x00\x00\x00\xc9\x00\x01\x00\x09\x00\x00\x00\x3c\x00\x01\x00\x05\x00\x00\x00\x10\x00\x01\x00\x2a\x00\x00\x00\x01\x00\x01\x00\x36\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		#alternativ 40
		#b=bytearray(b'\x0d\xff\x01\x28\x05\x08\x13\x01\x00\x16\x01\x02\x80\x00\x14\x02\x00\x02\xc1\xff\x01\x16\x31\x80\xa0\x80\x80\x01\x01\x00\x00\xa2\x80\xa0\x03\x00\x00\x01\xa4\x80\x30\x80\x02\x01\x01\x06\x04\x52\x01\x00\x01\x30\x80\x06\x02\x51\x01\x00\x00\x00\x00\x30\x80\x02\x01\x02\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x30\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x61\x80\x30\x80\x02\x01\x01\xa0\x80\x60\x80\xa1\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x03\x01\x00\x00\xbe\x80\x28\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x02\x01\x02\x81\x82\x00\x80\x80\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x64\x00\x01\x00\x28\x80\x00\x00\x00\x00\x00\x0f\xa0\x00\x00\x05\xb0\x00\x00\x05\xb0\xff\xff\xff\xff\x60\x00\x00\x00\x00\x01\x00\x0c\xf0\x01\x00\x08\x40\x00\x00\x00\x00\x00\x00\x00\x01\x02\x00\x34\x00\x06\x00\x30\x00\x01\x00\x21\x00\x00\x00\x01\x00\x01\x00\x06\x00\x00\x00\xc9\x00\x01\x00\x09\x00\x00\x00\x3c\x00\x01\x00\x05\x00\x00\x00\x10\x00\x01\x00\x2a\x00\x00\x00\x01\x00\x01\x00\x36\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
	
		return b
	
	def check_assoc_response(self, b):
		n=0
		if b[:1]==bytearray(b'\x0E'):
			n=1
			
		return n
	
	def check_MDS_event(self, b):
		n=0
		if b[:6]==bytearray(b'\xe1\x00\x00\x02\x00\x01'):
			n=1
			#get time since last assoc
			#self.assoc_rel_time=self.decode_rel_time(b[20:20+4])
			#get base time
			self.get_basetime_from_MDS_attr_lst(b[34:])
		return n
	
	def create_MDS_result_from_MDS_event(self, b):
		#extract relative_time
		d_l=list(struct.unpack('!I',b[20:24]))
		#increase relative_time
		e_time=struct.pack('!I',d_l[0]+50)
		#Construct MDS_result bytearray:
		#Session_id
		mds_result=b[:4]
		#head
		mds_result=mds_result+bytearray(b'\x00\x02\x00\x14')
		mds_result=mds_result+bytearray(b'\x00\x01\x00\x01\x00\x0e')
		mds_result=mds_result+bytearray(b'\x00\x21\x00\x00\x00\x00')
		#insert new timestamp
		mds_result=mds_result+e_time
		#Flags
		mds_result=mds_result+bytearray(b'\x0d\x06\x00\x00')
		return mds_result
	
	def single_poll_request(self, sid, n, nr, p_count):
		
		spr=bytearray()
		#session_id
		spr=spr+sid
		#head
		spr=spr+bytearray(b'\x00\x01\x00\x20')
		spr=spr+bytearray(b'\x00\x01\x00\x07\x00\x1a')
		spr=spr+bytearray(b'\x00\x21\x00\x00\x00\x00\x00\x00')
		#singe poll (1) or extended poll (2)
		if nr==1:
			spr=spr+bytearray(b'\x00\x00\x0C\x16')
		else:
			spr=spr+bytearray(b'\x00\x00\xf1\x3b')
		#length
		spr=spr+bytearray(b'\x00\x0C')
		#poll data request
		#poll number>counter
		spr=spr+struct.pack('!H', p_count)
		spr=spr+bytearray(b'\x00\x01')
		#metrics (1) or demogrphics (2)
		if n==1:
			spr=spr+bytearray(b'\x00\x06')
		else:
			spr=spr+bytearray(b'\x00\x2A')
		spr=spr+bytearray(b'\x00\x00')
		#from packet sniffing >> empiric appendix 00 00 00 00
		spr=spr+bytearray(b'\x00\x00\x00\x00')
		return spr
	
	def decode_float(self, b):
		#print(b)
		flo=0.00
		exponent=list(struct.unpack('!b', bytearray(b[:1])))[0]
		#print(exponent)
		if (b[1]>>7)==0:
			#print(">0")
			tempb=bytearray(b'\x00')
			tempb=tempb+b[1:4]
			#print(tempb)
			mantissa=list(struct.unpack('!i', tempb))[0]
		else:
			#print(">1")
			#pad to 32 bit with '10000000'
			b1=bytearray(b'\x80')
			b1=b1+b[1:4]
			#convert to int
			j=list(struct.unpack('!i', b1))[0]
			#create mask for old msb  > set it to 0
			c1=bytearray(b'\x00\x80\x00\x00')
			#convert to int
			k=list(struct.unpack('!i', c1))[0]
			#invert mask
			k=~k
			# bitwise and
			l=j&k
			#mantissa=l
			mantissa=l
			#convert back to bytearray
			#tempb=struct.pack('!i', l)
			#calculate mantissa
			#mantissa=list(struct.unpack('!i', tempb))[0]
		#print(mantissa)
		
		r_exp=(10**exponent)
		#print(r_exp)
		flo=mantissa*r_exp
		#print(flo)
		return flo
	
	def extract_physoi_id(self, p_id, observ_val, handle_id):
		#handel management for assigning timestamps to measurements
		#self.nbp_handle
		
		# art press sys: 18961 dia:18962 mean:18963
		#temp: 19272
		#bis: 61518
		
		#NBP
		if p_id==18949:
			self.p_nbp_sys=observ_val
			self.nbp_handle=handle_id
		if p_id==18950:
			self.p_nbp_dias=observ_val
		if p_id==18951:
			self.p_nbp_mean=observ_val
		if p_id==61669:
			self.p_nbp_pulse=observ_val
		#spo2
		if p_id==19384:
			self.p_spo2=observ_val
		if p_id==18466:
			self.p_spo2_pulse=observ_val
		#ecg
		if p_id==16770:
			self.p_ecg_pulse=observ_val
		#art_press (or 18967 ???)
		if p_id==18963:
			self.p_press_art=observ_val
		#temp
		if p_id==19272:
			self.p_temp=observ_val
	
	def check_id(self, objid, b, handle_id=0):
		#handel management for assigning timestamps to measurements
		# self.vital_timestamps
		
		#Patient data
		
		#id
		if objid==2394:
			self.p_id=b[2:].decode("utf-8")
		#gender
		if objid==2401:
			if list(struct.unpack('!H', b))[0]==1:
				self.p_gender="maennlich"
			elif list(struct.unpack('!H', b))[0]==2:
				self.p_gender="weiblich"
			else:
				self.p_gender="?"
		#birth
		if objid==2392:
			self.p_birth=self.decode_absolut_time(b)[0]
		
		#prename
		if objid==2397:
			self.p_pre_name=b[2:].decode("utf-8")
		
		#name
		if objid==2396:
			self.p_name=b[2:].decode("utf-8")
			
		#height
		if objid==2524:
			self.p_hight=self.decode_float(b)
		#weight
		if objid==2527:
			self.p_weight=self.decode_float(b)
		#bsa
		if objid==2390:
			self.p_bsa=self.decode_float(b)
		
		#age
		if objid==2520:
			self.p_age=self.decode_float(b)
		
		#=============================================================
		#check vital signs
	
		#label string
		if objid==2343:
			pass
		#observation
		if objid==2384:
			val_fl=self.decode_float(b[6:10])
			self.extract_physoi_id(list(struct.unpack('!H',b[:2]))[0], val_fl, handle_id)
		#compound observation
		if objid==2379:
			comp_count=list(struct.unpack('!H',b[:2]))[0]
			comp_len=list(struct.unpack('!H',b[2:4]))[0]
			comp_data=b[4:]
			n_comp=1
			while n_comp <= comp_count:
				val_fl=self.decode_float(comp_data[6:10])
				self.extract_physoi_id(list(struct.unpack('!H',comp_data[:2]))[0], val_fl, handle_id)
				comp_data=comp_data[10:]
				n_comp=n_comp+1
		#timestamp absolute
		if objid==2448:
			a_tm=self.decode_absolut_time(b)
			a_tm.append(handle_id)
			self.vital_timestamps.append(a_tm)
		#timestamp relative
		if objid==2447:
			rel_tm=self.decode_rel_time(b)
		
		#id
		if objid==2337:
			pass
		#id type
		if objid==2351:
			pass
	
	def decode_rel_time(self, b):
		rel_tm=list(struct.unpack('!I',b[:4]))[0]
		rel_tm_fl=float(rel_tm)*0.000125
		#print(rel_tm_fl)
		return rel_tm
	
	def decode_absolut_time(self, b):
		abs_tm=[]
		#date
		time_res=""
		time_res=time_res+str(b[3]>>4)
		time_res=time_res+str(b[3]&0x0f)
		time_res=time_res+"."
		time_res=time_res+str(b[2]>>4)
		time_res=time_res+str(b[2]&0x0f)
		time_res=time_res+"."
		time_res=time_res+str(b[0]>>4)
		time_res=time_res+str(b[0]&0x0f)
		time_res=time_res+str(b[1]>>4)
		time_res=time_res+str(b[1]&0x0f)
		abs_tm.append(time_res)
		#time
		time_res=""
		time_res=time_res+str(b[4]>>4)
		time_res=time_res+str(b[4]&0x0f)
		time_res=time_res+":"
		time_res=time_res+str(b[5]>>4)
		time_res=time_res+str(b[5]&0x0f)
		time_res=time_res+":"
		time_res=time_res+str(b[6]>>4)
		time_res=time_res+str(b[6]&0x0f)
		abs_tm.append(time_res)
		return abs_tm
	
	def get_basetime_from_MDS_attr_lst(self, b):
		l_count=list(struct.unpack('!H',b[:2]))[0]
		l_length=list(struct.unpack('!H',b[2:4]))[0]
		#print(l_count)
		#print(l_length)
		c=b[4:]
		c_c=1
		while c_c<=l_count:
			type_id=list(struct.unpack('!H',c[:2]))[0]
			type_length=list(struct.unpack('!H',c[2:4]))[0]
			#extracting base time from MDS_event
			if type_id==2447:
				#self.monitor_rel_time=self.decode_rel_time(c[4:4+type_length])
				self.monitor_rel_time=self.decode_rel_time(c[4:4+type_length])
			if type_id==2439:
				self.monitor_abs_time=self.decode_absolut_time(c[4:4+type_length])
			#reduce lenght of C
			c=c[4+type_length:]
			c_c=c_c+1
		#print(self.monitor_rel_time)
		#print(self.monitor_abs_time)
	
	def poll_single_parse(self, b):
		self.vital_timestamps=[]
		self.nbp_handle=""
		
		#rel_timestamp
		#print(b[28:28+4+8])
		temp_rel_t=self.decode_rel_time(b[28:28+4])
		#sanity check
		if(temp_rel_t >= self.monitor_rel_time):
			self.p_timestamp=temp_rel_t
		#print(self.p_timestamp)
		
		#parse list info
		l_count=list(struct.unpack('!H',b[46:48]))[0]
		l_length=list(struct.unpack('!H',b[48:50]))[0]
		#print(l_count)
		#print(l_length)
		#check length of dataset
		if (l_length != len(b[50:])):
			if self.debug_error:
				print("[Err] >> Wrong length of singel poll data!")
			return
		c=b[50:]
		#first recursion for poll list info (57)
		c_c=1
		while c_c<=l_count:
			#ignore context id (2 Byte)
			#print(c[:2]) # context id = 0
			con_count=list(struct.unpack('!H',c[2:4]))[0]
			con_length=list(struct.unpack('!H',c[4:6]))[0]
			#print(">")
			#print(con_count)
			#print(con_length)
			d=c[6:]
			#second recursion for single contxt poll (57)
			c_d=1
			while c_d<=con_count:
				#handel could be ignored???
				observ_handle=list(struct.unpack('!H',d[:2]))[0]
				#print (">>")
				#print ("handle:")
				#print(observ_handle)
				
				#Flag for handeling NBP timestamp
				timestamp_present=False
				nbp_present=False
				
				attr_count=list(struct.unpack('!H',d[2:4]))[0]
				attr_lenght=list(struct.unpack('!H',d[4:6]))[0]
				#print(attr_count)
				#print(attr_lenght)
				e=d[6:]
				#third recursion >> attr_lst
				c_e=1
				while c_e<=attr_count:
					type_id=list(struct.unpack('!H',e[:2]))[0]
					type_length=list(struct.unpack('!H',e[2:4]))[0]
					#print(">>>")
					#print("id: "+str(type_id))
					#print("length: "+str(type_length))
					#print("__________")
					self.check_id(type_id, e[4:4+type_length], observ_handle)
					
					#reduce lenght of E
					e=e[4+type_length:]
					c_e=c_e+1
				
				#reduce lenght of D
				d=d[6+attr_lenght:]
				c_d=c_d+1
				
			#reduce lenght  of C 
			c=c[6+con_length:]
			c_c=c_c+1
			
			#combine timestamps and values
			
			#print(self.vital_timestamps)
			#print("===========================================")
			self.combine_timestamps_and_values()
	
	def combine_timestamps_and_values(self):
		for n in self.vital_timestamps:
			#print(self.vital_timestamps)
			if n[2]==self.nbp_handle:
				self.p_nbp_time=[n[0],n[1]]
				break
	
	def linked_poll_single_parse(self, b):
		c=b[2:]
		return self.poll_single_parse(c)
	
	def extract_linked_data_parameters(self, b):
		temp_lr_lst=[]
		temp_package_cat=list(struct.unpack('!H',b[4:6]))[0]
		temp_package_pos=0
		temp_package_nr=0
		# if linked package > get number and pos
		if(temp_package_cat==5):
			temp_package_pos=list(struct.unpack('!B',b[8:9]))[0]
			temp_package_nr=list(struct.unpack('!B',b[9:10]))[0]
		temp_lr_lst.append(temp_package_nr)
		temp_lr_lst.append(temp_package_pos)
		temp_lr_lst.append(temp_package_cat)
		temp_lr_lst.append(b)
		return temp_lr_lst
	
	def sort_linked_data_list_and_remove_doubles(self, b):
		temp_lst=[]
		for n_1 in b:
			exist_in_temp_lst=False
			for n_2 in temp_lst:
				if (n_1[0]==n_2[0]):
					exist_in_temp_lst=True
					break
			if exist_in_temp_lst==False:
				temp_lst.append(n_1)
			
		ret_l=sorted(temp_lst, key=lambda x: x[0], reverse=False)
		
		return ret_l
	
	def linked_data_parse(self, b):
		for n in b:
			#get final remote operation message
			if(n[2]==2):
				#check if empty
				if len(n[3])<=50:
					#print(">>>> final remote operation message was empty >> continue")
					continue
				#if not empty pars message
				else:
					self.poll_single_parse(n[3])
			#parse all other messages
			else:
				self.linked_poll_single_parse(n[3])
	
	def do_events(self):
		
		self.is_active=True
		
		#Variables/Flags
		
		#request parameters 
		self.metric_demographic=2
		single_extended=2
		
		# poll counter
		pollcount=1
		# interval
		poll_interval=4
		
		#================================
		# Create UDP-socket
		#================================
		
		#host side
		host = ""
		port = 0
		host_addr = (host, port)
		
		#server side
		s_addr = self.ip
		s_port = 24105
		server_addr = (s_addr, s_port)
				
		#create UDP socket
		UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		bufsize = 8192  # 8 kByte
		
		# bind socket to host port
		try:
			UDPSock.bind(host_addr)
		except:
			if self.debug_error:
				print("[Err] >> Network-address in use!")
			self.is_active=False
			return -1
		
		# set socket timeout
		UDPSock.settimeout(15.0)
		
		#================================
		# Start connecting proc.
		#================================
		
		#send Assoc_request
		
		try:
			UDPSock.sendto(self.create_assoc_request(), (server_addr))
			if self.debug_info:
				print("[OK] send: Assoc_request")
		except:
			if self.debug_error:
				print("[Err] >> Could not send Assoc_request!")
			self.is_active=False
			return -1
		
		
		#receive Assoc_result
		try:
			(data, addr) = UDPSock.recvfrom(bufsize)
			if self.debug_info:
				print("[OK] receive: Assoc_result")
		except:
			if self.debug_error:
				print("[Err] >> Did not receive Assoc_result!")
			self.is_active=False
			return -1
		
		
		#check Assoc_result
		if self.check_assoc_response(data)==1:
			if self.debug_info:
				print("[OK] rec: assoc_result")
		else:
			if self.debug_error:
				print("[Err] >> Faulty assoc_result!")
			self.is_active=False
			return -1
		
		#receive MDS_event
		try:
			(data, addr) = UDPSock.recvfrom(bufsize)
			if self.debug_info:
				print("[OK] rec: MDS_event")
		except:
			if self.debug_error:
				print("[Err] >> Did not receive MDS_event!")
			self.is_active=False
			return -1
		
		
		#parse session id
		sessid=data[:4]
		
		#check MDS event
		if self.check_MDS_event(data)==1:
			if self.debug_info:
				print("[OK] rec: MDS_event")
		else:
			if self.debug_error:
				print(">>Faulty MDS_event!")
			self.is_active=False
			return -1
		
		#send MDS_result
		try:
			UDPSock.sendto(self.create_MDS_result_from_MDS_event(data), (server_addr))
			if self.debug_info:
				print("[OK] send: MDS_result")
		except:
			if self.debug_error:
				print("[Err] >> Could not send MDS_result!")
			self.is_active=False
			return -1
		
		
		
		#================================
		# Mainloop 
		#================================
		
		try:
			while self.run_loop==True:
				#self.p_name=self.p_name+"a"
				#send poll_request
				try:
					UDPSock.sendto(self.single_poll_request(sessid, self.metric_demographic, single_extended, pollcount), (server_addr))
					if self.debug_info:
						print("[OK] send: poll_request")
				except:
					if self.debug_error:
						print("[Err] >> Could not send poll_request!")
					self.is_active=False
					return -1
				
				#receive poll_result
				try:
					(data, addr) = UDPSock.recvfrom(bufsize)
					if self.debug_info:
						print("[OK] rec: poll_result")
				except:
					if self.debug_error:
						print("[Err] >> Did not receive poll_result!")
					self.is_active=False
					return -1
				
				#parse poll result
				
				#single result
				if data[5:6]==bytearray(b'\x02'):
					if self.debug_info:
						print("[OK] >>single result")
					self.poll_single_parse(data)
					#print(data)
				#fail
				if data[5:6]==bytearray(b'\x03'):
					if self.debug_info:
						print("[Err] >>Failed poll!!!!!")
				#linked result
				if data[5:6]==bytearray(b'\x05'):
					if self.debug_info:
						print("[OK] >>linked data")
					#receive all packages of linked result
					UDPSock.settimeout(2.0)
					linked_package_number=1
					data_lst=[]
					data_lst.append(self.extract_linked_data_parameters(data))
					while True:
						try:
							(data_linked, addr) = UDPSock.recvfrom(bufsize)
							data_lst.append(self.extract_linked_data_parameters(data_linked))
							linked_package_number=linked_package_number+1
							
						#except UDPSock.timeout:
						except:
							UDPSock.settimeout(15.0)
							self.linked_data_parse(self.sort_linked_data_list_and_remove_doubles(data_lst))
							now=datetime.datetime.now()
							self.p_pollingtime=now.strftime("%H:%M:%S %d.%m.%Y")
							break
				# increment counter
				pollcount=pollcount+1
				#change to metric poll
				self.metric_demographic=1
				#sleep (4s)> intervall of polling
				time.sleep(poll_interval)
			
			#===============================
			#End Main-loop; close connection
			#===============================
			if self.debug_info:
				print(">> closing connection...")
			UDPSock.sendto(self.create_release_request(), (server_addr))
				#send close_request
			try:
				(data, addr) = UDPSock.recvfrom(bufsize)
				if data[:2]==bytearray(b'\x0A\x18'):
					if self.debug_info:
						print("[OK]...closed!")
				else:
					if self.debug_error:
						print("[Err] >> No regular closing response!")
			except:
				if self.debug_error:
					print("[Err] >> Did not receive close response!")
			
			UDPSock.close()
			if self.debug_info:
				print("[exit]...<OK>")
			self.is_active=False
			return 0
		
		except Exception as e: 
			#print(e)
			if self.debug_error:
				print("[Err] >> connection error...")
			UDPSock.sendto(self.create_release_request(), (server_addr))
			#send close_request
			try:
				(data, addr) = UDPSock.recvfrom(bufsize)
				if data[:2]==bytearray(b'\x0A\x18'):
					if self.debug_info:
						print("[OK]...closed!")
				else:
					if self.debug_error:
						print("[Err] >> No regular closing response!")
			except:
				if self.debug_error:
					print("[Err] >> Did not receive close response!")
			
			UDPSock.close()
			if self.debug_info:
				print("[exit]...<OK>")
			self.is_active=False
			return -1

