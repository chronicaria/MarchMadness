# Result_Data.csv
# Wyoming,0.8987999999999173,Air Force,0.10120000000000187
# Davidson,0.5638999999999542,Loyola-Chicago,0.4360999999999683

#Ranking,Team,Wins,Losses,ELO
# 1,Auburn,23,2,1877.73
# 2,Houston,21,4,1817.93

import csv

results = 'Result_Data.csv'  
result_data = []
with open(results, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # skip header row
    for row in csv_reader:
        result_data.append(row)

teams = 'Final_Team_ELOs.csv'  
team_data = []
with open(teams, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # skip header row
    for row in csv_reader:
        team_data.append(row)

team_dict = {}
for team in team_data:
    team_dict[team[1]] = team[4]

record_data = {} # Team, array[win, loss]
for team in team_data:
    record_data[team[1]] = [int(team[2]), int(team[3])]


# 2. ELO Variables
k = 60
home_advantage = 150
spread_factor = 40
error_sd = 8.953

import numpy as np

for game in result_data:
    game_home_advantage = home_advantage
    if (game[4] == "N"):
        game_home_advantage = 0

    Rating_A = float(team_dict[game[0]])
    Rating_B = float(team_dict[game[2]])

    expected_spread = float(game[5])/10000
    actual_spread = expected_spread + np.random.normal(0, error_sd, 1)[0]

    if (actual_spread > 0): # home team win:
        Win_A = 1
        Win_B = 0
        record_data.get(game[0], [0, 0])[0] += 1
        record_data.get(game[2], [0, 0])[1] += 1
    else:
        Win_A = 0
        Win_B = 1
        record_data.get(game[0], [0, 0])[1] += 1
        record_data.get(game[2], [0, 0])[0] += 1
    
    Expected_A = round(1 / (1 + 10**((Rating_B - (Rating_A + game_home_advantage))/500)), 4)
    Expected_B = round(1 / (1 + 10**(((Rating_A + game_home_advantage) - Rating_B)/500)), 4)

    multiplier = np.log(abs(actual_spread)/3 + 1) * (2 / ((Rating_A - Rating_B)*.001+2)) #2.2
    team_dict[game[0]] = Rating_A + (k * multiplier) * (Win_A - Expected_A)
    team_dict[game[2]] = Rating_B + (k * multiplier) * (Win_B - Expected_B)

    # Home Team, Wins, Away Team, Losses, Neutral?, Spread (All Numbers / 10000)
    # Wyoming,8800,Air Force,1200,0,106000.00000001588

# Print the sorted teams
# Sort teams by ELO in descending order
sorted_teams = sorted(team_dict.items(), key=lambda x: x[1], reverse=True)

# Print the teams in the desired format
for i, (team, elo) in enumerate(sorted_teams[:10], start=1):
    wins, losses = record_data.get(team,[0, 0])
    if (wins == 0 & losses == 0):
        continue
    print(f"{i}. {team} ({wins}-{losses}): {elo:.2f}")

# POST-SEASON: MARCH MADNESS
bracket = 'Bracket.csv'  
bracket_data = []
with open(bracket, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # skip header row
    for row in csv_reader:
        bracket_data.append(row)

# First Four (Mar 18-19)
    # South 11 seeds, 16 seeds
    # East 12 seeds, 16 seeds

# First Round (Mar 20 - 21)

# Second Round (Mar 22 - 23)

# Sweet 16 (Regional Semifinals) (Mar 27 - 28)

# Elite 8 (Regional Finals) (Mar 29 - 30)

# Final Four (National Semifinals) (Apr 5)

# National Championship (Apr 7)

