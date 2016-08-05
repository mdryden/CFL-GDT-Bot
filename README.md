Baseball GDT Bot by Matt Bullock
=====================================

####Current Version: 1.0.0

This fork was created by Michael Dryden, to support game threads on /r/CFL

This project was originally written by Matt Bullock,
	A.K.A. /u/DetectiveWoofles on reddit and Woofles on GitHub.
	User avery_crudeman is the only other contributor.
	
The point of this project is to create a bot that will generate a
	game discussion thread that contains live linescore and boxscore,
	post it in the correct subreddit for that team, and keep it
	updated throughout the game.
	
Version 1.0 was written in a mix of Python and Java, and has been
	completely ported to Python for v2.0 and v3.0 (this version).

---

####SET UP OAuth!

Go to reddit.com’s app page, click on the “are you a developer? create an app” button. Fill out the name, description and about url. Name must be filled out, but the rest doesn’t. Write whatever you please. For redirect uri set it to `http://127.0.0.1:65010/authorize_callback`. All four variables can be changed later.

Next, open setup.py, fill in the client_id, client_secret and redirect_uri fields and run the script. Your browser will open. Click allow on the displayed web page. 

Enter the uniqueKey&code from the URL into the console -- wrapped in single quotes -- and the access information will be printed. This includes the final bit of info you need, the refresh token.

Finally, Copy sample_settings.json to the src folder and rename it to settings.json. Fill in the CLIENT_ID, CLIENT_SECRET, REDIRECT_URI and REFRESH_TOKEN fields in the settings.json file and save. 

####SET UP THE REST OF THE BOT!

Edit settings.json with the following information:

BOT_TIME_ZONE - time zone of the computer running the bot, uncomment the line that you want to use

TIME_ZONE - time zone of the team. uncomment the line that you want to use

POST_TIME - bot posts the thread POST_TIME hours before the game

SUBREDDIT - subreddit that you want the threads posted to

TEAM_CODE - three letter code that represents team, look this up

POST_GAME_THREAD - do you want a post game thread? - Not currently supported

SUGGESTED_SORT - what do you want the suggested sort to be? ("confidence", "top", "new", "controversial", "old", "random", "qa", "")

STICKY - do you want the thread stickied? (mod only)

MESSAGE - send submission shortlink to /u/baseballbot - Not supported (target will be changed if support is added)

THREAD_SETTINGS - what to include in game threads

POST_THREAD_SETTINGS - what to include in postgame threads
	
---	

If something doesn't seem right, feel free to message me or post it as a bug here.
	
This was written in Python 2.7, so beware if you are running Python 3 or
	above that it may not work correctly. Also make sure you install
	praw, simplejson and dateutil before running!
	
Modules being used:

	praw - interfacing reddit
	simplejson - JSON parsing
	dateutil - Date parsing
	urllib2 - pulling data from MLB servers
	ElementTree - XML parsing

###Updates

####v1.0.0
* Initial version forked from Baseball-GDT-Bot

	
