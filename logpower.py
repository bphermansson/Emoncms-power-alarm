#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
This scrips asks an Emoncms server for an energy value. If the value is high, ie if the monitored device
draws power, a notice is sent to a Smartphone.
The monitored device in this case is a washing maching, and actions are taken to just send a notice 
when the machine is started and when the wash is done. A washer draws power irregularly, so counters are 
used to make sure not to send notifications when the washer is idle during the wash cycle. 
Notifications are sent via NMA, http://www.notifymyandroid.com.
To use this service, an account is needed. This account gives a developer key, which is stored in the file "mydeveloperkey".

git add README.md
git commit -a

"""
import urllib2
import time
import logging
from pynma import PyNMA
from pprint import pprint
import os
import sys
# To load config file
import ConfigParser

p = None
global emonapi

def do_read_settings():
	# Load & read configuration
	# Settings are stored in a file called "settings".
	# Example:
	# [emoncms]
	# api=<api key from http://www.notifymyandroid.com>
	
	global emonapi

	if not (os.path.isfile("settings.txt")):
		# No settings found, exit
		print ("No file with settings found, exiting")		
		sys.exit()
	config = ConfigParser.ConfigParser()
	try:
		print "Load settings"
		config.read("settings.txt")
	except:
		print "Settings file not found"
		sys.exit()
	print config.sections()
	
	try:
		emonapi = config.get("emoncms", "apikey")
		print ("Api key found, good")
	except:
		print "No api key found in settings, exit."
		sys.exit()

def main(keys):
	print ("In main(), loop")
	# Read settings
 	do_read_settings()

	# Setup logging
	logger = logging.getLogger('washpower')
	hdlr = logging.FileHandler('/var/tmp/washpower.log')
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	logger.setLevel(logging.INFO)
	logger.info('Start log')
	
	# Variables
	runs = 0
	running = 0
	notrunning = 0
	washerrunning = 0
	
	# Eternal loop
	while(1):
		# Get data from Emoncms
		# TODO Find a better way to get data (locally)
		# Get value from Emoncms
		#response = urllib2.urlopen('http://192.168.1.6/emoncms/feed/value.json?id=23&apikey=1b3bdd0f474738012cb85b79f1b7e104')
		response = urllib2.urlopen('http://192.168.1.6/emoncms/feed/value.json?id=23&apikey='+emonapi)
		
		html = response.read()
		power = ''.join(e for e in html if e.isalnum())
		ipower=int(power)
		
		print ("Current power: " + power)
		#logger.info(power)
		#logtext = "running: " + str(running) + "---notrunning: " + str(notrunning)
		#logger.info(logtext)
		# For debug, read "power" from a local file
		#f = open('test', 'r')
		#power = int(f.read())
		#print str(power)
		
		# Power is higher than idle current? (Which in this case is 11)
		if ipower > 30:
			running+=1
			notrunning=0
			#print "running:"+str(running)
			
			if (running >= 3 and washerrunning == 0):
				# The power is high for three runs in a row
				logger.info("Washer is running")
				print "Washer is running"
				
				# Send NMA
				global p
				pkey = None
				p = PyNMA()
				if os.path.isfile("mydeveloperkey"):
					dkey = open("mydeveloperkey",'r').readline().strip()
					p.developerkey(dkey)
				p.addkey(keys)
				res = p.push("Emoncms alarm", 'Washer', 'Washer is running', '', batch_mode=False)
				pprint(res)
				washerrunning = 1
		else: 
			#print "Washer idle"
			if (washerrunning == 1):
				# Washer has been running but power is below limit
				notrunning+=1
				if (notrunning >=6):
					# Power has been below limit for three runs
					# so the washer is done
					washerrunning = 0
					# Reset running counter
					running = 0
					logger.info("Washer is done")
					print "Washer is done"
					# Send NMA
					#global p
					pkey = None
					p = PyNMA()
					if os.path.isfile("mydeveloperkey"):
						dkey = open("mydeveloperkey",'r').readline().strip()
						p.developerkey(dkey)
					p.addkey(keys)
					res = p.push("Emoncms alarm", 'Washer', 'Washer is done', '', batch_mode=False)
					pprint(res)
		#else:
			# Power is down after it's been up
		#	if (washerrunning == 1):
		#		logger.info("Washer is done")
		#		print "Washer is done"

		# Wait 2 minutes
		time.sleep(120)
		# For debug
		#time.sleep(3)

if __name__ == "__main__":
	if os.path.isfile('myapikey'):
		keys = [_f for _f in open("myapikey",'r').read().split("\n") if _f]
		print "Run main"
		main(keys)
	else:
		print("need a file named myapikey containing one apikey per line")


