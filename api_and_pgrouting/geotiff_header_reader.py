import rasterio

# Reference: https://rasterio.readthedocs.io/en/latest/
# This script is adapted from the official Rasterio documentation.

def read_geotiff_header(file_path):
    """Reads and prints the header information of a GeoTIFF file."""
    with rasterio.open(file_path) as dataset:
        print("Driver:", dataset.driver)
        print("Width:", dataset.width)
        print("Height:", dataset.height)
        print("Number of Bands:", dataset.count)
        print("Coordinate Reference System (CRS):", dataset.crs)
        print("Transform (Affine Matrix):", dataset.transform)
        print("Bounding Box:", dataset.bounds)
        print("Scale:", dataset.scales)
        print("Offset:", dataset.offsets)
        
        for i in range(1, dataset.count + 1):
            print(f"Band {i} description:", dataset.descriptions[i-1])
            print(f"Band {i} data type:", dataset.dtypes[i-1])

if __name__ == "__main__":
    file_path = "44 DEM30m - mitrearth (1).tif"
    read_geotiff_header(file_path)
