import csv
import numpy as np
import copy

# --- Read Team Data ---
with open('Data/Final_Team_ELOs.csv', newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # Skip header row
    team_data = list(csv_reader)

# Build dictionaries from team data:
# team_dict: {Team: ELO} and record_dict: {Team: [Wins, Losses]}
team_dict = {row[1]: float(row[4]) for row in team_data}
record_dict = {row[1]: [int(row[2]), int(row[3])] for row in team_data}

# --- ELO Parameters ---
k = 60
home_advantage = 150
spread_factor = 40
error_sd = 8.953

# --- Define Game Simulation Function ---
def simulate_game(team_A, team_B, location):
    """
    Simulate a game between team_A and team_B.
    If location is 'N', then no home advantage is applied.
    Updates the global dictionaries: sim_team_dict and sim_record_dict.
    Returns 1 if team_A wins, 0 if team_B wins.
    """
    local_adv = 0 if location == "N" else home_advantage
    Rating_A = sim_team_dict[team_A]
    Rating_B = sim_team_dict[team_B]
    expected_spread = (Rating_A + local_adv - Rating_B) / spread_factor
    actual_spread = expected_spread + np.random.normal(0, error_sd)
    
    # Update win/loss records
    if actual_spread > 0:
        Win_A, Win_B = 1, 0
        sim_record_dict[team_A][0] += 1
        sim_record_dict[team_B][1] += 1
    else:
        Win_A, Win_B = 0, 1
        sim_record_dict[team_A][1] += 1
        sim_record_dict[team_B][0] += 1
    
    # Calculate expected win probabilities
    Expected_A = 1 / (1 + 10 ** ((Rating_B - (Rating_A + local_adv)) / 500))
    Expected_B = 1 / (1 + 10 ** (((Rating_A + local_adv) - Rating_B) / 500))
    
    # Update ELO ratings
    multiplier = np.log(abs(actual_spread) / 3 + 1) * (2 / ((Rating_A - Rating_B) * 0.001 + 2))
    sim_team_dict[team_A] = Rating_A + (k * multiplier) * (Win_A - Expected_A)
    sim_team_dict[team_B] = Rating_B + (k * multiplier) * (Win_B - Expected_B)

    return Win_A  # 1 if team_A wins, 0 if team_B wins

# --- Read Schedule Data ---
with open('Data/2025_cleaned_schedule.csv', newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    schedule_data = list(csv_reader)

# --- Read Bracket Data ---
with open('Data/Bracket.csv', newline='') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    bracket_data = list(csv_reader)
# Format for bracket_data (CSV):
# Region,Seed,Team
# e.g., South,1,Auburn

start_date = "2025-02-19"  # Only simulate games on or after this date
simulations = 1
simulation_records = {}  # Cumulative simulation records for season stats
game_results = {}

# --- Setup Tournament Bracket ---
# Create a 4x16 array for regions (order: South, Midwest, West, East)
updating_bracket = np.empty([4, 16], dtype='U50')
for i in bracket_data:
    seed = int(i[1]) - 1
    if i[0] == "South":
        updating_bracket[0][seed] = i[2]
    if i[0] == "Midwest":
        updating_bracket[1][seed] = i[2]
    if i[0] == "West":
        updating_bracket[2][seed] = i[2]
    if i[0] == "East":
        updating_bracket[3][seed] = i[2]

# --- Initialize Tournament Progress Dictionary ---
# This will track for each team: [t64, t32, t16, t8, t4, t2, t1]
tournament_progress = {}
# Initialize keys for every team in the tournament bracket.
for team in bracket_data:
    tournament_progress[team[2]] = [0, 0, 0, 0, 0, 0, 0]

# --- Helper Function for Updating Bracket (First Four, etc.) ---
def update_bracket(idx1, idx2, region_idx, bracket_pos):
    """
    Simulate a game between the two teams (from bracket_data at idx1 and idx2)
    and update sim_bracket at the given region and position.
    """
    winner = simulate_game(bracket_data[idx1][2], bracket_data[idx2][2], "N")
    sim_bracket[region_idx][bracket_pos] = bracket_data[idx1][2] if winner == 1 else bracket_data[idx2][2]

# --- Simulation Loop ---
for i in range(simulations):
    print(f"Simulation {i+1}")
    # Create simulation copies for team ratings, records, and tournament bracket
    sim_team_dict = team_dict.copy()
    sim_record_dict = copy.deepcopy(record_dict)
    sim_bracket = copy.deepcopy(updating_bracket)
    
    # --- Regular Season Simulation ---
    for game in schedule_data:
        if game[0] < start_date:
            continue

        home_team = game[1]
        away_team = game[3]
        location = "N" if (len(game) >= 6 and game[5].strip().upper() == "N") else "H"

        winner = simulate_game(home_team, away_team, location)

        if (game[0], home_team, away_team, location) not in game_results:
            game_results[(game[0], home_team, away_team, location)] = [0, 0]

        if winner == 1:
            game_results[(game[0], home_team, away_team, location)][0] += 1  # Home team win
        else:
            game_results[(game[0], home_team, away_team, location)][1] += 1  # Away team win
    
    # --- Bracket Simulation (First Four) ---
    update_bracket(11, 12, 0, 11)  # South: 12th seed matchup
    update_bracket(16, 17, 0, 15)  # South: 16th seed matchup
    update_bracket(60, 61, 3, 10)  # East: 11th seed matchup
    update_bracket(66, 67, 3, 15)  # East: 16th seed matchup

    # --- Tournament Simulation: Round of 64 ---
    round64_pairings = [(0, 15), (1, 14), (2, 13), (3, 12),
                          (4, 11), (5, 10), (6, 9),  (7, 8)]
    region_round64_winners = [[] for _ in range(4)]
    for region in range(4):
        for idx_A, idx_B in round64_pairings:
            team_A = sim_bracket[region][idx_A]
            team_B = sim_bracket[region][idx_B]
            result = simulate_game(team_A, team_B, "N")
            winner = team_A if result == 1 else team_B
            region_round64_winners[region].append(winner)
    
    # --- Tournament Simulation: Round of 32 ---
    region_round32_winners = [[] for _ in range(4)]
    for region in range(4):
        winners64 = region_round64_winners[region]
        result = simulate_game(winners64[0], winners64[7], "N")
        game1 = winners64[0] if result == 1 else winners64[7]
        result = simulate_game(winners64[4], winners64[3], "N")
        game2 = winners64[4] if result == 1 else winners64[3]
        result = simulate_game(winners64[5], winners64[2], "N")
        game3 = winners64[5] if result == 1 else winners64[2]
        result = simulate_game(winners64[6], winners64[1], "N")
        game4 = winners64[6] if result == 1 else winners64[1]
        region_round32_winners[region] = [game1, game2, game3, game4]
    
    # --- Tournament Simulation: Round of 16 ---
    region_round16_winners = [[] for _ in range(4)]
    for region in range(4):
        winners32 = region_round32_winners[region]
        result = simulate_game(winners32[0], winners32[1], "N")
        game1 = winners32[0] if result == 1 else winners32[1]
        result = simulate_game(winners32[2], winners32[3], "N")
        game2 = winners32[2] if result == 1 else winners32[3]
        region_round16_winners[region] = [game1, game2]
    
    # --- Tournament Simulation: Regional Finals (Round of 8) ---
    region_champions = []
    for region in range(4):
        winners16 = region_round16_winners[region]
        result = simulate_game(winners16[0], winners16[1], "N")
        champion_region = winners16[0] if result == 1 else winners16[1]
        region_champions.append(champion_region)
    
    # --- Final Four ---
    result_semi1 = simulate_game(region_champions[0], region_champions[2], "N")
    semi1_winner = region_champions[0] if result_semi1 == 1 else region_champions[2]
    
    result_semi2 = simulate_game(region_champions[1], region_champions[3], "N")
    semi2_winner = region_champions[1] if result_semi2 == 1 else region_champions[3]
    
    # --- Championship Game ---
    result_final = simulate_game(semi1_winner, semi2_winner, "N")
    champion = semi1_winner if result_final == 1 else semi2_winner

    # --- (Optional) Update Tournament Progress & Season Stats ---
    # ... (your existing code updating tournament_progress and simulation_records) ...

    # --- Print the Simulated Bracket for the First Simulation ---
    if i == 0:
        print("\n========== SIMULATED BRACKET ==========")
        # First Four
        print("\nFirst Four:")
        print(f"  South First Four (Game 1): {bracket_data[11][2]} vs {bracket_data[12][2]} -> Winner: {sim_bracket[0][11]}")
        print(f"  South First Four (Game 2): {bracket_data[16][2]} vs {bracket_data[17][2]} -> Winner: {sim_bracket[0][15]}")
        print(f"  East First Four (Game 1): {bracket_data[60][2]} vs {bracket_data[61][2]} -> Winner: {sim_bracket[3][10]}")
        print(f"  East First Four (Game 2): {bracket_data[66][2]} vs {bracket_data[67][2]} -> Winner: {sim_bracket[3][15]}")

        # Round of 64
        print("\nRound of 64:")
        regions = ["South", "Midwest", "West", "East"]
        for region in range(4):
            print(f"  {regions[region]} Region:")
            for (idx_A, idx_B), winner in zip(round64_pairings, region_round64_winners[region]):
                team_A = sim_bracket[region][idx_A]
                team_B = sim_bracket[region][idx_B]
                print(f"    {team_A} vs {team_B} -> Winner: {winner}")

        # Round of 32
        print("\nRound of 32:")
        for region in range(4):
            print(f"  {regions[region]} Region:")
            winners64 = region_round64_winners[region]
            print(f"    Game 1: {winners64[0]} vs {winners64[7]} -> Winner: {region_round32_winners[region][0]}")
            print(f"    Game 2: {winners64[4]} vs {winners64[3]} -> Winner: {region_round32_winners[region][1]}")
            print(f"    Game 3: {winners64[5]} vs {winners64[2]} -> Winner: {region_round32_winners[region][2]}")
            print(f"    Game 4: {winners64[6]} vs {winners64[1]} -> Winner: {region_round32_winners[region][3]}")

        # Round of 16
        print("\nRound of 16:")
        for region in range(4):
            print(f"  {regions[region]} Region:")
            winners32 = region_round32_winners[region]
            print(f"    Game 1: {winners32[0]} vs {winners32[1]} -> Winner: {region_round16_winners[region][0]}")
            print(f"    Game 2: {winners32[2]} vs {winners32[3]} -> Winner: {region_round16_winners[region][1]}")

        # Regional Finals (Round of 8)
        print("\nRegional Finals:")
        for region in range(4):
            winners16 = region_round16_winners[region]
            print(f"  {regions[region]} Champion: {region_champions[region]} (from {winners16[0]} vs {winners16[1]})")

        # Final Four
        print("\nFinal Four:")
        print(f"  Semifinal 1: {region_champions[0]} vs {region_champions[2]} -> Winner: {semi1_winner}")
        print(f"  Semifinal 2: {region_champions[1]} vs {region_champions[3]} -> Winner: {semi2_winner}")

        # Championship Game
        print("\nChampionship Game:")
        print(f"  {semi1_winner} vs {semi2_winner} -> National Champion: {champion}")
        print("========================================\n")
    
    # (Rest of your simulation loop code for updating cumulative stats, etc.)
    # --- Update Cumulative Simulation Records (Season stats) ---
    for team in sim_team_dict:
        simulation_records.setdefault(team, [0, 0, 0])
        simulation_records[team][0] += sim_record_dict[team][0]  # Wins
        simulation_records[team][1] += sim_record_dict[team][1]  # Losses
        simulation_records[team][2] += sim_team_dict[team]         # ELO

# --- Average Season Results Over Simulations ---
for team in simulation_records:
    simulation_records[team] = [round(stat / simulations, 2) for stat in simulation_records[team]]

# --- Export Tournament Progress Dictionary to CSV ---
with open('Data/tournament_progress.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Team', 't64', 't32', 't16', 't8', 't4', 't2', 't1'])
    for team, counts in tournament_progress.items():
        writer.writerow([team] + counts)

# --- Sort and Display Season Results (Descending ELO) ---
sorted_teams = sorted(simulation_records.items(), key=lambda x: x[1][2], reverse=True)
for i, (team, stats) in enumerate(sorted_teams, 1):
    wins, losses, elo = stats
    # Uncomment the line below to print season results:
    # print(f"{i}. {team} ({wins}-{losses}): {elo} ELO")

# --- Export Game Results to CSV ---
with open('Data/game_simulation_results.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Date', 'Home Team', '# of Home Team Wins', 'Away Team', '# of Away Team Wins', 'Neutral'])
    for (date, home_team, away_team, location), (home_wins, away_wins) in game_results.items():
        writer.writerow([date, home_team, home_wins, away_team, away_wins, location])