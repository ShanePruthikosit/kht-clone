'''
postgreSQL.py
A python program used by api_provider2.py
interacting mostly with the postgreSQL database
which includes query functions and json and geojson
conversion function
              
              Created by Nathadon Samairat
                      & Panupong Dangkajitpetch
                      Oct 6, 2023
'''

# Essential libraries
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import geojson
from psycopg2 import sql
from shapely import wkb
from shapely.geometry import mapping
from shapely.wkb import loads as wkb_loads
import json
from village_url_model import village_url_data
from datetime import datetime
import pytz

from testing_cache import my_hash

bangkok_time = datetime.now(pytz.timezone('Asia/Bangkok')) #for future frontend display if needed

import sys
testing_path = '/home/kht-team/secret_function/'
sys.path.append(testing_path)
#from testing_cache import hash

# Database configurations
db_host = "127.0.0.1" 
db_port = "5432"
db_name = "mhs_geographic"
db_user = "postgres"
db_password = "M@3_ge0_D4t4"

# Connection parameters
connection_params = {
    "host": db_host,
    "port": db_port,
    "dbname": db_name,
    "user": db_user,
    "password": db_password,
}

''' ================================ Format converter ==================================== '''
'''
The function converts query output to a geojson format.
Arguments:
  cursor      - A cursor object to execute SQL queries
  query       - A query to be executed
Return data output in a geojson format.
'''
def query_to_geojson(cursor, query):
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    features = []
    for row in results:
        properties = dict(zip(columns, row))
        geometry_key = 'geom'
        geometry_str = properties.get(geometry_key)
        if geometry_str is not None:
            try:
                # Convert the hex WKB to a Shapely geometry
                geometry = wkb.loads(geometry_str, hex=True)
                # Convert the Shapely geometry to GeoJSON
                geometry_geojson = mapping(geometry)
                feature = geojson.Feature(properties=properties, geometry=geometry_geojson)
                features.append(feature)
            except (json.JSONDecodeError, ValueError):
                print(f"Invalid GeoJSON string: {geometry_str}")

    feature_collection = geojson.FeatureCollection(features)
    # geojson_result = geojson.dumps(feature_collection, indent=2)
    return feature_collection

'''
The function converts query output to a json format.
Arguments:
  cursor      - A cursor object to execute SQL queries
  query       - A query to be executed
Return data output in json format.
'''
def query_to_json(cursor, query):
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    features = []
    for row in results:
        properties = dict(zip(columns, row))
        feature = {"properties": properties}
        features.append(feature)
    feature_collection = {"type": "FeatureCollection", "features": features}
    return feature_collection

''' ================================ Query village ==================================== '''
'''
The function to query all villages or a specific village.
Arguments:
  village_id  - target village id leave blank to select all village
Return data output in geojson format.
'''
def get_village(village_id=""):
    query = None
    if village_id == "":
        query = sql.SQL('''SELECT village.*, 
                                    ARRAY_AGG(url2.url ORDER BY url2.sequence) AS urls, 
                                    ARRAY_AGG(url2.image_url ORDER BY url2.sequence) AS image_urls, 
                                    ARRAY_AGG(url2.article_title ORDER BY url2.sequence) AS article_titles, 
                                    ARRAY_AGG(url2.posted_date ORDER BY url2.sequence) AS posted_dates
                                FROM village
                                LEFT JOIN url2 ON village.id = url2.village_id
                                GROUP BY village.id
                                ORDER BY village.village_name''')
    else:
        query = sql.SQL('''SELECT village.*,
                            ARRAY_AGG(url2.url ORDER BY url2.sequence) AS urls, 
                            ARRAY_AGG(url2.image_url ORDER BY url2.sequence) AS image_urls, 
                            ARRAY_AGG(url2.article_title ORDER BY url2.sequence) AS article_titles, 
                            ARRAY_AGG(url2.posted_date ORDER BY url2.sequence) AS posted_dates
                        FROM village
                        LEFT JOIN url2 ON village.id = url2.village_id
                        WHERE village.id = {}::uuid
                        GROUP BY village.id
                        ORDER BY village.village_name''').format(sql.Literal(village_id))
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

'''
The function to query all village names.
Return a list of village names.
'''
def get_village_names():
    query = None
    query = sql.SQL("SELECT village_name FROM village_fix")
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        village_names = [row[0] for row in rows] 
        return village_names
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

'''
The function to query all village names in Thai.
Return a list of village names.
'''
def get_village_names_th():
    query = None
    query = sql.SQL("SELECT village_name_th FROM village_fix")
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        village_names_th = [row[0] for row in rows] 
        return village_names_th
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

'''
The function to query village with given start and end year or target year
of projects done in that village.
Arguments:
  year        - target year of the project
  start_year  - start year of the project
  end_year    - end year of the project
Return data output in geojson format.
'''
def get_village_project_by_year(year="", start_year="", end_year=""):
    query = None
    if year:
        start_year = year
        end_year = year
    query = sql.SQL("""
        SELECT village.*, 
            projectStatus.status_name,
            ARRAY_AGG(url2.url ORDER BY url2.sequence) AS urls, 
            ARRAY_AGG(url2.image_url ORDER BY url2.sequence) AS image_urls, 
            ARRAY_AGG(url2.article_title ORDER BY url2.sequence) AS article_titles, 
            ARRAY_AGG(url2.posted_date ORDER BY url2.sequence) AS posted_dates
        FROM village
        JOIN projectvillage ON projectvillage.village_id = village.id
        JOIN project ON project.id = projectvillage.project_id
        JOIN projectStatus ON project.status_id = projectStatus.status_id
        LEFT JOIN url2 ON village.id = url2.village_id
        WHERE EXTRACT(YEAR FROM TO_DATE(project.start_date, 'YYYY-MM-DD')) >= {} 
        AND EXTRACT(YEAR FROM TO_DATE(project.end_date, 'YYYY-MM-DD')) <= {}
        GROUP BY village.id, projectStatus.status_name, project.start_date
        ORDER BY project.start_date DESC
    """).format(sql.Literal(str(start_year)), sql.Literal(str(end_year)))
    try:
        mogrified_query = cursor.mogrify(query)
        print(mogrified_query.decode('utf-8'))
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

'''
The function to query village all villages that are 
not within the given distance to the target facility.
Arguments:
  distance            - distance to facility in kilometers (km)
  facility_type       - the facility type (eg. hospital or school)
Return data all villages that are not within the given distance to the target facility.
'''
def get_village_by_distance(distance="", facility_type=""):
    # Convert distance from km to meters
    distance_m = float(distance) * 1000
    print(f"Distance (meters): {distance_m}, Facility type: {facility_type}")
    query = sql.SQL("""
        SELECT DISTINCT v.*, 
            ARRAY_AGG(url2.url ORDER BY url2.sequence) AS urls, 
            ARRAY_AGG(url2.image_url ORDER BY url2.sequence) AS image_urls, 
            ARRAY_AGG(url2.article_title ORDER BY url2.sequence) AS article_titles, 
            ARRAY_AGG(url2.posted_date ORDER BY url2.sequence) AS posted_dates
        FROM village v
        JOIN {table} f 
          ON ST_DWithin(v.geom::geography, f.geom::geography, %s)
        LEFT JOIN url2 ON v.id = url2.village_id
        GROUP BY v.id
    """).format(table=sql.Identifier(facility_type))
    try:
        mogrified_query = cursor.mogrify(query, (distance_m,))
        print(mogrified_query.decode('utf-8'))
        cursor.execute(mogrified_query)
        geojson_result = query_to_geojson(cursor, mogrified_query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}") #Print the error message
        connection.rollback() #Rollback the transaction


'''
The function to query village by given a target facility and 
maximum the road distance form villages to that target facility.
Arguments:
  road distance       - road distance to facility in kilometers (km)
  facility_type       - the facility type (eg. hospital)
  facility_name       - the facility name (TH)
Return data output in geojson format.
'''
def get_village_by_road_distance(road_distance="", facility_type="", facility_name=""):
    pass

'''
The function to query village by given project type.
Arguments:
  project_type      - project type
Return data output in geojson format.
'''
def get_village_by_project_type(project_type=""):
    query = None 
    query = sql.SQL("""SELECT village.*,
                            ARRAY_AGG(url2.url ORDER BY url2.sequence) AS urls, 
        	            ARRAY_AGG(url2.image_url ORDER BY url2.sequence) AS image_urls, 
        	            ARRAY_AGG(url2.article_title ORDER BY url2.sequence) AS article_titles, 
                            ARRAY_AGG(url2.posted_date ORDER BY url2.sequence) AS posted_dates
                        FROM village
                        JOIN projectvillage ON projectvillage.village_id = village.id
                        JOIN project ON project.id = projectvillage.project_id
 			LEFT JOIN url2 ON village.id = url2.village_id
                        WHERE project.project_type = {}
              		GROUP BY village.id
			ORDER BY village.village_name
	""").format(sql.Literal(project_type))
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' ================================ Query project ==================================== '''
'''
The function to query project by given either village id or 
start year and end year of the project
Arguments:
  village_id          - target village id
  start_year          - start year of the project
  end_year            - end year of the project
Return data output in json format.
'''
def get_project(village_id="", start_year="", end_year=""):
    query = None
    if village_id == "":
        if start_year == "":
            start_year = -1
        if end_year == "":
            end_year = 9999
        query = sql.SQL("""SELECT project.*, projectStatus.status_name
                            FROM project 
                            JOIN projectStatus ON project.status_id = projectStatus.status_id
                            WHERE start_date >= {} 
                            AND end_date <= {}
                            ORDER BY project.start_date DESC""").format(sql.Literal(str(start_year)), sql.Literal(str(end_year)))
    else:
        query = sql.SQL("""SELECT DISTINCT project.id, project_name_en, start_date, end_date, 
                            project_type, projectStatus.status_name, projectvillage.village_id
                            FROM project
                            JOIN projectvillage ON projectvillage.project_id = project.id
                            JOIN projectStatus ON project.status_id = projectStatus.Status_id
                            WHERE village_id = {}::uuid
                            ORDER BY project.start_date DESC""").format(sql.Literal(village_id))
    try:
        cursor.execute(query)
        json_result = query_to_json(cursor, query)
        return json_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' ================================ Query project donor ==================================== '''
'''
The function to query donors of the target project
Arguments:
  project_id      - target project id
Return data output in json format.
'''
def get_project_donor(project_id=""):
    query = None
    query = sql.SQL("""SELECT donor.id,donor.donator_name
                        FROM donor
                        JOIN projectdonor ON projectdonor.donor_id = donor.id
                        WHERE projectdonor.project_id= {}::uuid""").format(sql.Literal(project_id))
    try:
        cursor.execute(query)
        json_result = query_to_json(cursor, query)
        return json_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' =================================== Query hospital ===================================== '''
'''
The function to query all hospitals
Return data output in geojson format.
'''
def get_hospital():
    query = None
    query = sql.SQL("SELECT * FROM hospital")
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' =================================== Query School ======================================= '''
'''
The function to query all schools
Return data output in geojson format.
'''
def get_school():
    query = None
    query = sql.SQL("SELECT * FROM school_old")
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' =================================== Query districts ====================================== '''
'''
The function to query all districts nodes
Return data output in geojson format.
'''
def get_mhs_districts():
    query = None
    query = sql.SQL("SELECT * FROM mhs_districts")
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' =================================== Query subdistricts ====================================== '''
'''
The function to query all sub districts nodes
Return data output in geojson format.
'''
def get_mhs_subdistricts():
    query = None
    query = sql.SQL("SELECT * FROM mhs_subdistricts")
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' ==================================== Query roads ====================================== '''
'''
The function to query all roads nodes
Return data output in geojson format.
'''
def get_mhs_roads():
    query = None
    query = sql.SQL("SELECT * FROM mhs_roads")
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' =================================== Query water area ==================================== '''
'''
The function to query all water area nodes
Return data output in geojson format.
'''
def get_mhs_water_areas():
    query = None
    query = sql.SQL("SELECT * FROM mhs_water_areas")
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' =================================== Query water lines ==================================== '''
'''
The function to query all water lines nodes
Return data output in geojson format.
'''
def get_mhs_water_lines():
    query = None
    query = sql.SQL("SELECT * FROM mhs_water_lines")
    try:
        cursor.execute(query)
        geojson_result = query_to_geojson(cursor, query)
        return geojson_result
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

''' =================================== Insert village url ==================================== '''
'''
The function to insert village url.
Arguements
    village_url_data    - village_url data in village_url_model.py
Returns message status if the data is inserted or not which
depends on the village name is found in the village table or not.
'''
def insert_village_url(village_url_data : village_url_data):
    # print(village_url_data)
    password = my_hash(village_url_data.password)
    query_password = sql.SQL('''
                                SELECT password
                                FROM Users
                                ORDER BY id
                                LIMIT 1;
                                    ''')
    cursor.execute(query_password)
    stored_password = cursor.fetchone()
    # print(password)
    # print(stored_password[0])
    if password == stored_password[0]:
        query = None
        params = (village_url_data.village_name, village_url_data.url, village_url_data.image_url, village_url_data.article_title, village_url_data.posted_date, village_url_data.village_name, village_url_data.village_name)
        query = sql.SQL("""
            INSERT INTO url2 (village_name, url, image_url, article_title, posted_date, created_time, sequence)
            SELECT %s, %s, %s, %s, %s, CAST(TO_CHAR(NOW()::date, 'DD/MM/YYYY') AS VARCHAR(256)),
            COALESCE((SELECT MAX(sequence) FROM url2 WHERE village_name = %s), 0) + 1
            WHERE EXISTS (
                SELECT 1
                FROM village
                WHERE LOWER(village.village_name) = LOWER(%s)
            )
        """)
        try:
            print(cursor.mogrify(query, params).decode('utf-8'))
            cursor.execute(query, params)
            connection.commit()
            rows_inserted = cursor.rowcount

            print(f"Rows inserted: {rows_inserted}")
            if rows_inserted == 0:
                print(f"Data not inserted into url table. {rows_inserted} rows inserted.")
                message = {
                    "status": "Failed",
                    "message": f"Password is correct but Village '{village_url_data.village_name}' not found in village table. Data not inserted into url table."
                }
            else:
                print(f"Data inserted into url table. {rows_inserted} rows inserted.")
                message = {
                    "status": "Success",
                    "message": f"Password is correct! Village '{village_url_data.village_name}' found in village table. Data inserted into url table."
                }
        except Exception as e:
            print(f"Error executing INSERT query: {e}")
            connection.rollback()
            error_message = {
            "status": "Failed",
            "message": f"Error executing query: {e}"
            }
            return error_message
    else:
        message = {
            "status": "Failed",
            "password_message": "The password you entered is incorrect. Please try again."
        }
    return message

def count_user(ip=""):
    query = None
    query = sql.SQL("""INSERT INTO ipaddr (ip, time_stamp) VALUES (%s, NOW())""")
    cursor.execute(query, (ip,))
    try:
        mogrified_query = cursor.mogrify(query)
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

def get_test_table():
    query = None
    query = sql.SQL("SELECT * FROM mhs_roads_test")
    try:
        cursor.execute(query)
    except Exception as e:
        print(f"Error executing query: {e}")  # Print the error message
        connection.rollback()  # Rollback the transaction

# Establish a connection to the database
try:
    connection = psycopg2.connect(**connection_params)
    print("Connected to the database!")
    cursor = connection.cursor() # Create a cursor object to execute SQL queries
    # print(get_test_table())

except psycopg2.Error as e:
    print(f"Unable to connect to the database. Error: {e}")

# function to close the database connection 
def close_all():
    if connection:
        cursor.close()
        connection.close()
        print("Connection closed.")
