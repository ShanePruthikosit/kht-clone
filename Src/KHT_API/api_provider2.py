'''
api_provider2.py
A python program to run a web server using uvicorn
and handle all API requests using fastapi which
will call postgreSQL functions and return back
the data output in geojson or json format.

              Created by Nathadon Samairat
                      & Panupong Dangkajitpetch
                      Oct 6, 2023
'''

# Libraries
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import postgreSQL
import json
import hashlib
import uvicorn
import ssl
import execjs
import psycopg2
from village_url_model import village_url_data


app = FastAPI()
user_dict = {}

''' CORS middleware to allow all origins configuration '''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace '*' with specific origins
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Origin", "Content-Type"],
)

# --- Begin Integration of Test PG API Functionality ---
# Define DB configuration for the routing API (adjust if needed)
ROUTING_DB_CONFIG = {
    "dbname": "osm_routing_test",
    "user": "postgres",
    "password": "M@3_ge0_D4t4",
    "host": "localhost",
    "port": "5432"
}

def get_route(start_node: int, end_node: int, use_elevation: bool = False):
    if use_elevation:
        node_table = "elevation_nodes"
        edge_table = "elevation_edges"
    else:
        node_table = "new_nodes"
        edge_table = "new_edges"

    query = f"""
    WITH 
    start_point AS (
        SELECT id AS source_id FROM {node_table} WHERE id = %s LIMIT 1
    ),
    end_point AS (
        SELECT id AS target_id FROM {node_table} WHERE id = %s LIMIT 1
    ),
    path_result AS (
        SELECT * 
        FROM pgr_dijkstra(
            'SELECT id, source, target, cost AS cost FROM {edge_table}',
            (SELECT source_id FROM start_point),
            (SELECT target_id FROM end_point),
            directed := false
        )
    ),
    path_with_geom AS (
        SELECT 
            p.seq,
            ST_AsGeoJSON(e.geom) AS geojson
        FROM 
            path_result p
        JOIN 
            {edge_table} e ON p.edge = e.id
    )
    SELECT json_agg(geojson ORDER BY seq) FROM path_with_geom;
    """

    try:
        conn = psycopg2.connect(**ROUTING_DB_CONFIG)
        cur = conn.cursor()
        cur.execute(query, (start_node, end_node))
        result = cur.fetchone()
        features = []
        if result and result[0]:
            aggregated = result[0]
            # If aggregated is a string, parse it; otherwise, assume it's already a list
            if isinstance(aggregated, str):
                aggregated_geojson = json.loads(aggregated)
            else:
                aggregated_geojson = aggregated

            for geojson_item in aggregated_geojson:
                if isinstance(geojson_item, str):
                    geometry = json.loads(geojson_item)
                else:
                    geometry = geojson_item

                features.append({
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {}  # Add additional properties if needed
                })
        geojson_response = {
            "type": "FeatureCollection",
            "features": features
        }
        cur.close()
        conn.close()
        return geojson_response
    except psycopg2.Error as e:
        return {"error": f"Database error: {e}"}

@app.get("/api/route/")
def get_shortest_route(start: int, end: int, use_elevation: int = 0):
    if not start or not end:
        raise HTTPException(status_code=400, detail="Missing start or end node")
    route_data = get_route(start, end, use_elevation=bool(use_elevation))
    return JSONResponse(content=route_data)
# --- End Integration of Test PG API Functionality ---


'''
Encryption ensuring the private connection 
Arguements
    message     - message to be encrypted
    key         - given hash value
Return if the key match with the hash value then
return True, otherwise return False.
'''
def check_valid(message, key):
    js_code = "const crypto = require('crypto');\n"
    with open("testpackage.js", "r") as js_file:
        js_code += js_file.read()
    js_code += ("""\nvar result = getOldTestPackage("{}")""").format(message)
    ctx = execjs.compile(js_code)
    hash_val = ctx.eval('result')
    print("compare {} {}".format(hash_val, key))
    if hash_val == key:
         return True
    else:
         return False

'''
Function handles root url whether the server is running or not 
Return success status message
'''
@app.get("/")
def read_root():
    return {"message": "The data hosting is working!"}

@app.get("/api/testpackage/")
def getHashFunction():
    return FileResponse('testpackage.js')

'''
Function handles all villages query decide which 
function to run by given arguments
Arguments
    village_id      - target village id
    year            - year of the project done in the villages
    start_year      - start year of the project done in the villages
    end_year        - end year of the project done in the villages
    project_type    - type of the project done in the villages
    distance        - maximum distance from facility to the villages
    road_distance   - maximum road distance from facility to the villages
    facility_type   - target facility type
    facility_name   - target facility name
Return data output in geojson format
'''
@app.get("/api/village/")
def pull_village_data(village_id="", year="", start_year="", end_year="", project_type="",
                        distance="", road_distance="", facility_type="", time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    if year != "" or (start_year != "" and end_year != ""):
        geojson_data = postgreSQL.get_village_project_by_year(year, start_year, end_year)
    elif facility_type != "":
        if distance != "":
            geojson_data = postgreSQL.get_village_by_distance(distance, facility_type)
        elif road_distance != "":
            geojson_data = postgreSQL.get_village_by_road_distance(distance, facility_type)
        else:
            geojson_data = {'Invalid argument'}
    elif project_type != "":
        geojson_data = postgreSQL.get_village_by_project_type(project_type)
    else:
        geojson_data = postgreSQL.get_village(village_id)
    return geojson_data

'''
Function to get all the village_names
from the village table
Returns a list of village names
'''
@app.get("/api/village_names/")
def pull_village_names():
    village_names = postgreSQL.get_village_names()
    return village_names

'''
Function handles all projects query
Return data output in json format
'''
@app.get("/api/project/")
def pull_project_data(village_id="", start_year="", end_year="", time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    json_data = postgreSQL.get_project(village_id, start_year, end_year)
    return json_data

'''
Function handles projects donor query
Return data output in json format
'''
@app.get("/api/project_donor/")
def pull_project_donor_data(project_id="", time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    json_data = postgreSQL.get_project_donor(project_id)
    return json_data

'''
Function handles school query
Return data output in json format
'''
@app.get("/api/school/")
def pull_school_data(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_school()
    return geojson_data

'''
Function handles hospital query
Return data output in geojson format
'''
@app.get("/api/hospital/")
def pull_hospital_data(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_hospital()
    return geojson_data

'''
Function handles district node query
Return data output in geojson format
'''
@app.get("/api/mhs_districts/")
def pull_mhs_districts_data(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_districts()
    return geojson_data

'''
Function handles sub district node query
Return data output in geojson format
'''
@app.get("/api/mhs_subdistricts/")
def pull_mhs_subdistricts_data(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_subdistricts()
    return geojson_data

'''
Function handles road node query
Return data output in geojson format
'''
@app.get("/api/mhs_roads/")
def pull_mhs_roads(request: Request, time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_roads()
    postgreSQL.count_user(request.client.host)
    return geojson_data

'''
Function handles water area node query 
Return data output in geojson format
'''
@app.get("/api/mhs_water_areas/")
def pull_mhs_water_areas(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_water_areas()
    return geojson_data

''' 
Function handles water line node query 
Return data output in geojson format
'''
@app.get("/api/mhs_water_lines")
def pull_mhs_water_lines(time="", key=""):
    geojson_data = postgreSQL.get_mhs_water_lines()
    return geojson_data

''' 
Function updates village url in the village_url table 
Return status message.
'''
@app.post("/api/post/village_url/")
async def create_village_url(village_url_data: village_url_data):
    # Insert the data into the database
    message = postgreSQL.insert_village_url(village_url_data)
    # if return Success, then update the url table
    return {"message": message}

''' 
Main function to ask user which host or port they like to run the server
and also get the self-signed ssl certificate data
'''
if __name__ == "__main__":
    import sys

    host = '0.0.0.0'  # '0.0.0.0' to bind to all available network interfaces
    port = 2546  # Change this to your desired port for HTTPS (443 is the default HTTPS port)

    argvs = sys.argv
    if len(argvs) == 3:
        host = argvs[1]
        port = int(argvs[2])

    cert_file = '/etc/letsencrypt/live/kht-map.org/fullchain.pem'
    key_file = '/etc/letsencrypt/live/kht-map.org/privkey.pem'
    passphrase = b'd0#KHTM@p67'

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file, password=passphrase)

    uvicorn.run(app, host=host, port=port, ssl_keyfile=key_file, ssl_certfile=cert_file, ssl_keyfile_password=passphrase)
    print("Running api_provider.py at host {} port {}".format(host, port))
