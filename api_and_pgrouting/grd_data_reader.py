import rasterio

grd_path = "44 DEM30m - mitrearth.grd"

with rasterio.open(grd_path) as dataset:
    print("Metadata:", dataset.meta)
    print("Transform:", dataset.transform)
    print("CRS:", dataset.crs)
    print("NoData Value:", dataset.nodata)
    print("Scale Factor:", dataset.scales if dataset.scales else "None")
    print("Offset:", dataset.offsets if dataset.offsets else "None")

    elevation_data = dataset.read(1)
    print("Elevation Sample:", elevation_data[100:105, 100:105])
