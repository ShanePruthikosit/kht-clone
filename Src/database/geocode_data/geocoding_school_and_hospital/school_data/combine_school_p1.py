import csv
import json

# Load data from JSON file
with open('school_data_p4_details.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Write to a new CSV file
with open('complete_school_data_p4.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["school_name", "province", "district", "sub_district", "postal_code", "formatted_address", "gps_latitude", "gps_longitude"])

    for item in data:
        lat, lon = item['LAT_LON'].split(',')
        formatted_address = item['FormattedAddress']
        # Split the address into its components (the formatt address is split by a space)
        address_components = formatted_address.split(' ')
        school_name = address_components[0]
        province = address_components[1]
        district = address_components[2]
        sub_district = address_components[3]
        postal_code = address_components[4]

        # Combine into a single line for CSV
        combined_data = [
            school_name.strip(),
            province.strip(),
            district.strip(),
            sub_district.strip(),
            postal_code.strip(),
            formatted_address,
            lat,
            lon
        ]
        writer.writerow(combined_data)  # Write the combined data to the CSV file