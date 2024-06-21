from coordinates.sat import satellite_xyz 
import gzip
import shutil
import os
from datetime import datetime

FILE_FOLDER = "./data"

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


    




