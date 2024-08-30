# https://data.go.th/dataset/34f2caea-233c-4fdd-a26c-3ef8b0d72a73/resource/90329440-f97e-4636-8939-82b2b449a21b/download/__csv.csv

# please read the csv file from the link above and write it to another csv file to the root directory of the project
import pandas as pd
import requests
import csv
import xlrd as xl

url = 'https://data.go.th/dataset/34f2caea-233c-4fdd-a26c-3ef8b0d72a73/resource/90329440-f97e-4636-8939-82b2b449a21b/download/__csv.csv'
df = pd.read_csv(url, encoding='iso-8859-11')
print(df)
df.to_csv('hospital.csv', index=False)

# read the csv file and write it to antoher csv file in new column format called hospital2.csv
# the new csv should only contain these columns: ชื่อหน่วยงาน, จังหวัด, อำเภอ, ตำบล, 
df = pd.read_csv('hospital.csv')
df = df[['ชื่อหน่วยงาน', 'จังหวัด', 'อำเภอ', 'ตำบล']]
print(df)
df.to_csv('hospital2.csv', index=False)

# district_url = 'https://data.go.th/dataset/39d8feba-ab42-4cc2-bb54-b23e73ddc488/resource/4226a380-5aa5-4892-be94-d66cf741ffa0/download/xx.xls'
# district_df = pd.read_excel(district_url)
# district_df = district_df.apply(lambda x: x.str.encode('iso-8859-11').str.decode('utf-8') if x.dtype == "object" else x)
# print(district_df)
# district_df.to_csv('district.csv', index=False)
