from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from ..view import *
import dash
from numpy.typing import NDArray
import requests
import re
from datetime import datetime, timedelta, timezone


BASE_URL = "http://127.0.0.1:8000"
FOLDER_PNG = "./assets"

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
            Output("input-sites", "invalid"),
            Output("selection-network", "invalid"),
            Output("selection-sats", "invalid"),
            Output("input-period-time", "invalid"),
            Output("input-lat", "invalid"),
            Output("input-lon", "invalid"),
            Output("input-z", "invalid"),
            Output("input-z-start", "invalid"),
            Output("input-z-end", "invalid"),
            Output("graph-site-data", "figure", allow_duplicate=True),
        ],
        [Input("calculate-tec", "n_clicks")],
        [
            State("input-sites", "value"),
            State("selection-network", "value"),
            State("selection-sats", "value"),
            State("input-period-time", "value"),
            State("input-lat", "value"),
            State("input-lon", "value"),
            State("input-z", "value"),
            State("input-z-start", "value"),
            State("input-z-end", "value"),
            State("all-sites-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def build_graph(
        n: int,
        input_sites: str,
        selection_network: str,
        selection_sats: str,
        input_period_time: int,
        input_lat: int,
        input_lon: int,
        input_z: int,
        input_z_start: int,
        input_z_end: int,
        all_sites_store: list[list[str | float]]
    ):
        
        site_data = create_site_data()
        values = [
            input_sites,
            selection_network,
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

        name_sites = np.array([site[0] for site in all_sites_store])
        network_site = np.array([site[1] for site in all_sites_store])
        if not return_values[0] and input_sites not in name_sites:
            return_values[0] = True
        elif not return_values[0] and input_sites in name_sites:
            index_site = np.where(name_sites == input_sites)[0]
            index_site = index_site.tolist()
            selection_network = selection_network if selection_network != "-" else ""
            if not return_values[1]:
                flag = False
                for i in index_site:
                    if selection_network == network_site[i]:
                        flag = True
                        break
                if not flag:
                    return_values[1] = True
        if True in return_values:
            return_values.append(site_data)
            return return_values
        
        # Отправка данных
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


    @app.callback(
        [
            Output("all-sites-store", "data"),
            Output("graph-site-map", "figure"),
            Output("date", "value"),
            Output("row_time_selection", "style"),
            Output("show-ver-tec", "disabled"),
            Output("graph-ver-tec", "figure"),
            Output("row-graph-ver-tec", "style"),
            Output("div-selection-satellites", "children"),
            Output("div-selection-network", "children"),
        ],
        [Input("url", "pathname")],
        [
            State("all-sites-store", "data"),
            State("date-store", "data"),
            State("ver-date-store", "data"),
            State("ver-tec-store", "data"),
            State("all-sats-store", "data"),
        ],
    )
    def update_all(
        pathname: str,
        all_sites_store: list[list[str | float]],
        date_store: str,
        date: str,
        ver_tec: str,
        all_sats: list[tuple[str | int]],
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
        site_map = create_site_map(all_sites)
        disabled = True
        if date is not None:
            disabled = False
        vertical_tec_map = create_vertical_tec_map()
        if ver_tec is not None:
            vertical_tec_map = create_vertical_tec_map(ver_tec)
        if all_sats is None:
            all_sats = []
        selection_satellites = create_selection_satellites(all_sats)

        all_network = [site[1] for site in all_sites]
        if all_network:
            all_network = list(set(all_network))
            all_network[0] = "-"
        selection_network = create_selection_network(all_network)

        if not all_sites:
            all_sites = None
        return (
            all_sites,
            site_map,
            filename,
            style_form,
            disabled,
            vertical_tec_map,
            style_ver_tec,
            selection_satellites,
            selection_network,
        )
