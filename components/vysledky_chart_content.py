import dash_mantine_components as dmc
from dash import dcc, html
import plotly.graph_objects as go
import numpy as np
from dash_iconify import DashIconify




def show_vysledky(args):

    folder_names = ["EKG", "FLEX", "EPOCHY", "HR A RESP"]
    data_names = np.array([["ekg", "ekgraw"],
                                ["flex", "flexraw"],                             
                                ["HR", "RESP"]], dtype=object)

    HR_names = np.array(["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDer"], dtype=object)

    if args["epocha"] != None:
        data_names = np.array([["ekg", "ekgraw"],
                                ["flex", "flexraw"], 
                                ["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDer"],                            
                                ["HR", "RESP"]], dtype=object) #np.array(data_names.tolist() + [HR_names.tolist()], dtype=object)
        
        

    maindiv = html.Div([
                    dcc.Graph(id="graph-id",figure=go.Figure(data=None, layout=dict(template='plotly_dark')),  style={"height":900, "width":"100%", "zoom": 1}),
                    html.Button("Reset graph", id="vysledky_reset_button", n_clicks=0, style={"display": "none"}),
            ], id="main-chart-div", style={"height":900, "width":"100%", "zoom": 1})

    def create_plot_form(names):
        form = []
        for folder, j in enumerate(names):
            form += [dmc.Divider(label=folder_names[folder]), dmc.Divider(label=folder_names[folder]), dmc.Divider(label=folder_names[folder])]
            for i in j:
                form += [
                            dmc.Checkbox(label=i.upper().replace("EPOCHY_", "").replace("-", ""),
                                    id={"type": "checkbox", "index": i.lower()}, w=100, size="xl"), dmc.Space(w=1), #f"chbox_{i.lower()}"
                        
                            dmc.Select(value="0", id={"type": "select", "index": i.lower()}, # id=f"select_{i.lower()}"
                                    data=[{"value": "0", "label":"y1"}, {"value": "1", "label": "y2"}], w=70)
                        ]
            
        
        return form

    side_div = html.Div([    
                    
                    dmc.SimpleGrid(cols=3,spacing="xs", verticalSpacing="md",
                    children=create_plot_form(data_names)
                    
                    ),

                    dmc.Space(h=20),
                    dmc.Button("Potvrdit", id="plot-button", n_clicks=0, color="green", size="lg"),

                    dcc.Loading(
                        id="chart_status",
                        type="default",
                        children=html.Div(id="status-message", children="Klikni pro zobrazení grafu!")
                    )

                ],style={"margin-left":15, "margin-top": 15})  



    header = html.Div([
        dcc.Location(id='url', refresh=False),
        
        dmc.Group([
            # Left icon (home)
            dcc.Link(
                dmc.ActionIcon(DashIconify(icon="line-md:home-md", width=60), color="white", variant="subtle", size=80),
                href="/",
                style={"width": "80px", "display": "flex", "justify-content": "flex-start"}
            ),
            
            # Center title
            html.Div(
                html.H1("Holter dekodér", style={"text-align": "center", "zoom": "1.2"}),
                style={"flex": "1", "display": "flex", "align-items": "center", "justify-content": "center"}
            ),
            
        ], justify="space_between", style={"height": "7.5vh", "width": "100vw", "padding": "0 2vw"}),
    ])



    return dmc.AppShell(
                [
                    
                    dmc.AppShellHeader(children=[header], px=10),
                    dmc.AppShellNavbar(children=[side_div]),
                    dmc.AppShellMain(children=[maindiv]),
                ],
                header={"height": "10vh"},
                padding="xl",    
                navbar={
                    "width": 300,
                    "breakpoint": "sm",
                    "collapsed": {"mobile": True},
                }
                
            )