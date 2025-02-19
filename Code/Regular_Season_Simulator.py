# 1. Convert CSV into 2-D List
import csv
import numpy as np

results = 'Data/Team_ELOs.csv'  
rating_data = []
with open(results, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # skip header row
    for row in csv_reader:
        rating_data.append(row)
# Format:
# Team,ELO
# Auburn,1821.88

# Convert to dict
rating_dict = {}
for i in rating_data:
    rating_dict[i[0]] = float(i[1])

schedule = 'Data/2025_cleaned_schedule.csv'
schedule_data = []
with open(schedule, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # skip header row
    for row in csv_reader:
        schedule_data.append(row)
# Format:
# Date,Home Team,Home Score,Away Team,Away Score,Neutral
# 2024-11-04,Siena,72,Brown,71

# 2. ELO Variables
k = 60
home_advantage = 150
spread_factor = 40
error_sd = 8.953

start_date = "2025-02-19"

record_data = {} # Team, array[win, loss]
for i in rating_dict:
    record_data[i] = [0, 0]

for game in schedule_data:
    game_home_advantage = home_advantage
    if (game[0] == start_date):
        break
    if (len(game) == 6):
        game_home_advantage = 0

    Rating_A = rating_dict.get(game[1], 0)
    Rating_B = rating_dict.get(game[3], 0)
    Score_A = int(game[2])
    Score_B = int(game[4])

    Pd = abs(Score_A - Score_B)
    if (Score_A - Score_B > 0):
        Win_A, Win_B = 1, 0
        record_data.get(game[1], [0, 0])[0] += 1
        record_data.get(game[3], [0, 0])[1] += 1
    else:
        Win_A, Win_B = 0, 1
        record_data.get(game[1], [0, 0])[1] += 1
        record_data.get(game[3], [0, 0])[0] += 1

    multiplier = np.log(Pd/3 + 1) * (2 / ((Rating_A - Rating_B)*.001+2))
    Expected_A = 1 / (1 + 10**((Rating_B - (Rating_A + game_home_advantage))/500))
    Expected_B = 1 / (1 + 10**(((Rating_A + game_home_advantage) - Rating_B)/500))
    
    rating_dict[game[1]] = round(Rating_A + (k * multiplier) * (Win_A - Expected_A), 2)
    rating_dict[game[3]] = round(Rating_B + (k * multiplier) * (Win_B - Expected_B), 2)

# Sort teams by ELO in descending order
sorted_teams = sorted(rating_dict.items(), key=lambda x: x[1], reverse=True)

# Print teams
for i, (team, elo) in enumerate(sorted_teams, start=1):
    wins, losses = record_data.get(team,[0, 0])
    if (wins == 0 & losses == 0):
        continue
    print(f"{i}. {team} ({wins}-{losses}): {elo:.2f}")

# Save to CSV
with open('Data/Final_Team_ELOs.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Ranking", "Team", "Wins", "Losses", "ELO"])
    for i, (team, elo) in enumerate(sorted_teams, start=1):
        wins, losses = record_data.get(team,[0, 0])
        if (wins == 0 & losses == 0):
            continue
        writer.writerow([i, team, wins, losses, f"{elo:.2f}"])