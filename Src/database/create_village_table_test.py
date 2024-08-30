'''
**NOT IN USED**
create_village_table_test.py 
A python program to create a village test table and
insert data from a CSV file into the table.
Also updates the table with new data from the CSV file.
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

def create_village_table_test():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        with psycopg2.connect(**params) as connection:
            with connection.cursor() as crsc:
                # create village table if it does not exist
                CREATE_TABLE = """CREATE TABLE IF NOT EXISTS villageTest2 (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        village_name VARCHAR(256),
                        created_time VARCHAR(256),
                        households INT,
                        road_conditions VARCHAR(256),
                        total_population INT,
                        gps_latitude DOUBLE PRECISION,
                        gps_longitude DOUBLE PRECISION,
                        population_without_enough_rice DOUBLE PRECISION,
                        children_aged_0_18 INT,
                        distance_to_town_km DOUBLE PRECISION,
                        adult_males INT,
                        adult_females INT,
                        distance_to_hospital_km DOUBLE PRECISION,
                        nearest_health_centre VARCHAR(256),
                        distance_to_pratom_km DOUBLE PRECISION,
                        annual_typhoid_cases INT,
                        distance_to_health_centre_km DOUBLE PRECISION,
                        distance_to_mathayom_km DOUBLE PRECISION,
                        common_diseases VARCHAR(256),
                        hosted_kht_projects VARCHAR(256),
                        record_id VARCHAR(256),
                        geom geometry(Point, 4326)
                    );"""
                crsc.execute(CREATE_TABLE)

                # Input and output file paths
                input_file_path = get_file_path('Data/Villages_001.csv')
                output_file_path = get_file_path('villages_test_001.csv')

                # Select columns and save to a  new CSV file
                columns_to_select = ['Village Name', 'Created Time', 'Households', 'Road Conditions', 'Total Population', 'GPS Latitude',
                    'GPS Longitude', '% Population Without Enough Rice', 'Children (Aged 0 - 18)',
                    'Distance to Town (km)', 'Adult Males', 'Adult Females', 'Distance to Hospital (km)',
                    'Nearest Health Centre', 'Distance to Pratom (km)', 'Annual Typhoid Cases',
                    'Distance to Health Centre (km)', 'Distance to Mathayom (km)', 'Common Diseases',
                    'Hosted KHT Projects', 'Record Id']

                select_columns_and_save_csv(input_file_path, output_file_path, columns_to_select)

                # Fetch the 'created_time' column from the 'villagetest' table
                crsc.execute("SELECT created_time FROM villageTest2;")
                existing_times = [item[0] for item in crsc.fetchall()]

                # Load the new CSV data into a DataFrame
                new_data = pd.read_csv(output_file_path)

                # Filter the new data to only include rows with 'created_time' values that don't exist in the database
                new_data = new_data[~new_data['created_time'].isin(existing_times)]
                
                # If there are no new rows, print a message and return
                if new_data.empty:
                    print('\nNo new rows to add to the village table.')
                else:
                    print('\nAdding new rows to the village table...')
                    num_rows_added = len(new_data)
                    print(f'{num_rows_added} rows added.')

                # Save the filtered data to a new CSV file
                new_data.to_csv(output_file_path, index=False)

                # Use 'copy_expert' to copy the new data from the CSV file into the 'villagetest' table
                with open(output_file_path, 'r') as f:
                    next(f)  # Skip the header
                    crsc.copy_expert(
                        "COPY villageTest2 (village_name, created_time, households, road_conditions, total_population, gps_latitude, gps_longitude, population_without_enough_rice, children_aged_0_18, distance_to_town_km, adult_males, adult_females, distance_to_hospital_km, nearest_health_centre, distance_to_pratom_km, annual_typhoid_cases, distance_to_health_centre_km, distance_to_mathayom_km, common_diseases, hosted_kht_projects, record_id) FROM STDIN WITH CSV HEADER",
                        f
                    )
                connection.commit()       

                # Remove any rows that gps_latitude and gps_longitude are null
                DELETE_ROWS = """DELETE FROM villageTest2 WHERE gps_latitude IS NULL OR gps_longitude IS NULL;"""
                crsc.execute(DELETE_ROWS)
                connection.commit()
                num_rows_deleted = crsc.rowcount
                print(f'{num_rows_deleted} rows deleted where gps_latitude and gps_longitude are null from the village table.')

                # Set the SRID of the 'geom' column to 4326
                SET_GEOM_SRID = """UPDATE villageTest2 SET geom = ST_SetSRID(ST_MakePoint(gps_longitude, gps_latitude), 4326);"""
                crsc.execute(SET_GEOM_SRID)
                connection.commit()          
                             
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')

