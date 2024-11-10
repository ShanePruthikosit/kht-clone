import json

def is_valid_feature(feature):
    if 'type' not in feature or feature['type'] != 'Feature':
        return False
    if 'geometry' not in feature or 'properties' not in feature:
        return False
    geometry = feature['geometry']
    if 'type' not in geometry or 'coordinates' not in geometry:
        return False
    return True

def correct_geojson(input_file, output_file):
    def convert_to_feature(geometry):
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": {}
        }

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)

            if 'type' not in data:
                print("Invalid GeoJSON: Missing 'type' field")
                return

            if data['type'] == 'FeatureCollection':
                features = data.get('features', [])
                corrected_features = [f for f in features if is_valid_feature(f)]
            elif data['type'] == 'GeometryCollection':
                geometries = data.get('geometries', [])
                corrected_features = [convert_to_feature(g) for g in geometries]
            else:
                print("Unable to auto-correct: Input type is not supported.")
                return

            corrected_geojson = {
                "type": "FeatureCollection",
                "features": corrected_features
            }

            with open(output_file, 'w') as out_f:
                json.dump(corrected_geojson, out_f, indent=4)
                print(f"Corrected GeoJSON saved to {output_file}")

    except FileNotFoundError:
        print(f"File {input_file} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Usage
input_file = 'C:/Users/panuo/OneDrive/Documents/aaSchool_Work/KHT_Team_y2s2/KHT_Team/Src/KHT_Homepage/data/subdistrict_area_test.geojson'
output_file = 'C:/Users/panuo/OneDrive/Documents/aaSchool_Work/KHT_Team_y2s2/KHT_Team/Src/KHT_Homepage/data/subdistrict_area_test_corrected.geojson'
correct_geojson(input_file, output_file)
