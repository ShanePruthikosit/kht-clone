'''
**NOT IN USED**
create_village_url_table.py 
A python program to create a villageUrl table and
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

def create_village_url_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        with psycopg2.connect(**params) as connection:
            with connection.cursor() as crsc:
                CREATE_TABLE = """CREATE TABLE IF NOT EXISTS villageUrl (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    village_id UUID,
                    url_id UUID
                );"""
                crsc.execute(CREATE_TABLE)

                INSERT_TO_VILLAGEURL_TABLE = """INSERT INTO villageUrl (village_id, url_id)
                                                    SELECT village.id, url.id
                                                    FROM url
                                                    JOIN village ON url.village_name = village.village_name
                                                    WHERE url.sequence = 1 OR url.village_name IN (
                                                        SELECT village_name
                                                        FROM url
                                                        GROUP BY village_name
                                                        HAVING COUNT(DISTINCT sequence) > 1);"""
                crsc.execute(INSERT_TO_VILLAGEURL_TABLE)
                connection.commit()
                                                    
                print('\nvillageUrl table created successfully.')           
                             
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')

