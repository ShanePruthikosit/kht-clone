'''
create_donor_table.py
A python program to create a donor table and
insert data from a CSV file into the table.
Also updates the table with new data from the CSV file.
Data is about donors contributing to a project for 
Karen Hilltribes Trust.
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import psycopg2
from clean_csv import select_columns_and_save_csv
from config import config
import pandas as pd
from get_file_path import get_file_path

'''
Function to create the donor table
'''
def create_donor_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)
        crsc = connection.cursor() 

        CREATE_TABLE = """CREATE TABLE IF NOT EXISTS Donor (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                record_id VARCHAR(256),
                donator_name VARCHAR(256),
                created_time VARCHAR(256)
            );"""
        crsc.execute(CREATE_TABLE)
        connection.commit()

        # Input and output file paths
        input_file_path = get_file_path('Donors_001.csv', 'Data')
        output_file_path = get_file_path('donors_001.csv')

        columns_to_select = ['Record Id', 'Full Name', 'Created Time']

        # Select columns and save to a  new CSV file
        select_columns_and_save_csv(input_file_path, output_file_path, columns_to_select)

        # Fetch the 'created_time' column from the 'project' table
        crsc.execute("SELECT created_time FROM donor;")
        existing_times = [item[0] for item in crsc.fetchall()]

        # Load the new CSV data into a DataFrame
        new_data = pd.read_csv(output_file_path)

        # Filter the new data to only include rows with 'created_time' values that don't exist in the database
        new_data = new_data[~new_data['created_time'].isin(existing_times)]
       
        # If there are no new rows, print a message and return
        if new_data.empty:
            print('\nNo new rows to add to the donor table.')
        else:
            print('\nAdding new rows to the donor table...')
            num_rows_added = len(new_data)
            print(f'{num_rows_added} rows added.')

        # Save the filtered data to a new CSV file
        new_data.to_csv(output_file_path, index=False)

        # Use 'copy_expert' to copy the new data from the CSV file into the 'project' table
        with open(output_file_path, 'r') as f:
            crsc.copy_expert(
                "COPY donor (record_id, donator_name, created_time) FROM STDIN WITH CSV HEADER",
                f
            )
        connection.commit()    

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')
