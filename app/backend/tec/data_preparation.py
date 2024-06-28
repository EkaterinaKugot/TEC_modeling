from coordinates.sat import satellite_xyz 
import gzip
import shutil
import os
from datetime import datetime
import numpy as np
import requests
from tec_calculation.ModelData import ModelData
import json
from numpy.typing import NDArray

FILE_FOLDER = "./data"
DOWNLOAD_URL = [
    "https://simurg.space/files2/{}/{}/nav/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz",
    "https://simurg.space/files2/{}/{}/nav/cddis.gsfc.nasa.gov/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz",
    "https://simurg.space/files/{}/{}/nav/cddis.gsfc.nasa.gov/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz"
]


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

def save_to_json(date: datetime, result: NDArray):
    filename = f"{FILE_FOLDER}/vertical_{date.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    data = {"result": result}
    if result is not None:
        with open(filename, "w") as f:
            json.dump(data, f)

def read_from_json(date: datetime) -> dict[str, bool]:
    filename = f"{FILE_FOLDER}/vertical_{date.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
        # os.remove(filename)
        return data["result"]
    else:
        return None

def calculate_vertical_tec(
        date: datetime,
        lat_step: int = 5,
        lon_step: int = 5
    ) -> list[list[float]]:
    z_step = 10
    part_size = (lat_step*110, lon_step*110, z_step)
    start_h_from_ground = 100
    end_h_from_ground = 1000

    lat_range = list(range(-90, 90, lat_step))
    lon_range = list(range(-180, 180, lon_step))

    h_site = 0
    h_sat = 20015780.84050447
    
    my_tecs = []
    
    for lat in lat_range:    
        m = ModelData(part_size, start_h_from_ground, end_h_from_ground)
        for lon in lon_range:
            tmp_my_tecs = dict()
            lat_rad = np.radians(lat)
            lon_rad = np.radians(lon)
            tec = m.calculate_TEC([lat_rad, lon_rad, h_site], [lat_rad, lon_rad, h_sat], date)
            tmp_my_tecs["lat"] = lat
            tmp_my_tecs["lon"] = lon
            tmp_my_tecs["tec"] = tec

            my_tecs.append(tmp_my_tecs)

    save_to_json(date, my_tecs)
    

    


    




