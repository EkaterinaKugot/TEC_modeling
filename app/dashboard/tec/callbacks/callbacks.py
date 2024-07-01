from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from ..view import *
import dash
from numpy.typing import NDArray
import requests
import re
from datetime import datetime


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
    def download_file(n1: int, date: str) -> list[dict[str, str] | str]:
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
            Output("open-window", "is_open", allow_duplicate=True),
            Output("date-store", "data", allow_duplicate=True),
            Output("date", "value", allow_duplicate=True),
            Output("row_time_selection", "style", allow_duplicate=True),
            Output("row-graph-ver-tec", "style", allow_duplicate=True),
            Output("graph-ver-tec", "figure", allow_duplicate=True),
            Output("ver-tec-store", "data", allow_duplicate=True),
            Output("show-ver-tec", "disabled", allow_duplicate=True),
            Output("ver-date-store", "data", allow_duplicate=True),
            Output("all-sats-store", "data", allow_duplicate=True),
            Output(
                "div-selection-satellites", "children", allow_duplicate=True
            ),
            Output("graph-site-data", "figure", allow_duplicate=True),
            Output("site-data-store", "data", allow_duplicate=True),
        ],
        [Input("open-file", "n_clicks")],
        [
            State("select-file", "value"),
            State("open-window", "is_open"),
        ],
        prevent_initial_call=True,
    )
    def open_file(
        n: int, filename: str, is_open: bool
    ) -> list[str | bool | dict[str, str] | go.Figure | None]:
        style_ver_tec = {
            "display": "flex",
            "justify-content": "center",
        }
        vertical_tec_map = create_vertical_tec_map()
        all_sats = None
        params = {"date": filename}
        url = BASE_URL + "/get_all_sats"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            all_sats = response.json()
        else:
            all_sats = []
        selection_satellites = create_selection_satellites(all_sats)
        if not all_sats:
            all_sats = None

        site_data = create_site_data()
        return (
            not is_open,
            filename,
            filename,
            {"margin-top": "10px"},
            style_ver_tec,
            vertical_tec_map,
            None,
            True,
            None,
            all_sats,
            selection_satellites,
            site_data,
            None,
        )

    @app.callback(
        [
            Output("time", "invalid", allow_duplicate=True),
            Output("show-ver-tec", "disabled", allow_duplicate=True),
            Output("ver-date-store", "data", allow_duplicate=True),
        ],
        [Input("build-ver-tec", "n_clicks")],
        [State("date-store", "data"), State("time", "value")],
        prevent_initial_call=True,
    )
    def build_vertical_tec(
        n: int, date_store: str, time_str: str
    ) -> list[bool | datetime | None]:
        pattern = r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"
        match = re.match(pattern, time_str)
        if match is None:
            return True, True, None
        else:
            date_str = f"{date_store} {time_str}"
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            params = {"date": date}
            url = BASE_URL + "/build_vertical_TEC"
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    return False, False, date
            except:
                pass
        return False, True, None

    @app.callback(
        [
            Output("show-ver-tec", "disabled", allow_duplicate=True),
            Output("ver-date-store", "data", allow_duplicate=True),
            Output("ver-tec-store", "data", allow_duplicate=True),
            Output("graph-ver-tec", "figure", allow_duplicate=True),
            Output("row-graph-ver-tec", "style", allow_duplicate=True),
        ],
        [Input("show-ver-tec", "n_clicks")],
        [
            State("ver-date-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def show_vertical_tec(
        n: int,
        date: str,
    ) -> list[bool | str | None | go.Figure | dict[str, str]]:
        vertical_tec_map = create_vertical_tec_map()
        style_ver_tec = {
            "display": "flex",
            "justify-content": "center",
        }

        params = {"date": date}
        url = BASE_URL + "/get_vertical_TEC"

        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            if result is None:
                return False, date, None, vertical_tec_map, style_ver_tec
            else:
                vertical_tec_map = create_vertical_tec_map(result)
                return True, None, result, vertical_tec_map, style_ver_tec
        return False, date, None, vertical_tec_map, style_ver_tec

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
        all_sites_store: list[list[str | float]],
    ) -> list[go.Figure | bool | list[list[str | float]]]:
        site_map = create_site_map(all_sites_store)
        return_value_list = [
            site_map,
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
            site_map = create_site_map(all_sites_store)
            return_value_list[0] = site_map
        return return_value_list
    
    @app.callback(
        [
            Output("input-sites", "value", allow_duplicate=True),
            Output("graph-site-map", "figure", allow_duplicate=True),
            Output("site-idx-name-store", "data", allow_duplicate=True),
        ],
        Input("graph-site-map", "clickData"),
        State("all-sites-store", "data"),
        prevent_initial_call=True,
    )
    def select_site(
        clickData: dict[str, list[dict[str, float | str | dict]]],
        all_sites_store: list[list[str | float]],
    ) -> list[str, dict[str, float], dict[str, str | int]]:
        text = clickData["points"][0]["text"].split(" ")[0]
        idx = clickData["points"][0]["pointIndex"]
        site_map = create_site_map(all_sites_store, idx)
        return text, site_map, {"idx": idx, "name": text}
    
    @app.callback(
        [
            Output("input-sites", "invalid"),
            Output("selection-sats", "invalid"),
            Output("input-period-time", "invalid"),
            Output("input-lat", "invalid"),
            Output("input-lon", "invalid"),
            Output("input-z", "invalid"),
            Output("input-z-start", "invalid"),
            Output("input-z-end", "invalid"),
            Output("graph-site-data", "figure", allow_duplicate=True),
            Output("site-data-store", "data", allow_duplicate=True),
        ],
        [Input("calculate-tec", "n_clicks")],
        [
            State("input-sites", "value"),
            State("selection-sats", "value"),
            State("input-period-time", "value"),
            State("input-lat", "value"),
            State("input-lon", "value"),
            State("input-z", "value"),
            State("input-z-start", "value"),
            State("input-z-end", "value"),
            State("date-store", "data"),
            State("site-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def build_graph(
        n: int,
        input_sites: str,
        selection_sats: str,
        input_period_time: int,
        input_lat: int,
        input_lon: int,
        input_z: int,
        input_z_start: int,
        input_z_end: int,
        date: str,
        site_data_store: dict[str, list],
    ):
        values = [
            input_sites,
            selection_sats,
            input_period_time,
            input_lat,
            input_lon,
            input_z,
            input_z_start,
            input_z_end,
        ]
        return_values = check_values(values)
        if not return_values[-2] and not return_values[-1] and values[-2] >= values[-1]:
            return_values[-2] = True
            return_values[-1] = True

        if True not in return_values:
            params = {
                "date": date, 
                "seconds": input_period_time,
                "lat": input_lat,
                "lon": input_lon,
                "z_step": input_z,
                "start_h_from_ground": input_z_start,
                "end_h_from_ground": input_z_end,
                "name_site": input_sites,
                "sat": selection_sats
            }
            url = BASE_URL + "/get_TEC"
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return return_values
            else:
                res = response.json()
                tecs = res["tecs"]
                times = res["times"]
                el = res["el"]
                if site_data_store is None:
                    site_data_store = dict()
                    site_data_store["tecs"] = []
                    site_data_store["times"] = []
                    site_data_store["el"] = []
                    site_data_store["names"] = []
                site_data_store["tecs"].append(tecs)
                site_data_store["times"].append(times)
                site_data_store["el"].append(el)
                site_data_store["names"].append(input_sites)

        site_data = create_site_data()
        add_traces_in_graph(site_data, site_data_store)
        return_values.append(site_data)
        return_values.append(site_data_store)
        return return_values
    
    def check_values(
            values: list[str | int | None]
    ) -> list[go.Figure | bool]:
        return_values = []
        for value in values:
            if value is None:
                return_values.append(True)
            else:
                return_values.append(False)
        return return_values
    
    def add_traces_in_graph(
            site_data: go.Figure, 
            site_data_store: dict[str, list],
    ) -> None:
        shift = -10
        traces = []
        tickvals = []
        if site_data_store is not None:
            for i, (x, y, name) in enumerate(zip(
                site_data_store["times"], 
                site_data_store["tecs"], 
                site_data_store["names"]
            )):
                y = list(map(lambda v: v + shift * (i + 1), y))
                tickvals.append(y[0])
                trace = go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    marker=dict(
                        size=5
                    ),
                    name=name,
                )
                traces.append(trace)
            site_data.add_traces(
                traces
            )
            site_data.layout.yaxis.tickmode = "array"
            site_data.layout.yaxis.tickvals = tickvals
            site_data.layout.yaxis.ticktext = site_data_store["names"]
            print(site_data.layout.yaxis.ticktext)
    
    @app.callback(
        [
            Output("graph-site-data", "figure", allow_duplicate=True),
            Output("site-data-store", "data", allow_duplicate=True),
        ],
        [Input("clear-graph", "n_clicks")],
        prevent_initial_call=True,
    )
    def clear_graph(
        n: int,
    ) -> list[go.Figure]:
        site_data = create_site_data()
        return site_data, None


    @app.callback(
        [
            Output("all-sites-store", "data"),
            Output("graph-site-map", "figure"),
            Output("graph-site-data", "figure"),
            Output("date", "value"),
            Output("row_time_selection", "style"),
            Output("show-ver-tec", "disabled"),
            Output("graph-ver-tec", "figure"),
            Output("row-graph-ver-tec", "style"),
            Output("div-selection-satellites", "children"),
            Output("input-sites", "value"),
        ],
        [Input("url", "pathname")],
        [
            State("all-sites-store", "data"),
            State("date-store", "data"),
            State("ver-date-store", "data"),
            State("ver-tec-store", "data"),
            State("all-sats-store", "data"),
            State("site-data-store", "data"),
            State("site-idx-name-store", "data")
        ],
    )
    def update_all(
        pathname: str,
        all_sites_store: list[list[str | float]],
        date_store: str,
        date: str,
        ver_tec: str,
        all_sats: list[tuple[str | int]],
        site_data_store: dict[str, list],
        site_idx_name: dict[str, str | int]
    ) -> list[go.Figure | str | dict[str, str] | bool | list[list[str | float]]]:
        if date_store is not None:
            filename = date_store
            style_form = {"margin-top": "10px"}
            style_ver_tec = {
                "display": "flex",
                "justify-content": "center",
            }
        else:
            filename = "none"
            style_form = {"visibility": "hidden"}
            style_ver_tec = {"visibility": "hidden"}

        all_sites = []
        if all_sites_store is None:
            url = BASE_URL + "/get_all_sites"
            response = requests.get(url)
            if response.status_code == 200:
                all_sites = response.json()
        else:
            all_sites = all_sites_store

        if site_idx_name is None:
            name_site = ""
            idx_site = None
        else:
            name_site = site_idx_name["name"]
            idx_site = site_idx_name["idx"]
        site_map = create_site_map(all_sites, idx_site)

        disabled = True
        if date is not None:
            disabled = False
        vertical_tec_map = create_vertical_tec_map()
        if ver_tec is not None:
            vertical_tec_map = create_vertical_tec_map(ver_tec)
        if all_sats is None:
            all_sats = []
        selection_satellites = create_selection_satellites(all_sats)

        site_data = create_site_data()
        add_traces_in_graph(site_data, site_data_store)

        if not all_sites:
            all_sites = None

       
        return (
            all_sites,
            site_map,
            site_data,
            filename,
            style_form,
            disabled,
            vertical_tec_map,
            style_ver_tec,
            selection_satellites,
            name_site 
        )
