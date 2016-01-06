import requests
import os.path


def init():
    players_dir = "players"
    all_players = "players.txt"

    if not os.path.exists(all_players):
        download_player_info(all_players)

    if not os.path.exists(players_dir):
        os.makedirs(players_dir)


def download_json(json_url):
    response = requests.get(json_url)
    response.raise_for_status()
    return response.json()

# def calculateUnadjustedPER():
#     factor = (2 / 3) - (0.5 * ())


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


def create_player_season_file(name, team, id):

    path = "players/" + name + ".txt"

    print("Acquring data for " + name + "...")

    player_file = open(path, "w")

    url = "http://stats.nba.com/stats/playergamelog?PlayerID=" + str(id) + "&Season=2015-16&SeasonType=Regular+Season"
    season_info = download_json(url)

    player_file.write(name + "\n")
    player_file.write(team + "\n")
    player_file.write("\n")

    player_file.write("Date\t\tMatchup\t\tWL\tMIN\tFGM\tFGA\tFG%\t3PM\tFTM\tFTA\tFT%\tREB\tAST\tSTL\tBLK\tTOV\tPF\tPTS\t+/-\n")
    games = season_info['resultSets'][0]['rowSet']

    total_games = 0
    total_min = 0
    total_fgm = 0
    total_fga = 0
    total_fg3m = 0
    total_ftm = 0
    total_fta = 0
    total_reb = 0
    total_ast = 0
    total_stl = 0
    total_blk = 0
    total_tov = 0
    total_pf = 0
    total_pts = 0
    total_plus_minus = 0

    for i in range(0, len(games)):
        game = games[i]
        total_games += 1

        date = game[3]
        matchup = game[4]
        wl = game[5]

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

        player_file.write(date + "\t" + matchup + "\t" + wl + "\t" + str(min) + "\t" + str(fgm) + "\t" + str(fga) + "\t" + str(fg_pct) + "\t" + str(fg3m) + "\t" + str(ftm) + "\t" + str(fta) + "\t" + str(ft_pct) + "\t" + str(reb) + "\t" + str(ast) + "\t" + str(stl) + "\t" + str(blk) + "\t" + str(tov) + "\t" + str(pf) + "\t" + str(pts) + "\t" + str(plus_minus) + "\n")

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
        player_file.write("\n\t\tTotal\t\tGames\tMIN\tFGM\tFGA\tFG%\t3PM\tFTM\tFTA\tFT%\tREB\tAST\tSTL\tBLK\tTOV\tPF\tPTS\t+/-\n")
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

        # player averages
        player_file.write("\n\t\tAverage\t\t\tMIN\tFGM\tFGA\tFG%\t3PM\tFTM\tFTA\tFT%\tREB\tAST\tSTL\tBLK\tTOV\tPF\tPTS\n")
        player_file.write("\t\t\t\t\t" + avg_min + "\t" + avg_fgm + "\t" + avg_fga + "\t" + avg_fg_pct + "\t" + avg_fg3m + "\t" + avg_ftm + "\t" + avg_fta + "\t" + avg_ft_pct + "\t" + avg_reb + "\t" + avg_ast + "\t" + avg_stl + "\t" + avg_blk + "\t" + avg_tov + "\t" + avg_pf + "\t" + avg_pts + "\t" + str(total_plus_minus) + "\n")

    player_file.close()

    # sec = 0.2
    # time.sleep(sec)
