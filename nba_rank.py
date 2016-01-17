from pymongo import MongoClient
import sys

# HOST = 'localhost'
HOST = '23.23.23.23'
PORT = 27017
DB = 'nba_db'
PLAYERS_COL = 'players'  # nba_db.players collection
SEASON_COL = 'season2015-16'
CURRENT_SEASON = "2015-16"  # nba_db.2015-16 collection and current season


def rank_players_on_date(date, stat, tie_breaker_stat=None):
    date_arg = parse_date(date)
    if date_arg == "invalid":
        print("Please enter a correct date. Check source nba_rank.py for details.")
        sys.exit()

    stat_arg = parse_stat(stat)
    if stat_arg == "invalid":
        print("Please enter a correct stat. Check source nba_rank.py for details.")
        sys.exit()

    if tie_breaker_stat is not None:
        tie_breaker_stat_arg = parse_stat(tie_breaker_stat)
        if stat_arg == "invalid":
            print("Please enter a correct stat for the tie breaker (when two or more players have an equivalent value for the stat being compared, the tie breaker stat will be used to sort them). Check source nba_rank.py for details.")
            sys.exit()

    # Get data from db
    client = MongoClient(HOST, PORT)
    db = client[DB]
    players_collection = db[PLAYERS_COL]
    season_collection = db[SEASON_COL]

    cursor = season_collection.find()
    players = dict()

    for document in cursor:
        # create a dict of ids mapped to games of the given date
        games = document["games"]
        for game in games:
            if game["date"] == date_arg:
                id = document["_id"]
                players[id] = game

    player_game_list = list()

    for id in players:
        player = players_collection.find({"_id": id})[0]
        name = player["first_name"] + " " + player["last_name"]
        team = player["team"]["abbrev"]

        game = players[id]

        home = game["home"]
        away = game["away"]
        matchup = home + " vs. " + away if home == team else home + " @ " + away

        winner = game["winner"]
        if winner == "Undecided":
            wl = "Ongoing"
        else:
            wl = "W" if home == winner else "L"

        stats = game["statistics"]

        min = stats["min"]
        fgm = stats["fgm"]
        fga = stats["fga"]
        fg_pct = stats["fg_pct"]
        fg3m = stats["fg3m"]
        fg3a = stats["fg3a"]
        fg3_pct = stats["fg3_pct"]
        ftm = stats["ftm"]
        fta = stats["fta"]
        ft_pct = stats["ft_pct"]
        reb = stats["reb"]
        ast = stats["ast"]
        stl = stats["stl"]
        blk = stats["blk"]
        tov = stats["tov"]
        pf = stats["pf"]
        pts = stats["pts"]
        plus_minus = stats["plus_minus"]
        linear_PER = stats["linear_PER"]

        player_game = {
            "name": name,
            "matchup": matchup,
            "wl": wl,
            "min": min,
            "fgm": fgm,
            "fga": fga,
            "fg_pct": fg_pct,
            "fg3m": fg3m,
            "fg3a": fg3a,
            "fg3_pct": fg3_pct,
            "ftm": ftm,
            "fta": fta,
            "ft_pct": ft_pct,
            "reb": reb,
            "ast": ast,
            "stl": stl,
            "blk": blk,
            "tov": tov,
            "pf": pf,
            "pts": pts,
            "plus_minus": plus_minus,
            "linear_PER": linear_PER
        }

        player_game_list.append(player_game)

    if tie_breaker_stat is not None:
        player_game_list.sort(key=lambda g: (g[stat_arg], g[tie_breaker_stat_arg]))
    else:
        player_game_list.sort(key=lambda g: g[stat_arg])
    return player_game_list


def parse_stat(stat):
    stat = stat.lower()

    switch = {
        "min": "min",
        "minutes": "min",
        "minute": "min",

        "fgm": "fgm",

        "fga": "fga",

        "fg_pct": "fg_pct",
        "fgpct": "fg_pct",
        "fg%": "fg_pct",

        "fg3m": "fg3m",
        "3pm": "fg3m",

        "fg3a": "fg3a",
        "3pa": "fg3a",

        "fg3_pct": "fg3_pct",
        "fg3pct": "fg3_pct",
        "fg3%": "fg3_pct",
        "3p_pct": "fg3_pct",
        "3ppct": "fg3_pct",
        "3p%": "fg3_pct",

        "ftm": "ftm",

        "fta": "fta",

        "ft_pct": "ft_pct",
        "ftpct": "ft_pct",
        "ft%": "ft_pct",

        "oreb": "oreb",
        "o_reb": "oreb",

        "dreb": "dreb",
        "d_reb": "dreb",

        "reb": "reb",
        "rebound": "reb",
        "rebounds": "reb",

        "ast": "ast",
        "assist": "ast",
        "assists": "ast",

        "stl": "stl",
        "steal": "stl",
        "steals": "stl",

        "blk": "blk",
        "block": "blk",
        "blocks": "blk",

        "tov": "tov",
        "to": "tov",
        "turnover": "tov",
        "turnovers": "tov",

        "pf": "pf",
        "foul": "pf",
        "fouls": "pf",

        "pts": "pts",
        "pt": "pts",
        "point": "pts",
        "points": "pts",

        "plus_minus": "plus_minus",
        "plus/minus": "plus_minus",
        "+/-": "plus_minus",
        "+-": "plus_minus",
        "pm": "plus_minus",
        "p/m": "plus_minus",
        "plusminus": "plus_minus",

        "linear_per": "linear_PER",
        "linearper": "linear_PER",
        "lper": "linear_PER",
        "l_per": "linear_PER",
        "per": "linear_PER"
    }

    return switch.get(stat, "invalid")


def parse_date(date):
    date = date.replace("/", "-")

    date_array = date.split("-")
    if len(date_array) > 3 or len(date_array) < 2:
        return "invalid"

    if len(date_array) == 2:
        # MM-DD
        if len(date_array[0]) > 2 or len(date_array[1]) > 2:
            return "invalid"
        if len(date_array[0]) == 1:
            date_array[0] = "0" + date_array[0]
        if len(date_array[1]) == 1:
            date_array[1] = "0" + date_array[1]

        if date_array[0][0] == "0":
            date_array.insert(0, "2016")
        else:
            date_array.insert(0, "2015")
        date = "-".join(date_array)

    else:
        # YYYY-MM-DD
        if len(date_array[0]) > 4 or len(date_array[0]) == 3 or len(date_array[1]) > 2 or len(date_array[2]) > 2:
            return "invalid"
        if len(date_array[0]) == 2:
            date_array[0] = "20" + date_array[0]  # 2015 or 2016
        if len(date_array[1]) == 1:
            date_array[1] = "0" + date_array[1]
        if len(date_array[2]) == 1:
            date_array[2] = "0" + date_array[2]

        date = "-".join(date_array)
    return date
