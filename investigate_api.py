
import requests
import json

# Headers copied from src/nba_api/stats/library/http.py
STATS_HEADERS = {
    "Host": "stats.nba.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://stats.nba.com/",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Sec-Ch-Ua": '"Chromium";v="140", "Google Chrome";v="140", "Not;A=Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Fetch-Dest": "empty",
}

# Parameters from test_pbp.py and playbyplayv2.py
params = {
    'GameID': '0042300405',
    'EndPeriod': '10',
    'StartPeriod': '1'
}

url = "https://stats.nba.com/stats/playbyplayv2"

try:
    response = requests.get(url, params=params, headers=STATS_HEADERS, timeout=30)
    print(f"Status Code: {response.status_code}")
    print("Response Text:")
    # Try to pretty-print if it's JSON, otherwise print as text
    try:
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
