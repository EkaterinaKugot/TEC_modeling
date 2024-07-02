from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from pathlib import Path
from .data_preparation import *
from simurg_core.geometry.coord import cart_to_lle
from tec_calculation.ModelData import ModelData

router = APIRouter()


@router.get("/get_all_sites", response_model=list[list[str | float]] | None)
async def get_all_sites() -> list[list[str | float]] | None:
    save_all_sites()
    filename = "all_sites"
    result = read_from_json(filename)
    if result:
        return result
    else:
        return None


@router.get("/downloaded_files", response_model=list[str])
async def get_downloaded_files(
    dir: str = "data", extension: str = ".rnx"
) -> list[str]:
    directory = Path(dir)
    file_names = []

    if not directory.is_dir():
        raise HTTPException(
            status_code=404,
            detail=f"Directory '{directory}' does not exist or is not a directory",
        )
    for file in directory.iterdir():
        if file.is_file() and file.suffix == extension:
            file_names.append(file.stem)
    return file_names


@router.get("/upload_file", response_model=bool)
async def upload_file(background_tasks: BackgroundTasks, date: str) -> bool:
    background_tasks.add_task(load_file, date)
    return True


@router.get("/get_all_sats", response_model=list[tuple[str, int]] | None)
async def get_all_sats(date: str) -> list[tuple[str, int]] | None:
    filename = date + ".rnx"
    all_sats = extract_all_sats(filename)
    if all_sats is None:
        return None
    else:
        return all_sats


@router.get("/build_vertical_TEC", response_model=bool)
async def build_vertical_TEC(
    background_tasks: BackgroundTasks, date: datetime
) -> bool:
    json_path = RNX_FOLDER + JSON_FOLDER
    filename = (
        f"{json_path}/vertical_{date.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    )
    if os.path.exists(filename):
        return True
    background_tasks.add_task(calculate_vertical_tec, date)
    return True


@router.get(
    "/get_vertical_TEC", response_model=list[dict[str, float | int]] | None
)
async def get_vertical_TEC(
    date: datetime,
) -> list[dict[str, float | int]] | None:
    filename = f"vertical_{date.strftime('%Y-%m-%d_%H-%M-%S')}"
    result = read_from_json(filename)
    if result:
        return result
    else:
        return None

@router.get("/get_TEC", response_model= dict[str, list] | None)
async def get_TEC(
    date: str,
    seconds: int,
    lat: int,
    lon: int,
    z_step: int,
    start_h_from_ground: int, 
    end_h_from_ground: int,
    name_site: str,
    sat: str
) -> dict[str, list] | None:
    input_file = f"{RNX_FOLDER}/{date}.rnx"
    start_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = start_date.replace(hour=0, minute=0, second=0)

    site_info_response = requests.get( f"https://api.simurg.space/sites/{name_site}" )
    site_info = site_info_response.json()

    site_x, site_y, site_z = site_info["xyz"][0], site_info["xyz"][1], site_info["xyz"][2]
    site_xyz = [site_x, site_y, site_z]
    start_lat, start_lon, start_h = cart_to_lle(site_x, site_y, site_z)
    start_line = (start_lat, start_lon, start_h)

    part_x = ModelData.convert_degrees_to_kms(lat)
    part_y = ModelData.convert_degrees_to_kms(lon)
    part_size = (part_x, part_y, z_step)


    result = calculate_tec(
        part_size,
        start_h_from_ground,
        end_h_from_ground,
        start_date,
        seconds,
        start_line,
        sat,
        input_file,
        site_xyz
    )
    return result

@router.get("/get_tec_simurg_core", response_model= dict[str, list] | None)
async def get_TEC(
    date: str,
    seconds: int,
    z_step: int,
    start_h_from_ground: int, 
    end_h_from_ground: int,
    name_site: str,
    sat: str,
    hmax: int, 
    half_thickness: int,
) -> dict[str, list] | None:
    input_file = f"{RNX_FOLDER}/{date}.rnx"
    start_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = start_date.replace(hour=0, minute=0, second=0)

    site_info_response = requests.get( f"https://api.simurg.space/sites/{name_site}" )
    site_info = site_info_response.json()

    site_x, site_y, site_z = site_info["xyz"][0], site_info["xyz"][1], site_info["xyz"][2]
    site_xyz = [site_x, site_y, site_z]

    result = calculate_with_get_tec(
        start_h_from_ground,
        end_h_from_ground,
        z_step,
        hmax, 
        half_thickness,
        start_date,
        seconds,
        sat,
        input_file,
        site_xyz
    )
    return result
