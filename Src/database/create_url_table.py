'''
**NOT IN USED**
create_url_table.py 
A python program to create a url table and
insert data from a CSV file into the table.
Also updates the table with new data from the CSV file.
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import os
import psycopg2
from config import config
import pandas as pd

def get_file_path(filename):
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    return file_path

def create_url_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        with psycopg2.connect(**params) as connection:
            with connection.cursor() as crsc:
                CREATE_TABLE = """CREATE TABLE IF NOT EXISTS url (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    village_name VARCHAR(256),
                    url VARCHAR(256),
                    article_title VARCHAR(256),
                    posted_date VARCHAR(256),
                    entered_date VARCHAR(256),
                    sequence INT
                );"""
                crsc.execute(CREATE_TABLE)

                # Input and output file paths
                input_file_path = get_file_path('Data/village_url.csv')
                output_file_path = get_file_path('village_url.csv') 

                # Fetch the 'created_time' column from the 'village' table
                crsc.execute("SELECT created_time FROM url;")
                existing_times = [item[0] for item in crsc.fetchall()]

                # Load the new CSV data into a DataFrame
                new_data = pd.read_csv(input_file_path)

                # Drop the 'id' column
                new_data = new_data.drop(columns='id')

                # Print the columns and first few rows of the new data
                print(new_data.head())

                # Filter the new data to only include rows with 'created_time' values that don't exist in the database
                new_data = new_data[~new_data['created_time'].isin(existing_times)]
                
                # If there are no new rows, print a message and return
                if new_data.empty:
                    print('\nNo new rows to add to the villageUrl table.')
                else:
                    print('\nAdding new rows to the villageUrl table...')
                    num_rows_added = len(new_data)
                    print(f'{num_rows_added} rows added.')

                # # Save the filtered data to a new CSV file
                new_data.to_csv(output_file_path, index=False)

                # Use 'copy_expert' to copy the new data from the CSV file into the 'village' table
                with open(output_file_path, 'r') as f:
                    next(f)  # Skip the header
                    crsc.copy_expert(
                        "COPY villageUrl (village_name, url, article_title, posted_date, entered_date, sequence) FROM STDIN WITH CSV HEADER",
                        f
                    )
                connection.commit()   

                # Define a SQL query to update the 'sequence' column in the 'url' table
                UPDATE_SEQUENCE = """
                    -- Create a Common Table Expression (CTE) named 'cte'
                    WITH cte AS (
                        -- Select the 'id' and the row number within each 'village_name' group
                        SELECT id, ROW_NUMBER() OVER(PARTITION BY village_name ORDER BY posted_date) AS rn
                        FROM url
                    )
                    -- Update the 'sequence' column in the 'url' table
                    UPDATE url
                    SET sequence = cte.rn  -- Set 'sequence' to the row number within each 'village_name' group
                    FROM cte  -- Use the 'cte' CTE in the UPDATE statement
                    WHERE url.id = cte.id;  -- Only update rows where the 'id' matches between the 'url' table and the 'cte' CTE
                """
                crsc.execute(UPDATE_SEQUENCE)
                connection.commit()

                print('url table created successfully.')           
                             
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')

