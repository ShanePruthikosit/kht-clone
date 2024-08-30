'''
create_school_table.py 
A python program to create a school table and
insert data from a CSV file into the table.
Also updates the table with new data from the CSV file.
The school data is from 
"https://th.wikipedia.org/wiki/รายชื่อโรงเรียนในจังหวัดแม่ฮ่องสอน#อำเภอเมืองแม่ฮ่องสอน"
converted to CSV format manually.
Then use https://pin-point.co/en/ to find the latitude 
and longitude of the school.
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import os
import psycopg2
from clean_csv import select_columns_and_save_csv
from config import config
import pandas as pd

def get_file_path(filename):
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    return file_path

def create_school_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        with psycopg2.connect(**params) as connection:
            with connection.cursor() as crsc:
                CREATE_TABLE = """CREATE TABLE IF NOT EXISTS school2 (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        school_name VARCHAR(255),
                        province VARCHAR(255),
                        district VARCHAR(255),
                        sub_district VARCHAR(255),
                        postal_code VARCHAR(255),
                        formatted_address VARCHAR(255),
                        gps_latitude DOUBLE PRECISION,
                        gps_longitude DOUBLE PRECISION,
                        geom geometry(Point, 4326)
                    );"""
                crsc.execute(CREATE_TABLE)

                # Input and output file paths
                input_file_path = get_file_path('Data/complete_school_data_p7.csv')
                output_file_path = get_file_path('schools.csv')

                # Select columns and save to a new CSV file
                columns_to_select = ['school_name', 'province', 'district', 'sub_district', 'postal_code', 'formatted_address', 'gps_latitude', 'gps_longitude']

                select_columns_and_save_csv(input_file_path, output_file_path, columns_to_select)

                # Load the new CSV data into a DataFrame
                new_data = pd.read_csv(output_file_path)

                # If there are no new rows, print a message and return
                if new_data.empty:
                    print('No new rows to add.')
                    return
                else:
                    print('Adding new rows to the district table...')

                # Save the filtered data to a new CSV file
                new_data.to_csv(output_file_path, index=False)

                # Use 'copy_expert' to copy the new data from the CSV file into the 'village' table
                with open(output_file_path, 'r') as f:
                    next(f)  # Skip the header
                    crsc.copy_expert(
                        "COPY school2 (school_name, province, district, sub_district, postal_code, formatted_address, gps_latitude, gps_longitude) FROM STDIN WITH CSV HEADER",
                        f
                    )
                connection.commit()

                # Set the SRID of the 'geom' column to 4326
                SET_GEOM_SRID = """UPDATE school2 SET geom = ST_SetSRID(ST_MakePoint(gps_longitude, gps_latitude), 4326);"""
                crsc.execute(SET_GEOM_SRID)

                print('School table created successfully.')
                             
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')

