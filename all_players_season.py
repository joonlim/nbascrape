# Script to download season information for all players

import nbascrape_functions as nba

nba.init()

players = open("players.txt", "r")
lines = players.read()
lines = lines.split("\n")
for line in lines:
    player_info = line.split(",")
    if len(player_info) < 2:
        break
    name = player_info[0]
    team = player_info[1]
    id = player_info[2]
    nba.create_player_season_file(name, team, id)
