
import requests
import json

GAME_ID = "0042400407"
URL = "https://stats.nba.com/stats/playbyplayv2"

PARAMS = {
    "GameID": GAME_ID,
    "StartPeriod": "0",
    "EndPeriod": "0",
}

HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Connection': 'keep-alive',
    'Referer': 'https://stats.nba.com/',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

print(f"Requesting data for Game ID: {GAME_ID}...")
print(f"URL: {URL}")
print(f"Params: {PARAMS}")

try:
    response = requests.get(URL, params=PARAMS, headers=HEADERS, timeout=60)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

    print(f"\nRequest successful! Status Code: {response.status_code}")
    
    # Try to parse and print pretty JSON
    try:
        data = response.json()
        print("\n--- API Response (JSON) ---")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError:
        print("\n--- API Response (Raw Text) ---")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"\nRequest failed: {e}")
