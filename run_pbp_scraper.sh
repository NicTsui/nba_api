#!/bin/bash

# --- Configuration ---
SEASON="2018-19"
SEASON_TYPES=("Regular Season" "Playoffs" "Pre Season" "All Star")
BATCH_SIZE=500
SLEEP_DURATION=180 # 3 minutes in seconds

echo "Starting the NBA PBP data scraping process for the ${SEASON} season."

for SEASON_TYPE in "${SEASON_TYPES[@]}"; do
    echo "====================================================="
    echo "Starting download for Season Type: ${SEASON_TYPE}"
    echo "====================================================="

    while true; do
        echo "-----------------------------------------------------"
        echo "Running Python script for '${SEASON_TYPE}' to fetch a batch of up to ${BATCH_SIZE} games..."
        echo "Start time: $(date)"
        
        # Execute the Python script and capture its output in real-time
        output=$(script -q /dev/null poetry run python3 get_all_pbp_data.py --season "$SEASON" --season-type "$SEASON_TYPE" --batch-size "$BATCH_SIZE")
        
        # Print the captured output
        echo "$output"

        # --- Check for Completion Conditions for the current SEASON_TYPE ---
        # 1. If the script explicitly states all games are processed.
        if echo "$output" | grep -q "All games for the season have already been processed"; then
            echo "Success: All games for '${SEASON_TYPE}' have been processed. Moving to the next season type."
            break # Exit the inner while loop
        fi

        # 2. If the script indicates 0 games are left to process.
        if echo "$output" | grep -q "REMAINING_GAMES_COUNT:0"; then
            echo "Success: All remaining games for '${SEASON_TYPE}' have been processed. Moving to the next season type."
            break # Exit the inner while loop
        fi
        
        # 3. If the script failed to find games for this season type.
        if echo "$output" | grep -q "Failed to find games for season"; then
            echo "Warning: The script failed to retrieve the game list for '${SEASON_TYPE}'. Moving to the next season type."
            break # Exit the inner while loop
        fi

        echo "Batch finished. Waiting for ${SLEEP_DURATION} seconds before the next run..."
        sleep "$SLEEP_DURATION"
    done
done

echo "====================================================="
echo "Scraping process complete for all season types."
echo "End time: $(date)"