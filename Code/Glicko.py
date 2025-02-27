import csv
import math
import numpy as np

def calculate_log_loss(predicted_probabilities, actual_outcomes):
    """Calculates the log loss."""
    epsilon = 1e-15
    log_loss = 0
    for prob, outcome in zip(predicted_probabilities, actual_outcomes):
        prob = max(epsilon, min(1 - epsilon, prob))
        log_loss += outcome * math.log(prob) + (1 - outcome) * math.log(1 - prob)
    return -log_loss / len(predicted_probabilities)

def calculate_brier_score(predicted_probabilities, actual_outcomes):
    """Calculates the Brier score."""
    brier_score = np.mean([(p - o)**2 for p, o in zip(predicted_probabilities, actual_outcomes)])
    return brier_score

def calculate_brier_skill_score(brier_score, baseline_brier_score=0.25):
    """Calculates the Brier Skill Score."""
    return 1 - (brier_score / baseline_brier_score)


def revert_to_conference_mean(teams, team_conferences, current_year, reversion_factor=1/3):
    """Reverts team ratings towards their conference mean."""

    conferences = {}
    for (year, team_id), conf_abbrev in team_conferences.items():
        if year == current_year:
            if conf_abbrev not in conferences:
                conferences[conf_abbrev] = []
            conferences[conf_abbrev].append(teams[team_id])

    conference_means = {}
    for conf_abbrev, conference_teams in conferences.items():
        if conference_teams:
            total_rating = sum(team.rating for team in conference_teams)
            conference_means[conf_abbrev] = total_rating / len(conference_teams)

    for conf_abbrev, conference_teams in conferences.items():
        if conf_abbrev in conference_means:
            mean_rating = conference_means[conf_abbrev]
            for team in conference_teams:
                team.rating = team.rating + reversion_factor * (mean_rating - team.rating)


def evaluate_parameters(teams, game_data, team_conferences, tau, vol, start_year, end_year, home_adv=0):
    """Evaluates parameters, including conference mean reversion, home advantage, and MOV multiplier."""

    for team in teams.values():
        team.rating = 1500
        team.rd = 350
        team.vol = vol

    predicted_probabilities = []
    actual_outcomes = []
    current_year = None

    for game in game_data:
        game_year = int(game[0])

        if game_year != current_year:
            if current_year is not None:
                 revert_to_conference_mean(teams, team_conferences, game_year)
            current_year = game_year

        if start_year <= game_year < end_year:
            team_id, opp_id = game[2], game[4]
            team_score, opp_score = int(game[3]), int(game[5])
            location = game[6]
            score = 1 if team_score > opp_score else 0
            margin = abs(team_score - opp_score) # Margin of Victory

            team, opponent = teams[team_id], teams[opp_id]

            mu_team, phi_team = team._scale_down()
            mu_opp, phi_opp = opponent._scale_down()

            # --- Home Advantage (Prediction) ---
            if location == 'H':
                mu_team += home_adv / 173.7178
            elif location == 'A':
                mu_opp += home_adv / 173.7178

            predicted_prob = E(mu_team, mu_opp, phi_opp)
            predicted_probabilities.append(predicted_prob)
            actual_outcomes.append(score)

            # --- Calculate ELO Difference (for MOV Multiplier) ---
            elo_diff = team.rating - opponent.rating
            if location == 'H':
                elo_diff += home_adv
            elif location == 'A':
                elo_diff -= home_adv
            if score == 0:  # Underdog won, make elo_diff negative
                elo_diff = -elo_diff

            # --- Margin of Victory Multiplier ---
            mov_multiplier = ((margin + 3)**0.8) / (7.5 + 0.006 * elo_diff)

            # --- Glicko-2 Update (with MOV Multiplier) ---
            glicko2(team, [opponent], [score], tau=tau, mov_multiplier=mov_multiplier)
            glicko2(opponent, [team], [1 - score], tau=tau, mov_multiplier=mov_multiplier)

    log_loss = calculate_log_loss(predicted_probabilities, actual_outcomes)
    brier_score = calculate_brier_score(predicted_probabilities, actual_outcomes)
    brier_skill_score = calculate_brier_skill_score(brier_score)

    return log_loss, brier_skill_score

# --- Player class, g, E --- (Same as before)
class Player:
    def __init__(self, rating=1500, rd=350, vol=0.06):
        self.rating = rating
        self.rd = rd
        self.vol = vol

    def _scale_down(self):
        return (self.rating - 1500) / 173.7178, self.rd / 173.7178

    def _scale_up(self, mu, phi):
        return 173.7178 * mu + 1500, 173.7178 * phi

def g(phi):
    return 1 / math.sqrt(1 + 3 * (phi**2) / (math.pi**2))

def E(mu, mu_j, phi_j):
    return 1 / (1 + math.exp(-g(phi_j) * (mu - mu_j)))
# --- glicko2 (Modified for MOV Multiplier) ---

def glicko2(player, opponents, scores, tau=0.5, epsilon=0.000001, mov_multiplier=1.0):
    """Implements Glicko-2 with a margin of victory multiplier."""

    mu, phi = player._scale_down()
    orig_vol = player.vol

    v_inv = 0
    for opp in opponents:
        mu_j, phi_j = opp._scale_down()
        v_inv += (g(phi_j)**2) * E(mu, mu_j, phi_j) * (1 - E(mu, mu_j, phi_j))
    v = 1 / v_inv if v_inv > 0 else float('inf')

    delta = 0
    for opp, score in zip(opponents, scores):
        mu_j, phi_j = opp._scale_down()
        delta += g(phi_j) * (score - E(mu, mu_j, phi_j))
    # --- Apply MOV Multiplier Here ---
    delta *= v * mov_multiplier  # Multiply delta by the MOV multiplier

    def f(x):
        ex = math.exp(x)
        term1 = ex * (delta**2 - phi**2 - v - ex) / (2 * (phi**2 + v + ex)**2)
        term2 = (x - a) / (tau**2)
        return term1 - term2

    a = math.log(orig_vol**2)
    A = a

    if delta**2 > phi**2 + v:
        B = math.log(delta**2 - phi**2 - v)
    else:
        k = 1
        while f(a - k * tau) < 0:
            k += 1
        B = a - k * tau

    fA = f(A)
    fB = f(B)
    while abs(B - A) > epsilon:
        C = A + (A - B) * fA / (fB - fA)
        fC = f(C)
        if fC * fB <= 0:
            A = B
            fA = fB
        else:
            fA = fA / 2
        B = C
        fB = fC

    new_vol = math.exp(A / 2)
    phi_star = math.sqrt(phi**2 + new_vol**2)
    new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
    new_mu = 0
    for opp, score in zip(opponents, scores):
        mu_j, phi_j = opp._scale_down()
        new_mu += g(phi_j) * (score - E(mu, mu_j, phi_j))

     # --- Apply MOV Multiplier to Rating Update ---
    new_mu = mu + (new_phi**2) * new_mu * mov_multiplier #also apply to new_mu
    new_rating, new_rd = player._scale_up(new_mu, new_phi)

    player.rating = new_rating
    player.rd = new_rd
    player.vol = new_vol

# --- Data Loading ---
results = 'Data/full_results.csv'
game_data = []
with open(results, newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        game_data.append(row)

team_ids_file = 'Data/MTeams.csv'
team_dict = {}
with open(team_ids_file, newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        team_dict[row[0]] = row[1]

team_conferences_file = 'Data/MTeamConferences.csv'
team_conferences = {}
with open(team_conferences_file, newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        year, team_id, conf_abbrev = int(row[0]), row[1], row[2]
        team_conferences[(year, team_id)] = conf_abbrev

teams = {team_id: Player() for team_id in team_dict}

# --- Data Splitting ---
train_data = [game for game in game_data if int(game[0]) < 2016]
val_data = [game for game in game_data if 2016 <= int(game[0]) < 2020]
test_data = [game for game in game_data if int(game[0]) >= 2020]

# --- Parameter Tuning ---
vol_values = [0.11]  # Example values - you can expand these
tau_values = [0.30]
home_adv_values = [100]

best_log_loss = float('inf')
best_brier_skill = -float('inf')
best_vol, best_tau, best_home_adv = 0.06, 0.3, 0 #initialize

for vol in vol_values:
    for tau in tau_values:
        for home_adv in home_adv_values:
            log_loss, brier_skill = evaluate_parameters(teams, train_data, team_conferences, tau, vol, 1985, 2016, home_adv)
            val_log_loss, val_brier_skill = evaluate_parameters(teams, val_data, team_conferences, tau, vol, 2016, 2020, home_adv)

            print(f"Vol: {vol}, Tau: {tau}, Home Adv: {home_adv}, Train Loss: {log_loss:.4f}, Val Loss: {val_log_loss:.4f}, Train Brier: {brier_skill:.4f}, Val Brier: {val_brier_skill:.4f}")

            if val_brier_skill > best_brier_skill:
                best_brier_skill = val_brier_skill
                best_log_loss = val_log_loss
                best_vol = vol
                best_tau = tau
                best_home_adv = home_adv

print(f"\nBest Vol: {best_vol}, Best Tau: {best_tau}, Best Home Adv: {best_home_adv}, Best Val Log Loss: {best_log_loss:.4f}, Best Val Brier Skill: {best_brier_skill:.4f}")

test_log_loss, test_brier_skill = evaluate_parameters(teams, test_data, team_conferences, best_tau, best_vol, 2020, 2025, best_home_adv)
print(f"Test Log Loss: {test_log_loss:.4f}, Test Brier Skill Score: {test_brier_skill:.4f}")

# --- Prediction and Ranking Functions ---

def predict_game(team_a_id, team_b_id, teams, home_adv=0):
    """Predicts game outcome with home advantage."""
    team_a, team_b = teams[team_a_id], teams[team_b_id]
    mu_a, phi_a = team_a._scale_down()
    mu_b, phi_b = team_b._scale_down()
    mu_a += home_adv / 173.7178  # Assume team_a is at home
    win_prob_a = E(mu_a, mu_b, phi_b)
    print(f"P({team_dict[team_a_id]} win): {win_prob_a:.4f}, P({team_dict[team_b_id]} win): {1 - win_prob_a:.4f}")

def print_rankings(teams, team_dict):
    """Prints teams ranked by rating."""
    ranked_teams = sorted(teams.items(), key=lambda item: item[1].rating, reverse=True)
    print("Rank | Team Name        | ELO  | RD  ")
    print("----|-----------------|------|-----")
    for rank, (team_id, player) in enumerate(ranked_teams, 1):
        team_name = team_dict[team_id]
        formatted_name = f"{team_name:<17}"
        print(f"{rank:4} | {formatted_name} | {int(round(player.rating)):4} | {int(round(player.rd)):3}")

# --- Example Usage ---
#predict_game("1400", "1211", teams, best_home_adv)
print_rankings(teams, team_dict)