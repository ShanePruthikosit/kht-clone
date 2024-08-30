import csv
import json

# Load data from JSON file
with open('hospital_data_p1_details.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

for item in data:
    lat_lon = item['LAT_LON']
    formatted_address = item['FormattedAddress']
    # Process lat_lon and formatted_address

# Combine into a single line for CSV
combined_data = [
    "โรงพยาบาลส่งเสริมสุขภาพตำบลห้วยปูลิง",
    "จ.แม่ฮ่องสอน",
    "อ.เมืองแม่ฮ่องสอน",
    "ต.ห้วยปูลิง",
    formatted_address,
    lat_lon
]

# Write to a new CSV file
with open('complete_hospital_data_p1.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["ชื่อหน่วยงาน", "จังหวัด", "อำเภอ", "ตำบล", "FormattedAddress", "LAT_LON"])
    writer.writerow(combined_data)
