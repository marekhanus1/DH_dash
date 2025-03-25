from dash import html, dcc
import dash_mantine_components as dmc
from components.tabs_content import show_tabs
from dash_iconify import DashIconify
from datetime import date
import plotly.graph_objs as go
from components.layout_content import layout_content


def create_layout():
    return dmc.MantineProvider(
        forceColorScheme="dark",
        theme=dmc.DEFAULT_THEME,
        children=html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='main-div', children=layout_content.before_start())
        ])
    )
