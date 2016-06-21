#!/usr/bin/python3
#
# This module has functionality to use the stats.nba.com API to download player
# and game information into a mongodb database.

import requests
from pymongo import MongoClient
import datetime
from threading import Thread
from sys import argv

HOST = 'localhost'
# HOST = "23.23.23.23"
PORT = 27017
DB_NAME = 'nba_db'
PLAYERS_COL = 'players'  # nba_db.players collection
SEASON_COL = 'season2015-16'
CURRENT_SEASON = "2015-16"  # nba_db.2015-16 collection and current season


class NBA_Downloader():

    def __init__(self, season, host, port, db, players_col, season_col):
        self.season = season
        client = MongoClient(host, port)
        db = client[DB_NAME]
        self.players_collection = db[players_col]
        self.season_collection = db[season_col]
        self.teams = self.init_teams()

    def download_all_players_general_info(self):
        all_players_url = 'http://stats.nba.com/stats/commonallplayers?LeagueID=00&Season=' + self.season + '&IsOnlyCurrentSeason=1'
        all_players_json = self.download_json(all_players_url)
        players_info = all_players_json['resultSets'][0]['rowSet']

        # 7 Threads
        p0 = 0
        p1 = len(players_info) // 7
        p2 = p1 * 2
        p3 = p1 * 3
        p4 = p1 * 4
        p5 = p1 * 5
        p6 = p1 * 6
        p7 = len(players_info)

        list0 = players_info[p0:p1]
        list1 = players_info[p1:p2]
        list2 = players_info[p2:p3]
        list3 = players_info[p3:p4]
        list4 = players_info[p4:p5]
        list5 = players_info[p5:p6]
        list6 = players_info[p6:p7]

        thread0 = Thread(target=self.download_info, args=(list0,))
        thread0.start()
        thread1 = Thread(target=self.download_info, args=(list1,))
        thread1.start()
        thread2 = Thread(target=self.download_info, args=(list2,))
        thread2.start()
        thread3 = Thread(target=self.download_info, args=(list3,))
        thread3.start()
        thread4 = Thread(target=self.download_info, args=(list4,))
        thread4.start()
        thread5 = Thread(target=self.download_info, args=(list5,))
        thread5.start()

        self.download_info(list6)

        thread0.join()
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()

    def download_info(self, player_info_list):
        for i in range(0, len(player_info_list)):
            id = player_info_list[i][0]
            last_updated = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

            player_url = 'http://stats.nba.com/stats/commonplayerinfo?PlayerID=' + str(id)
            player_json = self.download_json(player_url)
            p = player_json['resultSets'][0]['rowSet'][0]

            first_name = p[1]
            last_name = p[2]
            print("Acquring data for " + first_name + " " + last_name + "...")
            birthdate = p[6][:10]
            school = p[7]
            country = p[8]
            height = p[10]
            weight = p[11]
            jersey = p[13]
            position = p[14]
            roster_status = p[15]
            team = self.teams[p[18]]
            from_year = p[22]
            to_year = p[23]
            played_this_season = p[25]
            if played_this_season == "Y":
                played_this_season = True
            else:
                played_this_season = False

            self.add_player_to_db(id, last_updated, first_name, last_name, birthdate, school, country, height, weight, jersey, position, roster_status, team, from_year, to_year, played_this_season)

    def download_all_players_season(self):
        cursor = self.players_collection.find()
        cursor_list = list(cursor)

        # 7 Threads
        p0 = 0
        p1 = len(cursor_list) // 7
        p2 = p1 * 2
        p3 = p1 * 3
        p4 = p1 * 4
        p5 = p1 * 5
        p6 = p1 * 6
        p7 = len(cursor_list)

        list0 = cursor_list[p0:p1]
        list1 = cursor_list[p1:p2]
        list2 = cursor_list[p2:p3]
        list3 = cursor_list[p3:p4]
        list4 = cursor_list[p4:p5]
        list5 = cursor_list[p5:p6]
        list6 = cursor_list[p6:p7]

        thread0 = Thread(target=self.download_season, args=(list0,))
        thread0.start()
        thread1 = Thread(target=self.download_season, args=(list1,))
        thread1.start()
        thread2 = Thread(target=self.download_season, args=(list2,))
        thread2.start()
        thread3 = Thread(target=self.download_season, args=(list3,))
        thread3.start()
        thread4 = Thread(target=self.download_season, args=(list4,))
        thread4.start()
        thread5 = Thread(target=self.download_season, args=(list5,))
        thread5.start()

        self.download_season(list6)

        thread0.join()
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()

    def download_season(self, player_list):

        for document in player_list:
            id = document['_id']
            name = document['first_name'] + " " + document['last_name']
            self.download_player_season(id, name)

    # Private

    def download_json(self, json_url):
        # response = requests.get(json_url)
        response = requests.get(json_url, headers={'User-Agent': 'Mozilla/5.0'}) 
        response.raise_for_status()
        return response.json()

    def add_player_to_db(self, id, last_updated, first_name, last_name, birthdate, school, country, height, weight, jersey, position, roster_status, team, from_year, to_year, played_this_season):

        key = {'_id': id}

        document = {
            "_id": id,
            "last_updated": last_updated,
            "first_name": first_name,
            "last_name": last_name,
            "birthdate": birthdate,
            "school": school,
            "country": country,
            "height": height,
            "weight": weight,
            "jersey": jersey,
            "position": position,
            "roster_status": roster_status,
            "team": {
                "name": team.name,
                "city": team.city,
                "abbrev": team.abbrev
            },
            "from_year": from_year,
            "to_year": to_year,
            "played_this_season": played_this_season
        }

        self.players_collection.update(key, document, upsert=True)

    def download_player_season(self, id, name):
        print("Acquring game data for " + name + "...")
        last_updated = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

        url = "http://stats.nba.com/stats/playergamelog?PlayerID=" + str(id) + "&Season=" + self.season + "&SeasonType=Regular+Season"
        season_info = self.download_json(url)
        games_json = season_info['resultSets'][0]['rowSet']

        games = list()
        total_games = 0
        total_stats = GameStatistics()
        average_stats = GameStatistics()

        for i in range(0, len(games_json)):
            g = games_json[i]
            total_games += 1

            game_id = g[2]
            date = self.parse_date(g[3])

            # WAS @ ORL
            # WAS vs. ORL
            matchup = g[4].split(' ')
            if matchup[1] == '@':
                home = matchup[2]
                away = matchup[0]
            else:
                home = matchup[0]
                away = matchup[2]

            wl = g[5]
            if wl is None:
                winner = "Undecided"
            else:
                if wl == "W":
                    winner = home
                else:
                    winner = away

            min = g[6]
            fgm = g[7]
            fga = g[8]
            fg_pct = 0
            if fga != 0:
                fg_pct = fgm / fga
            fg3m = g[10]
            fg3a = g[11]
            fg3_pct = 0
            if fg3a != 0:
                fg3_pct = fg3m / fg3a
            ftm = g[13]
            fta = g[14]
            ft_pct = 0
            if fta != 0:
                ft_pct = ftm / fta
            oreb = g[16]
            dreb = g[17]
            reb = g[18]
            ast = g[19]
            stl = g[20]
            blk = g[21]
            tov = g[22]
            pf = g[23]
            pts = g[24]
            plus_minus = g[25]
            per = self.calculateLinearPER(min, fgm, fga, fg3m, ftm, fta, oreb, dreb, ast, stl, blk, tov, pf, pts)

            total_stats.add(min, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, stl, blk, tov, pf, pts, plus_minus, per)

            statistics = {
                "min": min,
                "fgm": fgm,
                "fga": fga,
                "fg_pct": round(fg_pct, 3),
                "fg3m": fg3m,
                "fg3a": fg3a,
                "fg3_pct": round(fg3_pct, 3),
                "ftm": ftm,
                "fta": fta,
                "ft_pct": round(ft_pct, 3),
                "oreb": oreb,
                "dreb": dreb,
                "reb": reb,
                "ast": ast,
                "stl": stl,
                "blk": blk,
                "tov": tov,
                "pf": pf,
                "pts": pts,
                "plus_minus": plus_minus,
                "per": round(per, 3)
            }

            game = {
                "id": game_id,
                "date": date,
                "home": home,
                "away": away,
                "winner": winner,
                "statistics": statistics
            }

            games.append(game)

        tfg_pct = 0
        if total_stats.fga != 0:
            tfg_pct = total_stats.fgm / total_stats.fga

        tfg3_pct = 0
        if total_stats.fg3a != 0:
            tfg3_pct = total_stats.fg3m / total_stats.fg3a

        tft_pct = 0
        if total_stats.fta != 0:
            tft_pct = total_stats.ftm / total_stats.fta

        total = {
            "min": total_stats.min,
            "fgm": total_stats.fgm,
            "fga": total_stats.fga,
            "fg_pct": round(tfg_pct, 3),
            "fg3m": total_stats.fg3m,
            "fg3a": total_stats.fg3a,
            "fg3_pct": round(tfg3_pct, 3),
            "ftm": total_stats.ftm,
            "fta": total_stats.fta,
            "ft_pct": round(tft_pct, 3),
            "oreb": total_stats.oreb,
            "dreb": total_stats.dreb,
            "reb": total_stats.reb,
            "ast": total_stats.ast,
            "stl": total_stats.stl,
            "blk": total_stats.blk,
            "tov": total_stats.tov,
            "pf": total_stats.pf,
            "pts": total_stats.pts,
            "plus_minus": total_stats.plus_minus,
            "per": round(total_stats.per, 3)
        }

        if total_games > 0:
            amin = total_stats.min / total_games
            afgm = total_stats.fgm / total_games
            afga = total_stats.fga / total_games
            afg3m = total_stats.fg3m / total_games
            afg3a = total_stats.fg3a / total_games
            aftm = total_stats.ftm / total_games
            afta = total_stats.fta / total_games
            aoreb = total_stats.oreb / total_games
            adreb = total_stats.dreb / total_games
            areb = total_stats.reb / total_games
            aast = total_stats.ast / total_games
            astl = total_stats.stl / total_games
            ablk = total_stats.blk / total_games
            atov = total_stats.tov / total_games
            apf = total_stats.pf / total_games
            apts = total_stats.pts / total_games
            aplus_minus = total_stats.plus_minus / total_games
            aper = self.calculateLinearPER(amin, afgm, afga, afg3m, aftm, afta, aoreb, adreb, aast, astl, ablk, atov, apf, apts)
            average_stats.add(amin, afgm, afga, afg3m, afg3a, aftm, afta, aoreb, adreb, areb, aast, astl, ablk, atov, apf, apts, aplus_minus, aper)

        average = {
            "min": round(average_stats.min, 3),
            "fgm": round(average_stats.fgm, 3),
            "fga": round(average_stats.fga, 3),
            "fg_pct": round(tfg_pct, 3),
            "fg3m": round(average_stats.fg3m, 3),
            "fg3a": round(average_stats.fg3a, 3),
            "fg3_pct": round(tfg3_pct, 3),
            "ftm": round(average_stats.ftm, 3),
            "fta": round(average_stats.fta, 3),
            "ft_pct": round(tft_pct, 3),
            "oreb": round(average_stats.oreb, 3),
            "dreb": round(average_stats.dreb, 3),
            "reb": round(average_stats.reb, 3),
            "ast": round(average_stats.ast, 3),
            "stl": round(average_stats.stl, 3),
            "blk": round(average_stats.blk, 3),
            "tov": round(average_stats.tov, 3),
            "pf": round(average_stats.pf, 3),
            "pts": round(average_stats.pts, 3),
            "plus_minus": round(average_stats.plus_minus, 3),
            "per": round(average_stats.per, 3)
        }

        self.add_season_to_db(id, last_updated, games, total, average)

    def add_season_to_db(self, id, last_updated, games, total, average):

        key = {'_id': id}

        document = {
            "_id": id,
            "last_updated": last_updated,
            "games": games,
            "total": total,
            "average": average
        }

        self.season_collection.update(key, document, upsert=True)

    def init_teams(self):
        teams = dict()
        teams["ATL"] = Team("Hawks", "Atlanta", "ATL")
        teams["BKN"] = Team("Nets", "Brooklyn", "BKN")
        teams["BOS"] = Team("Celtics", "Boston", "BOS")
        teams["CHA"] = Team("Hornets", "Charlotte", "CHA")
        teams["CHI"] = Team("Bulls", "Chicago", "CHI")
        teams["CLE"] = Team("Cavaliers", "Cleveland", "CLE")
        teams["DAL"] = Team("Mavericks", "Dallas", "DAL")
        teams["DEN"] = Team("Nuggets", "Denver", "DEN")
        teams["DET"] = Team("Pistons", "Detroit", "DET")
        teams["GSW"] = Team("Warriors", "Golden State", "GSW")
        teams["HOU"] = Team("Rockets", "Houston", "HOU")
        teams["IND"] = Team("Pacers", "Indiana", "IND")
        teams["LAC"] = Team("Clippers", "Los Angeles", "LAC")
        teams["LAL"] = Team("Lakers", "Los Angeles", "LAL")
        teams["MEM"] = Team("Grizzlies", "Memphis", "MEM")
        teams["MIA"] = Team("Heat", "Miami", "MIA")
        teams["MIL"] = Team("Bucks", "Milwaukee", "MIL")
        teams["MIN"] = Team("Timberwolves", "Minnesota", "MIN")
        teams["NOP"] = Team("Pelicans", "New Orleans", "NOP")
        teams["NYK"] = Team("Knicks", "New York", "NYK")
        teams["OKC"] = Team("Thunder", "Oklahoma City", "OKC")
        teams["ORL"] = Team("Magic", "Orlando", "ORL")
        teams["PHI"] = Team("76ers", "Philadelphia", "PHI")
        teams["PHX"] = Team("Suns", "Phoenix", "PHX")
        teams["POR"] = Team("Trailblazers", "Portland", "POR")
        teams["SAC"] = Team("Kings", "Sacramento", "SAC")
        teams["SAS"] = Team("Spurs", "San Antonio", "SAS")
        teams["TOR"] = Team("Raptors", "Toronto", "TOR")
        teams["UTA"] = Team("Jazz", "Utah", "UTA")
        teams["WAS"] = Team("Wizards", "Washington", "WAS")
        teams[""] = Team("", "", "")
        return teams

    def parse_date(self, date):
        # parse a date in this format: "JAN 09, 2016"
        date_array = date.split(" ")
        month = date_array[0]
        if month == "JAN":
            month = "01"
        elif month == "FEB":
            month = "02"
        elif month == "MAR":
            month = "03"
        elif month == "APR":
            month = "04"
        elif month == "MAY":
            month = "05"
        elif month == "JUN":
            month = "06"
        elif month == "JUL":
            month = "07"
        elif month == "AUG":
            month = "08"
        elif month == "SEP":
            month = "09"
        elif month == "OCT":
            month = "10"
        elif month == "NOV":
            month = "11"
        elif month == "DEC":
            month = "12"
        day = date_array[1][:2]
        year = date_array[2]
        return year + "-" + month + "-" + day

    def calculateLinearPER(self, min, fgm, fga, fg3m, ftm, fta, oreb, dreb, ast, stl, blk, tov, pf, pts):
        # [ FGM x 85.910
        # + Steals x 53.897
        # + 3PTM x 51.757
        # + FTM x 46.845
        # + Blocks x 39.190
        # + Offensive_Reb x 39.190
        # + Assists   x 34.677
        # + Defensive_Reb x 14.707
        # - Foul x 17.174
        # - FT_Miss   x 20.091
        # - FG_Miss   x 39.190
        # - TO x 53.897 ]
        # x (1 / Minutes).
        per_total = (fgm * 85.910) + (stl * 53.897) + (fg3m * 51.757) + (ftm * 46.845) + (blk * 39.190) + (oreb * 39.190) + (ast * 34.677) + (dreb * 14.707) - (pf * 17.174) - ((fta - ftm) * 20.091) - ((fga - fgm) * 39.190) - (tov * 53.897)
        if min == 0:
            return 0
        else:
            return per_total / min


class Team():
    """
    An object representing an NBA Team
    """

    def __init__(self, name, city, abbrev):
        self.name = name
        self.city = city
        self.abbrev = abbrev


class GameStatistics():
    """
    An object representing an NBA Game
    """

    def __init__(self):
        self.min = 0
        self.fgm = 0
        self.fga = 0
        self.fg3m = 0
        self.fg3a = 0
        self.ftm = 0
        self.fta = 0
        self.oreb = 0
        self.dreb = 0
        self.reb = 0
        self.ast = 0
        self.stl = 0
        self.blk = 0
        self.tov = 0
        self.pf = 0
        self.pts = 0
        self.plus_minus = 0
        self.per = 0

    def add(self, min, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, stl, blk, tov, pf, pts, plus_minus, per):
        self.min += min
        self.fgm += fgm
        self.fga += fga
        self.fg3m += fg3m
        self.fg3a += fg3a
        self.ftm += ftm
        self.fta += fta
        self.oreb += oreb
        self.dreb += dreb
        self.reb += reb
        self.ast += ast
        self.stl += stl
        self.blk += blk
        self.tov += tov
        self.pf += pf
        self.pts += pts
        self.plus_minus += plus_minus
        self.per += per


if len(argv) > 1:
    downloader = NBA_Downloader(CURRENT_SEASON, HOST, PORT, DB_NAME, PLAYERS_COL, SEASON_COL)

    if argv[1] == "info":
        downloader.download_all_players_general_info()
    elif argv[1] == "season":
        downloader.download_all_players_season()
    elif argv[1] == "all":
        downloader.download_all_players_general_info()
        downloader.download_all_players_season()
    else:
        print("Enter a correct flag.")
else:
    print("Enter a correct flag.")

# -info -game -all