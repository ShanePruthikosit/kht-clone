from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import json
import uvicorn

app = FastAPI()

# CORS middleware allows all origin configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Origin", "Content-Type"],
)

# Connection setup
DB_CONFIG = {
    "dbname": "osm_routing_test",
    "user": "postgres",
    "password": "M@3_ge0_D4t4",
    "host": "localhost",
    "port": "5432"
}

def get_route(start_node: int, end_node: int):
    query = """
    WITH 
    start_point AS (
        SELECT id AS source_id FROM new_nodes WHERE id = %s LIMIT 1
    ),
    end_point AS (
        SELECT id AS target_id FROM new_nodes WHERE id = %s LIMIT 1
    ),
    path_result AS (
        SELECT * 
        FROM pgr_dijkstra(
            'SELECT id, source, target, cost AS cost FROM new_edges',
            (SELECT source_id FROM start_point),
            (SELECT target_id FROM end_point),
            directed := true
        )
    ),
    path_with_geom AS (
        SELECT 
            p.seq,
            ST_AsGeoJSON(e.geom) AS geojson
        FROM 
            path_result p
        JOIN 
            new_edges e ON p.edge = e.id
    )
    SELECT json_agg(geojson ORDER BY seq) FROM path_with_geom;
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
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

                features.append({
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {} 
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


# API endpoint
@app.get("/api/route/")
def get_shortest_route(start: int, end: int):
    if not start or not end:
        raise HTTPException(status_code=400, detail="Missing start or end node")
    route_data = get_route(start, end)
    return JSONResponse(content=route_data)


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Routing API is running!"}


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 1150
    uvicorn.run(app, host=host, port=port)
