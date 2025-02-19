import csv
import numpy as np

# Load game data
results = 'Data/full_results.csv'
game_data = []
with open(results, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    for row in csv_reader:
        game_data.append(row)

# Load team data and create ID to name mapping
team_data = []
team_ids = 'Data/MTeams.csv'
with open(team_ids, newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        team_data.append(row)
team_dict = {row[0]: row[1] for row in team_data}

# WIP