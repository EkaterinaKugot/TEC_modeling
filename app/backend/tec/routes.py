from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from pathlib import Path
from .data_preparation import *


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
async def get_downloaded_files(dir: str = "data", extension: str = ".rnx") -> list[str]:
    directory = Path(dir)
    file_names = []

    if not directory.is_dir():
        raise HTTPException(status_code=404, detail=f"Directory '{directory}' does not exist or is not a directory")

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
async def build_vertical_TEC(background_tasks: BackgroundTasks, date: datetime) -> bool:
    json_path = RNX_FOLDER + JSON_FOLDER
    filename = f"{json_path}/vertical_{date.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    if os.path.exists(filename):
        return True
    background_tasks.add_task(calculate_vertical_tec, date)
    return True

@router.get("/get_vertical_TEC", response_model=list[dict[str, float | int]] | None)
async def get_vertical_TEC(date: datetime) -> list[dict[str, float | int]] | None:
    filename = f"vertical_{date.strftime('%Y-%m-%d_%H-%M-%S')}"
    result = read_from_json(filename)
    if result:
        return result
    else:
        return None
