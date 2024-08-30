#!/bin/bash

# Locating the source file and its final destination
source_dir="/home/kht-team/KHT_Team/Src/database"

# Define the log file and current date
log_file="/home/kht-team/KHT_Team/Src/update_tables_db_log.txt"

# create the log file in /home/kht-team/KHT_Team/Src
echo "Creating log file: $log_file"
touch "$log_file" 
current_date_time=$(date '+%Y/%m/%d %H:%M')

# Change directory to the source directory
echo "Changing directory to: $source_dir"
cd "$source_dir" || exit

# update the database tables
echo "Running Python script: main.py"
python3 main.py > "$log_file" 2>&1

# Log the date and time to the log file
echo "Script run at $current_date_time" >> "$log_file"
echo "Script execution completed."
