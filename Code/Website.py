import csv

def generate_html(csv_rankings_path, csv_games_path, csv_tournament_path, output_file='Data/rankings.html'):
    # Read team rankings data
    with open(csv_rankings_path, 'r') as f:
        rankings_reader = csv.reader(f)
        rankings_headers = next(rankings_reader)
        rankings_rows = list(rankings_reader)

    # Read game predictions data and calculate percentages
    with open(csv_games_path, 'r') as f:
        games_reader = csv.reader(f)
        games_headers = next(games_reader)
        games_rows = []
        for row in games_reader:
            home_wins = int(row[2])
            away_wins = int(row[4])
            total = home_wins + away_wins
            home_pct = round((home_wins / total) * 100, 1)
            away_pct = round((away_wins / total) * 100, 1)
            formatted_row = [
                row[0],  # Date
                row[1],  # Home Team
                f"{home_pct}%",
                row[3],  # Away Team
                f"{away_pct}%",
                row[5]   # Neutral
            ]
            games_rows.append(formatted_row)

    # Read tournament predictions data and format percentages
    with open(csv_tournament_path, 'r') as f:
        tournament_reader = csv.reader(f)
        tournament_headers = next(tournament_reader)
        
        # Read and sort data before formatting
        data_rows = list(tournament_reader)
        # Sort by champion count (last column) descending, using index 6 for t1
        data_rows.sort(key=lambda x: int(x[6]), reverse=True)

        # Format sorted data into percentages
        tournament_rows = []
        for row in data_rows:
            formatted_row = [row[0]]  # Team name
            for value in row[1:]:  # Convert counts to percentages
                pct = round(int(value) / 1000, 2)
                formatted_row.append(f"{pct}%")
            tournament_rows.append(formatted_row)

    # Generate HTML with tabs
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Basketball Stats</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .tab {{ overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }}
        .tab button {{
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            font-size: 17px;
        }}
        .tab button:hover {{ background-color: #ddd; }}
        .tab button.active {{ background-color: #3498db; color: white; }}
        .tabcontent {{ display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }}
        table {{
            border-collapse: collapse;
            width: 90%;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #f1f1f1; }}
    </style>
</head>
<body>
    <h1>Basketball Statistics</h1>
    
    <div class="tab">
        <button class="tablinks active" onclick="openTab(event, 'rankings')">Team Rankings</button>
        <button class="tablinks" onclick="openTab(event, 'predictions')">Game Predictions</button>
        <button class="tablinks" onclick="openTab(event, 'tournament')">March Madness</button>
    </div>

    <div id="rankings" class="tabcontent" style="display: block;">
        <h2>Team Rankings</h2>
        <table>
            <thead><tr>{"".join(f'<th>{h}</th>' for h in rankings_headers)}</tr></thead>
            <tbody>{"".join(f'<tr>{"".join(f"<td>{cell}</td>" for cell in row)}</tr>' for row in rankings_rows)}</tbody>
        </table>
    </div>

    <div id="predictions" class="tabcontent">
        <h2>Game Predictions</h2>
        <table>
            <thead><tr>
                <th>Date</th>
                <th>Home Team</th>
                <th>Home Win %</th>
                <th>Away Team</th>
                <th>Away Win %</th>
                <th>Neutral</th>
            </tr></thead>
            <tbody>{"".join(
                f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>'
                for row in games_rows
            )}</tbody>
        </table>
    </div>

    <div id="tournament" class="tabcontent">
        <h2>March Madness Predictions</h2>
        <table>
            <thead><tr>
                <th>Team</th>
                <th>Round of 64</th>
                <th>Round of 32</th>
                <th>Sweet 16</th>
                <th>Elite 8</th>
                <th>Final 4</th>
                <th>Championship</th>
                <th>Champion</th>
            </tr></thead>
            <tbody>{"".join(
                f'<tr><td>{row[0]}</td>{"".join(f"<td>{cell}</td>" for cell in row[1:])}</tr>'
                for row in tournament_rows
            )}</tbody>
        </table>
    </div>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }}
    </script>
</body>
</html>'''

    with open(output_file, 'w') as f:
        f.write(html)

    print(f"HTML file generated as '{output_file}'")

# Generate the HTML from all CSV files
generate_html(
    csv_rankings_path='Data/Final_Team_ELOs.csv',
    csv_games_path='Data/game_simulation_results.csv',
    csv_tournament_path='Data/tournament_progress.csv'
)