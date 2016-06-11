#!/usr/bin/python3
# Usage: python3 nba.py lebron james

import nbascrape_functions as nba
from subprocess import call
import sys
import os
import nba_rank as rank
from colors import Color


def parse_name(argv):
    name = ""
    for s in argv:
        name += s
        name += " "
    return name.strip()


def display_player_rankings():
    if len(sys.argv) < 4:
        print("Please enter a date and stat.")
        sys.exit()

    date = sys.argv[2]
    stat = sys.argv[3]

    if len(sys.argv) > 4:
        tie_breaker_stat = sys.argv[4]
        sorted_players = rank.rank_players_on_date(date, stat, tie_breaker_stat)
    else:
        sorted_players = rank.rank_players_on_date(date, stat)

    if len(sorted_players) == 0:
        print("Could not find any games on that day.")
        sys.exit()

    print(Color.YELLOW + "WL\tMIN\tFGM\tFGA\tFG%\t3PM\t3PA\t3P%\tFTM\tFTA\tFT%\tREB\tAST\tSTL\tBLK\tTOV\tPF\tPTS\t+/-\tPER\tName" + Color.NONE)

    for p in sorted_players:
        # date = p["date"]
        name = p["name"][:16]
        # matchup = p["matchup"]
        wl = p["wl"]
        min = p["min"]
        fgm = p["fgm"]

        fga = p["fga"]
        fg_pct = p["fg_pct"]
        fg3m = p["fg3m"]
        fg3a = p["fg3a"]
        fg3_pct = p["fg3_pct"]
        ftm = p["ftm"]
        fta = p["fta"]
        ft_pct = p["ft_pct"]
        reb = p["reb"]
        ast = p["ast"]
        stl = p["stl"]
        blk = p["blk"]
        tov = p["tov"]
        pf = p["pf"]
        pts = p["pts"]
        plus_minus = p["plus_minus"]
        per = p["per"]

        print(wl + "\t" + str(min) + "\t" + str(fgm) + "\t" + str(fga) + "\t" + str(fg_pct) + "\t" + str(fg3m) + "\t" + str(fg3a) + "\t" + str(fg3_pct) + "\t" + str(ftm) + "\t" + str(fta) + "\t" + str(ft_pct) + "\t" + str(reb) + "\t" + str(ast) + "\t" + str(stl) + "\t" + str(blk) + "\t" + str(tov) + "\t" + str(pf) + "\t" + str(pts) + "\t" + str(plus_minus) + "\t" + str(per) + "\t" + name)

    print(Color.YELLOW + "WL\tMIN\tFGM\tFGA\tFG%\t3PM\t3PA\t3P%\tFTM\tFTA\tFT%\tREB\tAST\tSTL\tBLK\tTOV\tPF\tPTS\t+/-\tPER\tName" + Color.NONE)


def display_player_stats():
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
    print()
    call(["cat", "players/" + name + ".txt"])

    # Delete players/ and players.txt
    os.remove("players.txt")
    os.remove("players/" + name + ".txt")
    os.rmdir("players/")


if len(sys.argv) < 2:
        print("Please enter a player name or [-r DATE STAT].")
        sys.exit()

if sys.argv[1] == "-r" or sys.argv[1] == "--rank":
    display_player_rankings()

elif sys.argv[1] == "-i" or sys.argv[1] == "--image":
    nba.init()
    nba.download_player_images()
    os.remove("players/" + name + ".txt")
    os.rmdir("players/")

elif sys.argv[1] == '-m' or sys.argv[1] == "--missed":
    nba.download_missed_players()

else:
    display_player_stats()