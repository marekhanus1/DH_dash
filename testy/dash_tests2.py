"""

from dash import Dash, dcc, html
import plotly.express as px
import dash_mantine_components as dmc
from dash import _dash_renderer
from dash import dcc
import plotly.graph_objs as go
import random

_dash_renderer._set_react_version("18.2.0")


app = Dash(__name__, external_stylesheets=dmc.styles.ALL, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=2"},])



x = [i for i in range(1000000)]
y = [random.randint(1,10000) for i in range(1000000)]






s = html.Div([
        dcc.Store(id='stage-store'),
        html.H1("Holter dekodér", style={"text-align": "center"}),
        
        html.Div([
            
            dcc.Graph(figure=go.Figure(data=[go.Scatter(x=x, y=y)]))
        ])
    ])

app.layout =dmc.MantineProvider(
        forceColorScheme="dark",
        theme=dmc.DEFAULT_THEME,
        children=s
    )




if __name__ == '__main__':
    app.run(debug=True)


"""
"""
import dash
from dash import dcc, html
import h5py
import datetime
import plotly.graph_objects as go; import numpy as np
from plotly_resampler import FigureResampler, FigureWidgetResampler

# Path to HDF5 file
hdf5_filename = "ekg_data.h5"

# Function to read from HDF5
def read_hdf5_data():
    with h5py.File(hdf5_filename, 'r') as f:
        int_array1 = f['ekg'][:]
        int_array2 = f['ekgraw'][:]
        time_array = f['ekgtime'][:]

    # Convert timestamps back to datetime objects
    datetime_array = [datetime.datetime.fromtimestamp(ts) for ts in time_array]

    return int_array1, int_array2, datetime_array


"""
import h5py
import datetime

import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback_context, dcc, html, no_update

from plotly_resampler import FigureResampler
from plotly.subplots import make_subplots

import pandas as pd

import dash_mantine_components as dmc
from dash import _dash_renderer
from dash_iconify import DashIconify
_dash_renderer._set_react_version("18.2.0")
# Path to HDF5 file
hdf5_filename = "DH_data.h5"

# Function to read from HDF5
def read_hdf5_data(names, time_names):
    with h5py.File(hdf5_filename, 'r') as f:
        decoded_data = {}
        decoded_time = {}

        for i in names:
            for j in i:
                decoded_data[j] = f[j][:]

        for i in time_names:
            a = f[i][:]
            decoded_time[i] = [datetime.datetime.fromtimestamp(ts) for ts in a]

    return decoded_data, decoded_time

data_names = np.array([["ekg", "ekgraw"],
        ["flex", "flexraw"], 
        ["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD"],
        ["HR", "RESP"]], dtype=object)

folder_names = ["EKG", "FLEX", "EPOCHY", "HR A RESP"]


time_names = ["ekgtime", "flextime", "epochy_time", "HR_RESP_time"]

data, time = read_hdf5_data(data_names, time_names)
print(data["ekg"][:100])


# --------------------------------------Globals ---------------------------------------
app = Dash(__name__, external_stylesheets=dmc.styles.ALL, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=2"},])

style = {
    "zoom": 1.5,
}



fig = FigureResampler(
    make_subplots(specs=[[{"secondary_y": True}]]),
    default_n_shown_samples=1_000,
    verbose=False,
)

maindiv = html.Div([
            html.Div([
                
                dcc.Graph(id="graph-id",figure=go.Figure(data=None, layout=dict(template='plotly_dark')),  style={"height":900, "zoom": 1}),
            ], style={"zoom":1})
            
        ], id="main-div")


def create_plot_form(names):
    
    form = []
    for folder, j in enumerate(names):
        form += [dmc.Divider(label=folder_names[folder]), dmc.Divider(label=folder_names[folder]), dmc.Divider(label=folder_names[folder])]
        for i in j:
            form += [
                        dmc.Checkbox(label=i.upper().replace("EPOCHY_", "").replace("-", ""),
                                  id=f"chbox_{i.lower()}", w=100, size="xl"), dmc.Space(w=1), 
                     
                        dmc.Select(value="0", id=f"select_{i.lower()}", 
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
            dmc.Group([
                dcc.Link(dmc.ActionIcon(DashIconify(icon="line-md:home-md", width=60), color="white", variant="subtle", size=80), href="/", style={"width":"10%", "height":"10%", "height":80}),
                dmc.Space(w="40%"),
                dmc.Center([html.H1("Holter dekodér", style={"text-align": "center", "zoom":"1.2"})], style={"height":80}),
                
            
            ], style={"height":80}),
        ], style={"vertical-align":"TOP", "height":80})


appshell = dmc.AppShell(
            [
                dmc.AppShellHeader(children=[header], px=10),
                dmc.AppShellNavbar(children=[side_div]),
                dmc.AppShellMain(children=[maindiv]),
            ],
            header={"height": 80},
            padding="xl",    
            navbar={
                "width": 300,
                "breakpoint": "sm",
                "collapsed": {"mobile": True},
            },
            
        )

app.layout = dmc.MantineProvider(
        forceColorScheme="dark",
        theme=dmc.DEFAULT_THEME,
        children=appshell
    )


# ------------------------------------ DASH logic -------------------------------------
# The callback used to construct and store the graph's data on the serverside
@app.callback(
    [Output("graph-id", "figure"), Output("status-message", "children")],
    Input("plot-button", "n_clicks"),

    [State(f"chbox_{i.lower()}", 'checked') for j in data_names for i in j]+
    [State(f"select_{i.lower()}", 'value') for j in data_names for i in j],



    prevent_initial_call=True,
)
def plot_graph(*inputs):
    print(inputs)
    ctx = callback_context
    if len(ctx.triggered) and "plot-button" in ctx.triggered[0]["prop_id"]:
        # Note how the replace method is used here on the global figure object
        global fig
        if len(fig.data):
            # Replace the figure with an empty one to clear the graph
            fig.replace(make_subplots(specs=[[{"secondary_y": True}]]))

        total_elements = sum(len(sublist) for sublist in data_names)
        print(total_elements)
        for i in range(total_elements):
            if inputs[i+1] == True:     

                current_index = 0           
                for row_index in range(data_names.shape[0]):
                    row_length = len(data_names[row_index])  # Length of the current row
                    if current_index + row_length > i:
                        col_index = i - current_index  # Calculate the column index
                        break
                    current_index += row_length

                fig.add_trace(go.Scattergl(name=data_names[row_index][col_index]), hf_x=time[time_names[row_index]], hf_y=data[data_names[row_index][col_index]], secondary_y = int(inputs[i+(total_elements+1)]))


        fig.update_layout(height=900, template="plotly_dark")

        status_update = "Graf nastaven!"
        return fig, status_update
    else:
        return no_update, no_update


# The plotly-resampler callback to update the graph after a relayout event (= zoom/pan)
fig.register_update_graph_callback(app=app, graph_id="graph-id")

# --------------------------------- Running the app ---------------------------------
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)

