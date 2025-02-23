#!/bin/bash
python3 Code/ELO.py
python3 Code/Schedule_Cleaner.py Data/2025_schedule.csv Data/2025_cleaned_schedule.csv
python3 Code/Regular_Season_Simulator.py
python3 Code/March_Madness_Simulator.py
python3 Code/Website.py