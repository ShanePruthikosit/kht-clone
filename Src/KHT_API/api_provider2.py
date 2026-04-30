'''
api_provider2.py (BROKEN VERSION)
==================================
Deliberately broken for testing purposes.
One bug introduced per tested function/behavior:

BUG 1: get_route — uses elevation tables even when use_elevation=False
BUG 2: get_route — assembles features without wrapping in {"type": "Feature", ...}
BUG 3: pull_village_data — facility_type without distance returns 200 instead of 400
BUG 4: pull_village_data — year filter branch ignored; always calls get_village()
BUG 5: check_valid — always returns True regardless of key match
BUG 6: read_root — returns wrong message key
BUG 7: get_shortest_route — missing start/end validation (no 422 on missing params handled wrong)
BUG 8: pull_village_data — no auth check (always allows through)
BUG 9: pull_mhs_water_lines — requires auth (should be public)
BUG 10: create_village_url — GET method allowed instead of POST only
'''

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
import os
from dotenv import load_dotenv
from village_url_model import village_url_data

load_dotenv()
hostname = os.getenv('hostname', 'kht-map.org')
app = FastAPI()
user_dict = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Origin", "Content-Type"],
)

ROUTING_DB_CONFIG = {
    "dbname": "osm_routing_test",
    "user": "postgres",
    "password": "M@3_ge0_D4t4",
    "host": "localhost",
    "port": "5432"
}

def get_route(start_node: int, end_node: int, use_elevation: bool = False):
    # BUG 1: always uses elevation tables regardless of use_elevation flag
    node_table = "elevation_nodes"
    edge_table = "elevation_edges"

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
            if isinstance(aggregated, str):
                aggregated_geojson = json.loads(aggregated)
            else:
                aggregated_geojson = aggregated

            for geojson_item in aggregated_geojson:
                if isinstance(geojson_item, str):
                    geometry = json.loads(geojson_item)
                else:
                    geometry = geojson_item

                # BUG 2: appends raw geometry dict instead of wrapping in Feature
                features.append(geometry)

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


def check_valid(message, key):
    # BUG 5: always returns True — no actual validation performed
    return True


# BUG 6: returns wrong key name 'status' instead of 'message'
@app.get("/")
def read_root():
    return {"status": "The data hosting is working!"}


@app.get("/api/testpackage/")
def getHashFunction():
    return FileResponse('testpackage.js')


@app.get("/api/village/")
def pull_village_data(village_id="", year="", start_year="", end_year="",
                     project_type="", distance="", road_distance="",
                     facility_type="", time="", key=""):

    # BUG 8: auth check removed — anyone can access village data
    # if not check_valid(time, key):
    #     raise HTTPException(status_code=401, detail="Key mismatch")

    try:
        # BUG 4: year filter branch skipped — always falls through to get_village()
        if facility_type != "":
            if distance != "":
                result = postgreSQL.get_village_by_distance(distance, facility_type)
            elif road_distance != "":
                result = postgreSQL.get_village_by_road_distance(road_distance, facility_type)
            else:
                # BUG 3: returns 200 with error dict instead of raising 400
                return {"error": "Invalid argument"}
        elif project_type != "":
            result = postgreSQL.get_village_by_project_type(project_type)
        else:
            result = postgreSQL.get_village(village_id)

        if result is None:
            return {"type": "FeatureCollection", "features": []}
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in pull_village_data: {e}")
        return {"type": "FeatureCollection", "features": []}


@app.get("/api/village_names/")
def pull_village_names():
    village_names = postgreSQL.get_village_names()
    return village_names


@app.get("/api/village_names_th/")
def pull_village_names_th():
    village_names_th = postgreSQL.get_village_names_th()
    return village_names_th


@app.get("/api/project/")
def pull_project_data(village_id="", start_year="", end_year="", time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    json_data = postgreSQL.get_project(village_id, start_year, end_year)
    return json_data


@app.get("/api/project_donor/")
def pull_project_donor_data(project_id="", time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    json_data = postgreSQL.get_project_donor(project_id)
    return json_data


@app.get("/api/school/")
def pull_school_data(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_school()
    return geojson_data


@app.get("/api/hospital/")
def pull_hospital_data(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_hospital()
    return geojson_data


@app.get("/api/mhs_districts/")
def pull_mhs_districts_data(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_districts()
    return geojson_data


@app.get("/api/mhs_subdistricts/")
def pull_mhs_subdistricts_data(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_subdistricts()
    return geojson_data


@app.get("/api/mhs_roads/")
def pull_mhs_roads(request: Request, time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_roads()
    postgreSQL.count_user(request.client.host)
    return geojson_data


@app.get("/api/mhs_water_areas/")
def pull_mhs_water_areas(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_water_areas()
    return geojson_data


# BUG 9: water lines now requires auth (should be public — no auth check)
@app.get("/api/mhs_water_lines")
def pull_mhs_water_lines(time="", key=""):
    if not check_valid(time, key):
       return {'Error' : 'Key mismatch'}
    geojson_data = postgreSQL.get_mhs_water_lines()
    return geojson_data


# BUG 10: GET method allowed on POST-only endpoint
@app.api_route("/api/post/village_url/", methods=["GET", "POST"])
async def create_village_url(village_url_data: village_url_data = None):
    if village_url_data is None:
        return {"message": "No data provided"}
    message = postgreSQL.insert_village_url(village_url_data)
    return {"message": message}


if __name__ == "__main__":
    import sys
    host = '0.0.0.0'
    port = 2546
    argvs = sys.argv
    if len(argvs) == 3:
        host = argvs[1]
        port = int(argvs[2])
    cert_file = f'/etc/letsencrypt/live/{hostname}/fullchain.pem'
    key_file  = f'/etc/letsencrypt/live/{hostname}/privkey.pem'
    passphrase = b'd0#KHTM@p67'
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file, password=passphrase)
    uvicorn.run(app, host=host, port=port, ssl_keyfile=key_file,
                ssl_certfile=cert_file, ssl_keyfile_password=passphrase)