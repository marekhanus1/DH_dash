# pip install dash dash-leaflet dash-resizable-panels
import dash
import dash_leaflet as dl
from dash import html
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle
from dash.dependencies import Input, Output, State


handle = {"height": "100%", "width": "3px", "backgroundColor": "#51ada6"}
layout = html.Div([
    PanelGroup(id="panel-group", 
               children=[
                    Panel(id="panel-1",children=[html.Div([html.P("Dummy component")])]),
                    PanelResizeHandle(html.Div(style=handle)),
                    Panel(id="panel-2",
                          children=[
                            dl.Map(center=[45.81, 15.98], zoom=12, children=[
                                dl.TileLayer(),
                                dl.FeatureGroup([dl.EditControl()]),
                                
                            ], style={'height': '100%', 'width': '100%'})]
                    )], direction="horizontal",),
], style={"height": "100vh"})



app = dash.Dash(__name__)


app.layout = layout


if __name__ == "__main__":
    app.run_server(debug=True)