from dash import html, dcc
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from enum import Enum
from .languages import languages
from datetime import datetime, date, timedelta
# from ..processing import DataProducts

language = languages["en"]

def create_layout(all_sites: list[list[str | float]]) -> html.Div:
    left_side = _create_left_side(all_sites)
    data_tab = _create_data_tab()
    tab_lat_lon = _create_selection_tab_lat_lon()

    size_map = 5
    size_data = 7
    layout = html.Div(
        [
            dcc.Store(id="all-sites-store", storage_type="session", data=all_sites),
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
                                    tab_lat_lon,
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

def _create_left_side(all_sites: list[list[str | float]]) -> list[dbc.Row]:
    site_map = create_site_map(all_sites)
    download_window = _create_download_window()
    open_window = _create_open_window()
    selection_satellites = _create_empty_selection_satellites()
    left_side = [
        dbc.Row(
            dbc.Col(
                    [
                        download_window,
                        html.Div(
                            open_window,
                            style={"margin-left": "15px"},
                        ),
                        html.Div(
                            selection_satellites,
                            style={"margin-left": "15px"},
                        ),
                    ],
                    style={"display": "flex", "justify-content": "flex-start"},
                ) 
        ),
        dbc.Row(
            dcc.Graph(id="graph-site-map", figure=site_map, style={"height": "300px"}),
            style={"margin-top": "20px"}
        ),
        dbc.Row(
            html.Img(src="assets/tec.png", style={"height": "300px"}),
            style={"margin-top": "10px"}
        ),
    ]
    return left_side

def create_site_map(all_sites: list[list[str | float]]) -> go.Figure:
    site_map = go.Scattergeo(
        lon = [point[3] for point in all_sites],
        lat = [point[2] for point in all_sites],
        text = [point[0] for point in all_sites],
        mode="markers",
        marker=dict(size=4, color="Silver", line=dict(color="gray", width=1)),
        hoverlabel=dict(bgcolor="white"),
        hoverinfo="text+lat+lon",
    )

    figure = go.Figure(site_map)
    figure.update_layout(
        title_font=dict(size=24, color="black"),
        margin=dict(l=0, t=0, r=0, b=0),
        geo=dict(projection_type="robinson"),
    )
    figure.update_geos(
        landcolor="white",
        showcountries=True,  # показывать границы стран
        showrivers=True,     # показывать реки
        rivercolor='RoyalBlue',   # цвет линий рек
        showland=True,
        showlakes=True,
        lakecolor='RoyalBlue'
    )

    return figure

def _create_download_window() -> html.Div:
    download_window = html.Div(
        [
            dbc.Button(language["buttons"]["download"], id="download"),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(language["buttons"]["download"])
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
                        dbc.ModalTitle(language["buttons"]["open"])
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
                                            "width": "50%",
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

def _create_empty_selection_satellites() -> dbc.Select:
    select = dbc.Select(
        id="selection-satellites",
        options=[],
        placeholder=language["data-tab"]["selection-satellites"],
        style={"width": "150px", "margin-right": "20px"},
        persistence=True,
        persistence_type="session",
    )
    return select

def _create_data_tab() -> list[dbc.Row]:
    site_data = create_site_data()
    time_slider = _create_time_slider()
    input_shift = _create_input_shift()
    data_tab = [
        dbc.Row(
            dcc.Graph(id="graph-site-data", figure=site_data),
            style={"margin-top": "20px"},
        ),
        dbc.Row(
            html.Div(time_slider, id="div-time-slider"),
            style={"margin-top": "25px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        input_shift,
                        dbc.Button(
                            language["buttons"]["clear-all"],
                            id="clear-all",
                        ),
                    ],
                    style={"display": "flex", "justify-content": "flex-end"},
                ),
            ],
            style={
                "margin-top": "20px",
            },
        ),
    ]
    return data_tab

def create_site_data() -> go.Figure:
    site_data = go.Figure()

    site_data.update_layout(
        title=language["data-tab"]["graph-site-data"]["title"],
        title_font=dict(size=24, color="black"),
        plot_bgcolor="white",
        margin=dict(l=0, t=60, r=0, b=0),
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
        )
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
        value=-0.5,
        persistence=-0.5,
        persistence_type="session",
        style={"width": "80px", "margin-right": "20px"},
    )
    return input

def _create_selection_tab_lat_lon() -> list[dbc.Row]:
    tab_lat_lon = [
        
    ]
    return tab_lat_lon
