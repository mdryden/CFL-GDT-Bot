# does all the post generating and editing

import player

import xml.etree.ElementTree as ET
import urllib2
import simplejson as json
from datetime import datetime, timedelta
import time
from dateutil import parser

class Editor:

	

	def __init__(self,time_info,thread_settings, post_thread_settings, year, api_key):
		(self.time_zone,self.time_change,) = time_info
		(self.thread_tag, (self.header, self.box_score, self.line_score, self.scoring_plays, self.highlights, self.footer)) = thread_settings
		(self.post_thread_tag, (self.post_header, self.post_box_score, self.post_line_score, self.post_scoring_plays,self.post_highlights, self.post_footer)) = post_thread_settings
		self.year = year
		self.api_key = api_key
		self.subreddits = {
			"BC": "/r/BC_Lions",
			"CGY": "/r/Stampeders",
			"EDM": "/r/Eskimos",
			"SSK": "/r/riderville",
			"WPG": "/r/WinnipegBlueBombers",
			"HAM": "/r/ticats",
			"TOR": "/r/Argonauts",
			"OTT": "/r/redblacks",
			"MTL": "/r/Alouettes"
		}
		
		self.placeholders = {
			"BC": "####[](/placeholder)",
			"CGY": "#####[](/placeholder)",
			"EDM": "#####[](/placeholder)",
			"SSK": "####[](/placeholder)\n####[](/placeholder)",
			"WPG": "####[](/placeholder)\n#####[](/placeholder)",
			"HAM": "####[](/placeholder)\n######[](/placeholder)",
			"TOR": "#####[](/placeholder)\n####[](/placeholder)",
			"OTT": "#####[](/placeholder)\n#####[](/placeholder)",
			"MTL": "#####[](/placeholder)\n######[](/placeholder)",
		}
		

	def get_data(self,url):
		while True:
			try:
				response = urllib2.urlopen(url)
				break
			except:
				print "Couldn't find json, trying again..."
				time.sleep(20)
			
		data = json.load(response)
		return data

	def generate_title(self,game,thread):
		if thread == "game": title = self.thread_tag + " "
		elif thread == "post": title = self.post_thread_tag + " "
					
		timestring = game.get('date_start')
		date_object = parser.parse(timestring)
		
		title += self.generate_matchup(game, False)
		
		title +=  " - "
		title += date_object.strftime("%B") + " " + date_object.strftime("%d, %Y").lstrip("0")
		print "Returning title..."
		return title
		
	def generate_matchup(self,game,logos):
		awayUrl = self.get_cflstats_url(game.get("team_1").get("abbreviation"))
		homeUrl = self.get_cflstats_url(game.get("team_2").get("abbreviation"))
		awaySeason = self.get_data(awayUrl)
		homeSeason = self.get_data(homeUrl)
		
		away = game.get("team_1").get("location") + " " + game.get("team_1").get("nickname")
		awayRecord = self.generate_record(awaySeason.get("Standing").get("Wins"), awaySeason.get("Standing").get("Losses"), awaySeason.get("Standing").get("Ties"))
		home = game.get("team_2").get("location") + " " + game.get("team_2").get("nickname")
		homeRecord = self.generate_record(homeSeason.get("Standing").get("Wins"), homeSeason.get("Standing").get("Losses"), homeSeason.get("Standing").get("Ties"))
		
		matchup = ""
		
		if logos:
			matchup += "[](/" + game.get("team_1").get("abbreviation") + ") "
		matchup += away + " (" + awayRecord + ")"
		matchup += " @ "
		if logos:
			matchup += "[](/" + game.get("team_2").get("abbreviation") + ") "
		matchup += home + " (" + homeRecord + ")"
		
		return matchup		
		
	def get_cflstats_url(self, abbr):
		if abbr == "OTT":
			abbr = "ORB"
			
		return "http://cflstats.ca/team/" + abbr + "/" + self.year + ".json"
	
	def generate_record(self,wins,losses,ties):
		record = str(wins) + "-" + str(losses)
		if ties > 0:
			record = record + "-" + str(ties);
		
		return record;
		

	def generate_code(self,gameid,type,shortlink):
		code = ""
		
		url = "http://api.cfl.ca/v1/games/" + self.year + "/game/" + str(gameid) + "?include=rosters,boxscore,play_by_play&key=" + self.api_key
		game = self.get_data(url).get("data")[0]
		
		away_abbr = game.get("team_1").get("abbreviation")
		home_abbr = game.get("team_2").get("abbreviation")
		csgameid = str(self.year) + str(game.get("game_number")).zfill(3)
		shortlink = shortlink[shortlink.rfind("/") + 1:]
				
		code = open(type + "/thread.txt", "r").read()
		
		code = code.replace("{matchup}", self.generate_matchup(game, True))
		code = code.replace("{game_start}", self.get_game_start(game))
		code = code.replace("{stadium}", game.get("venue").get("name"))
		code = code.replace("{conditions}", self.get_conditions(type, game))
		code = code.replace("{game_id}", str(gameid))
		code = code.replace("{cs_game_id}", csgameid)
		code = code.replace("{shortlink}", shortlink)
		code = code.replace("{lineups}", self.get_lineups(type, game))
		code = code.replace("{linescore}", self.get_linescore(type, game))
		code = code.replace("{boxscore}", self.get_boxscore(type, game))
		code = code.replace("{scoring_plays}", self.get_scoring_plays(type, game))
		code = code.replace("{away_subreddit}", self.subreddits[away_abbr])
		code = code.replace("{home_subreddit}", self.subreddits[home_abbr])
		
		code = code.replace("{placeholder}", self.placeholders[home_abbr])
		
		print "Returning all code"
		return code
	
	def get_game_start(self, game):
		game_start = parser.parse(game.get('date_start'))
		timezone = self.time_zone
		t = timedelta(hours=self.time_change)
		timezone = self.time_zone
		game_start = game_start - t
		
		return game_start.strftime("%I:%M %p ").lstrip("0") + timezone
		
	def get_conditions(self, type, game):
		code = open(type + "/conditions.txt", "r").read()
		
		weather = game.get("weather")		
		coin_toss = game.get("coin_toss")		
		
		if weather.get("sky") != "":
			code = code.replace("{sky}", weather.get("sky").title())
			code = code.replace("{temp}", str(weather.get("temperature")))
			code = code.replace("{wind_speed}", weather.get("wind_speed"))
			code = code.replace("{wind_dir}", weather.get("wind_direction").upper())
			code = code.replace("{field}", weather.get("field_conditions").title())
		else:
			code = code.replace("{sky}", "")
			code = code.replace("{temp}", "")
			code = code.replace("{wind_speed}", "")
			code = code.replace("{wind_dir}", "")
			code = code.replace("{field}", "")
				
		if coin_toss.get("coin_toss_winner") != "":
			code = code.replace("{coin_toss}", coin_toss.get("coin_toss_winner_election"))
		else:
			code = code.replace("{coin_toss}", "")
			
		return code

	def get_linescore(self,type,game):	
			
		team1 = game.get('team_1')
		team2 = game.get("team_2")
		
		overtime = len(team1.get("linescores")) > 4
		filename = "/linescore.txt" if not overtime else "/linescore_ot.txt"
	
		code = open(type + filename, "r").read()
			
		final = ""
		
		if game.get("event_status").get("name") == "Final":
			final = " - Final"

		code = code.replace("{final}", final)
		
		code = code.replace("{away}", self.get_teamlinescore(type, team1, overtime))
		code = code.replace("{home}", self.get_teamlinescore(type, team2, overtime))
		
		print "Returning linescore"
		#print linescore
		return code
		#except:
		#	print "Missing data for linescore, returning blank text..."
		#	return linescore

			
	def get_teamlinescore(self,type,team,overtime):
		filename = "/linescore_team.txt" if not overtime else "/linescore_team_ot.txt"
		code = open(type + filename, "r").read()
		
		code = code.replace("{abbr}", team.get('abbreviation'))
		
		x = 1
		#if type(team.get(")) is list:
		for item in team.get("linescores"):
			marker = "{q" + str(x) + "}"
			code = code.replace(marker, str(item.get('score')))
			x = x + 1
			
		for i in range(x, 6):
			marker = "{q" + str(i) + "}"
			code = code.replace(marker, "")
				
		code = code.replace("{total}", str(team.get('score')))
			
		return code

	def get_lineups(self,type,game):
		
		rosterAway = game.get("rosters").get("teams").get("team_1").get("roster")
		rosterHome = game.get("rosters").get("teams").get("team_2").get("roster")
		
		if len(rosterAway) == 0:
			return ""
			
		code = open(type + "/lineups.txt", "r").read()
		rowcode = open(type + "/lineups_row.txt", "r").read()
		
		code = code.replace("{away_abbr}", game.get("team_1").get("abbreviation"))
		code = code.replace("{home_abbr}", game.get("team_2").get("abbreviation"))
		
		awayStarters = []
		homeStarters = []
		
		for i in range(0, len(rosterAway)):
			if (rosterAway[i].get("is_starter") == True):
				awayStarters.append(rosterAway[i])
				
			if (rosterHome[i].get("is_starter") == True):
				homeStarters.append(rosterHome[i])
				
		for i in range(0, len(awayStarters)):
			row = rowcode
			row = row.replace("{away_number}", str(awayStarters[i].get("uniform")))
			row = row.replace("{away_first}", awayStarters[i].get("first_name"))
			row = row.replace("{away_last}", awayStarters[i].get("last_name"))
			row = row.replace("{home_number}", str(homeStarters[i].get("uniform")))
			row = row.replace("{home_first}", homeStarters[i].get("first_name"))
			row = row.replace("{home_last}", homeStarters[i].get("last_name"))			
			code += row
			
		print "Returning lineups"
		return code
			
	def get_boxscore(self,type,game):
		if (game.get("event_status").get("name") == "Pre-Game"):
			return ""
						
		team1 = game.get("boxscore").get("teams").get("team_1")
		team2 = game.get("boxscore").get("teams").get("team_2")
			
		code = open(type + "/boxscore.txt", "r").read()
				
		rowcode = open(type + "/passing_row.txt", "r").read()	
		code = code.replace("{passing_rows}", self.get_team_stats_rows(rowcode, team1, team2, "passing"))
				
		rowcode = open(type + "/rushing_row.txt", "r").read()	
		code = code.replace("{rushing_rows}", self.get_team_stats_rows(rowcode, team1, team2, "rushing"))
				
		rowcode = open(type + "/receiving_row.txt", "r").read()	
		code = code.replace("{receiving_rows}", self.get_team_stats_rows(rowcode, team1, team2, "receiving"))
				
		rowcode = open(type + "/field_goals_row.txt", "r").read()	
		code = code.replace("{kicking_rows}", self.get_team_stats_rows(rowcode, team1, team2, "field_goals"))
		
		return code
		
	def get_team_stats_rows(self,rowcode,team1,team2,statname):			
		code = self.get_team_stats_row(rowcode,team1.get("abbreviation"),team1.get(statname))
		
		if code != "":
			code += "\n"
		
		code += self.get_team_stats_row(rowcode,team2.get("abbreviation"),team2.get(statname))
		
		return code
		
	def get_team_stats_row(self,rowcode,abbr,stats):
	
		if stats == None:
			return ""
	
		code = rowcode
		code = code.replace("{abbr}", abbr)
		
		for key, value in stats.items():
			code = code.replace("{" + key + "}", str(value))
			
		return code
		
	def get_scoring_plays(self,type,game):		
		scoringPlays = []
		
		for play in game.get("play_by_play"):
			if play.get("play_result_points") > 0:
				scoringPlays.append(play)		
				
		if len(scoringPlays) == 0:
			return ""		
		
		code = open(type + "/scoring_plays.txt", "r").read()
		rowcode = open(type + "/scoring_plays_row.txt", "r").read()
		
		code = code.replace("{away_abbr}", game.get("team_1").get("abbreviation"))
		code = code.replace("{home_abbr}", game.get("team_2").get("abbreviation"))
		
		for play in scoringPlays:
			row = rowcode
			row = row.replace("{qtr}", str(play.get("quarter")))
			row = row.replace("{time}", play.get("play_clock_start"))
			row = row.replace("{play}", play.get("play_summary"))
			row = row.replace("{away_score}", str(play.get("team_visitor_score")))
			row = row.replace("{home_score}", str(play.get("team_home_score")))
			code += row
			
		return code