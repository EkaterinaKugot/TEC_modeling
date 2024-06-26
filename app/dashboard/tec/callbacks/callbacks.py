from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from ..view import *
import dash
from numpy.typing import NDArray
import time
import requests
from requests.exceptions import HTTPError

BASE_URL = "http://127.0.0.1:8000"

language = languages["en"]

def register_callbacks(app: dash.Dash) -> None:
    @app.callback(
        [
            Output("download-window", "is_open"),
            Output("downloaded", "style", allow_duplicate=True),
            Output("downloaded", "children", allow_duplicate=True),
        ],
        [Input("download", "n_clicks")],
        [State("download-window", "is_open")],
        prevent_initial_call=True,
    )
    def open_close_download_window(
        n1: int, is_open: bool
    ) -> list[bool | dict[str, str] | str]:
        style = {"visibility": "hidden"}
        return not is_open, style, ""
    
    @app.callback(
        [
            Output("downloaded", "style", allow_duplicate=True),
            Output("downloaded", "children", allow_duplicate=True),
        ],
        [Input("download-file", "n_clicks")],
        [State("date-selection", "date")],
        prevent_initial_call=True,
    )
    def download_file( 
        n1: int, 
        date: str
    ) -> list[dict[str, str] | str]:
        text = language["download_window"]["successаfuly"]
        color = "green"
        if date is None:
            text = language["download_window"]["unsuccessаfuly"]
        else:
            file_names = []
            try:
                url = BASE_URL + "/downloaded_files"
                response = requests.get(url)
                if response.status_code == 200:
                    file_names = response.json()
            except:
                pass
            if date in file_names:
                text = language["download_window"]["repeat-action"]
            else:
                url = BASE_URL + "/upload_file"
                params = {"date": date}
                try:
                    response = requests.get(url, params=params)
                    if response.status_code != 200:
                        text != language["download_window"]["error"]
                except:
                    pass

        if text != language["download_window"]["successаfuly"]:
            color = "red"
        style = {
            "text-align": "center",
            "margin-top": "10px",
            "color": color,
        }
        return style, text
    

    @app.callback(
        [
            Output("open-window", "is_open", allow_duplicate=True),
            Output("select-file", "options"),
        ],
        [Input("open", "n_clicks")],
        [State("open-window", "is_open")],
        prevent_initial_call=True,
    )
    def open_close_open_window(
        n1: int, is_open: bool
    ) -> list[bool | list[dict[str, str]]]:
        options = []
        try:
            url = BASE_URL + "/downloaded_files"
            response = requests.get(url)
            if response.status_code == 200:
                options = response.json()
        except:
            pass
        return not is_open, options
    

    @app.callback(
        [
            Output("graph-site-map", "figure", allow_duplicate=True),
            Output("site-lat", "invalid"),
            Output("site-lon", "invalid"),
            Output("site-name", "invalid"),
            Output("all-sites-store", "data", allow_duplicate=True),
        ],
        [Input("add-site", "n_clicks")],
        [
            State("site-lat", "value"),
            State("site-lon", "value"),
            State("site-name", "value"),
            State("all-sites-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def add_new_site(
        n: int,
        site_lat: float,
        site_lon: float,
        site_name: str,
        all_sites_store: list[list[str | float]]
    ) -> list[go.Figure | bool | list[list[str | float]]]:
        figure = create_site_map(all_sites_store)
        return_value_list = [
            figure,
            False,
            False,
            False,
            all_sites_store,
        ]
        if site_lat is None:
            return_value_list[1] = True
        if site_lon is None:
            return_value_list[2] = True
        if site_name is None:
            return_value_list[3] = True

        if True in return_value_list:
            return return_value_list
        else:
            all_sites_store.append([site_name, "", site_lat, site_lon])
            return_value_list[4] = all_sites_store
            figure = create_site_map(all_sites_store)
            return_value_list[0] = figure
        return return_value_list


        