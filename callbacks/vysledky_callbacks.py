from components.layout_content import layout_content
from dash import Output, Input, State, no_update, callback_context, ctx

from plotly.subplots import make_subplots
import plotly.graph_objects as go

from components.utils import Utils
from components.vysledky_chart_content import data_names, time_names

class VysledkyCallbacks(Utils):
    def vysledky_callbacks(self):
        ##################################### VYSLEDKY ##################################### 
        ##################################### VYSLEDKY ##################################### 
        ##################################### VYSLEDKY ##################################### 
        @self.app.callback(
            #[Output('output-div', 'children'), ],
            
            [Output('my-interval2', 'disabled'), Output("fileinfo_div", "children", allow_duplicate=True)],
            Input('my-interval2', 'n_intervals'),
            prevent_initial_call=True, 
            suppress_callback_exceptions=True
            
        )
        def interval_callback(n_clcik):
            print("GELLO")
            infodiv_content = self.handle_info()

                
            return True, infodiv_content


        @self.app.callback(
            Output('main-div', 'children', allow_duplicate=True),
            Input('url', 'pathname'),
            prevent_initial_call=True
        )
        
        def display_page(pathname):
            print(f"Current pathname: {pathname}")
            if self.stage_num >= 3 and self.path_name != pathname:
                    self.path_name = pathname
                    if pathname == '/':
                        return layout_content.decoding_done()
                    
                    elif pathname == '/vysledky':
                        return layout_content.chart_vysledky()
                    
                    elif pathname == '/epochy':
                        return layout_content.epochy()
                    
                    else:
                        return layout_content.decoding_done()

            else:
                return no_update



        @self.app.callback(
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
                
                if len(self.fig.data):
                    # Replace the figure with an empty one to clear the graph
                    self.fig.replace(make_subplots(specs=[[{"secondary_y": True}]]))

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

                        self.fig.add_trace(go.Scattergl(name=data_names[row_index][col_index]), hf_x=self.time[time_names[row_index]], hf_y=self.data[data_names[row_index][col_index]], secondary_y = int(inputs[i+(total_elements+1)]))


                self.fig.update_layout(
                    height=900, 
                    template="plotly_dark", 
                    xaxis=dict(
                        titlefont=dict(size=18),  # X axis title font size
                        tickfont=dict(size=16)    # X axis tick font size
                    ),
                    yaxis=dict(
                        titlefont=dict(size=18),  # Y axis title font size
                        tickfont=dict(size=16)    # Y axis tick font size
                    ),
                )

                status_update = "Graf nastaven!"
                return self.fig, status_update
            else:
                return no_update, no_update
            

        self.app.clientside_callback(
            """
                function(id) {
                    document.addEventListener("keydown", function(event) {
                        
                        // Reset zoomu grafu
                        if (event.key == 'h' || event.key == 'r') {
                            document.getElementById('vysledky_reset_button').click()
                        }
                    });
                    return window.dash_clientside.no_update       
                }
            """,
            Output("vysledky_reset_button", "id"),
            Input("vysledky_reset_button", "id")
        )

        @self.app.callback(
            Output('graph-id', 'figure', allow_duplicate=True),
            Input('vysledky_reset_button', 'n_clicks'),
            prevent_initial_call=True
        )
        def reset_axes(n_clicks):
            # Update axes to autorange
            self.fig.update_xaxes(autorange=True)
            self.fig.update_yaxes(autorange=True)
            return self.fig