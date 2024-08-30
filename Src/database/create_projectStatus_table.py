'''
create_projectStatus_table.py 
A python program to create a projectStatus table.
This table is created to store the status of the project.
Where there are 4 types of status: New, Ongoing, Repair, Extension
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import psycopg2
from config import config

'''
Function to create the projectStatus table
'''
def create_projectStatus_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)

        crsc = connection.cursor()
       
        CREATE_TABLE = """CREATE TABLE IF NOT EXISTS projectStatus (
                status_id INTEGER PRIMARY KEY,
                status_name VARCHAR(256)
            );"""
        crsc.execute(CREATE_TABLE)
        connection.commit()

        #insert into table 1 - New, 2 - Ongoing, 3 - Repair
        INSERT_TABLE = """
            INSERT INTO projectStatus (status_id, status_name) 
            VALUES
                (1, 'New'),
                (2, 'Ongoing'),
                (3, 'Repair'),
                (4, 'Extension');
        """
        crsc.execute(INSERT_TABLE)
        connection.commit()
       
        print('projectStatus table created successfully.')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')
