from coordinates.sat import satellite_xyz 
import gzip
import shutil
import os
from datetime import datetime
import json
import requests

FILE_FOLDER = "./data"
DOWNLOAD_URL = [
    "https://simurg.space/files2/{}/{}/nav/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz",
    "https://simurg.space/files2/{}/{}/nav/cddis.gsfc.nasa.gov/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz",
    "https://simurg.space/files/{}/{}/nav/cddis.gsfc.nasa.gov/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz"
]

RE = 6378000.0  # in meters

def extract_gz(input_file: str, output_file:  str) -> None:
    with gzip.open(input_file, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    os.remove(input_file)

def get_sat_coords(
        input_file_gz: str, 
        satellite: str = 'C', 
        number: int = 40, 
        epoch: datetime = datetime(2024, 1, 1, 12, 0, 0)
    ) -> tuple[float]:
    input_file = f"{FILE_FOLDER}/{input_file_gz}"

    output_file_name = os.path.splitext(os.path.basename(input_file_gz))[0]
    output_file = f"{FILE_FOLDER}/{output_file_name}"

    if not os.path.exists(output_file):
        extract_gz(input_file, output_file)

    x, y, z = satellite_xyz(output_file, satellite, number, epoch)
    return x, y, z #m

def load_file(date: str) -> None:
    output_file = f"{FILE_FOLDER}/{date}.rnx.gz"
    datetime_date = datetime.strptime(date, '%Y-%m-%d')

    year = str(datetime_date.year)
    day_of_year = datetime_date.timetuple().tm_yday
    if day_of_year < 10:
        day_of_year = "00" + str(day_of_year)
    elif day_of_year < 100:
        day_of_year = "0" + str(day_of_year)
    else:
        day_of_year = str(day_of_year)

    urls = []
    for url in DOWNLOAD_URL:
        urls.append(url.format(year, day_of_year, year, day_of_year))
    print(urls)

    with open(output_file, "wb") as f:
        for url in urls:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                break
        if response.status_code != 200:
            response.raise_for_status()

        f.write(response.content)

    input_file = output_file
    output_file_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"{FILE_FOLDER}/{output_file_name}"
    extract_gz(input_file, output_file)
    


    




