from dash import html, dcc
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from enum import Enum
from .languages import languages
from datetime import datetime, date, timedelta
import numpy as np


language = languages["en"]


def create_layout() -> html.Div:
    left_side = _create_left_side()
    data_tab = _create_data_tab()
    site_addition = _create_site_addition()

    size_map = 5
    size_data = 7
    layout = html.Div(
        [
            dcc.Store(id="all-sites-store", storage_type="session"),
            dcc.Store(id="date-store", storage_type="session"),
            dcc.Store(id="ver-date-store", storage_type="session"),
            dcc.Store(id="ver-tec-store", storage_type="session"),
            dcc.Store(id="all-sats-store", storage_type="session"),
            dcc.Store(id="site-data-store", storage_type="session"),
            dcc.Store(id="site-idx-name-store", storage_type="session"),
            dcc.Location(id="url", refresh=False),
            dbc.Row(
                [
                    dbc.Col(
                        left_side,
                        width={"size": size_map},
                        style={"padding-left": "0px"},
                    ),
                    dbc.Col(
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    data_tab,
                                    label=language["data-tab"]["label"],
                                    tab_style={"marginLeft": "auto"},
                                    label_style={"color": "gray"},
                                    active_label_style={
                                        "font-weight": "bold",
                                        "color": "#2C3E50",
                                    },
                                ),
                                dbc.Tab(
                                    site_addition,
                                    label=language["tab-adding-site"]["label"],
                                    label_style={"color": "gray"},
                                    active_label_style={
                                        "font-weight": "bold",
                                        "color": "#2C3E50",
                                    },
                                    style={"text-align": "center"},
                                ),
                            ],
                        ),
                        width={"size": size_data},
                        style={"padding-right": "0px"},
                    ),
                ]
            ),
        ],
        style={
            "margin-top": "30px",
            "margin-left": "50px",
            "margin-right": "50px",
        },
    )
    return layout


def _create_left_side() -> list[dbc.Row]:
    site_map = create_site_map()
    download_window = _create_download_window()
    open_window = _create_open_window()
    time_selection = _create_time_selection()
    vertical_tec_map = create_vertical_tec_map()
    left_side = [
        dbc.Row(
            dbc.Col(
                [
                    download_window,
                    html.Div(
                        open_window,
                        style={"margin-left": "15px"},
                    ),
                ],
                style={"display": "flex", "justify-content": "flex-start"},
            )
        ),
        dbc.Row(
            dcc.Graph(
                id="graph-site-map", figure=site_map, style={"height": "300px"}
            ),
            style={"margin-top": "20px"},
        ),
        dbc.Row(
            time_selection,
            id="row_time_selection",
            style={"visibility": "hidden"},
        ),
        dbc.Row(
            dbc.Col(
                html.Div("", id="status-ver-tec"),
                style={"display": "flex", "justify-content": "center", "color": "red", "mergin-top": "10px"},
            ),
            id="div-status-ver-tec",
            style={"visibility": "hidden"},
        ),
        dbc.Row(
            dcc.Graph(
                id="graph-ver-tec",
                figure=vertical_tec_map,
                style={
                    "width": "85%",
                    "height": "270px",
                    "margin-top": "10px",
                },
            ),
            id="row-graph-ver-tec",
            style={"visibility": "hidden"},
        ),
    ]
    return left_side


def _create_time_selection() -> list[html.Div]:
    time_selection = [
        dbc.Label(language["time_selection"]["date"], width=1),
        dbc.Col(
            dbc.Input(
                type="text",
                id="date",
                readonly=True,
            ),
            width=3,
        ),
        dbc.Label(language["time_selection"]["time"], width=1),
        dbc.Col(
            dbc.Input(
                type="text",
                id="time",
                value="00:00:00",
                pattern="^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$",
                invalid=False,
                persistence="00:00:00",
                persistence_type="session",
            ),
            width=3,
        ),
        dbc.Col(
            dbc.Button(language["buttons"]["build"], id="build-ver-tec"),
            width=2,
        ),
        dbc.Col(
            dbc.Button(
                language["buttons"]["show"], id="show-ver-tec", disabled=True
            ),
            style={"margin-left": "-20px"},
        ),
    ]
    return time_selection


def create_vertical_tec_map(
    ver_tec: list[dict[str, float | int]] = list()
) -> go.Figure:
    values = [entry["tec"] for entry in ver_tec]
    if len(values) == 0:
        cmin = 0
        cmax = 0
    else:
        cmin = np.min(values)
        cmax = np.max(values)
    scattermapbox = go.Scattermapbox(
        lat=[entry["lat"] for entry in ver_tec],
        lon=[entry["lon"] for entry in ver_tec],
        mode="markers",
        marker=go.scattermapbox.Marker(
            size=30,
            color=values,
            colorscale="Viridis",
            cmin=cmin,
            cmax=cmax,
            opacity=0.07,
            colorbar=dict(
                thickness=15,
                x=0.99,
            ),
        ),
        hoverinfo="none",
    )
    layout = go.Layout(
        hovermode="closest",
        mapbox=dict(
            style="open-street-map",
            center=dict(
                lat=25,
                lon=0,
            ),
            zoom=-0.5,
        ),
        dragmode=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig = go.Figure(data=[scattermapbox], layout=layout)
    return fig


def create_site_map(all_sites: list[list[str | float]] = [], idx: int = None) -> go.Figure:
    text = [f"{point[0]} ({point[1]})" for point in all_sites]
    colors = ["Silver"] * len(all_sites)
    if idx is not None:
        colors[idx] = "red"
    if len(colors) == 0:
        colors = "Silver"
    outline_scattermapbox = go.Scattermapbox(
        lat=[point[2] for point in all_sites],
        lon=[point[3] for point in all_sites],
        mode="markers",
        marker=go.scattermapbox.Marker(
            size=7,  
            color="gray",
        ),
        showlegend=False,
        hoverinfo='skip'  
    )
    
    scattermapbox = go.Scattermapbox(
        lat=[point[2] for point in all_sites],
        lon=[point[3] for point in all_sites],
        mode="markers",
        marker=go.scattermapbox.Marker(
            size=5,
            color=colors
        ),
        showlegend=False,
        text=text,
        hovertemplate="%{lat} %{lon}<br>%{text}</b><extra></extra>",
    )
    layout = go.Layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(
                lat=0,
                lon=0,
            ),
            zoom=-0.2,
        ),
        dragmode=False,
        margin=dict(l=0, r=0, t=0, b=0),
        hoverlabel=dict(
            bgcolor="white", 
            font_color="black"  
        )
    )
    figure = go.Figure(data=[outline_scattermapbox, scattermapbox], layout=layout)

    return figure


def _create_download_window() -> html.Div:
    download_window = html.Div(
        [
            dbc.Button(language["buttons"]["download"], id="download"),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(language["download_window"]["title"])
                    ),
                    dbc.ModalBody(
                        [
                            dbc.Label(
                                language["download_window"]["label"],
                                style={"font-size": "18px"},
                            ),
                            dcc.DatePickerSingle(
                                id="date-selection",
                                min_date_allowed=date(1998, 1, 1),
                                max_date_allowed=datetime.now()
                                - timedelta(days=1),
                                display_format="YYYY-MM-DD",
                                placeholder="YYYY-MM-DD",
                                date=datetime.now().strftime("%Y-%m-%d"),
                                style={"margin-left": "15px"},
                            ),
                            html.Div(
                                dbc.Button(
                                    language["buttons"]["download"],
                                    id="download-file",
                                    style={"margin-left": "10px"},
                                ),
                                style={
                                    "text-align": "center",
                                    "margin-top": "20px",
                                },
                            ),
                            html.Div(
                                "",
                                id="downloaded",
                                style={
                                    "visibility": "hidden",
                                },
                            ),
                        ]
                    ),
                ],
                id="download-window",
                is_open=False,
            ),
        ]
    )
    return download_window


def _create_open_window() -> html.Div:
    open_window = html.Div(
        [
            dbc.Button(language["buttons"]["open"], id="open"),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(language["open_window"]["title"])
                    ),
                    dbc.ModalBody(
                        [
                            html.Div(
                                [
                                    dbc.Label(
                                        language["open_window"]["label"],
                                        style={
                                            "font-size": "18px",
                                            "margin-top": "5px",
                                        },
                                    ),
                                    dbc.Select(
                                        id="select-file",
                                        options=[],
                                        style={
                                            "width": "40%",
                                            "margin-left": "15px",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justify-content": "flex-start",
                                },
                            ),
                            html.Div(
                                dbc.Button(
                                    language["buttons"]["open"],
                                    id="open-file",
                                ),
                                style={
                                    "text-align": "center",
                                    "margin-top": "20px",
                                },
                            ),
                        ]
                    ),
                ],
                id="open-window",
                is_open=False,
            ),
        ]
    )
    return open_window


def _create_data_tab() -> list[dbc.Row]:
    site_data = create_site_data()
    time_slider = _create_time_slider()
    input_shift = _create_input_shift()
    selection_satellites = create_selection_satellites()
    input_sites = _create_input_sites()
    input_period_time = _create_input_period_time()
    input_half_thickness = _create_input_half_thickness()
    input_hmax = _create_input_hmax()
    input_z_step = _create_input_z_step()
    input_z_start = _create_input_z_start()
    input_z_end = _create_input_z_end()
    data_tab = [
        dbc.Row(
            dbc.Col(
                [
                    dbc.Label(language["data-tab"]["selection-sites"]+":", width=1),
                    html.Div(
                        input_sites,
                        style={"width": "110px", "margin-right": "20px", "margin-left": "-15px"},
                    ),
                    dbc.Label(language["data-tab"]["selection-sats"]+":", width=1),
                    html.Div(
                        selection_satellites,
                        id="div-selection-satellites",
                        style={"width": "110px", "margin-right": "20px", "margin-left": "10px"},
                    ),
                    dbc.Label(language["data-tab"]["input-half-thickness"], width=1),
                    html.Div(
                        input_half_thickness,
                        style={"width": "70px", "margin-right": "20px", "margin-left": "20px"},
                    ),
                ],
                style={"display": "flex", "justify-content": "center"},
            ),
            style={"margin-top": "20px"},
        ),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Label(language["data-tab"]["input-hmax"], width=1),
                    html.Div(
                        input_hmax,
                        style={"width": "70px", "margin-right": "20px"},
                    ),
                    
                    html.Div(
                        input_z_start,
                        style={"width": "100px", "margin-right": "5px"},
                    ),
                    html.Div(
                        input_z_end,
                        style={"width": "100px", "margin-right": "5px"},
                    ),
                    html.Div(
                        input_z_step,
                        style={"width": "90px", "margin-right": "20px"},
                    ),
                    dbc.Label(language["data-tab"]["input-period-time"]+":", width=1),
                    html.Div(
                        input_period_time,
                        style={"width": "80px", "margin-left": "-20px"},
                    ), 
                    dbc.Button(
                        language["buttons"]["build"],
                        id="calculate-tec",
                        style={"margin-left": "20px"}
                    ),
                ],
                style={"display": "flex", "justify-content": "center"},
            ),
            style={"margin-top": "10px", "margin-left": "10px"},
        ),
        dbc.Row(
            dbc.Col(
                html.Div("", id="status-get-tec"),
                style={"display": "flex", "justify-content": "center", "color": "red", "mergin-top": "10px"},
            ),
            id="div-status-get-tec",
            style={"visibility": "hidden"},
        ),
        dbc.Row(
            dcc.Graph(id="graph-site-data", figure=site_data),
            style={"margin-top": "10px"},
        ),
        dbc.Row(
            html.Div(time_slider, id="div-time-slider"),
            style={"margin-top": "20px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        input_shift,
                        dbc.Button(
                            language["buttons"]["clear-graph"],
                            id="clear-graph",
                        ),
                    ],
                    style={"display": "flex", "justify-content": "flex-end"},
                ),
            ],
            style={
                "margin-top": "10px",
            },
        ),
    ]
    return data_tab


def create_site_data() -> go.Figure:
    site_data = go.Figure()

    site_data.update_layout(
        title_font=dict(size=24, color="black"),
        plot_bgcolor="white",
        margin=dict(l=0, t=0, r=0, b=0),
        xaxis=dict(
            title=language["data-tab"]["graph-site-data"]["xaxis"],
            gridcolor="#E1E2E2",
            linecolor="black",
            showline=True,
            mirror=True,
        ),
        yaxis=dict(
            gridcolor="#E1E2E2",
            linecolor="black",
            showline=True,
            mirror=True,
        ),
    )
    return site_data


def _create_time_slider() -> dcc.RangeSlider:
    marks = {i: f"{i:02d}:00" if i % 3 == 0 else "" for i in range(25)}
    time_slider = dcc.RangeSlider(
        id="time-slider",
        min=0,
        max=24,
        step=1,
        marks=marks,
        value=[0, 24],
        allowCross=False,
        tooltip={
            "placement": "top",
            "style": {"fontSize": "18px"},
            "template": "{value}:00",
        },
        disabled=True,
        persistence=True,
        persistence_type="session",
    )
    return time_slider


def _create_input_shift() -> dbc.Input:
    input = dbc.Input(
        id="input-shift",
        type="number",
        step="0.5",
        value=-10,
        persistence=-10,
        persistence_type="session",
        style={"width": "80px", "margin-right": "15px"},
    )
    return input


def _create_input_period_time() -> dbc.Input:
    input = dbc.Input(
        id="input-period-time",
        type="number",
        step="1",
        min=10,
        invalid=False,
        placeholder=language["data-tab"]["input-period-time"],
        persistence=True,
        persistence_type="session",
    )
    return input


def create_selection_satellites(
    all_sats: list[tuple[str, int]] = []
) -> dbc.Select:
    options = [str(sat[0]) + str(sat[1]) for sat in all_sats]
    select = dbc.Select(
        id="selection-sats",
        options=options,
        placeholder=language["data-tab"]["selection-sats"],
        invalid=False,
        persistence=True,
        persistence_type="session",
    )
    return select


def _create_input_sites() -> dbc.Input:
    input = dbc.Input(
        id="input-sites",
        type="text",
        placeholder=language["data-tab"]["selection-sites"],
        readonly=True,
        invalid=False,
        persistence=True,
        persistence_type="session",
    )
    return input


def _create_input_z_step() -> dbc.Input:
    input = dbc.Input(
        id="input-z",
        type="number",
        placeholder=language["data-tab"]["input-z"],
        min=1,
        invalid=False,
        persistence=True,
        persistence_type="session",
    )
    return input

def _create_input_z_start() -> dbc.Input:
    input = dbc.Input(
        id="input-z-start",
        type="number",
        placeholder=language["data-tab"]["input-z-start"],
        min=80,
        invalid=False,
        persistence=True,
        persistence_type="session",
    )
    return input

def _create_input_z_end() -> dbc.Input:
    input = dbc.Input(
        id="input-z-end",
        type="number",
        placeholder=language["data-tab"]["input-z-end"],
        min=80,
        invalid=False,
        persistence=True,
        persistence_type="session",
    )
    return input


def _create_input_hmax() -> dbc.Input:
    input = dbc.Input(
        id="input-hmax",
        type="number",
        min=1,
        value=300,
        invalid=False,
        persistence=True,
        persistence_type="session",
    )
    return input


def _create_input_half_thickness() -> dbc.Input:
    input = dbc.Input(
        id="input-half-thickness",
        type="number",
        min=1,
        value=100,
        invalid=False,
        persistence=True,
        persistence_type="session",
    )
    return input


def _create_site_addition() -> list[dbc.Row]:
    site_addition = [
        dbc.Row(
            [
                dbc.Label(language["tab-adding-site"]["lat"], width=2),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="site-lat",
                        min=-90,
                        max=90,
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "-30px"},
                ),
                dbc.Label(language["tab-adding-site"]["lon"], width=2),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        id="site-lon",
                        min=-180,
                        max=180,
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "-30px"},
                ),
            ],
            style={"margin-top": "30px", "margin-left": "25px"},
        ),
        dbc.Row(
            [
                dbc.Label(language["tab-adding-site"]["name"], width=2),
                dbc.Col(
                    dbc.Input(
                        type="text",
                        id="site-name",
                        invalid=False,
                    ),
                    width=4,
                    style={"margin-left": "-30px"},
                ),
            ],
            style={"margin-top": "15px", "margin-left": "25px"},
        ),
        dbc.Button(
            language["buttons"]["add-site"],
            id="add-site",
            style={"margin-top": "20px"},
        ),
    ]
    return site_addition
