'''
create_project_table.py 
A python program to create a project table and
insert data from a CSV file into the table.
Also updates the table with new data from the CSV file.
This data is about projects that the Karen Hilltribes Trust 
is working on or has worked on.
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import psycopg2
from clean_csv import select_columns_and_save_csv
from config import config
import pandas as pd
import traceback
from get_file_path import get_file_path

'''
Function to create the project table
'''
def create_project_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)
        crsc = connection.cursor() 
        CREATE_TABLE = """CREATE TABLE IF NOT EXISTS project (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                project_name_en VARCHAR(256),
                zoho_project_type_id VARCHAR(256),
                created_time VARCHAR(256),
                start_date VARCHAR(256),
                end_date VARCHAR(256),
                donor1_id VARCHAR(256),
                donor3_id VARCHAR(256),
                donor2_id VARCHAR(256),
                zoho_village_id VARCHAR(256),
                status VARCHAR(256),
                project_type VARCHAR(256)
            );"""
        crsc.execute(CREATE_TABLE)
        connection.commit()

        # Input and output file paths
        input_file_path = get_file_path('Project_Cases_001.csv', 'Data')
        output_file_path = get_file_path('project_001.csv')

        columns_to_select = ['Solution Title', 'Product Name.id', 'Created Time', 'Project Start Date', 'Project End Date', 'Donor 1 (D1).id', 'Donor 3 (D3).id', 'Donor 2 (D2).id', 'Village.id', 'Project Type']

        # Select columns and save to a  new CSV file
        select_columns_and_save_csv(input_file_path, output_file_path, columns_to_select)

        # Fetch the 'created_time' column from the 'project' table
        crsc.execute("SELECT created_time FROM project;")
        existing_times = [item[0] for item in crsc.fetchall()]

        # Load the new CSV data into a DataFrame
        new_data = pd.read_csv(output_file_path)

        # Filter the new data to only include rows with 'created_time' values that don't exist in the database
        new_data = new_data[~new_data['created_time'].isin(existing_times)]
       
        # If there are no new rows, print a message and return
        if new_data.empty:
            print('\nNo new rows to add to the project table.')
        else:
            print('\nAdding new rows to the project table...')
            num_rows_added = len(new_data)
            print(f'{num_rows_added} total rows added to the project table.')

        # Save the filtered data to a new CSV file
        new_data.to_csv(output_file_path, index=False)

        # Use 'copy_expert' to copy the new data from the CSV file into the 'project' table
        with open(output_file_path, 'r') as f:
            next(f)  # Skip the header
            crsc.copy_expert(
                "COPY project (project_name_en, zoho_project_type_id, created_time, start_date, end_date, donor1_id, donor3_id, donor2_id, zoho_village_id, status) FROM STDIN WITH CSV DELIMITER ',' QUOTE '\"' NULL 'null'",
                f
            )
        connection.commit()    

        # add column for status_id  
        ADD_PROJECTSTATUS_COLUMN = """ALTER TABLE project
            ADD COLUMN IF NOT EXISTS status_id INTEGER REFERENCES projectStatus (status_id);"""
        crsc.execute(ADD_PROJECTSTATUS_COLUMN)
        connection.commit()

        # Update the 'status_id' column based on the values from the projectStatus table
        UPDATE_STATUS_ID = """
            UPDATE project
            SET status_id = projectStatus.status_id
            FROM projectStatus
            WHERE project.status = projectStatus.status_name;
        """
        crsc.execute(UPDATE_STATUS_ID)
        connection.commit()

        # also add the project_type to the project table based on
        # the relationship between the project.zoho_project_type_id and projectType.zoho_project_type_id
        UPDATE_PROJECT_TYPE = """
            UPDATE project
            SET project_type = projectType.project_type_name_en
            FROM projectType
            WHERE project.zoho_project_type_id = projectType.zoho_project_type_id;
        """
        crsc.execute(UPDATE_PROJECT_TYPE)
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        tb = traceback.format_exc()
        print("Error:", error)
        print(tb)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')


