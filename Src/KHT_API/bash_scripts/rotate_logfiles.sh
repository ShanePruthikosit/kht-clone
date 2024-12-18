#!/bin/bash

# Define log directory
LOG_DIR=~/logs

# Number of log files to keep
NUM_LOGS=3

# Function to rotate logs
rotate_logs() {
  LOG_FILES=$(find "$LOG_DIR" -name "$1*.log")
  NUM_FILES=$(echo "$LOG_FILES" | wc -l)

  if [ $NUM_FILES -gt $NUM_LOGS ]; then
    sorted_files=$(echo "$LOG_FILES" | sort)
    FILES_TO_DELETE=$(echo "$sorted_files" | head -n $(($NUM_FILES - $NUM_LOGS)))
    echo "$FILES_TO_DELETE" | xargs rm -f
  fi
}

# Rotate logs for each type
rotate_logs "ROTATE_BACKUPS"
rotate_logs "mhs_geographic_backup"
