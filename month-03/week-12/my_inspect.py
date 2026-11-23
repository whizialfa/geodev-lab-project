"""Challenge: inspect my AMAC Landsat red band and Copernicus DEM."""
from pathlib import Path

import rasterio

RED = Path("data/raw/week12_amac/B4_red.tif")
DEM = Path("data/raw/week12_amac/dem_amac.tif")


def inspect(path: Path, label: str) -> None:
    with rasterio.open(path) as src:
        masked = src.read(1, masked=True)
        print(f"--- {label}: {path.name} ---")
        print("size:", src.width, "x", src.height, "bands:", src.count)
        print("dtype:", src.dtypes[0])
        print("crs:", src.crs)
        print("nodata:", src.nodata)
        print("cell size:", src.res)
        print("bounds:", src.bounds)
        print("transform:", src.transform)
        print(
            "masked min/max/mean:",
            round(float(masked.min()), 2),
            round(float(masked.max()), 2),
            round(float(masked.mean()), 2),
        )


inspect(RED, "Landsat-9 red (B4)")
inspect(DEM, "Copernicus GLO-30 DEM")
