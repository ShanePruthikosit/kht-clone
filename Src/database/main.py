'''
main.py 
A python program to connect to the PostgreSQL database
and create tables from other python programs in the database folder.
              Created by Panupong Dangkajitpetch
                      Oct 6, 2023
'''
import psycopg2
from config import config
from create_projectVillage_table import create_projectVillage_table
from create_project_table import create_project_table 
from create_village_table import create_village_table
from create_donor_table import create_donor_table
from create_projectDonor_table import create_projectDonor_table
from create_district_table import create_district_table

def connect():
    connection = None

    try:    
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)

        crsc = connection.cursor()

        # create_projectStatus_table()
        # create_project_type_table()

        create_village_table()
        create_project_table()
        create_projectVillage_table() # This needs to be updated everytime village is updated
        create_donor_table()
        create_projectDonor_table() # This needs to be updated everytime donor is updated
        create_district_table() 

        # create_hospital_table()
        # create_school_table()
        # create_url_table2()

        # create_village_table_test()
       
        print('PostgreSQL database version:')
        crsc.execute('SELECT version()')
        db_version = crsc.fetchone()
        print(db_version)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')

if __name__ == '__main__':
    connect()






