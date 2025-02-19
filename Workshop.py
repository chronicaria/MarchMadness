# def predict(Home_Team, Away_Team, Neutral):

#     expected_spread = round((Rating_A + local_home_advantage - Rating_B) / spread_factor, 2)

#     Expected_A = round(1 / (1 + 10**((Rating_B - (Rating_A + local_home_advantage))/500))*100, 2)
#     print("Spread: " + str(expected_spread))
#     print("Chance of " + Home_Team + " winning: " + str(Expected_A))

# predict("Duke", "Illinois", "1")

predict_data = [
    ["Duke", "Illinois", "1"],
    ["Miami FL", "Duke", "0"],
    ["Duke", "Florida St", "0"],
    ["Duke", "Wake Forest", "0"],
    ["North Carolina", "Duke", "0"],

    ["Auburn", "Arkansas", "0"],
    ["Auburn", "Georgia", "0"],
    ["Auburn", "Mississippi", "0"],
    ["Kentucky", "Auburn", "0"],
    ["Texas A&M", "Auburn", "0"],
    ["Auburn", "Alabama", "0"]
]
result_data = np.zeros((len(predict_data), 2)) # Format: Home_Team wins, Away_team wins
win_list = []
# Format: Home_Team, Away_Team, Neutral

for i in range(10000): # 10k simulations
    simulation_team_ELOs = team_ELOs.copy()
    win_string = ""
    for game in range(len(predict_data)):
        local_home_advantage = home_advantage
        if (predict_data[game][2] == "1"):
            local_home_advantage = 0
        ID_A = [key for key, val in team_dict.items() if val == predict_data[game][0]][0]
        ID_B = [key for key, val in team_dict.items() if val == predict_data[game][1]][0]
        Rating_A = int(simulation_team_ELOs[ID_A])
        Rating_B = int(simulation_team_ELOs[ID_B])

        expected_spread = round((Rating_A + local_home_advantage - Rating_B) / spread_factor, 2)
        Expected_A = round(1 / (1 + 10**((Rating_B - (Rating_A + local_home_advantage))/500)), 2)
        Expected_B = 1 / (1 + 10**(((Rating_A + local_home_advantage) - Rating_B)/500))

        actual_spread = expected_spread + np.random.normal(0, error_sd, 1)
        if (actual_spread > 0): # home team win:
            result_data[game][0] += 1/10000
            Win_A = 1
            Win_B = 0
            win_string += "W"
        else:
            result_data[game][1] += 1/10000
            Win_A = 0
            Win_B = 1
            win_string += "L"
        
        multiplier = np.log(abs(actual_spread)/3 + 1) * (2 / ((Rating_A - Rating_B)*.001+2)) #2.2
        simulation_team_ELOs[ID_A] = Rating_A + (k * multiplier) * (Win_A - Expected_A)
        simulation_team_ELOs[ID_B] = Rating_B + (k * multiplier) * (Win_B - Expected_B)
    win_list.append(win_string)

# games included until 2025-01-28 

win_count = 0
for win in win_list:
    if (win == "WLWWLWWWLLW"): 
        win_count += 1

print(result_data)
print(win_count)