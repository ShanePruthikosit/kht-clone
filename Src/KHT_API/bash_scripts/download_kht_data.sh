#!/bin/bash

download_path=/home/kht-team/KHT_Team/Src/database/Backups
folder_id="14P46_R7w8ip-8ZjKPhhMA1dY3ZWUr479"

echo "Download path: $download_path"
echo "Folder ID: $folder_id"

gdown --folder "$folder_id" -O "$download_path"

if [ $? -eq 0 ]; then
    echo "Download of the most recent ZIP file successfully"
else
    echo "Download failed. Check $log_file for more information."
fi
