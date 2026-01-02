import os
import time
import json
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv3
from nba_api.stats.library.parameters import Season
import pandas as pd

# Season to get data for
SEASON = "2021-22"
TIMEOUT = 60

# Custom headers based on successful requests and project changelog
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

# Create a directory to store the PBP data
output_dir = "pbp_data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get all games for the specified season
print(f"Finding all games for the {SEASON} season...")
game_finder = None  # Initialize before try block
game_ids = []
try:
    game_finder = leaguegamefinder.LeagueGameFinder(
        season_nullable=SEASON, league_id_nullable="00", headers=CUSTOM_HEADERS, timeout=TIMEOUT
    )
    games = game_finder.get_data_frames()[0]
    game_ids = games["GAME_ID"].unique()
    print(f"Found {len(game_ids)} games for the {SEASON} season.")
except Exception as e:
    print(f"Failed to find games for season {SEASON}: {e}")
    if game_finder and hasattr(game_finder, 'nba_response') and game_finder.nba_response:
        print(f"API Response: {json.dumps(game_finder.nba_response.get_dict(), indent=2)}")

# Use a check that works for both numpy arrays and lists
if len(game_ids) > 0:
    for i, game_id in enumerate(game_ids):
        print(f"Processing game {i+1}/{len(game_ids)}: {game_id}...")
        file_path = os.path.join(output_dir, f"pbp_data_{game_id}.csv")

        if os.path.exists(file_path):
            print(f"  Data for game {game_id} already exists. Skipping.")
            continue
        
        # Also check for the .unavailable marker
        if os.path.exists(file_path.replace('.csv', '.unavailable')):
            print(f"  Data for game {game_id} is known to be unavailable. Skipping.")
            continue

        try:
            # Initialize the endpoint without making the request immediately
            pbp = playbyplayv3.PlayByPlayV3(
                game_id=game_id,
                timeout=TIMEOUT,
                headers=CUSTOM_HEADERS,
                get_request=False
            )
            # Manually trigger the request
            pbp.get_request()
            
            # Get the raw dictionary from the response
            response_dict = pbp.nba_response.get_dict()

            # Check if the response is empty or indicates no data
            if not response_dict or 'game' not in response_dict:
                print(f"  Data not available for game {game_id}. The API returned an empty or invalid response. Skipping.")
                # Create a marker file to avoid retrying
                with open(file_path.replace('.csv', '.unavailable'), 'w') as f:
                    f.write(f"Data not available for game {game_id} as of {time.ctime()}")
                continue

            # If data is present, get the DataFrame
            pbp_df = pbp.get_data_frames()[0]

            # Save the PBP data to a CSV file
            pbp_df.to_csv(file_path, index=False)
            print(f"  Successfully saved PBP data for game {game_id} to {file_path}")

        except Exception as e:
            print(f"  An unexpected error occurred for game {game_id}: {e}. Skipping.")

        # Add a delay to avoid making too many requests in a short period
        time.sleep(0.6)
    
    print("\nFinished processing all games.")
else:
    print("\nCould not retrieve game list. Unable to process any games.")
