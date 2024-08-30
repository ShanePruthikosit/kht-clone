import requests
import csv

# Define your Pinpoint API key
PINPOINT_API_KEY = '6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935'

# Pinpoint API endpoint
PINPOINT_API_URL = 'https://api.pin-point.co/v1/geocode'

def geocode_address(province, district, subdistrict, postal_code):
    address = f"{subdistrict}, {district}, {province}, Thailand {postal_code}"
    params = {
        'address': address,
        'key': PINPOINT_API_KEY
    }
    response = requests.get(PINPOINT_API_URL, params=params)
    data = response.json()
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None

def geocode_addresses_from_csv(csv_file):
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            agency_name = row['ชื่อหน่วยงาน']
            province = row['จังหวัด']
            district = row['อำเภอ']
            subdistrict = row['ตำบล']
            postal_code = row['รหัสไปรษณีย์']
            
            lat, lng = geocode_address(province, district, subdistrict, postal_code)
            if lat is not None and lng is not None:
                print(f"Agency: {agency_name}, Latitude: {lat}, Longitude: {lng}")
            else:
                print(f"Failed to geocode address for agency: {agency_name}")

if __name__ == "__main__":
    csv_file_path = 'hospital2.csv'
    geocode_addresses_from_csv(csv_file_path)
