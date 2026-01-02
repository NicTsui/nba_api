from nba_api.live.nba.endpoints import scoreboard

# 获取当天的记分板数据
board = scoreboard.ScoreBoard()
print("今日比赛:")
games = board.games.get_dict()

for game in games:
    print(f"{game['gameId']}: {game['awayTeam']['teamName']} vs {game['homeTeam']['teamName']}")
