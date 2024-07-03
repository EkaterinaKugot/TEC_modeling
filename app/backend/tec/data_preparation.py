from coordinates.sat import satellite_xyz, read_nav_data
from simurg_core.geometry.coord import cart_to_lle, xyz_to_el_az
from simurg_core.models.simple_tec import get_tec
import gzip
import shutil
import os
from datetime import datetime, timedelta
import numpy as np
import requests
from tec_calculation.ModelData import ModelData
import json
from numpy.typing import NDArray

RNX_FOLDER = "./data"
JSON_FOLDER = "/json"
DOWNLOAD_URL = [
    "https://simurg.space/files2/{}/{}/nav/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz",
    "https://simurg.space/files2/{}/{}/nav/cddis.gsfc.nasa.gov/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz",
    "https://simurg.space/files/{}/{}/nav/cddis.gsfc.nasa.gov/BRDC00IGS_R_{}{}0000_01D_MN.rnx.gz",
]


def extract_gz(input_file: str, output_file: str) -> None:
    with gzip.open(input_file, "rb") as f_in:
        with open(output_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(input_file)


def load_file(date: str) -> None:
    if not os.path.exists(RNX_FOLDER):
        os.makedirs(RNX_FOLDER)
    output_file = f"{RNX_FOLDER}/{date}.rnx.gz"
    datetime_date = datetime.strptime(date, "%Y-%m-%d")

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
    output_file = f"{RNX_FOLDER}/{output_file_name}"
    extract_gz(input_file, output_file)


def save_to_json(name: str, result: list) -> None:
    json_path = RNX_FOLDER + JSON_FOLDER
    if not os.path.exists(json_path):
        os.makedirs(json_path)
    filename = f"{json_path}/{name}.json"
    data = {"result": result}
    if result is not None:
        with open(filename, "w") as f:
            json.dump(data, f)


def read_from_json(name: str) -> list:
    json_path = RNX_FOLDER + JSON_FOLDER
    filename = f"{json_path}/{name}.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
        return data["result"]
    else:
        return None


def calculate_vertical_tec(
    date: datetime, lat_step: int = 5, lon_step: int = 5
) -> list[list[float]]:
    z_step = 10
    part_size = (lat_step * 110, lon_step * 110, z_step)
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
            tec = m.calculate_TEC(
                [lat_rad, lon_rad, h_site], [lat_rad, lon_rad, h_sat], date
            )
            tmp_my_tecs["lat"] = lat
            tmp_my_tecs["lon"] = lon
            tmp_my_tecs["tec"] = tec

            my_tecs.append(tmp_my_tecs)
    filename = f"vertical_{date.strftime('%Y-%m-%d_%H-%M-%S')}"
    save_to_json(filename, my_tecs)


def save_all_sites() -> None:
    json_path = RNX_FOLDER + JSON_FOLDER
    filename = f"{json_path}/all_sites.json"
    if not os.path.exists(filename):
        rq = requests.post(
            "https://simurg.iszf.irk.ru/api",
            json={"method": "get_site", "args": {}},
        )
        all_sites_tmp = rq.json()
        all_sites = []
        for site in all_sites_tmp:
            if site[1] == "base":
                all_sites.append(site)
        save_to_json("all_sites", all_sites)


def extract_all_sats(filename: str) -> list[str] | None:
    path_file = f"{RNX_FOLDER}/{filename}"
    if not os.path.exists(path_file):
        return None
    else:
        data = read_nav_data(path_file)
        all_sats = []
        for sat in data:
            all_sats.append(sat)
        return all_sats
    

def calculate_tec(
        part_size: tuple[float, float, float],
        start_h_from_ground: int,
        end_h_from_ground: int,
        start_date: datetime,
        seconds: int,
        start_line: tuple[float, float, float],
        sat: str,
        input_file: str,
        site_xyz: list[float]
) -> dict[str, list]:
    end_date = start_date + timedelta(days=1)
    satellite = sat[0]
    number = int(sat[1:])

    my_tecs = []
    times = []
    el_sat = []

    m = ModelData(part_size, start_h_from_ground, end_h_from_ground)
    while start_date < end_date:
        sat_x, sat_y, sat_z  = satellite_xyz(input_file, satellite, number, start_date) #sat_z - m
        el, az = xyz_to_el_az(site_xyz, [sat_x, sat_y, sat_z])

        if np.radians(el) < 0:
            start_date += timedelta(seconds=seconds)
            continue

        el_sat.append(el)

        end_lat, end_lon, end_h = cart_to_lle(sat_x, sat_y, sat_z)
        end_line = [end_lat, end_lon, end_h]

        tec = m.calculate_TEC(start_line, end_line, start_date)
        times.append(start_date)
        my_tecs.append(tec)
        start_date += timedelta(seconds=seconds)
    result = {"tecs": my_tecs, "times": times, "el": el_sat}
    return result

def calculate_with_get_tec(
        start_h_from_ground: int,
        end_h_from_ground: int,
        z_step: int,
        hmax: int,
        half_thickness: int,
        start_date: datetime,
        seconds: int,
        sat: str,
        input_file: str,
        site_xyz: list[float]
) -> dict[str, list] | None:
    end_date = start_date + timedelta(days=1)
    satellite = sat[0]
    number = int(sat[1:])

    tecs = []
    times = []
    el_sat = []

    kargs = {"z_start": start_h_from_ground, "z_end": end_h_from_ground, "l_step": z_step,
        "ne_0": 2e12, "hmax": hmax, "half_thickness": half_thickness}

    while start_date < end_date:
        yday = start_date.timetuple().tm_yday       
        UT = start_date.hour + start_date.minute / 60. + start_date.second / 3600.

        try:
            sat_x, sat_y, sat_z  = satellite_xyz(input_file, satellite, number, start_date) 
        except:
            return None
        el, az = xyz_to_el_az(site_xyz, [sat_x, sat_y, sat_z])

        if np.radians(el) < 0:
            start_date += timedelta(seconds=seconds)
            continue

        start_lat, start_lon, _ = cart_to_lle(site_xyz[0], site_xyz[1], site_xyz[2])

        tec = get_tec(yday=yday, UT=UT, az=np.radians(az), el=np.radians(el),
                        lat_0=start_lat, lon_0=start_lon,
                        **kargs)
        tecs.append(tec)
        times.append(start_date)
        el_sat.append(el)
        start_date += timedelta(seconds=seconds)
    result = {"tecs": tecs, "times": times, "el": el_sat}
    return result
