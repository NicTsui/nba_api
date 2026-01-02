import os
import time
import json
import argparse
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv3
from nba_api.stats.library.parameters import SeasonType
import pandas as pd

# --- Argument Parser Setup ---
parser = argparse.ArgumentParser(description="Fetch NBA play-by-play data for a specific season.")
parser.add_argument("--season", type=str, default="2023-24", help="The season to fetch data for (e.g., '2023-24').")
parser.add_argument("--season-type", type=str, default=SeasonType.regular, help="The season type to fetch data for (e.g., 'Regular Season', 'Playoffs').")
parser.add_argument("--batch-size", type=int, default=500, help="Maximum number of games to process in one run.")
args = parser.parse_args()

# --- Constants and Configuration ---
SEASON = args.season
SEASON_TYPE = args.season_type
BATCH_SIZE = args.batch_size
TIMEOUT = 60

CUSTOM_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://stats.nba.com/',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

# --- Directory Setup ---
output_dir = "pbp_data"
os.makedirs(output_dir, exist_ok=True)

# --- Main Script ---
def main():
    # Get all games for the specified season
    print(f"Finding all games for the {SEASON} {SEASON_TYPE}...")
    game_finder = None
    all_game_ids = []
    try:
        game_finder = leaguegamefinder.LeagueGameFinder(
            season_nullable=SEASON,
            season_type_nullable=SEASON_TYPE,
            league_id_nullable="00",
            headers=CUSTOM_HEADERS,
            timeout=TIMEOUT
        )
        games = game_finder.get_data_frames()[0]
        all_game_ids = games["GAME_ID"].unique()
        print(f"Found {len(all_game_ids)} total games for the {SEASON} {SEASON_TYPE}.")
    except Exception as e:
        print(f"Failed to find games for season {SEASON}: {e}")
        if game_finder and hasattr(game_finder, 'nba_response') and game_finder.nba_response:
            print(f"API Response: {json.dumps(game_finder.nba_response.get_dict(), indent=2)}")
        return  # Exit if we can't get the game list

    # Identify games that still need to be processed
    pending_game_ids = []
    for game_id in all_game_ids:
        file_path = os.path.join(output_dir, f"pbp_data_{game_id}.csv")
        unavailable_marker_path = file_path.replace('.csv', '.unavailable')
        if not os.path.exists(file_path) and not os.path.exists(unavailable_marker_path):
            pending_game_ids.append(game_id)

    if not pending_game_ids:
        print("All games for the season have already been processed. Nothing to do.")
        return

    # Limit to the next batch
    games_to_process = pending_game_ids[:BATCH_SIZE]
    print(f"Found {len(pending_game_ids)} games to process. This run will handle a batch of {len(games_to_process)}.")

    # Process the batch of games
    for i, game_id in enumerate(games_to_process):
        print(f"Processing game {i+1}/{len(games_to_process)}: {game_id}...")
        file_path = os.path.join(output_dir, f"pbp_data_{game_id}.csv")

        try:
            pbp = playbyplayv3.PlayByPlayV3(
                game_id=game_id,
                timeout=TIMEOUT,
                headers=CUSTOM_HEADERS,
                get_request=False
            )
            pbp.get_request()
            
            response_dict = pbp.nba_response.get_dict()

            if not response_dict or 'game' not in response_dict or not response_dict['game']['actions']:
                print(f"  Data not available or empty for game {game_id}. Marking as unavailable.")
                with open(file_path.replace('.csv', '.unavailable'), 'w') as f:
                    f.write(f"Data not available for game {game_id} as of {time.ctime()}")
                continue

            pbp_df = pbp.get_data_frames()[0]
            pbp_df.to_csv(file_path, index=False)
            print(f"  Successfully saved PBP data for game {game_id} to {file_path}")

        except Exception as e:
            print(f"  An unexpected error occurred for game {game_id}: {e}. Skipping.")

        time.sleep(0.6)
    
    remaining_games = len(pending_game_ids) - len(games_to_process)
    print(f"\nFinished processing batch. REMAINING_GAMES_COUNT:{remaining_games}")

if __name__ == "__main__":
    main()