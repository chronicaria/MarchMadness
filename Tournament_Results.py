import csv

# Read the CSV data into a list of dictionaries.
data = []
with open('tournament_progress.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Convert numeric values from strings to integers.
        team_data = {
            'Team': row['Team'],
            't64': int(row['t64']),
            't32': int(row['t32']),
            't16': int(row['t16']),
            't8': int(row['t8']),
            't4': int(row['t4']),
            't2': int(row['t2']),
            't1': int(row['t1'])
        }
        data.append(team_data)

# Sort the list by t1 (national championship count) in descending order.
data.sort(key=lambda x: x['t1'], reverse=True)

# Print header line.
print("Team: RD64, RD32, Sweet 16, Elite 8, Final 4, Semi, Title")

# Print the results formatted as percentages (dividing by 100) with one decimal place.
for row in data:
    team = row['Team']
    percentages = [
        row['t64'] / 100,  # RD64
        row['t32'] / 100,  # RD32
        row['t16'] / 100,  # Sweet 16
        row['t8']  / 100,  # Elite 8
        row['t4']  / 100,  # Final 4
        row['t2']  / 100,  # Semi
        row['t1']  / 100   # Title
    ]
    percentages_str = ", ".join(f"{p:.1f}%" for p in percentages)
    print(f"{team}: {percentages_str}")
