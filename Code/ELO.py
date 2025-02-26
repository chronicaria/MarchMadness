# Men's
# 11.393, 0.3, 8.834


# 1. Convert CSV into 2-D List, skipping the header
import csv
import numpy as np

results = 'Data/full_results.csv'  
game_data = []
with open(results, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # skip header row
    for row in csv_reader:
        game_data.append(row)

# ap preseason poll data
preseason_results = 'Data/AP_Preseason_Polls.csv'  
preseason_poll_data = []
with open(preseason_results, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # skip header row
    for row in csv_reader:
        preseason_poll_data.append(row)

# 2. ELO Variables
base_ELO = 1500
reversion_factor = 1/3
k = 50
home_advantage = 140
spread_factor = 40
in_conference_multiplier = 0.7
out_conference_multiplier = 1.3

# 3. Find the Teams and Index them
team_data =[]
team_ids = 'Data/MTeams.csv'
with open(team_ids, newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        team_data.append(row)
team_dict = {}
for i in team_data:
    team_dict[i[0]] = i[1] # id, name pairs

# 3. Initialize team_ELOs
team_ELOs = {}
for game in game_data:
    wteam = game[2]
    lteam = game[4]
    team_ELOs[wteam] = base_ELO
    team_ELOs[lteam] = base_ELO

brier_scores = []
error_list = []
def calculate_elos(Rating_A, Rating_B, Score_A, Score_B, WLoc, Conf):
    local_home_advantage = home_advantage
    if (WLoc == "A"):
        local_home_advantage = -1*local_home_advantage
    if (WLoc == "N"):
        local_home_advantage = 0
    Pd = abs(Score_A - Score_B)
    if Score_A > Score_B:
        Win_A, Win_B = 1, 0
    else:
        Win_A, Win_B = 0, 1

    expected_spread = (Rating_A + local_home_advantage - Rating_B) / spread_factor
    actual_spread = Score_A - Score_B

    spread_differential = round(actual_spread - expected_spread, 2)
    error_list.append(spread_differential)

    multiplier = np.log(Pd/3 + 1) * (2 / ((Rating_A - Rating_B)*.001+2)) #2.2
    if (Conf == "Yes"):
        multiplier *= in_conference_multiplier
    else:
        multiplier *= out_conference_multiplier

    Expected_A = 1 / (1 + 10**((Rating_B - (Rating_A + local_home_advantage))/500))
    Expected_B = 1 / (1 + 10**(((Rating_A + local_home_advantage) - Rating_B)/500))
    brier_scores.append((Expected_A - Win_A)**2)

    New_Rating_A = Rating_A + (k * multiplier) * (Win_A - Expected_A)
    New_Rating_B = Rating_B + (k * multiplier) * (Win_B - Expected_B) 
    return [New_Rating_A, New_Rating_B]

conferences = 'Data/MTeamConferences.csv' 
conference_data = []
with open(conferences, newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # skip header row
    for row in csv_reader:
        conference_data.append(row)

cur_season = 1984
confs = {}

def yearly_reset():
    for i in conference_data:
        if (int(i[0]) == cur_season):
            confs.setdefault(i[2], []).append(i[1])

    # Season,TeamID,ConfAbbrev
    # 1985,1102,wac
    # 1985,1103,ovc
    # 1985,1104,sec

    # adjust based on ap preseason poll
    # +(26-x)*10, 20?
    for i in preseason_poll_data:
        if (int(i[0]) == cur_season):
            # team-key from value
            team_id = [key for key, val in team_dict.items() if val == i[2]][0]
            team_ELOs[team_id] += (26-int(i[1]))*5

    for conf in confs:
        id_list = confs[conf]
        conf_avg = 0
        conf_size = 0
        for id in id_list: #calculate avg
            conf_avg += team_ELOs[id]
            conf_size += 1
        conf_avg /= conf_size

        for id in id_list: # reversion to conf average
            team_ELOs[id] -= (team_ELOs[id] - conf_avg) * reversion_factor


def are_teams_in_same_conf(confs, team_a, team_b):
    def find_conference(team):
        for conf_name, teams in confs.items():
            if team in teams:
                return conf_name
        return None
    
    conf_a = find_conference(team_a)
    conf_b = find_conference(team_b)
    
    return "Yes" if conf_a == conf_b and conf_a is not None else "No"

for game in game_data:
    if (int(game[0]) != cur_season):
        cur_season += 1
        confs = {}
        yearly_reset()
    cur_season = int(game[0])

    wteam = game[2]
    lteam = game[4]
    wscore = int(game[3])
    lscore = int(game[5])
    
    # Get current ELOs
    rating_a = team_ELOs.get(wteam, base_ELO)
    rating_b = team_ELOs.get(lteam, base_ELO)

    conf_status = are_teams_in_same_conf(confs, wteam, lteam)

    # Calculate new ELOs
    new_elos = calculate_elos(rating_a, rating_b, wscore, lscore, game[6], conf_status)
    team_ELOs[wteam] = round(new_elos[0], 2)
    team_ELOs[lteam] = round(new_elos[1], 2)

yearly_reset()
team_names_list = []
team_ELO_list = []
for x in team_ELOs:
    # team_dict: id, name pairs
    team_names_list.append(team_dict[x])
    team_ELO_list.append(team_ELOs[x])
teams_with_ELO = zip(team_names_list, team_ELO_list)
sorted_teams = sorted(teams_with_ELO, key=lambda x: x[1], reverse=True)

# Print the sorted teams
for team, ELO in sorted_teams:
    print(f"{team}: {round(ELO, 2)}")

brier_skill_score = 1 - (round(sum(brier_scores) / len(brier_scores),3) / 0.25)
mse = 0
for x in error_list:
    mse += x*x
mse /= len(error_list)
rmse = round(np.sqrt(mse), 3)

# average_error = round(sum(error_list)/len(error_list),3)
error_sd = round(np.std(error_list),3)

print("_")
print("RMSE: " + str(rmse))
print("BSS: " + str(round(brier_skill_score,3)))
print("Error SD: " + str(error_sd))

export_list = [list(item) for item in sorted_teams]
with open('Team_ELOs.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Team", "ELO"])
    writer.writerows(sorted_teams)
