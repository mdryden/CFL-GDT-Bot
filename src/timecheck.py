# does all the time checking

import urllib2
import time
from datetime import datetime
import simplejson as json
from dateutil import parser
from dateutil.tz import *

class TimeCheck:

	def __init__(self,time_before):
		self.time_before = time_before
		self.currentday = datetime.today()

	def gametoday(self,game):
		gameStart = parser.parse(game.get('date_start'))
		#print "today: " + str(today.date()) + ", gameStart: " + str(gameStart.date())
		#use current day so we can avoid relooping over the same completed games.
		return datetime.today().date() == gameStart.date()

	def ready(self,game):
	
		#if game.get("game_id") == 2302:
		#	return True
	
		if game.get("event_status").get("name") == "Final":
			return False
		else:
			date_object = parser.parse(game.get('date_start'))
			
			check = datetime.now(tzutc())
			diff = date_object - check
			seconds = (diff.days * 24 * 60 * 60) + diff.seconds
			
			#print "Game start: " + str(date_object)
			#print "Seconds from now: " + str(seconds)
			#print "Time before: " + str(self.time_before)
			
			return seconds <= self.time_before

	def ppcheck(self,game):
		return False

