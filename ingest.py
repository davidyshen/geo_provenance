from geoprovenance.download import ingest_zip_single
import requests
import os

source_url = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_30s_elev.zip"

ingest_zip_single(
    url=source_url,
    file="wc2.1_30s_elev.tif",
    name="srtm_elevation",
    tags=["climate", "elevation", "tif"],
)

