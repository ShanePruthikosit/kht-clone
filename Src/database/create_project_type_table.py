'''
create_project_type_table.py
This table contains 7 types of projects that the Karen
Hilltribes Trust does. It is stored in the projectType table
School Buses, Irrigation, WASH, Domitory Meals, Building Dormitories,
Further Education Scholarships, and Bus and Meals.
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import os
import psycopg2
from clean_csv import select_columns_and_save_csv
from config import config
import pandas as pd

'''
Function to get the file path
Arguments
    filename    - name of the file
Returns the file path
'''
def get_file_path(filename):
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    return file_path

'''
Function to create the project type table
'''
def create_project_type_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)
        crsc = connection.cursor() 

        CREATE_TABLE = f"""CREATE TABLE IF NOT EXISTS projectType (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                zoho_project_type_id VARCHAR(255),
                project_type_name_en VARCHAR(255),
                created_time VARCHAR(255)
            );"""
        crsc.execute(CREATE_TABLE)
        connection.commit()

        input_file_path = get_file_path('Data/Programmes_001.csv')
        output_file_path = get_file_path('project_types.csv')

        columns_to_select = ['Record Id', 'Product Name', 'Created Time']

        # Select columns and save to a  new CSV file
        select_columns_and_save_csv(input_file_path, output_file_path, columns_to_select)

        # Fetch the 'created_time' column from the 'project' table
        crsc.execute("SELECT created_time FROM projectType;")
        existing_times = [item[0] for item in crsc.fetchall()]

        # Load the new CSV data into a DataFrame
        new_data = pd.read_csv(output_file_path)

        # Filter the new data to only include rows with 'created_time' values that don't exist in the database
        new_data = new_data[~new_data['created_time'].isin(existing_times)]
       
        # If there are no new rows, print a message and return
        if new_data.empty:
            print('\nNo new rows to add to the projectType table.')
        else:
            print('\nAdding new rows to the projectType table...')
            num_rows_added = len(new_data)
            print(f'{num_rows_added} rows added.')

        # Save the filtered data to a new CSV file
        new_data.to_csv(output_file_path, index=False)

        # Use 'copy_expert' to copy the new data from the CSV file into the 'project' table
        with open(output_file_path, 'r') as f:
            next(f)  # Skip the header
            crsc.copy_expert(
                "COPY projectType (zoho_project_type_id, project_type_name_en, created_time) FROM STDIN WITH CSV",
                f
            )
        connection.commit()   

        # Alter the projectTest table to add a new column called 'project_type'
        ADD_PROJECT_TYPE_COLUMN = """ALTER TABLE projectTest ADD COLUMN project_type VARCHAR(255);"""
        crsc.execute(ADD_PROJECT_TYPE_COLUMN)
        connection.commit()   

        print('Added column \'project_type\' to projectTest table.')
        
        # Use the query above to update the 'project_type' column in the 'project' table
        UPDATE_PROJECT_TYPE_COLUMN = """UPDATE projectTest SET project_type = projectType.project_type_name_en
            FROM projectType 
            WHERE projectType.zoho_project_type_id = projectTest.zoho_project_type_id;"""
        crsc.execute(UPDATE_PROJECT_TYPE_COLUMN)
        connection.commit()   

        print('Updated column \'project_type\' in projectTest table.')

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')
