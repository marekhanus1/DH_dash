
import dash
from dash import dcc, html, dash_table, no_update, callback_context
import dash_mantine_components as dmc
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle
import pandas as pd
import random
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from dash_iconify import DashIconify
from dash import _dash_renderer
import h5py
import datetime
import numpy as np
import dash_ag_grid as dag

from plotly_resampler import FigureResampler
from plotly.subplots import make_subplots

_dash_renderer._set_react_version("18.2.0")

# GRAF
app = dash.Dash(__name__, external_stylesheets=dmc.styles.ALL, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=2"},])

data_names = np.array([["ekg", "ekgraw"],
                            ["flex", "flexraw"], 
                            ["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDer"],
                            ["HR", "RESP"]], dtype=object)

time_names = ["ekgtime", "flextime", "epochy_time", "HR_RESP_time"]

def read_hepochy_data5_data(names, time_names):
    with h5py.File("DH_data.h5", 'r') as f:
        decoded_data = {}
        decoded_time = {}

        for i in names:
            for j in i:
                decoded_data[j] = f[j][:]

        for i in time_names:
            a = f[i][:]
            decoded_time[i] = [datetime.datetime.fromtimestamp(ts) for ts in a]

    return decoded_data, decoded_time


all_data, time = read_hepochy_data5_data(data_names, time_names)



fig = FigureResampler(
    make_subplots(specs=[[{"secondary_y": True}]]),
    default_n_shown_samples=1_000,
    verbose=False,
)



# EPOCHY

data = {k: all_data[k] for k in data_names[2]}

epochy_data = pd.DataFrame(data)
cas_epochy = [i.strftime("%H:%M:%S") for i in time["epochy_time"]]
epochy_data.insert(0, "Čas epochy", cas_epochy)
epochy_data.insert(0, "Číslo epochy", range(1, len(epochy_data) + 1))

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
    
]

tabulka = dag.AgGrid(
    id="epochy_gridtable",
    columnDefs=columnDefs,
    className="ag-theme-alpine-dark",
    columnSize="sizeToFit",
    style={"height": "40vh", "width": "100%"},
    defaultColDef={"filter": True},
    dashGridOptions = {'rowSelection': 'single', 'animateRows': False}
)

epochy_nastaveni_content = html.Div([
    dmc.Card([
        dmc.NumberInput(label="Minimální hodnota RR", id="epochy_RRmin", value=350),
        dmc.NumberInput(label="Maximální hodnota RR", id="epochy_RRmax", value=2000),
        dmc.NumberInput(label="Maximální hodnota SDNN", id="epochy_SDNN", value=500),
        dmc.NumberInput(label="Maximální hodnota RMSSD", id="epochy_RMSSD", value=500),
        dmc.NumberInput(label="Maximální hodnota FlexDeriv", id="epochy_FlexDeriv", value=30),
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
            dmc.ActionIcon(DashIconify(icon="line-md:home-md", width=60), color="white", variant="subtle", size=80),
            href="/",
            style={"width": "80px", "display": "flex", "justify-content": "flex-start"}
        ),
        
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




"""
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
        PanelGroup(
            id='panel-group',
            children=[
                Panel(
                    children=[dcc.Graph(id="epochy_graph",figure=go.Figure(data=None, layout=dict(template='plotly_dark')),  style={"height":"70vh", "zoom": 1})],
                    defaultSizePercentage=25, minSizePercentage=40
                ),
                PanelResizeHandle(html.Div(style={"backgroundColor": "white", "width": "100%", "height": "5px"})),
                Panel(
                    children=[
                        tabulka,
                        html.Div(id='selected-row')
                    ],
                    minSizePercentage=25
                )
            ],
            direction='vertical',
            style={"height": "89vh"}
        )
    ], style={"height": "89vh"}, id="main-div")
])
"""

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
        
        dcc.Graph(id="epochy_graph",figure=go.Figure(data=None, layout=dict(template='plotly_dark', margin=dict(l=125, r=0, t=0, b=50))),  style={"height":"50vh", "zoom": 1})   
    ], style={"height": "50vh"})
])



epochy_appshell = dmc.AppShell(
            [
                dmc.AppShellHeader(children=[header], px=10),
                dmc.AppShellMain(children=[epochy_maindiv]),
                dmc.AppShellFooter(children=[tabulka])
            ],
            header={"height": "10vh"},
            footer={"height": "40vh"},
            padding="xs",    
)

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme=dmc.DEFAULT_THEME,
    children=html.Div([
        #header
        epochy_appshell
    ], id="main-div")
)

@app.callback(
    Output("epochy_drawer", "opened"),
    Input("epochy_nastaveni", "n_clicks"),
    prevent_initial_call=True
)
def open_epochy_drawer(n):
    if n:
        return True
    else: 
        no_update


@app.callback(
    [Output("epochy_gridtable", "columnDefs"),
    Output("epochy_gridtable", "rowData"),
    Output("epochy_stats", "children")],
    Input("epochy_submitbutton", "n_clicks"),
    [State(i, "value") for i in ["epochy_RRmin", "epochy_RRmax", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDeriv"]],
    prevent_initial_call=True

)
def epochy_set_limits(*inputs):
    if inputs[0]:
        
        limits = {
            'epochy_RR-min': {"operator": "<", "threshold": inputs[1], "override_false": False},
            'epochy_RR-max': {"operator": ">", "threshold": inputs[2], "override_false": False},
            'epochy_SDNN': {"operator": ">", "threshold": inputs[3], "override_false": False},
            'epochy_RMSSD': {"operator": ">", "threshold": inputs[4], "override_false": False},
            'epochy_FlexDer': {"operator": ">", "threshold": inputs[5], "override_false": True}
        }

        stats =  {
            'epochy_RR-min': 0,
            'epochy_RR-max': 0,
            'epochy_SDNN':   0,
            'epochy_RMSSD':  0,
            'epochy_FlexDer':0,
            'arytmie': 0
        }

        def check_arytmie(row):
            arytmie = False
            for col, rule in limits.items():
                if col in row:
                    value = row[col]
                    operator = rule["operator"]
                    threshold = rule["threshold"]
                    override_false = rule["override_false"]
                    
                    # Evaluate based on operator
                    limit_exceeded = (value > threshold) if operator == ">" else (value < threshold)
                    
                    # Apply override logic
                    if limit_exceeded:
                        stats[col] += 1
                        if override_false:
                            arytmie = False
                        else:
                            arytmie = True

            if arytmie == True:
                stats["arytmie"] += 1

            return arytmie

        # Calculate "Arytmie" column
        epochy_data['arytmie'] = epochy_data.apply(check_arytmie, axis=1)
        pocet_epoch = len(epochy_data["arytmie"])
        
        

        stats_content = [
                            dmc.Stack(
                                children=[
                                    dmc.Text("Nadlimitní epochy:"), 

                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'Arytmie: {stats["arytmie"]}/{pocet_epoch} [{(round(stats["arytmie"]/pocet_epoch*100))} %]')]),

                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'RR-min: {stats["epochy_RR-min"]}/{pocet_epoch} [{(round(stats["epochy_RR-min"]/pocet_epoch*100))} %]')]),
                                    
                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'Arytmie: {stats["epochy_RR-max"]}/{pocet_epoch} [{(round(stats["epochy_RR-max"]/pocet_epoch*100))} %]')]),

                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'SDNN: {stats["epochy_SDNN"]}/{pocet_epoch} [{(round(stats["epochy_SDNN"]/pocet_epoch*100))} %]')]),

                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'RMSSD: {stats["epochy_RMSSD"]}/{pocet_epoch} [{(round(stats["epochy_RMSSD"]/pocet_epoch*100))} %]')]),
                                    
                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'FlexDer: {stats["epochy_FlexDer"]}/{pocet_epoch} [{(round(stats["epochy_FlexDer"]/pocet_epoch*100))} %]')]),       
                                ]
                            )
                        ]
                
        

        for i in range(len(inputs)-2):
            if i == 0:
                columnDefs[i+4]["cellStyle"] = {"styleConditions": [{"condition": f"params.value < {int(inputs[i+1])}", "style": {"border": "1px solid red", }}]}
            else:
                columnDefs[i+4]["cellStyle"] = {"styleConditions": [{"condition": f"params.value > {int(inputs[i+1])}", "style": {"border": "1px solid red"}}]}
        
        columnDefs[8]["cellStyle"] = {"styleConditions": [{"condition": f"params.value > {int(inputs[5])}", "style": {"border": "1px solid green"}}]}
        columnDefs[9]["cellStyle"] = {"styleConditions": [{"condition": "params.value === true", "style": {"border": "1px solid red"}}]}
        #print(columnDefs)
        
        row_data = epochy_data.to_dict("records")
        return columnDefs,row_data, stats_content
    else:
        return no_update, no_update, no_update





@app.callback(
    Output("epochy_graph", "figure"),
    Input("epochy_gridtable", "selectedRows"),
    
    prevent_initial_call=True,
)
def epochy_show_chart(selection):
    ctx = callback_context
    if len(ctx.triggered) and "epochy_gridtable" in ctx.triggered[0]["prop_id"] and len(ctx.triggered[0]["value"]) > 0:
        # Note how the replace method is used here on the global figure object
        global fig
        if len(fig.data):
            # Replace the figure with an empty one to clear the graph
            fig.replace(make_subplots(specs=[[{"secondary_y": True}]]))

        cislo_epochy = selection[0]["Číslo epochy"]-1
        delka_epochy_s = round((time["epochy_time"][1]-time["epochy_time"][0]).total_seconds())


        ekg_epocha = list(all_data["ekg"][cislo_epochy*500*delka_epochy_s:cislo_epochy*500*delka_epochy_s+500*delka_epochy_s])
        ekg_epocha_cz = list(time["ekgtime"][cislo_epochy*500*delka_epochy_s:cislo_epochy*500*delka_epochy_s+500*delka_epochy_s])
    

        fig.add_trace(go.Scattergl(name=f"EKG EPOCHA {cislo_epochy}"), hf_x=ekg_epocha_cz, hf_y=ekg_epocha)
        

        fig.update_layout(template="plotly_dark", margin=dict(l=125, r=0, t=0, b=50))

        
        return fig
    else:
        return no_update

    
fig.register_update_graph_callback(app=app, graph_id="graph-id")
fig.register_update_graph_callback(app=app, graph_id="epochy_graph")

if __name__ == "__main__":
    app.run_server(debug=True)

