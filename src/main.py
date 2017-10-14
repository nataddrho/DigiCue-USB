#!/usr/bin/env python

#Nathan Rhoades 10/13/2017

import serial, serialport, bgapi, gui, digicueblue, traceback
import time, threading, sys

if sys.version_info[0]<3:
	import Tkinter as Tk
else:
	import tkinter as Tk

class App(threading.Thread): #thread GUI to that BGAPI can run in background

	def __init__(self,dcb):
		self.dcb = dcb
		threading.Thread.__init__(self)
		self.start()
		
	def callback(self):
		self.root.quit()
		
	def run(self):
		self.root = Tk.Tk()
		self.gui = gui.GUI(self.root, self.dcb)
		self.root.mainloop()

def main():

	try:
		f = open("comport.cfg","r")
		comport = f.readline().strip(' ')
		f.close()		
	except:
		#open comport selection gui
		serialport.launch_selection()
		return	
	try:		
		#open serial port and launch application
		print "Opening %s"%comport
		ser = serial.Serial(comport,115200,timeout=1,writeTimeout=1)		
		dcb = digicueblue.DigicueBlue(filename="data.csv",debugprint=False)
		app = App(dcb)
		bg = bgapi.Bluegiga(dcb,ser,debugprint=True)		
	except:		
		print traceback.format_exc()
		try:
			ser.close()
		except:
			pass
		text = """Please make sure the BLED112 dongle is plugged into the COM port
		specified in comport.cfg, and that no other programs are using the port.
		Use the serialport GUI to help select the correct port."""
		text = text.replace('\n',' ')		
		text = text.replace('\t','')
		print text
		serialport.launch_selection()
		
		
if __name__ == '__main__':
	main()