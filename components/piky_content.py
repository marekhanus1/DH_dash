import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import dcc, html
import plotly.graph_objects as go
from dash_iconify import DashIconify
from components.utils import Utils

columnDefs = [
    {"headerName": "Číslo piku", 'field': 'Číslo piku'},
    {"headerName": "Čas piku", 'field': 'Čas piku' },
    {"headerName": "P píky", 'field': 'peaks_P_prominence'},
    {"headerName": "P", 'field': 'peaks_P'},
    {"headerName": "PR", 'field': 'peaks_PR'},
    {"headerName": "QRS", 'field': 'peaks_QRS'},
    {"headerName": "QTc", 'field': 'peaks_QTc' },
    {"headerName": "FlexDer", 'field': 'peaks_FlexDer' },
    {"headerName": "Arytmie", 'field': 'arytmie'},
    {'headerName': 'Hodnocení', 'field': 'hodnoceni', 'editable': True}
    
]

def show_piky():
    config = Utils.read_config()

    

    tabulka = dag.AgGrid(
        id="piky_gridtable",
        columnDefs=columnDefs,
        className="ag-theme-alpine-dark",
        columnSize="sizeToFit",
        style={"height": "40vh", "width": "95%"},
        defaultColDef={"filter": True},
        dashGridOptions = {'rowSelection': 'single', 'animateRows': False}
    )

    piky_nastaveni_content = html.Div([
        dmc.Card([
            dmc.Stack(gap=10, children=[

                dmc.Checkbox("Zobrazit vyhodnocení neurokit2",  id={"type": "piky_checkbox", "index": "chbox_piky_neurokit2"}, checked=config.get("chbox_piky_neurokit"), size=20),
                dmc.Checkbox("Zobrazit meze ideálního signálu", id={"type": "piky_checkbox", "index": "chbox_piky_meze"}, checked=config.get("chbox_piky_meze"), size=20),
                
                dmc.NumberInput(label="Délka zobrazení píků [s]", id={"type": "piky_input2", "index": "piky_delkaZobrazeni"}, value=config.get("piky_delkaZobrazeni"), w=370),

                dmc.Divider(labelPosition="center", label="Nastavení mezních hodnot"),
                
                dmc.Group([
                    dmc.NumberInput(label="Minimální hodnota P",   id={"type": "piky_input", "index": "piky_Pmin"},   value=config.get("piky_Pmin")  , w=170),
                    dmc.NumberInput(label="Maximální hodnota P",   id={"type": "piky_input", "index": "piky_Pmax"},   value=config.get("piky_Pmax")  , w=170),
                ], gap=30),

                dmc.Group([
                    dmc.NumberInput(label="Minimální hodnota PR",  id={"type": "piky_input", "index": "piky_PRmin"},  value=config.get("piky_PRmin") , w=170),
                    dmc.NumberInput(label="Maximální hodnota PR",  id={"type": "piky_input", "index": "piky_PRmax"},  value=config.get("piky_PRmax") , w=170),
                ], gap=30),

                dmc.NumberInput(label="Maximální hodnota QRS", id={"type": "piky_input", "index": "piky_QRSmax"}, value=config.get("piky_QRSmax"), w=370),
                dmc.NumberInput(label="Maximální hodnota QTc", id={"type": "piky_input", "index": "piky_QTcmax"}, value=config.get("piky_QTcmax"), w=370),
                dmc.NumberInput(label="Maximální hodnota FlexDer", id={"type": "piky_input", "index": "piky_FlexDermax"}, value=config.get("piky_FlexDer"), w=370),


            ])
        ]),
        dmc.Space(h=10),

        dmc.Button("Potvrdit", color="green", id="piky_submitbutton"),
        dmc.Space(h=30),

        html.Div(id="piky_stats")
    ])



    header = html.Div([
        dcc.Location(id='url', refresh=False),
        dmc.Group([
            # Left icon (home)
            dcc.Link(
                dmc.ActionIcon(DashIconify(icon="line-md:home-md", width=60), color="white", id="piky_home", variant="subtle", size=80),
                href="/",
                style={"width": "80px", "display": "flex", "justify-content": "flex-start"}
            ),
            
            dmc.ActionIcon(DashIconify(icon="la:save", width=40, id="piky_save_icon"), color="white", id="piky_save", variant="subtle", size=80),

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
                id="piky_nastaveni",
                style={"width": "80px", "display": "flex", "justify-content": "flex-end"}
            ),
            
        ], justify="space_between", style={"height": "7.5vh", "width": "100vw", "padding": "0 2vw"}),
    ])

    
    piky_maindiv = html.Div([
        dmc.Drawer(
                title="Nastavení",
                id="piky_drawer",
                padding="md",
                position="right",
                opened=True,
                children=[
                    piky_nastaveni_content
                ]
            ),
        # Main layout
        html.Div([
            
            dcc.Graph(id="piky_graph",figure=go.Figure(data=None, layout=dict(template='plotly_dark', margin=dict(l=125, r=0, t=0, b=50))),  style={"height":"50vh", "zoom": 1}),
            dmc.Group([
                html.Button("Set Category A", id="piky_category_a", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category S", id="piky_category_s", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category N", id="piky_category_n", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category A", id="piky_category_a_shift", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category S", id="piky_category_s_shift", n_clicks=0, style={"display": "none"}),
                html.Button("Set Category N", id="piky_category_n_shift", n_clicks=0, style={"display": "none"}),
                html.Button("Reset graph", id="piky_reset_button", n_clicks=0, style={"display": "none"}),
                html.Button("Arrow UP", id="piky_arrowup_button", n_clicks=0, style={"display": "none"}),
                html.Button("Arrow DOWN", id="piky_arrowdown_button", n_clicks=0, style={"display": "none"}),
            ])
        ], style={"height": "50vh"})
    ])

    return dmc.AppShell(
            [
                dmc.AppShellHeader(children=[header], px=10),
                dmc.AppShellMain(children=[piky_maindiv]),
                dmc.AppShellFooter(children=[tabulka])
            ],
            header={"height": "10vh"},
            footer={"height": "40vh"},
            padding="xs",
            style={"overflow": "hidden"}
        )