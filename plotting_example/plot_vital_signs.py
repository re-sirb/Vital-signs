#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
from time import sleep
from  ipv_data_source import ipv_data_source as device

class plot_vital_signs:
	
	def __init__(self, duration=60, init_timestamp_poll="00:00:00"):
		
		plt.axis([0, duration, 0, 200])
		plt.xlabel('minutes')
		plt.yticks(np.arange(0, 201, step=20))
		plt.xticks(np.arange(0, duration+1, step=5))
		plt.grid()
		
		
		green_patch = mpatches.Patch(color='#3ddc01', label='Heart rate')
		blue_patch = mpatches.Patch(color='#006eca', label='Oxygen saturation')
		red_patch = mpatches.Patch(color='red', label='Blood pressure')
		plt.legend(handles=[green_patch, blue_patch, red_patch])
		
		self.last_pl=0
		self.last_sa=0
		self.last_tm_pl=0
		self.last_tm_sa=0
		self.start_plot_pl=True
		self.start_plot_sa=True
		
	
	def plot_new_values(self, time_stamp, RRsys=0, RRdias=0, Pulse=0, SaO2=0):
		if(((RRsys > 0)and(RRdias > 0))and((RRsys < 300)and(RRdias < 300))):
			plt.plot([time_stamp], [RRsys], 'rv', [time_stamp], [RRdias], 'r^')
			plt.plot([time_stamp,time_stamp], [RRsys,RRdias], color='r', linewidth=1)
		if((Pulse > 0)and(Pulse < 300)):
			if(self.start_plot_pl==True):
				self.last_pl=Pulse
				self.start_plot_pl=False
			plt.plot([self.last_tm_pl, time_stamp], [self.last_pl, Pulse], color='#3ddc01', marker='.', linewidth=1)
			self.last_pl=Pulse
			self.last_tm_pl=time_stamp
		if((SaO2 > 0)and(SaO2 < 150)):
			if(self.start_plot_sa==True):
				self.last_sa=SaO2
				self.start_plot_sa=False
			plt.plot([self.last_tm_sa, time_stamp], [self.last_sa, SaO2], color='#006eca', linewidth=1)
			self.last_sa=SaO2
			self.last_tm_sa=time_stamp
		#plt.text(30, 1, "txt", color='blue', fontsize=8)
		

#timescale of plot in min
duration=30

#insert correct monitor IP here
dev_1 = device("192.168.2.117")

plot_v = plot_vital_signs(duration)

dev_1.start_client()

dev_1.start_watchdog()

last_vital_time=0
last_NBP_time=datetime.strptime("01.01.1990 00:00:00",'%d.%m.%Y %H:%M:%S')


try:
	while True:
		#get new patient data
		temp_l=dev_1.get_vital_signs()
		###########################################
		#RR/SaO2
		#get time in minutes since connection started
		diff_time=((temp_l[8][1]*0.000125)/60)-((temp_l[9][1]*0.000125)/60)
		#if new data is available: plot data
		if(diff_time!=last_vital_time):
			plot_v.plot_new_values(diff_time, SaO2=float(temp_l[5][1]), Pulse=float(temp_l[6][1]))
			last_vital_time=diff_time
		##########################################
		#NBP
		#get times
		v=temp_l[4][1]
		w=temp_l[10][1]
		#if time in minutes since connection started >0 and new data is available: plot data
		if(((v-w).total_seconds()>0)and(last_NBP_time!=v)):
			calc_time=(float((v-w).total_seconds())/60)
			plot_v.plot_new_values(calc_time, RRsys=float(temp_l[0][1]), RRdias=float(temp_l[1][1]))
			last_NBP_time=v
		plt.pause(2)
		#plt.show()
#except (KeyboardInterrupt, SystemExit):
#	raise
except:
	dev_1.halt_client()
	print("\client halted...\n")
	plt.close()
	print("exit...[OK]")
