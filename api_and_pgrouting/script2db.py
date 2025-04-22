import json
import psycopg2

# Database connection setup (replace with your connection details)
conn = psycopg2.connect(
    dbname="osm_routing_test", 
    user="urd2024", 
    password="password", 
    host="127.0.0.1", 
    port="5432"
)
cursor = conn.cursor()

# Load the GeoJSON file
with open('graph.json') as f:
    data = json.load(f)

# Iterate over the features in the GeoJSON
for feature in data['features']:
    geometry = feature['geometry']
    properties = feature['properties']
    
    # Handling Point geometry for nodes
    if geometry['type'] == 'Point':
        osm_id = properties['osmId']
        lat, lon = geometry['coordinates']
        
        # Insert the Point data into the nodes table
        cursor.execute("""
            INSERT INTO nodes (osm_id, lat, lon, geom)
            VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """, (osm_id, lat, lon, lon, lat))  # lon, lat order for MakePoint
        
    # Handling LineString geometry for edges
    elif geometry['type'] == 'LineString':
        osm_id = properties['osmId']
        src = properties['src']
        tgt = properties['tgt']
        coordinates = geometry['coordinates']
        
        # Get the start and end coordinates for the LineString (edges)
        start_lat, start_lon = coordinates[0]  # First point in the LineString
        end_lat, end_lon = coordinates[-1]  # Last point in the LineString
        
        # Insert the LineString data into the edges table
        cursor.execute("""
            INSERT INTO edges (osm_id, source, target, cost, geom)
            VALUES (%s, %s, %s, ST_Distance(a.geom, b.geom), ST_MakeLine(a.geom, b.geom))
            FROM nodes a, nodes b
            WHERE a.osm_id = %s AND b.osm_id = %s;
        """, (osm_id, src, tgt, src, tgt))  # Reference nodes by osm_id
        
# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()

print("Data successfully inserted into nodes and edges tables.")
