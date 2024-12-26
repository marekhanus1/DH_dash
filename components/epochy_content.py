import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import dcc, html
import plotly.graph_objects as go
from dash_iconify import DashIconify
from components.utils import Utils

columnDefs = [
    {"headerName": "Číslo epochy", 'field': 'Číslo epochy'},
    {"headerName": "Čas epochy", 'field': 'Čas epochy' },
    {"headerName": "HR", 'field': 'epochy_HR'},
    {"headerName": "RESP", 'field': 'epochy_RESP'},
    {"headerName": "RR-min", 'field': 'epochy_RR-min'},
    {"headerName": "RR-max", 'field': 'epochy_RR-max' },
    {"headerName": "SDNN", 'field': 'epochy_SDNN' },
    {"headerName": "RMSSD", 'field': 'epochy_RMSSD'},
    {"headerName": "FlexDer", 'field': 'epochy_FlexDer' },
    {"headerName": "Arytmie", 'field': 'arytmie'},
    {'headerName': 'Hodnocení', 'field': 'hodnoceni', 'editable': True}
    
]

def show_epochy():
    config = Utils.read_config()

    

    tabulka = dag.AgGrid(
        id="epochy_gridtable",
        columnDefs=columnDefs,
        className="ag-theme-alpine-dark",
        columnSize="sizeToFit",
        style={"height": "40vh", "width": "95%"},
        defaultColDef={"filter": True},
        dashGridOptions = {'rowSelection': 'single', 'animateRows': False}
    )

    epochy_nastaveni_content = html.Div([
        dmc.Card([
            dmc.NumberInput(label="Minimální hodnota RR", id="epochy_RRmin", value=config.get("RR_min")),
            dmc.NumberInput(label="Maximální hodnota RR", id="epochy_RRmax", value=config.get("RR_max")),
            dmc.NumberInput(label="Maximální hodnota SDNN", id="epochy_SDNN", value=config.get("SDNN")),
            dmc.NumberInput(label="Maximální hodnota RMSSD", id="epochy_RMSSD", value=config.get("RMSSD")),
            dmc.NumberInput(label="Maximální hodnota FlexDeriv", id="epochy_FlexDeriv", value=config.get("FlexDer")),
        ]),
        dmc.Space(h=10),

        dmc.Button("Potvrdit", color="green", id="epochy_submitbutton"),
        dmc.Space(h=30),

        html.Div(id="epochy_stats")
    ])



    header = html.Div([
        dcc.Location(id='url', refresh=False),
        dmc.Group([
            # Left icon (home)
            dcc.Link(
                dmc.ActionIcon(DashIconify(icon="line-md:home-md", width=60), color="white", id="epochy_home", variant="subtle", size=80),
                href="/",
                style={"width": "80px", "display": "flex", "justify-content": "flex-start"}
            ),
            
            dmc.ActionIcon(DashIconify(icon="la:save", width=40, id="epochy_save_icon"), color="white", id="epochy_save", variant="subtle", size=80),

            # Center title
            html.Div(
                html.H1("Holter dekodér", style={"text-align": "center", "zoom": "1.2"}),
                style={"flex": "1", "display": "flex", "align-items": "center", "justify-content": "center"}
            ),
            
            # Right icon (settings)
            dmc.ActionIcon(
                
                DashIconify(icon="clarity:settings-solid", width=60),
                size=80,
                variant="subtle",
                color="white",
                id="epochy_nastaveni",
                style={"width": "80px", "display": "flex", "justify-content": "flex-end"}
            ),
            
        ], justify="space_between", style={"height": "7.5vh", "width": "100vw", "padding": "0 2vw"}),
    ])

    
    epochy_maindiv = html.Div([
        dmc.Drawer(
                title="Nastavení",
                id="epochy_drawer",
                padding="md",
                position="right",
                opened=True,
                children=[
                    epochy_nastaveni_content
                ]
            ),
        # Main layout
        html.Div([
            
            dcc.Graph(id="epochy_graph",figure=go.Figure(data=None, layout=dict(template='plotly_dark', margin=dict(l=125, r=0, t=0, b=50))),  style={"height":"50vh", "zoom": 1}),
            dmc.Group([
                html.Button("Set Category A", id="epochy_category_a", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category S", id="epochy_category_s", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category N", id="epochy_category_n", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category A", id="epochy_category_a_shift", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category S", id="epochy_category_s_shift", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category N", id="epochy_category_n_shift", n_clicks=0, style={"display": "none"}),
                html.Button("Reset graph", id="epochy_reset_button", n_clicks=0, style={"display": "none"}),
                html.Button("Arrow UP", id="epochy_arrowup_button", n_clicks=0, style={"display": "none"}),
                html.Button("Arrow DOWN", id="epochy_arrowdown_button", n_clicks=0, style={"display": "none"}),
            ])
        ], style={"height": "50vh"})
    ])

    return dmc.AppShell(
            [
                dmc.AppShellHeader(children=[header], px=10),
                dmc.AppShellMain(children=[epochy_maindiv]),
                dmc.AppShellFooter(children=[tabulka])
            ],
            header={"height": "10vh"},
            footer={"height": "40vh"},
            padding="xs",
            style={"overflow": "hidden"}
        )