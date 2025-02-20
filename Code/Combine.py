import csv

# Read the first file and store header and rows
with open('Data/full_results.csv', 'r') as f1:
    reader = csv.reader(f1)
    header = next(reader)  # Save the header
    rows1 = list(reader)

# Read the second file, skip its header, and store rows
with open('Data/MNCAATourneyCompactResults.csv', 'r') as f2:
    reader = csv.reader(f2)
    next(reader)  # Skip the header
    rows2 = list(reader)

# Combine the rows from both files
combined = rows1 + rows2

# Sort the combined rows by Season (as int) and DayNum (as int)
sorted_rows = sorted(combined, key=lambda x: (int(x[0]), int(x[1])))

# Write the sorted rows to a new CSV file
with open('Data/combined_results.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)
    writer.writerows(sorted_rows)