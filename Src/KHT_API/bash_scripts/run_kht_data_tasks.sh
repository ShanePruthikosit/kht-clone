# This file will first download the KHT DATA file using download_kht_data.sh
# And then will get the most recent file, unzip it and move it to /KHT_Team/Src
# using get_recent_kht_data.sh

#!/bin/bash

scripts_path="/home/kht-team/KHT_Team/Src"


cd "$scripts_path"

# Run the download script first
sudo sh "$scripts_path/download_kht_data.sh"

# Check if the download script completed successfully
if [ $? -eq 0 ]; then
    # Run the extract and move script
    sudo sh "$scripts_path/get_recent_kht_data.sh"
else
    echo "Download script failed. Aborting."
    exit 1
fi
