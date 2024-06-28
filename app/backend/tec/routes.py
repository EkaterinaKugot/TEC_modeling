from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
from .data_preparation import *


router = APIRouter()


@router.get("/downloaded_files", response_model=List[str])
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

@router.get("/build_vertical_TEC", response_model=bool)
async def build_vertical_TEC(background_tasks: BackgroundTasks, date: datetime) -> bool:
    filename = f"{FILE_FOLDER}/vertical_{date.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    if os.path.exists(filename):
        return True
    background_tasks.add_task(calculate_vertical_tec, date)
    return True

@router.get("/get_vertical_TEC", response_model=List[Dict[str, float | int]] | None)
async def get_vertical_TEC(date: datetime) -> list[dict[str, float | int]] | None:
    result = read_from_json(date)
    if result:
        return result
    else:
        return None
