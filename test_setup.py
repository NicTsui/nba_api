from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# 1. 查找勒布朗·詹姆斯 (LeBron James) 的 ID
nba_players = players.get_players()
lebron = [player for player in nba_players if player['full_name'] == 'LeBron James'][0]
lebron_id = lebron['id']

print(f"LeBron James ID: {lebron_id}")

# 2. 获取他的职业生涯数据
career = playercareerstats.PlayerCareerStats(player_id=lebron_id)
df = career.get_data_frames()[0]

# 3. 打印前几行数据
print("\n职业生涯数据 (前5行):")
print(df.head())
