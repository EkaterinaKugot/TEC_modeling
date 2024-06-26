from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from ..view import *
import dash
from pathlib import Path
from numpy.typing import NDArray
import time


language = languages["en"]

def register_callbacks(app: dash.Dash) -> None:
    pass