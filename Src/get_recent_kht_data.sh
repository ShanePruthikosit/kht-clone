#!/bin/bash

download_path="/home/kht-team/KHT_Team/Src/database/Backups"
database_path=/home/kht-team/KHT_Team/Src/database/Data

# Change to the directory
cd "$download_path"

# Find all backup files in the directory and sort them by date (assuming filenames are in the format KHT_DATA_YYYY_MM_DD.zip)
backup_files=$(find . -maxdepth 1 -name "KHT_DATA_*" -type f | sort -r)
num_files=$(echo "$backup_files" | wc -l)

# Get the most recent file (the first file in the sorted list)
KHT_DATA_RECENT=$(echo "$backup_files" | head -n 1)

# Delete all files except the most recent file
files_to_delete=$(echo "$backup_files" | grep -v "$KHT_DATA_RECENT")
echo "$files_to_delete" | xargs rm -f

# Unzip the most recent file
unzip -o "$KHT_DATA_RECENT"

# Remove the existing "Data" directory
rm -rf "$database_path"

# Move the "Data" directory or file to the database path
cp -r "Data" "$database_path"
