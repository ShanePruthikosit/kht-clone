import rasterio
import numpy as np
import os

# Reference: https://rasterio.readthedocs.io/en/latest/
# Path to the GeoTIFF file
script_dir = os.path.dirname(os.path.abspath(__file__))
geotiff_path = os.path.join(script_dir, "44 DEM30m - mitrearth (1).tif")

with rasterio.open(geotiff_path) as dataset:
    # Read the first band from the DEM
    # Reference: https://rasterio.readthedocs.io/en/latest/topics/reading.html
    elevation_data = dataset.read(1)
    
    # Get the spatial metadata
    # Reference: https://rasterio.readthedocs.io/en/latest/topics/georeferencing.html
    transform = dataset.transform
    crs = dataset.crs
    
    # Get the dimensions
    height, width = elevation_data.shape
    
    # Create an array of coordinates and heights
    # Reference: GIS Stack Exchange
    coordinates = []
    for row in range(height):
        for col in range(width):
            x, y = transform * (col, row)  # Convert pixel to geographic coordinates
            z = elevation_data[row, col]
            coordinates.append((x, y, z))

# Save the data to a CSV file
# Reference: https://docs.python.org/3/library/csv.html
import csv
output_csv = os.path.join(script_dir, "extracted_heights.csv")
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["X", "Y", "Z"])
    writer.writerows(coordinates)

print(f"Extracted height values saved to: {output_csv}")
