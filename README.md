nba.py FIRST LAST: View a player's 2015-16 stats on the terminal.

Usage:

python3 nba.py kevin durant

--------------------------------------------------------------------------------
nba.py -r DATE STAT [STAT2] : View a list of players who played on a given date sorted by a given stat.
Note: This only works after the nba_mongodb/nba_downloader.py script has run and finished.

Optional: STAT2: If a second stat is given, the list is sorted by both attributes.

Usage:

python3 nba.py -r 2015-12-25 per
python3 nba.py -r 01-25 ast stl
python3 nba.py -r 2016/1/20 points turnovers
python3 nba.py -r 1/10 ft% fta

--------------------------------------------------------------------------------

nba_mongodb/nba_downloader.py : Update a mongodb with player and player game information.

Usage:

python3 nba_mongodb/nba_downloader.py