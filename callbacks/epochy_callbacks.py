from dash import Output, Input, State, no_update, callback_context, ctx
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.utils import Utils
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from components.epochy_content import columnDefs


class EpochyCallbacks(Utils):
    def epochy_callbacks(self):
        #######################################################################################
        ############################################ EPOCHY ###################################
        #######################################################################################
        @self.app.callback(
            Output("epochy_drawer", "opened"),
            Input("epochy_nastaveni", "n_clicks"),
            prevent_initial_call=True
        )
        def open_epochy_drawer(n):
            if n:
                return True
            else: 
                no_update


        @self.app.callback(
            [Output("epochy_gridtable", "columnDefs"),
            Output("epochy_gridtable", "rowData"),
            Output("epochy_stats", "children")],
            Input("epochy_submitbutton", "n_clicks"),
            [State(i, "value") for i in ["epochy_RRmin", "epochy_RRmax", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDeriv"]],
            prevent_initial_call=True

        )
        def epochy_set_limits(*inputs):
            if inputs[0]:
                
                config = Utils.read_config()
                config_names = ["RR_min", "RR_max", "SDNN", "RMSSD", "FlexDer"]
                
                for i in range(len(config_names)):
                    config[config_names[i]] = inputs[i+1]

                print(config)

                self.write_config(config)


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
                self.epochy_data['arytmie'] = self.epochy_data.apply(check_arytmie, axis=1)

                # If hodnoceni is not in the dataframe, add it
                if "hodnoceni" not in self.epochy_data.columns:
                    self.epochy_data["hodnoceni"] = ""
                

                pocet_epoch = len(self.epochy_data["arytmie"])
                
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
                
                row_data = self.epochy_data.to_dict("records")
                return columnDefs,row_data, stats_content
            else:
                return no_update, no_update, no_update





        @self.app.callback(
            Output("epochy_graph", "figure"),
            Input("epochy_gridtable", "selectedRows"),
            
            prevent_initial_call=True,
        )
        def epochy_show_chart(selection):
            ctx = callback_context
            if len(ctx.triggered) and "epochy_gridtable" in ctx.triggered[0]["prop_id"] and len(ctx.triggered[0]["value"]) > 0:
                # Note how the replace method is used here on the global figure object
                if len(self.fig.data):
                    # Replace the figure with an empty one to clear the graph
                    self.fig.replace(make_subplots(specs=[[{"secondary_y": True}]]))

                cislo_epochy = selection[0]["Číslo epochy"]-1
                delka_epochy_s = round((self.time["epochy_time"][1]-self.time["epochy_time"][0]).total_seconds())


                ekg_epocha = list(self.data["ekg"][cislo_epochy*500*delka_epochy_s:cislo_epochy*500*delka_epochy_s+500*delka_epochy_s])
                ekg_epocha_cz = list(self.time["ekgtime"][cislo_epochy*500*delka_epochy_s:cislo_epochy*500*delka_epochy_s+500*delka_epochy_s])
            

                self.fig.add_trace(go.Scattergl(name=f"EKG EPOCHA {cislo_epochy}"), hf_x=ekg_epocha_cz, hf_y=ekg_epocha)
                

                self.fig.update_layout(template="plotly_dark", margin=dict(l=125, r=0, t=0, b=50),
                                       xaxis=dict(
                                            titlefont=dict(size=18),  # X axis title font size
                                            tickfont=dict(size=16)    # X axis tick font size
                                        ),
                                        yaxis=dict(
                                            titlefont=dict(size=18),  # Y axis title font size
                                            tickfont=dict(size=16)    # Y axis tick font size
                                        ),
                                        hoverlabel=dict(
                                            font=dict(
                                                size=20  # Change this to your desired font size
                                            )
                                        )
                                    )

                
                return self.fig
            else:
                return no_update
            
        self.app.clientside_callback(
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
                        

                        if(event.key == 'ArrowDown'){
                            document.getElementById('epochy_arrowdown_button').click()
                        }

                        if(event.key == 'ArrowUp'){
                            document.getElementById('epochy_arrowup_button').click()
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
        @self.app.callback(
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

                # create folder Holter_epochy_vysledky if it doens't exist
                Utils.create_folder("Holter_epochy_vysledky")

                filename = f"Holter_epochy_vysledky/Holter_{self.args['date']}_epochy.csv"

                # Save data to csv
                self.epochy_data = pd.DataFrame(row_data)
                self.epochy_data.to_csv(filename, index=False)
                print("Data saved.")
                return DashIconify(icon="dashicons:saved", width=40, id="epochy_save_icon") # change icon to saved
            elif ctx.triggered_id == "epochy_home": 
                self.epochy_data = pd.DataFrame(row_data) # Save data to DF
                return no_update #dcc.Location(pathname="/", id="home")
            else:
                return no_update
            
        # Callback for automatic select of row in table
    
        @self.app.callback(
            [Output("epochy_gridtable", "selectedRows", allow_duplicate=True),Output("epochy_gridtable", "scrollTo", allow_duplicate=True)],
            Input("epochy_arrowdown_button", "n_clicks"),
            Input("epochy_arrowup_button", "n_clicks"),
            State("epochy_gridtable", "selectedRows"),
            State("epochy_gridtable", "rowData"),
            prevent_initial_call=True
        )
        
        def arrow_movement(up,down,selected_rows,row_data):
            print(ctx.triggered_id)

            selected_index = selected_rows[0]["Číslo epochy"] - 1

            if ctx.triggered_id == "epochy_arrowdown_button":
                print("DOWN")
                new_selected_row = row_data[selected_index + 1] if selected_index < len(row_data) - 1 else row_data[selected_index]
                
            elif ctx.triggered_id == "epochy_arrowup_button":
                print("UP")
                new_selected_row = row_data[selected_index - 1] if selected_index > 0 else row_data[selected_index]

            return [new_selected_row], {"data": new_selected_row}

        # Callback to handle button clicks and update the category, then select the row below it, so it's easier for user.
        @self.app.callback(
            [Output('epochy_gridtable', 'rowData', allow_duplicate=True), Output("epochy_gridtable", "selectedRows", allow_duplicate=True), Output("epochy_save", "children", allow_duplicate=True), Output("epochy_gridtable", "scrollTo", allow_duplicate=True)],
            Input('epochy_category_a', 'n_clicks'),
            Input('epochy_category_s', 'n_clicks'),
            Input('epochy_category_n', 'n_clicks'),
            State('epochy_gridtable', 'selectedRows'),
            State('epochy_gridtable', 'rowData'),
            State("epochy_gridtable", "scrollTo"), 
            prevent_initial_call=True
        )
        def set_category(n_clicks_a, n_clicks_s, n_clicks_n, selected_rows, row_data, scroll_to):
            
            if not selected_rows:
                return no_update, no_update, no_update, no_update  # No row selected, return current data unchanged

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
            print(row_below)

            return row_data, [row_below], DashIconify(icon="la:save", width=40, id="epochy_save_icon"), {"data": row_below}
        
        @self.app.callback(
            Output('epochy_gridtable', 'scrollTo', allow_duplicate=True),
            Input('epochy_gridtable', 'scrollTo'),
            prevent_initial_call=True
        )
        def scroll_to_row(scroll_to):
            print(f"SCROLL TO: {scroll_to}")
            return scroll_to | {'rowPosition': 'middle'}

        # Write category to all empty cells
        @self.app.callback(
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
        

        @self.app.callback(
            Output('epochy_graph', 'figure', allow_duplicate=True),
            Input('epochy_reset_button', 'n_clicks'),
            prevent_initial_call=True
        )
        def reset_axes(n_clicks):
            # Update axes to autorange
            self.fig.update_xaxes(autorange=True)
            self.fig.update_yaxes(autorange=True)
            return self.fig