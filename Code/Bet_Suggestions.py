import csv

def calculate_ev(american_odd, win_prob):
    if american_odd < 0:
        profit = 100 / abs(american_odd)
    else:
        profit = american_odd / 100
    lose_prob = 1 - win_prob
    ev = (win_prob * profit) - (lose_prob * 1)
    return ev * 100  # Convert to percentage

# Read game simulation results into a dictionary with frozenset keys
sim_dict = {}
with open('Data/game_simulation_results.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        home_team = row['Home Team'].strip()
        away_team = row['Away Team'].strip()
        key = frozenset([home_team, away_team])
        sim_dict[key] = {
            'home_team': home_team,
            'away_team': away_team,
            'home_wins': int(row['# of Home Team Wins']),
            'away_wins': int(row['# of Away Team Wins'])
        }

# Set the EV threshold percentage (e.g., 5.0 means +5% EV)
ev_threshold = 10.0

# Process each spread, calculate EV, and filter by threshold
with open('Data/Spreads.csv', 'r') as f:
    reader = csv.reader(f)
    for spread_row in reader:
        if len(spread_row) != 4:
            continue  # Skip invalid rows

        team1 = spread_row[0].strip()
        try:
            odds1 = int(spread_row[1].strip())
        except ValueError:
            print(f"Invalid odds for {team1}: {spread_row[1]}")
            continue

        team2 = spread_row[2].strip()
        try:
            odds2 = int(spread_row[3].strip())
        except ValueError:
            print(f"Invalid odds for {team2}: {spread_row[3]}")
            continue

        # Lookup simulation data
        key = frozenset([team1, team2])
        if key not in sim_dict:
            print(f"No simulation data found for game: {team1} vs {team2}")
            continue

        sim_data = sim_dict[key]
        home_team_sim = sim_data['home_team']
        away_team_sim = sim_data['away_team']
        home_wins = sim_data['home_wins']
        away_wins = sim_data['away_wins']

        # Determine win probabilities for each team in the spread
        if team1 == home_team_sim:
            win_prob1 = home_wins / 10000
        else:
            win_prob1 = away_wins / 10000

        if team2 == home_team_sim:
            win_prob2 = home_wins / 10000
        else:
            win_prob2 = away_wins / 10000

        # Calculate expected values for both teams
        ev1 = calculate_ev(odds1, win_prob1)
        ev2 = calculate_ev(odds2, win_prob2)

        # Filter out bets that don't meet the threshold
        if ev1 < ev_threshold and ev2 < ev_threshold:
            continue

        # Output results for bets meeting the EV threshold
        print(f"{team1} vs {team2}:")
        if ev1 >= ev_threshold:
            print(f"  {team1} EV: {ev1:.2f}%")
        if ev2 >= ev_threshold:
            print(f"  {team2} EV: {ev2:.2f}%")
        print()  # Add a blank line for readability
