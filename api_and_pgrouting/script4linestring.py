import json

# Function to generate SQL insert statements from GeoJSON data
def generate_sql_insert(graph_data, table_name="roads"):
    insert_statements = []
    
    for feature in graph_data:
        if feature['geometry']['type'] == 'LineString':
            osm_id = feature['properties']['osmId']
            coordinates = feature['geometry']['coordinates']
            
            # Format coordinates into WKT LineString format
            wkt_coordinates = ', '.join(f"{lon} {lat}" for lon, lat in coordinates)
            wkt_line = f"LINESTRING({wkt_coordinates})"
            
            # Create the SQL insert statement with an additional raw_line column
            sql_statement = f"INSERT INTO {table_name} (osm_id, geom, raw_line) VALUES ({osm_id}, ST_GeomFromText('{wkt_line}'), '{wkt_line}');"
            insert_statements.append(sql_statement)
    
    return insert_statements

# Read the GeoJSON data from the input file
input_file = 'graph.json'
with open(input_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract the 'features' key that contains the list of features
features = data['features']

# Generate SQL insert statements
sql_statements = generate_sql_insert(features)

# Print out each SQL statement
for sql in sql_statements:
    print(sql)

# Optionally, you can write the output to a .sql file
output_file = 'insert_roads.sql'
with open(output_file, 'w', encoding='utf-8') as file:
    for sql in sql_statements:
        file.write(sql + '\n')

print(f"SQL insert statements written to {output_file}")
