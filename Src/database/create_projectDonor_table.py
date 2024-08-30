'''
create_projectDonor_table.py
A python program to create a projectDonor table.
This table is created to store the relationship between projects and donors 
where one project can have multiple donors. It uses the project table and donor table 
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import os
import psycopg2
from config import config

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
Function to create the projectDonor table
'''
def create_projectDonor_table():
    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)
        crsc = connection.cursor()
       
        CREATE_TABLE = """CREATE TABLE IF NOT EXISTS projectDonor (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                project_id UUID,
                donor_id UUID,
                FOREIGN KEY (project_id) REFERENCES project(id),
                FOREIGN KEY (donor_id) REFERENCES donor(id)
            );"""
        crsc.execute(CREATE_TABLE)
        connection.commit()

        # Reset the projectDonor table
        DELETE_ALL_ROWS = """DELETE FROM projectDonor;"""
        crsc.execute(DELETE_ALL_ROWS)
        connection.commit()

        INSERT_TO_PROJECTDONOR_TABLE_DONOR1 = """
        INSERT INTO projectDonor (project_id, donor_id)
        SELECT DISTINCT project.id AS project_id, donor.id AS donor_id
        FROM project
        JOIN donor ON project.donor1_id = donor.record_id
        """
        crsc.execute(INSERT_TO_PROJECTDONOR_TABLE_DONOR1)
        connection.commit()

        INSERT_TO_PROJECTDONOR_TABLE_DONOR2 = """
        INSERT INTO projectDonor (project_id, donor_id)
        SELECT DISTINCT project.id AS project_id, donor.id AS donor_id
        FROM project
        JOIN donor ON project.donor2_id = donor.record_id
        """
        crsc.execute(INSERT_TO_PROJECTDONOR_TABLE_DONOR2)
        connection.commit()

        INSERT_TO_PROJECTDONOR_TABLE_DONOR3 = """
        INSERT INTO projectDonor (project_id, donor_id)
        SELECT DISTINCT project.id AS project_id, donor.id AS donor_id
        FROM project
        JOIN donor ON project.donor3_id = donor.record_id
        """
        crsc.execute(INSERT_TO_PROJECTDONOR_TABLE_DONOR3)
        connection.commit()
                                            
        print('\nprojectDonor table created successfully.')

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')
