import csv

def process_line(line):
    line = line.strip()
    if not line:
        return None
    parts = line.split()
    if not parts:
        return None
    date_part = parts[0]
    rest_parts = parts[1:]
    scores = []
    score_indices = []
    for i, part in enumerate(rest_parts):
        if part.isdigit():
            scores.append(part)
            score_indices.append(i)
            if len(scores) == 2:
                break
    if len(scores) < 2:
        return None  # Not enough scores found
    score1_index = score_indices[0]
    score2_index = score_indices[1]
    # Extract team1 and team2
    team1 = ' '.join(rest_parts[:score1_index])
    score1 = rest_parts[score1_index]
    team2 = ' '.join(rest_parts[score1_index + 1:score2_index])
    score2 = rest_parts[score2_index]
    # Determine home and away teams
    home_team = None
    home_score = None
    away_team = None
    away_score = None
    neutral = False
    if team1.startswith('@'):
        home_team = team1[1:].strip()
        home_score = score1
        away_team = team2.strip()
        away_score = score2
    elif team2.startswith('@'):
        home_team = team2[1:].strip()
        home_score = score2
        away_team = team1.strip()
        away_score = score1
    else:
        # Neutral game
        home_team = team1.strip()
        home_score = score1
        away_team = team2.strip()
        away_score = score2
        neutral = True
    # Prepare the CSV row
    row = [date_part, home_team, home_score, away_team, away_score]
    if neutral:
        row.append('N')
    return row

def main():
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input.csv output.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, mode='r') as infile, open(output_file, mode='w', newline='') as outfile:
        csv_reader = csv.reader(infile)
        csv_writer = csv.writer(outfile)

        # Write the header to the output CSV
        csv_writer.writerow(["Date", "Home Team", "Home Score", "Away Team", "Away Score", "Neutral"])

        for line in csv_reader:
            processed = process_line(' '.join(line))  # Convert CSV row to a space-separated string
            if processed:
                csv_writer.writerow(processed)

if __name__ == "__main__":
    main()
