#!/usr/bin/python3
# Usage: python3 nba.py lebron james

import nbascrape_functions as nba
from subprocess import call
import sys
import os


def parse_name(argv):
    name = ""
    for s in argv:
        name += s
        name += " "
    return name.strip()

nba.init()

if len(sys.argv) < 2:
    print("Please enter a player name.")
    sys.exit()

sys.argv.pop(0)
arg_name = parse_name(sys.argv)

players = open("players.txt", "r")
lines = players.read()
lines = lines.split("\n")
for line in lines:
    player_info = line.split(",")
    if len(player_info) < 2:
        print(arg_name + " was not found. Would you like to try another player?")
        sys.exit()
    name = player_info[0]
    team = player_info[1]
    id = player_info[2]
    if arg_name.lower() == name.lower():
        break


nba.create_player_season_file(name, team, id)
call(["cat", "players/" + name + ".txt"])

# Delete players/ and players.txt
os.remove("players.txt")
os.remove("players/" + name + ".txt")
os.rmdir("players/")
