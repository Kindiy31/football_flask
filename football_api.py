import requests
from data import api_key
import json

def get_live_table_data():
    url = 'https://api.football-data.org/v2/competitions/PL/standings'
    headers = {'X-Auth-Token': api_key}  # Потрібно отримати API-токен на football-data.org
    response = requests.get(url, headers=headers)
    data = response.json()
    standings = data['standings'][0]['table']
    table_data = []

    for team in standings:
        team_name = team['team']['name']
        points = team['points']
        matches_played = team['playedGames']
        wins = team['won']
        draws = team['draw']
        losses = team['lost']

        table_data.append({
            'team': team_name,
            'points': points,
            'matches_played': matches_played,
            'wins': wins,
            'draws': draws,
            'losses': losses
        })

    return table_data

print(get_live_table_data())