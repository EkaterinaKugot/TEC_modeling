from tec import *
from dash import Dash

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

app.layout = create_layout()

register_callbacks(app)

if __name__ == "__main__":
    app.run_server()
