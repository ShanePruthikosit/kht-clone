import rasterio
import numpy as np

# Step 1: Open the GeoTIFF file
file_path = '44 DEM30m - mitrearth (1).tif'  # Replace with your GeoTIFF file path

with rasterio.open(file_path) as src:
    # Step 2: Read the raster data from the first band (Z values)
    band_data = src.read(1)  # Read the first band

# Step 3: Convert the data to raw binary format
# Make sure the data type is compatible with binary format (e.g., float32, int16)
# For example, using int16 for 16-bit data:
raw_binary_data = band_data.astype(np.int16).tobytes()

# Optional: Save the raw binary data to a file
with open('output.raw', 'wb') as f:
    f.write(raw_binary_data)

print("Raw binary data saved to 'output.raw'")
