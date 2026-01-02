from nba_api.stats.endpoints import playbyplayv3
import json
import pandas as pd

# 这里使用 2024年总决赛 G5 (凯尔特人 vs 独行侠) 作为示例 ID
# 你也可以替换为你从 test_live.py 中获取的今日比赛 ID
game_id = '0042300405'
output_filename = f"pbp_data_{game_id}.csv"

print(f"正在获取比赛 {game_id} 的逐回合数据...")

# 1. 初始化接口 (使用 get_request=False 避免立即报错)
pbp = playbyplayv3.PlayByPlayV3(game_id=game_id, get_request=False)

try:
    # 2. 手动触发请求
    pbp.get_request()
    
    # 3. 获取 DataFrame
    df = pbp.get_data_frames()[0]

    # 4. 保存完整数据到 CSV
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ 成功！完整比赛数据已保存到文件: {output_filename}")

    # 5. 筛选关键列以便在屏幕上预览
    columns = ['clock', 'description', 'scoreHome', 'scoreAway']
    print(f"\n--- 比赛数据预览 (前 10 个回合) ---")
    print(df[columns].head(10))


except Exception as e:
    print(f"\n请求出错: {e}")
    if hasattr(pbp, 'nba_response'):
        print(f"API 响应内容: {json.dumps(pbp.nba_response.get_dict(), indent=2)}")