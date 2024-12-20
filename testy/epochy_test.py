
import dash
from dash import dcc, html, dash_table, no_update, callback_context, ctx
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

# Initialize the Dash app
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
    {'headerName': 'Hodnocení', 'field': 'hodnoceni', "cellRenderer": "agAnimateShowChangeCellRenderer",}
    
]

tabulka = dag.AgGrid(
    id="epochy_gridtable",
    columnDefs=columnDefs,
    className="ag-theme-alpine-dark",
    columnSize="sizeToFit",
    style={"height": "40vh", "width": "100%"},
    defaultColDef={"filter": True},
    dashGridOptions={"rowSelection": "single"},
    getRowId="params.data.Číslo epochy",
    #
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
        
        dcc.Graph(id="epochy_graph",figure=go.Figure(data=None, layout=dict(template='plotly_dark', margin=dict(l=125, r=0, t=0, b=50))),  style={"height":"50vh", "zoom": 1}),
        dmc.Group([
            html.Button("Set Category A", id="epochy_category_a", n_clicks=0, style={"display": "none"}),
            html.Button("Set Category S", id="epochy_category_s", n_clicks=0, style={"display": "none"}),
            html.Button("Set Category N", id="epochy_category_n", n_clicks=0, style={"display": "none"}),
            html.Button("Set Category A", id="epochy_category_a_shift", n_clicks=0, style={"display": "none"}),
            html.Button("Set Category S", id="epochy_category_s_shift", n_clicks=0, style={"display": "none"}),
            html.Button("Set Category N", id="epochy_category_n_shift", n_clicks=0, style={"display": "none"}),
            html.Button("Reset graph", id="epochy_reset_button", n_clicks=0, style={"display": "none"}),
            html.Button("Arrow keys", id="epochy_arrowkeys_button", n_clicks=0, style={"display": "none"}),
        ])
    ])
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
    ], id="main-div"),
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
        epochy_data["hodnoceni"] = ""

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


app.clientside_callback(
    """
        function(id) {
            document.addEventListener("keydown", function(event) {
                
                // Kategorie pro epochy
                if(event.shiftKey) // Write all empty cells with category
                {
                    if (event.key.toLowerCase() == 'a') {
                        document.getElementById('epochy_category_a_shift').click()
                    }
                    if (event.key.toLowerCase() == 's') {
                        document.getElementById('epochy_category_s_shift').click()
                    }
                    if (event.key.toLowerCase() == 'n') {
                        document.getElementById('epochy_category_n_shift').click()
                    }
                }
                else // Write only selected cell with category
                {
                    if (event.key.toLowerCase() == 'a') {
                        document.getElementById('epochy_category_a').click()
                    }
                    if (event.key.toLowerCase() == 's') {
                        document.getElementById('epochy_category_s').click()
                    }
                    if (event.key.toLowerCase() == 'n') {
                        document.getElementById('epochy_category_n').click()
                    };
                }
                
                // If keys = SHIFT + S, save the data
                if (event.shiftKey && event.key.toLowerCase() == 's') {
                    document.getElementById('epochy_save').click()
                }

                
                // Reset zoomu grafu
                if (event.key.toLowerCase() == 'h' || event.key.toLowerCase() == 'r') {
                    document.getElementById('epochy_reset_button').click()
                }
                
                /*
                if (event.key == 'ArrowDown') {
                    // Logic to select the row below by row-index value
                    let selectedRow = document.querySelector('.ag-row-selected');
                    if (selectedRow) {
                        let rowIndex = parseInt(selectedRow.getAttribute('row-index'));
                        let nextRow = document.querySelector(`.ag-row[row-index="${rowIndex + 1}"]`);
                        if (nextRow) {
                            nextRow.click();
                        }
                    }
                    
                }
                if (event.key == 'ArrowUp') {
                    
                    // Logic to select the row above by row-index value
                    let selectedRow = document.querySelector('.ag-row-selected');
                    if (selectedRow) {
                        let rowIndex = parseInt(selectedRow.getAttribute('row-index'));
                        let prevRow = document.querySelector(`.ag-row[row-index="${rowIndex - 1}"]`);
                        if (prevRow) {
                            prevRow.click();
                        }
                    }
                }
                */
                
            });
            return window.dash_clientside.no_update       
        }
    """,
    Output("epochy_category_a", "id"),
    Input("epochy_category_a", "id")
)

# Save data from table back into pandas dataframe than to csv
@app.callback(
    Output("epochy_save", "children"),
    Input("epochy_save", "n_clicks"),
    Input("epochy_home", "n_clicks"),
    State("epochy_gridtable", "rowData"),
    prevent_initial_call=True
)
def save_data(n_clicks, n_clicks_home, row_data):
    print(ctx.triggered_id)

    if ctx.triggered_id == "epochy_save":
        print("Saving data...")
        # Save data to csv
        epochy_data = pd.DataFrame(row_data)
        epochy_data.to_csv("epochy_data.csv", index=False) # TODO Change based on date
        print("Data saved.")
        return DashIconify(icon="dashicons:saved", width=40, id="epochy_save_icon") # change icon to saved
    elif ctx.triggered_id == "epochy_home": 
        epochy_data = pd.DataFrame(row_data) # Save data to DF
        return dcc.Location(pathname="/", id="home")
    else:
        return no_update

    
# Callback to handle button clicks and update the category, then select the row below it, so it's easier for user.
# I need to move cell focus to the next row after setting the category
@app.callback(
            [Output('epochy_gridtable', 'rowData', allow_duplicate=True), Output("epochy_gridtable", "selectedRows"), Output("epochy_save", "children", allow_duplicate=True), Output("epochy_gridtable", "scrollTo")],
            Input('epochy_category_a', 'n_clicks'),
            Input('epochy_category_s', 'n_clicks'),
            Input('epochy_category_n', 'n_clicks'),
            State('epochy_gridtable', 'selectedRows'),
            State('epochy_gridtable', 'rowData'),
            State("epochy_gridtable", "scrollTo"), 
            prevent_initial_call=True
        )

def set_category(n_clicks_a, n_clicks_s, n_clicks_n, selected_rows, row_data, scroll_to):
    
    print(f"SCROLLLLLLL: {scroll_to}")
    if not selected_rows:
        return no_update, no_update, no_update  # No row selected, return current data unchanged

    print(ctx.triggered_id, selected_rows[0]['Číslo epochy'])

    # Determine which button was clicked
    category = None
    if ctx.triggered_id == "epochy_category_a":
        category = 'A'
    elif ctx.triggered_id == "epochy_category_s":
        category = 'S'
    elif ctx.triggered_id == "epochy_category_n":
        category = 'N'
        
    # Update the category in the selected row
    row_data[selected_rows[0]['Číslo epochy'] - 1]["hodnoceni"] = category
    
    # Find the index of the selected row in the current sorted order
    selected_index = next(i for i, row in enumerate(row_data) if row['Číslo epochy'] == selected_rows[0]['Číslo epochy'])

    # Select the row below the current one
    row_below = row_data[selected_index + 1] if selected_index < len(row_data) - 1 else row_data[selected_index]

    return row_data, [row_below], DashIconify(icon="la:save", width=40, id="epochy_save_icon"), {"data": row_below}

# Write category to all empty cells
@app.callback(
    [Output('epochy_gridtable', 'rowData', allow_duplicate=True), Output("epochy_gridtable", "selectedRows", allow_duplicate=True), Output("epochy_save", "children", allow_duplicate=True)],
    Input('epochy_category_a_shift', 'n_clicks'),
    Input('epochy_category_s_shift', 'n_clicks'),
    Input('epochy_category_n_shift', 'n_clicks'),
    State('epochy_gridtable', 'selectedRows'),
    State('epochy_gridtable', 'rowData'), 
    prevent_initial_call=True
)
def set_empty_category(n_clicks_a, n_clicks_s, n_clicks_n, selected_rows, row_data):
    if not selected_rows:
        return no_update, no_update, no_update
    
    category = None
    if ctx.triggered_id == "epochy_category_a_shift":
        category = 'A'
    elif ctx.triggered_id == "epochy_category_s_shift":
        category = 'S'
    elif ctx.triggered_id == "epochy_category_n_shift":
        category = 'N'

    # See which rows are empty
    empty_rows = [row for row in row_data if (row["hodnoceni"] == None or row["hodnoceni"] == "")]
    for row in empty_rows:
        row["hodnoceni"] = category

    # Connect empty rows with row_data
    for row in empty_rows:
        row_data[row["Číslo epochy"] - 1] = row
    return row_data, no_update, DashIconify(icon="la:save", width=40, id="epochy_save_icon")
    
    

@app.callback(
    Output('epochy_graph', 'figure', allow_duplicate=True),
    Input('epochy_reset_button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_axes(n_clicks):
    # Update axes to autorange
    global fig
    fig.update_xaxes(autorange=True)
    fig.update_yaxes(autorange=True)
    return fig

@app.callback(
    Output("epochy_graph", "figure"),
    Input("epochy_gridtable", "selectedRows"),
    
    prevent_initial_call=True,
)
def epochy_show_chart(selection):
    ctx = callback_context
    print(ctx.triggered)
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
        

        fig.update_layout(template="plotly_dark", margin=dict(l=125, r=0, t=0, b=50),
                                       xaxis=dict(
                                            titlefont=dict(size=18),  # X axis title font size
                                            tickfont=dict(size=16)    # X axis tick font size
                                        ),
                                        yaxis=dict(
                                            titlefont=dict(size=18),  # Y axis title font size
                                            tickfont=dict(size=16)    # Y axis tick font size
                                        )
                                    )

        
        return fig
    else:
        return no_update


fig.register_update_graph_callback(app=app, graph_id="graph-id")
fig.register_update_graph_callback(app=app, graph_id="epochy_graph")

if __name__ == "__main__":
    app.run_server(debug=True)

