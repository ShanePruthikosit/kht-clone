#an important thing to note is that this file only handles points(nodes) not linestring(edges)
import json

# Open the output file in write mode
with open('output_queries.txt', 'w', encoding='utf-8') as output_file:
    
    # Load the GeoJSON file with UTF-8 encoding
    with open('graph.json', encoding='utf-8') as f:
        data = json.load(f)

    # Iterate over the features in the GeoJSON
    for feature in data['features']:
        osm_id = feature['properties']['osmId']
        
        geometry = feature['geometry']
        geometry_type = geometry['type']
        
        # Handle 'Point' geometry type (which contains only a pair of coordinates)
        if geometry_type == 'Point':
            lat, lon = geometry['coordinates']
            sql = f"INSERT INTO nodes (osm_id, lat, lon, geom) VALUES ({osm_id}, {lat}, {lon}, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326));\n"
            output_file.write(sql)  # Write the SQL statement to the file
        
        # Handle 'LineString' geometry type (which contains a list of coordinate pairs)
        elif geometry_type == 'LineString':
            coordinates = geometry['coordinates']
            for coord in coordinates:
                lat, lon = coord  # Unpack each pair in the coordinates array
                sql = f"INSERT INTO nodes (osm_id, lat, lon, geom) VALUES ({osm_id}, {lat}, {lon}, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326));\n"
                output_file.write(sql)
        
        # Handle 'Polygon' geometry type (which contains an array of coordinates arrays)
        elif geometry_type == 'Polygon':
            coordinates = geometry['coordinates'][0]  # First array of coordinates in the polygon
            for coord in coordinates:
                lat, lon = coord  # Unpack each pair in the polygon's coordinates
                sql = f"INSERT INTO nodes (osm_id, lat, lon, geom) VALUES ({osm_id}, {lat}, {lon}, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326));\n"
                output_file.write(sql)
        
        # If the geometry type is something else, print a message
        else:
            output_file.write(f"Skipping feature with unexpected geometry type: {geometry_type}\n")

print("SQL queries have been written to 'output_queries.txt'.")
