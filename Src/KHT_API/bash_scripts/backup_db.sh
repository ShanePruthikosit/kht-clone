#!/bin/bash

# Define backup and log directory
BACKUP_DIR=~/backups
LOG_DIR=~/logs

# Create backup and log directory 
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"

# Get today's date in YYYY-MM-DD format
TODAY_DATE=$(date +%Y-%m-%d) 

# Define backup filename with date
BACKUP_FILE="$BACKUP_DIR/mhs_geographic_backup_$TODAY_DATE.sql"

# Define log filename with date
LOG_FILE="$LOG_DIR/mhs_geographic_backup_$TODAY_DATE.log"

# Perform the backup and log to file
{
  pg_dump -U postgres mhs_geographic > "$BACKUP_FILE" &&
  echo "$(date +'%Y-%m-%d %H:%M:%S') Database backup to $BACKUP_FILE completed."
} >> "$LOG_FILE" 2>&1 # write the stderr and stdout to the log file
