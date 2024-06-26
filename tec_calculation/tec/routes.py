from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
from .data_preparation import load_file


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
