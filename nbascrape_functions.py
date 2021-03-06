import requests
import os.path
from colors import Color
import sys
from urllib.request import Request, urlopen

class League:
    GOOD_FG_PCT = 0.52
    BAD_FG_PCT = 0.37

    GOOD_FG3M = 2.4
    BAD_FG3M = 0.1

    GOOD_FT_PCT = 0.88
    BAD_FT_PCT = 0.57

    GOOD_REB = 9.5
    BAD_REB = 1.7

    GOOD_AST = 6.15
    BAD_AST = 0.1

    GOOD_STL = 1.75
    BAD_STL = 0.3

    GOOD_BLK = 1.57
    BAD_BLK = 0.1

    GOOD_TOV = 0.5
    BAD_TOV = 3.0

    GOOD_PTS = 21.4
    BAD_PTS = 6.3

    GOOD_PER = 25.0
    BAD_PER = 5.0


def init():
    players_dir = "players"
    all_players = "players.txt"

    if not os.path.exists(all_players):
        download_player_info(all_players)

    if not os.path.exists(players_dir):
        os.makedirs(players_dir)


def download_json(json_url):
    # response = requests.get(json_url)
    response = requests.get(json_url, headers={'User-Agent': 'Mozilla/5.0'})
    response.raise_for_status()
    return response.json()

def calculateLinearPER(min, fgm, fga, fg3m, ftm, fta, oreb, dreb, ast, stl, blk, tov, pf, pts):
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


# Downloads player info into a file called players.txt
def download_player_info(players_file_name):
    all_players_url = 'http://stats.nba.com/stats/commonallplayers?LeagueID=00&Season=2015-16&IsOnlyCurrentSeason=1'
    nba_players = download_json(all_players_url)
    players_info = nba_players['resultSets'][0]['rowSet']

    players_file = open(players_file_name, "w")
    for i in range(0, len(players_info)):
        player = players_info[i]

        last_first = player[1].split(',')
        if len(last_first) > 1:
            name = last_first[1][1:] + " " + last_first[0]
        else:
            name = last_first[0]
        id = player[0]
        team = player[9]
        players_file.write(name + "," + team + "," + str(id) + "\n")

    players_file.close()


def create_player_season_file(name, team, id, season):

    path = "players/" + name + ".txt"

    print("Acquring data for " + name + "...")

    player_file = open(path, "w")

    url = "http://stats.nba.com/stats/playergamelog?PlayerID=" + str(id) + "&Season=2015-16&SeasonType={0}".format(season)
    season_info = download_json(url)

    player_file.write(name + "\t")
    player_file.write(team + "\n")
    player_file.write("\n")

    player_file.write(Color.YELLOW + "Date\t\tMatchup\t\tWL\tMIN\tFGM\tFGA\tFG%\t3PM\tFTM\tFTA\tFT%\tREB\tAST\tSTL\tBLK\tTOV\tPF\tPTS\t+/-\tPER\n" + Color.NONE)
    games = season_info['resultSets'][0]['rowSet']

    total_games = 0
    total_min = 0
    total_fgm = 0
    total_fga = 0
    total_fg3m = 0
    total_ftm = 0
    total_fta = 0
    total_oreb = 0
    total_dreb = 0
    total_reb = 0
    total_ast = 0
    total_stl = 0
    total_blk = 0
    total_tov = 0
    total_pf = 0
    total_pts = 0
    total_plus_minus = 0

    for game in reversed(games):
        total_games += 1

        date = game[3]
        matchup = game[4]
        wl = game[5]
        if wl is None:
            wl = "Ongoing"

        min = game[6]
        total_min += min

        fgm = game[7]
        total_fgm += fgm

        fga = game[8]
        total_fga += fga

        if fga != 0:
            fg_pct = fgm / fga
            fg_pct = "%.3f" % fg_pct
        else:
            fg_pct = "%.3f" % 0

        fg3m = game[10]
        total_fg3m += fg3m

        ftm = int(game[13])
        total_ftm += ftm

        fta = game[14]
        total_fta += fta

        if fta != 0:
            ft_pct = ftm / fta
            ft_pct = "%.3f" % ft_pct
        else:
            ft_pct = "%.3f" % 0

        oreb = game[16]
        total_oreb += oreb

        dreb = game[17]
        total_dreb += dreb

        reb = game[18]
        total_reb += reb

        ast = game[19]
        total_ast += ast

        stl = game[20]
        total_stl += stl

        blk = game[21]
        total_blk += blk

        tov = game[22]
        total_tov += tov

        pf = game[23]
        total_pf += pf

        pts = game[24]
        total_pts += pts

        plus_minus = game[25]
        total_plus_minus += plus_minus

        per = calculateLinearPER(min, fgm, fga, fg3m, ftm, fta, oreb, dreb, ast, stl, blk, tov, pf, pts)
        per = "%.3f" % per

        player_file.write(date + "\t" + matchup + "\t" + wl + "\t" + str(min) + "\t" + str(fgm) + "\t" + str(fga) + "\t" + str(fg_pct) + "\t" + str(fg3m) + "\t" + str(ftm) + "\t" + str(fta) + "\t" + str(ft_pct) + "\t" + str(reb) + "\t" + str(ast) + "\t" + str(stl) + "\t" + str(blk) + "\t" + str(tov) + "\t" + str(pf) + "\t" + str(pts) + "\t" + str(plus_minus) + "\t" + str(per) + "\n")

    if total_games > 0:

        if total_fga != 0:
            avg_fg_pct = total_fgm / total_fga
            avg_fg_pct = "%.3f" % avg_fg_pct
        else:
            avg_fg_pct = "%.3f" % 0

        if total_fta != 0:
            avg_ft_pct = total_ftm / total_fta
            avg_ft_pct = "%.3f" % avg_ft_pct
        else:
            avg_ft_pct = "%.3f" % 0

        # player totals
        player_file.write(Color.YELLOW + "\n\t\tTotal\t\tGames\tMIN\tFGM\tFGA\tFG%\t3PM\tFTM\tFTA\tFT%\tREB\tAST\tSTL\tBLK\tTOV\tPF\tPTS\t+/-\n" + Color.NONE)
        player_file.write("\t\t\t\t" + str(total_games) + "\t" + str(total_min) + "\t" + str(total_fgm) + "\t" + str(total_fga) + "\t" + avg_fg_pct + "\t" + str(total_fg3m) + "\t" + str(total_ftm) + "\t" + str(total_fta) + "\t" + avg_ft_pct + "\t" + str(total_reb) + "\t" + str(total_ast) + "\t" + str(total_stl) + "\t" + str(total_blk) + "\t" + str(total_tov) + "\t" + str(total_pf) + "\t" + str(total_pts) + "\t" + str(total_plus_minus) + "\n")

        avg_min = total_min / total_games
        avg_min = "%.3f" % avg_min

        avg_fgm = total_fgm / total_games
        avg_fgm = "%.3f" % avg_fgm

        avg_fga = total_fga / total_games
        avg_fga = "%.3f" % avg_fga

        avg_fg3m = total_fg3m / total_games
        avg_fg3m = "%.3f" % avg_fg3m

        avg_ftm = total_ftm / total_games
        avg_ftm = "%.3f" % avg_ftm

        avg_fta = total_fta / total_games
        avg_fta = "%.3f" % avg_fta

        avg_reb = total_reb / total_games
        avg_reb = "%.3f" % avg_reb

        avg_ast = total_ast / total_games
        avg_ast = "%.3f" % avg_ast

        avg_stl = total_stl / total_games
        avg_stl = "%.3f" % avg_stl

        avg_blk = total_blk / total_games
        avg_blk = "%.3f" % avg_blk

        avg_tov = total_tov / total_games
        avg_tov = "%.3f" % avg_tov

        avg_pf = total_pf / total_games
        avg_pf = "%.3f" % avg_pf

        avg_pts = total_pts / total_games
        avg_pts = "%.3f" % avg_pts

        avg_per = calculateLinearPER(total_min, total_fgm, total_fga, total_fg3m, total_ftm, total_fta, total_oreb, total_dreb, total_ast, total_stl, total_blk, total_tov, total_pf, total_pts)
        avg_per = "%.3f" % avg_per

        # player averages
        player_file.write(Color.YELLOW + "\n\t\tAverage\t\t\tMIN\tFGM\tFGA\tFG%\t3PM\tFTM\tFTA\tFT%\tREB\tAST\tSTL\tBLK\tTOV\tPF\tPTS\t+/-\tPER\n" + Color.NONE)
        player_file.write("\t\t\t\t\t" + avg_min + "\t" + avg_fgm + "\t" + avg_fga + "\t" + avg_fg_pct + "\t" + avg_fg3m + "\t" + avg_ftm + "\t" + avg_fta + "\t" + avg_ft_pct + "\t" + avg_reb + "\t" + avg_ast + "\t" + avg_stl + "\t" + avg_blk + "\t" + avg_tov + "\t" + avg_pf + "\t" + avg_pts + "\t" + str(total_plus_minus) + "\t" + avg_per + "\n")

    player_file.close()

    # sec = 0.2
    # time.sleep(sec)


def download_player_images():
    image_dir = "player_images"

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    log_file = open("download_player_images_logs.txt", "w")
    log_file.write("Failed to download: \n")
    image_url_start = 'http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/'
    image_url_end = '.png'

    players = open("players.txt", "r")
    lines = players.read()
    lines = lines.split("\n")
    for line in lines:
        player_info = line.split(",")
        if len(player_info) < 2:
            # Complete.
            sys.exit()

        # Edit name
        name = edit_name(player_info[0])

        # Download image
        image_url = image_url_start + name + image_url_end

        try:
            download_web_image(image_url, image_dir + "/" + name)
        except urllib.error.HTTPError:
            print("Exception caught: Failed to download " + name)
            log_file.write(name + "\n")
            continue
            # sys.exit()
        print("Successfully downloaded " + name + ".png.")


def download_web_image(url, name):
    full_name = str(name) + ".png"
    urllib.request.urlretrieve(url, full_name)


def download_missed_players():
    image_dir = "player_images"
    image_url_start = 'http://i.cdn.turner.com/nba/nba/.element/img/2.0/sect/statscube/players/large/'
    image_url_end = '.png'
    # Guys that are always failed to download:
    missed_players = [
        'dj_augustin',
        'jose_barea',
        'timothy_hardaway',
        'oj_mayo',
        'etwaun_moore',
        'larry_nance',
        'jj_obrien',
        'johnny_obryant',
        'kyle_oquinn',
        'kelly_oubre',
        'dangelo_russell',
        'jr_smith',
        'amare_stoudemire'
    ]

    for name in missed_players:

        # Download image
        image_url = image_url_start + name + image_url_end

        try:
            download_web_image(image_url, image_dir + "/" + name)
        except urllib.error.HTTPError:
            print("Exception caught: Failed to download " + name)
            continue
            # sys.exit()
        print("Successfully downloaded " + name + ".png.")


def edit_name(name):
    return name.lower().replace(' ', '_').replace('.', '').replace("'", "")
    