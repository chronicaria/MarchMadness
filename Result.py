# Result_Data.csv
# #Wyoming,0.8987999999999173,Air Force,0.10120000000000187
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

team = input("Team: ")
team_full_data = []
for i in team_data:
    if (i[1] == team):
        team_full_data = i
        print(i[0] + ". " + i[1] + " (" + i[2] + "-" + i[3] + "): " + i[4] + " ELO")

print("_")
win_chances = []
for j in result_data:
    j[5] = round(float(j[5])/10000, 1)

    if (j[4] == "N"): # neutral game
        if (j[0] == team): #home game
            win_chance = round(float(j[1])/100, 1)
            win_chances.append(win_chance)
            print(j[0] + " (N) " + j[2] + ": " + str(win_chance) + "% | " + str(j[5]))
        if (j[2] == team): # away game
            win_chance = round(float(j[3])/100, 1)
            win_chances.append(win_chance)
            print(j[2] + " (N) " + j[0] + ": " + str(win_chance) + "% | " + str(j[5]*-1))
        continue

    if (j[0] == team): #home game
        win_chance = round(float(j[1])/100, 1)
        win_chances.append(win_chance)
        print(j[0] + " vs " + j[2] + ": " + str(win_chance) + "% | " + str(j[5]))
    if (j[2] == team): # away game
        win_chance = round(float(j[3])/100, 1)
        win_chances.append(win_chance)
        print(j[2] + " @ " + j[0] + ": " + str(win_chance) + "% | " + str(j[5]*-1))

win_all = 1
for i in win_chances:
    win_all *= i/100
win_all = round(win_all*100, 2)
print("_")
print("Win Out: " + str(win_all) + "%")

avg_wins = float(team_full_data[2])
avg_losses = float(team_full_data[3])
for i in win_chances:
    avg_wins += round(i/100, 2)
    avg_losses += 1 - round(i/100, 2)
avg_wins = round(avg_wins, 1)
avg_losses = round(avg_losses, 1)

print("Expected W/L: " + str(avg_wins) + "-" + str(avg_losses))

# #Wyoming,0.8987999999999173,Air Force,0.10120000000000187
# Davidson,0.5638999999999542,Loyola-Chicago,0.4360999999999683