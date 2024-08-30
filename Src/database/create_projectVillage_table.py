'''
create_projectVillage_table.py 
A python program to create a projectVillage table.
This table is created to store the relationship between projects and villages
where one project can have multiple villages and one village can have multiple projects.
It uses the project table and village table
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import os
import psycopg2
from config import config

def get_file_path(filename):
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    return file_path

def create_projectVillage_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)
        crsc = connection.cursor()
       
        CREATE_TABLE = """CREATE TABLE IF NOT EXISTS projectvillage (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                village_id UUID,
                project_id UUID 
            );"""
        crsc.execute(CREATE_TABLE)
        connection.commit()
        
        # Reset the projectVillage table
        DELETE_ALL_ROWS = """DELETE FROM projectvillage;"""
        crsc.execute(DELETE_ALL_ROWS)
        connection.commit()

        INSERT_TO_PROJECTVILLAGE_TABLE = """INSERT INTO projectvillage (village_id, project_id)
                                            SELECT village.id AS village_id, project.id AS project_id
                                            FROM project
                                            JOIN village ON project.zoho_village_id = village.record_id;"""
        crsc.execute(INSERT_TO_PROJECTVILLAGE_TABLE)
        connection.commit()
                                            
        print('\nprojectVillage table created successfully.')

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')





