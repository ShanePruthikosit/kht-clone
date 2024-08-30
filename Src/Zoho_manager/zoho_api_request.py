import requests
import json
import time

# Configuration
client_id = "1000.EZWWO3SW0U3IA27GLHM7QD78MHVQWJ"
client_secret = "81fc29b20c049335ebb4d6b8a74830843d485db256"
authen_code = "" # input("Enter the authorization code from the redirect URL: ")
test_params = {'fields':"""Last_Name"""}

# Get data parameters
villages_params = {'fields',"""
    Village_Name, Village_Type, Total_Population, Adult_Males, Adults_Females
    ,GPS_Latitude, GPS_Longitude, Nearest_Hospital_id, Nearest_Mathayom_(Seconary)_Id,
    Nearest_Pratom_(Primary)_Id, Case_Studies, District_Id
"""}
projects_params = {'fields',"""
    Solution_Title, Status, Village_Id, Project_Start_Date, Project_End_Date
    Amount_Donated, Water_Problems_Description, Other_Villages, Project_Budget_THB
    Total_Spend-THB
"""}
districts_prams = {'fields',"""
    Town/District_Name, Types
"""} # / in the name?
# Missing hospital data
# Missing school data

# read the access_token.txt
file_path = 'access_token.txt'
with open(file_path, 'r') as file:
    authen_code = file.read().strip()

# overwrite file
with open(file_path, 'w') as file:
    pass

# all out put files location
output_files = ['Villages.json', 'Projects_cases.json', '']

def get_access_token(code):
    token_url = "https://accounts.zoho.com/oauth/v2/token" # https://accounts.zoho.eu
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    token_data = json.loads(response.text)
    if "error" in token_data:
        print(f"Error: {token_data['error']}")
        return None, None
    else:
        return token_data['access_token'], token_data['refresh_token']

def get_data(access_token, params):
    url = "https://www.zohoapis.com/crm/v5/Leads" # https://www.zohoapis.eu
    headers = {'Authorization': 'Zoho-oauthtoken {}'.format(access_token)}
    data = []
    while True: # get the data until the last page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            result = response.json()
            data += result["data"]
            if result['info']['next_page_token'] != None:
                params['page_token'] = result['info']['next_page_token']
            else:
                print("Read all pages!")
                break
        else:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)
            break
    params['page_token'] = None
    return data

def get_new_access_token(refresh_token):
    refresh_url = "https://accounts.zoho.com/oauth/v2/token" # https://accounts.zoho.eu
    param = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    response = requests.post(refresh_url, params=param)
    if response.status_code == 200:
        access_token = json.loads(response.text)["access_token"]
        data = response.json()
        data = json.dumps(data, indent=2)
        return access_token
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None

access_token, refresh_token = get_access_token(authen_code)
count = 0

while True:
    if access_token != None:
        print("getting data...")
        data = get_data(access_token, test_params)
        with open('Zoho_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=2)
    # if count >= 10:
    #     if refresh_token != None:
    #         print("getting a new access token...")
    #         access_token = get_new_access_token(refresh_token)
    count += 1
    print("count {}".format(count))
    time.sleep(3)