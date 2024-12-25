from dash import Output, Input, State, no_update, callback_context, ctx
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.utils import Utils
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from components.piky_content import columnDefs


class PikyCallbacks(Utils):
    def piky_callbacks(self):
        #######################################################################################
        ############################################ PÍKY ###################################
        #######################################################################################
        @self.app.callback(
            Output("piky_drawer", "opened"),
            Input("piky_nastaveni", "n_clicks"),
            prevent_initial_call=True
        )
        def open_piky_drawer(n):
            if n:
                return True
            else: 
                no_update


        @self.app.callback(
            [Output("piky_gridtable", "rowData")],
            Input("piky_submitbutton", "n_clicks"),
            #[State(i, "value") for i in ["piky_RRmin", "piky_RRmax", "piky_SDNN", "piky_RMSSD", "piky_FlexDeriv"]],
            State("chbox_piky_neurokit2", "checked"), State("chbox_piky_meze", "checked"),
            prevent_initial_call=True

        )
        def piky_set_limits(*inputs):
            if inputs[0]:
                
                self.zobraz_cary = [False, False]
                if inputs[1] == True:
                    self.zobraz_cary[0] = True
                if inputs[2] == True:
                    self.zobraz_cary[1] = True
                    

                row_data = self.piky_data.to_dict("records")
                return [row_data]
            else:
                return no_update





        @self.app.callback(
            Output("piky_graph", "figure"), Output("piky_gridtable", "scrollTo", allow_duplicate=True),
            Input("piky_gridtable", "selectedRows"),
            State("piky_gridtable", "virtualRowData"),
            
            prevent_initial_call=True,
        )
        def piky_show_chart(selection, row_data):
            ctx = callback_context
            if len(ctx.triggered) and "piky_gridtable" in ctx.triggered[0]["prop_id"] and len(ctx.triggered[0]["value"]) > 0:
                # Note how the replace method is used here on the global figure object
                if len(self.fig.data):
                    # Replace the figure with an empty one to clear the graph
                    self.fig.replace(make_subplots(specs=[[{"secondary_y": True}]]))

                cislo_piky = selection[0]["Číslo piku"]-1
                delka_piky_s = round((self.time["peaks_time"][1]-self.time["peaks_time"][0]).total_seconds(),2)


                print(cislo_piky)
                
                # Find peak index in EKG data
                for i in range(len(self.time["ekgtime"])):
                    if self.time["peaks_time"][cislo_piky] == self.time["ekgtime"][i]:
                        break
                pik_index = i
                start = int(i-250*delka_piky_s)
                end = int(i+250*delka_piky_s)
                


                ekg_pik = list(self.data["ekg"][start:end])
                ekg_pik_cz = list(self.time["ekgtime"][start:end])
            

                self.fig.add_trace(go.Scattergl(name=f"EKG Pík {cislo_piky}"), hf_x=ekg_pik_cz, hf_y=ekg_pik)
                
                self.fig.add_vline(x=self.time["peaks_time"][cislo_piky].timestamp() * 1000, line_dash="dot", line_color="red", line_width=1, annotation_text="R pík")

                print(self.time["ekgtime"][pik_index-30])
                
                if self.zobraz_cary[1] == True:
                    self.fig.add_vline(x=self.time["ekgtime"][pik_index-30].timestamp() * 1000, line_dash="dash", line_color="red", line_width=2, annotation_text="-60 ms") # 60 ms before peak
                    self.fig.add_vline(x=self.time["ekgtime"][pik_index+30].timestamp() * 1000, line_dash="dash", line_color="red", line_width=2, annotation_text="+60 ms") # 60 ms after peak

                    self.fig.add_vline(x=self.time["ekgtime"][pik_index-60].timestamp() * 1000, line_dash="dash", line_color="orange", line_width=2, annotation_text="-120 ms") # 120 ms before peak
                    self.fig.add_vline(x=self.time["ekgtime"][pik_index-110].timestamp() * 1000, line_dash="dash", line_color="orange", line_width=2, annotation_text="-180 ms") # 180 ms before peak

                    self.fig.add_vline(x=self.time["ekgtime"][pik_index+160].timestamp() * 1000, line_dash="dash", line_color="blue", line_width=2, annotation_text="+320 ms") # 320 ms after peak
                    self.fig.add_vline(x=self.time["ekgtime"][pik_index+225].timestamp() * 1000, line_dash="dash", line_color="blue", line_width=2, annotation_text="+450 ms") # 450 ms after peak
                
                #['ECG_P_Peaks', 'ECG_P_Onsets', 'ECG_P_Offsets', 'ECG_Q_Peaks', 'ECG_R_Onsets', 'ECG_R_Offsets', 'ECG_S_Peaks', 'ECG_T_Peaks', 'ECG_T_Onsets', 'ECG_T_Offsets']

                if cislo_piky != 0 and self.zobraz_cary[0] == True:
                    for i in self.Piky_points_names:
                        if self.data[i][cislo_piky] != 0:
                            self.fig.add_vline(x=self.data[i][cislo_piky] * 1000, line_dash="dash", line_color="pink", line_width=2, annotation_text=i.replace("ECG_", ""))
                    

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

                
                selected_index = next((i for i, item in enumerate(row_data) if item['Číslo piku'] == cislo_piky+1), None)
                scroll_to = {"data": row_data[selected_index]}
                return self.fig, scroll_to
            else:
                return no_update, no_update
            
        self.app.clientside_callback(
            """
                function(id) {
                    document.addEventListener("keydown", function(event) {
                        
                        // Kategorie pro piky
                        if(event.shiftKey) // Write all empty cells with category
                        {
                            if (event.key.toLowerCase() == 'a') {
                                document.getElementById('piky_category_a_shift').click()
                            }
                            if (event.key.toLowerCase() == 's') {
                                document.getElementById('piky_category_s_shift').click()
                            }
                            if (event.key.toLowerCase() == 'n') {
                                document.getElementById('piky_category_n_shift').click()
                            }
                        }
                        else // Write only selected cell with category
                        {
                            if (event.key.toLowerCase() == 'a') {
                                document.getElementById('piky_category_a').click()
                            }
                            if (event.key.toLowerCase() == 's') {
                                document.getElementById('piky_category_s').click()
                            }
                            if (event.key.toLowerCase() == 'n') {
                                document.getElementById('piky_category_n').click()
                            };
                        }
                        
                        // If keys = SHIFT + S, save the data
                        if (event.shiftKey && event.key.toLowerCase() == 's') {
                            document.getElementById('piky_save').click()
                        }

                        
                        // Reset zoomu grafu
                        if (event.key.toLowerCase() == 'h' || event.key.toLowerCase() == 'r') {
                            document.getElementById('piky_reset_button').click()
                        }
                        

                        if(event.key == 'ArrowDown'){
                            document.getElementById('piky_arrowdown_button').click()
                        }

                        if(event.key == 'ArrowUp'){
                            document.getElementById('piky_arrowup_button').click()
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
            Output("piky_category_a", "id"),
            Input("piky_category_a", "id")
        )
        # Save data from table back into pandas dataframe than to csv
        @self.app.callback(
            Output("piky_save", "children"),
            Input("piky_save", "n_clicks"),
            Input("piky_home", "n_clicks"),
            State("piky_gridtable", "rowData"),
            prevent_initial_call=True
        )
        def save_data(n_clicks, n_clicks_home, row_data):
            print(ctx.triggered_id)

            if ctx.triggered_id == "piky_save":
                print("Saving data...")

                # create folder Holter_piky_vysledky if it doens't exist
                Utils.create_folder("Holter_piky_vysledky")

                filename = f"Holter_piky_vysledky/Holter_{self.args['date']}_piky.csv"

                # Save data to csv
                self.piky_data = pd.DataFrame(row_data)
                self.piky_data.to_csv(filename, index=False)
                print("Data saved.")
                return DashIconify(icon="dashicons:saved", width=40, id="piky_save_icon") # change icon to saved
            elif ctx.triggered_id == "piky_home": 
                self.piky_data = pd.DataFrame(row_data) # Save data to DF
                return no_update #dcc.Location(pathname="/", id="home")
            else:
                return no_update
            
        # Callback for automatic select of row in table
    
        @self.app.callback(
            [Output("piky_gridtable", "selectedRows", allow_duplicate=True),Output("piky_gridtable", "scrollTo", allow_duplicate=True)],
            Input("piky_arrowdown_button", "n_clicks"),
            Input("piky_arrowup_button", "n_clicks"),
            State("piky_gridtable", "selectedRows"),
            State("piky_gridtable", "virtualRowData"),
            prevent_initial_call=True
        )
        
        def arrow_movement(up,down,selected_rows,row_data):
            print(ctx.triggered_id)
            print(up, down)

            cislo_piku = selected_rows[0]["Číslo piku"]
            selected_index = next((i for i, item in enumerate(row_data) if item['Číslo piku'] == cislo_piku), None)

            if ctx.triggered_id == "piky_arrowdown_button":
                new_selected_row = row_data[selected_index + 1] if selected_index < len(row_data) - 1 else row_data[selected_index]
                
            elif ctx.triggered_id == "piky_arrowup_button":
                new_selected_row = row_data[selected_index - 1] if selected_index > 0 else row_data[selected_index]

            return [new_selected_row], {"data": new_selected_row}

        # Callback to handle button clicks and update the category, then select the row below it, so it's easier for user.
        @self.app.callback(
            [Output('piky_gridtable', 'rowData', allow_duplicate=True), Output("piky_gridtable", "selectedRows"), Output("piky_save", "children", allow_duplicate=True), Output("piky_gridtable", "scrollTo")],
            Input('piky_category_a', 'n_clicks'),
            Input('piky_category_s', 'n_clicks'),
            Input('piky_category_n', 'n_clicks'),
            State('piky_gridtable', 'selectedRows'),
            State('piky_gridtable', 'rowData'),        # rowData == všechna data v původním pořadí
            State('piky_gridtable', 'virtualRowData'), # virtualRowData == aktuální pořadí dat (s uživatelskými filtry)
            State("piky_gridtable", "scrollTo"), 
            prevent_initial_call=True
        )
        def set_category(n_clicks_a, n_clicks_s, n_clicks_n, selected_rows, row_data, virtualRowData, scroll_to):
            
            if not selected_rows:
                return no_update, no_update, no_update  # No row selected, return current data unchanged

            print(ctx.triggered_id, selected_rows[0]['Číslo píku'])

            # Determine which button was clicked
            category = None
            if ctx.triggered_id == "piky_category_a":
                category = 'A'
            elif ctx.triggered_id == "piky_category_s":
                category = 'S'
            elif ctx.triggered_id == "piky_category_n":
                category = 'N'
                
            # Update the category in the selected row
            row_data[selected_rows[0]['Číslo píku'] - 1]["hodnoceni"] = category
            
            # Find the index of the selected row in the current sorted order
            cislo_piku = selected_rows[0]["Číslo piku"]
            selected_index = next((i for i, item in enumerate(virtualRowData) if item['Číslo píku'] == cislo_piku), None) # Zjisti index vybraného řádku v tabulce pomocí virtualRowData

            # Select the row below the current one
            row_below = virtualRowData[selected_index + 1] if selected_index < len(virtualRowData) - 1 else virtualRowData[selected_index]
            print(row_below)

            return row_data, [row_below], DashIconify(icon="la:save", width=40, id="piky_save_icon"), {"data": row_below}
        
        @self.app.callback(
            Output('piky_gridtable', 'scrollTo', allow_duplicate=True),
            Input('piky_gridtable', 'scrollTo'),
            prevent_initial_call=True
        )
        def scroll_to_row(scroll_to):
            print(f"SCROLL TO: {scroll_to}")
            return scroll_to | {'rowPosition': 'middle'}

        # Write category to all empty cells
        @self.app.callback(
            [Output('piky_gridtable', 'rowData', allow_duplicate=True), Output("piky_save", "children", allow_duplicate=True)],
            Input('piky_category_a_shift', 'n_clicks'),
            Input('piky_category_s_shift', 'n_clicks'),
            Input('piky_category_n_shift', 'n_clicks'),
            State('piky_gridtable', 'selectedRows'),
            State('piky_gridtable', 'rowData'), 
            prevent_initial_call=True
        )
        def set_empty_category(n_clicks_a, n_clicks_s, n_clicks_n, selected_rows, row_data):
            if not selected_rows:
                return no_update, no_update
            
            category = None
            if ctx.triggered_id == "piky_category_a_shift":
                category = 'A'
            elif ctx.triggered_id == "piky_category_s_shift":
                category = 'S'
            elif ctx.triggered_id == "piky_category_n_shift":
                category = 'N'

            # See which rows are empty
            empty_rows = [row for row in row_data if (row["hodnoceni"] == None or row["hodnoceni"] == "")]
            for row in empty_rows:
                row["hodnoceni"] = category

            # Connect empty rows with row_data
            for row in empty_rows:
                row_data[row["Číslo píku"] - 1] = row
            return row_data, DashIconify(icon="la:save", width=40, id="piky_save_icon")
        

        @self.app.callback(
            Output('piky_graph', 'figure', allow_duplicate=True),
            Input('piky_reset_button', 'n_clicks'),
            prevent_initial_call=True
        )
        def reset_axes(n_clicks):
            # Update axes to autorange
            self.fig.update_xaxes(autorange=True)
            self.fig.update_yaxes(autorange=True)
            return self.fig