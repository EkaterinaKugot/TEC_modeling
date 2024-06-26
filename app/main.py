from tec import *
from dash import Dash
import requests

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY]
)
server = app.server

rq = requests.post("https://simurg.iszf.irk.ru/api", 
                    json={"method": "get_site", "args": {}} 
                    )
all_sites = rq.json()

app.layout = create_layout(all_sites)

register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)