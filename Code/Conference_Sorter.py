import pandas as pd

def main():
    # Load the CSV files
    elo_df = pd.read_csv('Data/Final_Team_ELOs.csv')
    teams_df = pd.read_csv('Data/MTeams.csv')
    conferences_df = pd.read_csv('Data/MTeamConferences.csv')
    
    # Filter the conference data for the year 2025
    conf_2025 = conferences_df[conferences_df['Season'] == 2025]
    
    # Merge the elo data with teams to get the team IDs.
    merged_df = pd.merge(elo_df, teams_df, left_on='Team', right_on='TeamName', how='left')
    
    # Merge the result with the 2025 conference data using the team ID
    final_df = pd.merge(merged_df, conf_2025, on='TeamID', how='left')
    
    # Sort by conference abbreviation and then by ranking (both ascending)
    final_df_sorted = final_df.sort_values(by=['ConfAbbrev', 'Ranking'])
    
    # Select only the desired columns
    output_df = final_df_sorted[['Ranking', 'Team', 'Wins', 'Losses', 'ELO', 'ConfAbbrev']]
    
    # Write the filtered and sorted data to a new CSV file
    output_df.to_csv('Data/Sorted_ELOs_by_Conference.csv', index=False)
    
    print("CSV created: Sorted_ELOs_by_Conference.csv")

if __name__ == '__main__':
    main()
