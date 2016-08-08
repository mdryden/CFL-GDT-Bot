'''

CFL GAME THREAD BOT

Written by:
/u/pudds
/u/DetectiveWoofles
/u/avery_crudeman

Please contact us on Reddit or Github if you have any questions.

'''

import editor
from datetime import datetime
import timecheck
import time
import simplejson as json
import praw
import urllib2

class Bot:

	def __init__(self):
		self.YEAR = None
		self.BOT_TIME_ZONE = None
		self.TEAM_TIME_ZONE = None
		self.POST_TIME = None
		self.USERNAME = None
		self.PASSWORD = None
		self.SUBREDDIT = None
		self.TEAM_CODE = None
		self.PREGAME_THREAD = None
		self.POST_GAME_THREAD = None
		self.STICKY = None
		self.SUGGESTED_SORT = None
		self.MESSAGE = None
		self.PRE_THREAD_SETTINGS = None
		self.THREAD_SETTINGS = None
		self.POST_THREAD_SETTINGS = None
		self.API_KEY = None

	def read_settings(self):
		with open('settings.json') as data:
			settings = json.load(data)

			self.CLIENT_ID = settings.get('CLIENT_ID')
			if self.CLIENT_ID == None: return "Missing CLIENT_ID"

			self.CLIENT_SECRET = settings.get('CLIENT_SECRET')
			if self.CLIENT_SECRET == None: return "Missing CLIENT_SECRET"

			self.REDIRECT_URI = settings.get('REDIRECT_URI')
			if self.REDIRECT_URI == None: return "Missing REDIRECT_URI"

			self.REFRESH_TOKEN = settings.get('REFRESH_TOKEN')
			if self.REFRESH_TOKEN == None: return "Missing REFRESH_TOKEN"	 

			self.API_KEY = settings.get('API_KEY')
			if self.API_KEY == None: return "Missing API_KEY"

			self.YEAR = settings.get('YEAR')
			if self.YEAR == None: return "Missing YEAR"		   

			self.BOT_TIME_ZONE = settings.get('BOT_TIME_ZONE')
			if self.BOT_TIME_ZONE == None: return "Missing BOT_TIME_ZONE"

			self.TEAM_TIME_ZONE = settings.get('TEAM_TIME_ZONE')
			if self.TEAM_TIME_ZONE == None: return "Missing TEAM_TIME_ZONE"

			self.POST_TIME = settings.get('POST_TIME')
			if self.POST_TIME == None: return "Missing POST_TIME"

			self.SUBREDDIT = settings.get('SUBREDDIT')
			if self.SUBREDDIT == None: return "Missing SUBREDDIT"

			self.POST_GAME_THREAD = settings.get('POST_GAME_THREAD')
			if self.POST_GAME_THREAD == None: return "Missing POST_GAME_THREAD"

			self.STICKY = settings.get('STICKY')
			if self.STICKY == None: return "Missing STICKY"

			self.SUGGESTED_SORT = settings.get('SUGGESTED_SORT')
			if self.SUGGESTED_SORT == None: return "Missing SUGGESTED_SORT"

			self.MESSAGE = settings.get('MESSAGE')
			if self.MESSAGE == None: return "Missing MESSAGE"

			temp_settings = settings.get('THREAD_SETTINGS')
			content_settings = temp_settings.get('CONTENT')
			self.THREAD_SETTINGS = (temp_settings.get('THREAD_TAG'),
									(content_settings.get('HEADER'), content_settings.get('BOX_SCORE'),
									 content_settings.get('LINE_SCORE'), content_settings.get('SCORING_PLAYS'),
									 content_settings.get('HIGHLIGHTS'), content_settings.get('FOOTER'))
								 )
			if self.THREAD_SETTINGS == None: return "Missing THREAD_SETTINGS"

			temp_settings = settings.get('POST_THREAD_SETTINGS')
			content_settings = temp_settings.get('CONTENT')
			self.POST_THREAD_SETTINGS = (temp_settings.get('POST_THREAD_TAG'),
									(content_settings.get('HEADER'), content_settings.get('BOX_SCORE'),
									 content_settings.get('LINE_SCORE'), content_settings.get('SCORING_PLAYS'),
									 content_settings.get('HIGHLIGHTS'), content_settings.get('FOOTER'))
								 )
			if self.POST_THREAD_SETTINGS == None: return "Missing POST_THREAD_SETTINGS"

		return 0

	def run(self):

		error_msg = self.read_settings()

		if error_msg != 0:
			print error_msg
			return

		r = praw.Reddit('OAuth CFLBot V. 3.0.1'
						'https://github.com/pudds/CFL-GDT-Bot')
		r.set_oauth_app_info(client_id=self.CLIENT_ID,
							client_secret=self.CLIENT_SECRET,
							redirect_uri=self.REDIRECT_URI)		
		r.refresh_access_information(self.REFRESH_TOKEN)		

		if self.TEAM_TIME_ZONE == 'ET':
			time_info = (self.TEAM_TIME_ZONE,0)
		elif self.TEAM_TIME_ZONE == 'CT':
			time_info = (self.TEAM_TIME_ZONE,1)
		elif self.TEAM_TIME_ZONE == 'MT':
			time_info = (self.TEAM_TIME_ZONE,2)
		elif self.TEAM_TIME_ZONE == 'PT':
			time_info = (self.TEAM_TIME_ZONE,3)
		else:
			print "Invalid time zone settings."
			return

		edit = editor.Editor(time_info, self.THREAD_SETTINGS, self.POST_THREAD_SETTINGS, self.YEAR, self.API_KEY)

		if self.BOT_TIME_ZONE == 'ET':
			time_before = self.POST_TIME * 60 * 60
		elif self.BOT_TIME_ZONE == 'CT':
			time_before = (1 + self.POST_TIME) * 60 * 60
		elif self.BOT_TIME_ZONE == 'MT':
			time_before = (2 + self.POST_TIME) * 60 * 60
		elif self.BOT_TIME_ZONE == 'PT':
			time_before = (3 + self.POST_TIME) * 60 * 60
		else:
			print "Invalid bot time zone settings."
			return

		timechecker = timecheck.TimeCheck(time_before)

		while True:
			games = self.get_games(timechecker)
			
			if len(games) > 0:
				self.game_loop(timechecker, edit, r, games)
			
			print "Sleeping for 10 minutes"
			print datetime.strftime(datetime.today(), "%d %I:%M %p")
			time.sleep(10 * 60)
	
	def get_games(self, timechecker):		
		today = datetime.today()
		todayFilter = datetime.strftime(today, "%Y-%m-%d")
		url = "http://api.cfl.ca/v1/games/" + self.YEAR + "?key=" + self.API_KEY

		response = ""
		while not response:
			try:
				response = urllib2.urlopen(url)
			except:
				print "Couldn't find URL, trying again..."
				time.sleep(20)

		data = json.load(response)
		
		games = data.get("data")
		
		activeGames = []
		
		for game in games:
			if timechecker.ready(game):
				activeGames.append(game)
		
		if len(activeGames) > 0:
			print "Ready to monitor " + str(len(activeGames)) + " games today"
		else:
			print "No games are ready"
				
		return activeGames

	def game_loop(self, timechecker, edit, r, games):
		
		while True:
			for i in range(len(games), 0, -1):
				#print "i = " + str(i)
				game = games[i-1]
				gameid = game.get("game_id")
				
				title = edit.generate_title(game,"game")
				print "Title = " + title
				try:
					posted = False
					subreddit = r.get_subreddit(self.SUBREDDIT)
					for submission in subreddit.get_new():
						if submission.title == title:
							print "Thread already posted, getting submission..."
							sub = submission
							posted = True
					if not posted:
						print "Submitting game thread..."
						sub = r.submit(self.SUBREDDIT, title, edit.generate_code(gameid,"game", ""))
						print "Game thread submitted..."
						print "Sleeping for two minutes..."
						time.sleep(120)
						if self.STICKY:
							print "Stickying submission..."
							sub.sticky()
							print "Submission stickied..."
						if self.SUGGESTED_SORT != None:
							print "Setting suggested sort to " + self.SUGGESTED_SORT + "..."
							sub.set_suggested_sort(self.SUGGESTED_SORT)
							print "Suggested sort set..."
						if self.MESSAGE:
							print "Messaging Baseballbot..."
							#r.send_message('baseballbot', 'Gamethread posted', sub.short_link)
							print "Baseballbot messaged..."
					print datetime.strftime(datetime.today(), "%d %I:%M %p")
					time.sleep(5)
				except Exception, err:
					print err
					time.sleep(300)
				pgt_submit = False
									
				try:
					code = edit.generate_code(gameid,"game", sub.short_link)
					sub.edit(code)
					print "Edits submitted..."
					print "Sleeping for two minutes..."
					print datetime.strftime(datetime.today(), "%d %I:%M %p")
					time.sleep(120)
				except Exception, err:
					print "Couldn't submit edits, trying again..."
					print datetime.strftime(datetime.today(), "%d %I:%M %p")
					time.sleep(10)
					
				if " - Final" in code:
					del games[i-1]
					print datetime.strftime(datetime.today(), "%d %I:%M %p")
					print "Game final..."
					pgt_submit = True
					
				if pgt_submit:
					if self.POST_GAME_THREAD:
						print "Submitting postgame thread..."
						posttitle = edit.generate_title(d,"post")
						sub = r.submit(self.SUBREDDIT, posttitle, edit.generate_code(d,"post"))
						print "Postgame thread submitted..."
						if self.STICKY:
							print "Stickying submission..."
							sub.sticky()
							print "Submission stickied..."
					
				time.sleep(10)
			#end for
			
			if len(games) == 0:
				break
			
			time.sleep(10)
		#end while

if __name__ == '__main__':
	program = Bot()
	program.run()
