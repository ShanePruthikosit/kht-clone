import json

# Open GeoJSON file with UTF-8 encoding
with open('graph.json', encoding='utf-8') as f:
    data = json.load(f)

# Create SQL output file
with open('insert_statements.sql', 'w') as sql_file:
    for feature in data['features']:
        geometry = feature['geometry']
        properties = feature['properties']
        
        # Handling Point geometry for nodes
        if geometry['type'] == 'Point':
            osm_id = properties['osmId']
            node_id = feature['id']  # Read the id from the feature
            lon, lat = geometry['coordinates']  # Correct order for GeoJSON [lon, lat]
            
            # Write the Point insert SQL statement to file
            sql_file.write(f"""
            INSERT INTO new_nodes (osm_id, id, lat, lon, geom)
            VALUES ({osm_id}, {node_id}, {lat}, {lon}, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326));
            \n
            """)
        
        # Handling LineString geometry for edges
        elif geometry['type'] == 'LineString':
            osm_id = properties.get('osmId')
            src = feature.get('src')  # Access src directly from feature
            tgt = feature.get('tgt')  # Access tgt directly from feature
            
            # Log missing src or tgt and continue
            if src is None or tgt is None:
                print(f"Warning: Missing src ({src}) or tgt ({tgt}) for LineString with osm_id {osm_id}.")
                continue
            
            coordinates = geometry['coordinates']
            
            # Create ST_MakeLine with all coordinates using an array, ensuring [lon, lat] order
            coord_string = ', '.join([f"ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)" for lon, lat in coordinates])
            coord_array = f"ARRAY[{coord_string}]"
            
            # Calculate cost using the distance between the first and last point (lat, lon order)
            start_lon, start_lat = coordinates[0]
            end_lon, end_lat = coordinates[-1]
            cost = f"ST_Distance(ST_SetSRID(ST_MakePoint({start_lon}, {start_lat}), 4326), ST_SetSRID(ST_MakePoint({end_lon}, {end_lat}), 4326))"
            
            # Write the LineString insert SQL statement to file with all points included in the line
            sql_file.write(f"""
            INSERT INTO new_edges (osm_id, source, target, cost, geom)
            VALUES ({osm_id}, {src}, {tgt}, {cost}, ST_MakeLine({coord_array}));
            \n
            """)

print("SQL insert statements written to 'insert_statements.sql'")
