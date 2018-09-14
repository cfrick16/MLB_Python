#!/usr/bin/env python3

import re
#    0      1    2     3    4    5         6           7          8          9
# [Inning, Top, Outs, 1st, 2nd, 3rd, Home_team_lead, Runs, Home_team_wins, Play]
situations = [[]]

def add_run(score_multiplier, sit):
	sit[7] = sit[7] + 1
	sit[6] = sit[6] + score_multiplier

def play_parser(full_play,sit, score_multiplier) -> bool :
	sit[9] = full_play
	arr = full_play.split('.')
	play = arr[0]
	advances = "N"
	if(len(arr) > 1):
		advances = arr[1]
	assert(len(arr) < 3)

	out_recorded = 0
	if(advances != "N") :
		bases = advances.split(';')
		for b in bases :
			if(b[0] != "B") : 
				sit[int(b[0]) + 2] = False
			if 'X' in b and 'E' not in b:
				out_recorded = out_recorded + 1
				sit[2] = sit[2] + 1
			elif (b[2] == 'H') :
				add_run(score_multiplier, sit)
			else :
				assert('-' in b or 'E' in b)
				sit[int(b[2]) + 2] = True

	sp = play.split('/')
	if 'B' not in advances and 'E' not in sp[0]:
		if("DP" in play):
			sit[2] = sit[2] + 2 - out_recorded
		elif("TP" in play):
			sit[2] = sit[2] + 3 - out_recorded
		elif(play[0] == "K" or play[0].isnumeric() or play[0:2] == "CS"):
			sit[2] = sit[2] + 1
		elif(play[0:2] == "HP" or play[0] == "W" or play[0] == "I"):
			sit[3] = True
		elif(play[0] == "S" or play[0] == "C" or play[0] == "E"):
			sit[3] = True
		elif(play[0] == "D"):
			sit[4] = True
		elif(play[0] == "H"):
			add_run(score_multiplier, sit)
		elif(play[0] == "T"):
			sit[5] = True
		elif(play[0] == "F"):
			p = 1 + 1
		elif("CS" in play):
			sit[2] = sit[2] + 1
		elif(play[0:2] == "PO"):
			if("(E" not in play):
				sit[2] = sit[2] + 1 - out_recorded
		else :
			if(play[0:2] != "NP" and play[0:3] != "FLE" and 
				play[0:2] != "OA" and play[0:2] !="PB" 
				and play[0:2] != "BK"):
				print(play[0:2])
			return advances != "N"

		return True





def game_parser(plays, home_team_wins) :
	sit = [1, "Top", 0, False, False, False, 0, 0, home_team_wins, "Start"]
	situations.append(sit)
	for x in plays :
		sit = sit.copy()
		if(sit[1] != ("Top", "Bot")[int(x[1])]):
			sit[1] = ("Top", "Bot")[int(x[1])]
			sit[0] = int(x[0])
			sit[2] = 0
			sit[3] = False
			sit[4] = False
			sit[5] = False

		if(play_parser(x[2], sit, (-1, 1)[int(x[1])]) or True):
			situations.append(sit)




def team_parser(contents, home_lineup) :
	once = False # TODO: Delete
	i = 0
	while(len(contents) > i) :
		if(contents[0] == "id"):
			print(contents[1])
		home_team_wins = False
		line = contents[i].split(',')
		if(line[1] == "wp") :
			#Found new game
			if line[2][0:8] in home_lineup :
				home_team_wins = True
			# Load Game
			game = []
			while(line[1] != "er") :
				if(line[0] == "play") :
					game.append([line[1], line[2], line[6][0:len(line[6]) - 1]])
				i = i + 1
				line = contents[i].split(",")
			game_parser(game, home_team_wins)
			if(once):
				i = len(contents) # TODO: Delete
		i = i + 1



if __name__ == "__main__":

	situations.pop()
	team_lineup = []

	nl_teams = ("ARI", "ATL", "CHN", "CIN", "COL", "LAN", "MIA", "MIL", "NYN",
		"PHI", "PIT", "SDN", "SFN", "SLN", "WAS")
	al_teams = ("ANA", "BAL", "BOS", "CHA", "CLE", "DET", "HOU", "KCA", "MIN", 
		"NYA", "OAK", "SEA", "TBA", "TEX", "TOR")

	for team in nl_teams :
		team_file=open("2017eve/"+ team + "2017.ROS", "r").readlines()
		for line in team_file:
			team_lineup.append(line.split(',')[0])

		f=open("2017eve/2017" + team + ".EVN", "r")
		contents = f.readlines()
		team_parser(contents, team_lineup)


	for team in al_teams :
		team_file=open("2017eve/"+ team + "2017.ROS", "r").readlines()
		for line in team_file:
			team_lineup.append(line.split(',')[0])

		f=open("2017eve/2017" + team + ".EVA", "r")
		contents = f.readlines()
		team_parser(contents, team_lineup)





	# for x in situations:
	# 	print(x)