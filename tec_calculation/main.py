from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
from tec import *
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)