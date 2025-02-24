# Get user inputs
american_odd = int(input("Enter American odds: "))
win_percent = input("Enter win percentage: ").strip('%')

# Convert inputs to numerical values
win_prob = float(win_percent) / 100
lose_prob = 1 - win_prob

# Calculate profit multiplier based on odds sign
if american_odd < 0:
    profit = 100 / abs(american_odd)
else:
    profit = american_odd / 100

# Calculate Expected Value
ev = (win_prob * profit) - (lose_prob * 1)
ev_percent = ev * 100

# Display result
print(f"Expected Value: {ev_percent:.2f}%")