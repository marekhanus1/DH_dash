from dash import Output, Input, State, no_update, callback_context, ctx, ALL
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.utils import Utils
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from components.piky_content import columnDefs
import numpy as np
import os


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
            Output("piky_gridtable", "rowData"), Output("piky_stats", "children"), Output("piky_gridtable", "columnDefs"),
            Input("piky_submitbutton", "n_clicks"),
            #[State(i, "value") for i in ["piky_RRmin", "piky_RRmax", "piky_SDNN", "piky_RMSSD", "piky_FlexDeriv"]],
            State({"type": "piky_checkbox", "index": ALL}, "checked"),
            State({"type": "piky_input", "index": ALL}, "value"),
            State({"type": "piky_input2", "index": ALL}, "value"),
            prevent_initial_call=True

        )
        def piky_set_limits(*inputs):
            if inputs[0]:
                self.zobraz_cary = [False, False]
                if inputs[1][0] == True:
                    self.zobraz_cary[0] = True
                if inputs[1][1] == True:
                    self.zobraz_cary[1] = True

                self.delka_piky_s = inputs[3][0]

                config = Utils.read_config()
                print(inputs)
                config_names = ["chbox_piky_neurokit", "chbox_piky_meze", "piky_Pmin", "piky_Pmax", "piky_PRmin", "piky_PRmax","piky_QTcmin", "piky_QTcmax" , "piky_QRSmax", "piky_FlexDer","piky_prominenceP", "piky_delkaZobrazeni"]

                index_num = 0
                for i in inputs[1:]:
                    for j in i:
                        config[config_names[index_num]] = j
                        index_num += 1
                

                self.write_config(config)

                limits = {
                    'peaks_P': {"operator": "<>", "threshold": [inputs[2][0], inputs[2][1]], "override_false": False},
                    'peaks_PR': {"operator": "<>", "threshold":[inputs[2][2], inputs[2][3]], "override_false": False},
                    'peaks_QTc': {"operator": "<>", "threshold": [inputs[2][4], inputs[2][5]], "override_false": False},
                    'peaks_QRS': {"operator": ">", "threshold":      inputs[2][6], "override_false": False},
                    'peaks_FlexDer': {"operator": ">", "threshold": inputs[2][7], "override_false": True}
                }
                stats =  {
                    'peaks_P': 0,
                    #'peaks_P_max': 0,
                    'peaks_PR': 0,
                    #'peaks_PR_max': 0,
                    'peaks_QRS':   0,
                    'peaks_QTc':  0,
                    'peaks_FlexDer':0,
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
                            if operator == "<>":
                                limit_exceeded = (value < threshold[0]) or (value > threshold[1])
                            elif operator == ">":
                                limit_exceeded = (value > threshold)
                            else:
                                limit_exceeded = (value < threshold)

                            if np.isnan(value):
                                limit_exceeded = True
                            
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
                self.piky_data['arytmie'] = self.piky_data.apply(check_arytmie, axis=1)

                # If hodnoceni is not in the dataframe, add it
                if "hodnoceni" not in self.piky_data.columns:
                    self.piky_data["hodnoceni"] = ""

                    # Check if the file exists
                    filename = f"Holter_piky_vysledky/Holter_{self.args['date']}_piky.csv"
                    if os.path.exists(filename):
                        # Read the file
                        saved_data = pd.read_csv(filename)
                        
                        # Check if "hodnoceni" column exists in the saved data
                        if "hodnoceni" in saved_data.columns:
                            # Update the "hodnoceni" column in self.piky_data
                            self.piky_data["hodnoceni"] = saved_data["hodnoceni"]

                pocet_piku = len(self.piky_data["arytmie"])
                
                print(stats)

                stats_content = [
                            dmc.Stack(
                                children=[
                                    dmc.Text("Nadlimitní píky:"), 

                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'Arytmie: {stats["arytmie"]}/{pocet_piku} [{(round(stats["arytmie"]/pocet_piku*100))} %]')]),

                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'P: {stats["peaks_P"]}/{pocet_piku} [{(round(stats["peaks_P"]/pocet_piku*100))} %]')]),
                                    
                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'PR: {stats["peaks_PR"]}/{pocet_piku} [{(round(stats["peaks_PR"]/pocet_piku*100))} %]')]),

                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'QRS: {stats["peaks_QRS"]}/{pocet_piku} [{(round(stats["peaks_QRS"]/pocet_piku*100))} %]')]),

                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'QTc: {stats["peaks_QTc"]}/{pocet_piku} [{(round(stats["peaks_QTc"]/pocet_piku*100))} %]')]),
                                    
                                    dmc.Group([dmc.Space(w=20),
                                               dmc.Text(f'FlexDer: {stats["peaks_FlexDer"]}/{pocet_piku} [{(round(stats["peaks_FlexDer"]/pocet_piku*100))} %]')]),       
                                ]
                            )
                        ]

                columnDefs[2]["cellStyle"] = {"styleConditions": [
                                                {"condition": f"params.value > 1", "style": {"border": "2px solid red", }} # P Píky
                                            ]}
                
                columnDefs[3]["cellStyle"] = {"styleConditions": [
                                                {"condition": f"params.value < {int(inputs[2][0])}", "style": {"border": "1px solid red", }}, # P
                                                {"condition": f"params.value > {int(inputs[2][1])}", "style": {"border": "1px solid red", }}
                                            ]}
                columnDefs[4]["cellStyle"] = {"styleConditions": [
                                                {"condition": f"params.value < {int(inputs[2][2])}", "style": {"border": "1px solid red", }}, # PR
                                                {"condition": f"params.value > {int(inputs[2][3])}", "style": {"border": "1px solid red", }}
                                            ]}


                columnDefs[6]["cellStyle"] = {"styleConditions": [
                                                {"condition": f"params.value < {int(inputs[2][4])}", "style": {"border": "1px solid red", }}, # QTc
                                                {"condition": f"params.value > {int(inputs[2][5])}", "style": {"border": "1px solid red", }}
                                                ]}

                columnDefs[5]["cellStyle"] = {"styleConditions": [
                                                {"condition": f"params.value > {int(inputs[2][6])}", "style": {"border": "1px solid red", }}, # QRS
                                                {"condition": f"params.value === {int(inputs[2][6])}", "style": {"border": "1px solid red", }}

                                            ]}                

                columnDefs[7]["cellStyle"] = {"styleConditions": [
                                                {"condition": f"params.value > {int(inputs[2][7])}", "style": {"border": "1px solid green", }} # FlexDer
                                            ]}
                
                columnDefs[8]["cellStyle"] = {"styleConditions": [{"condition": "params.value === true", "style": {"border": "1px solid red"}}]} # ARYTMIE

                
                def decode_P_prominence(threshold):
                    filtered_data = [
                        [
                            [index for index, value in zip(pair[0], pair[1]) if value >= threshold],  # Filter indexes
                            [value for value in pair[1] if value >= threshold]                        # Filter values
                        ]
                        if any(value >= threshold for value in pair[1]) else [[], []]                # Check if pair has any valid values
                        for pair in self.data["peaks_P_prominence"]
                    ]

                    return filtered_data

                
                self.P_prominence_data = decode_P_prominence(inputs[2][8])
                print(self.P_prominence_data)


                piky_len = []
                for i in self.P_prominence_data:
                    piky_len.append(len(i[0]))

                
                try: 
                    self.piky_data.drop(columns=["peaks_P_prominence"], inplace=True)
                except: 
                    pass
                
                self.piky_data.insert(2, "peaks_P_prominence", piky_len)

                row_data = self.piky_data.to_dict("records")
                return row_data, stats_content, columnDefs
            else:
                return no_update, no_update, no_update





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
                delka_piky_s = self.delka_piky_s


                print(cislo_piky)
                
                # Find peak index in EKG data
                for i in range(len(self.time["ekgtime"])):
                    if self.time["peaks_time"][cislo_piky] == self.time["ekgtime"][i]:
                        break


                pik_index = i
                start = int(i-250*delka_piky_s)
                if start < 0:
                    start = 0
                end = int(i+250*delka_piky_s)
                if end > len(self.data["ekg"]):
                    end = len(self.data["ekg"])
                
                


                ekg_pik = list(self.data["ekg"][start:end])
                
                ekg_pik_cz = list(self.time["ekgtime"][start:end])
                print(len(ekg_pik))

                self.fig.add_trace(go.Scattergl(name=f"EKG Pík {cislo_piky}"), hf_x=ekg_pik_cz, hf_y=ekg_pik)
                
                self.fig.add_vline(x=self.time["peaks_time"][cislo_piky].timestamp() * 1000, line_dash="dot", line_color="red", line_width=1, annotation_text="R pík")

                print(self.time["ekgtime"][pik_index-30])
                
                if self.zobraz_cary[1] == True:
                    self.fig.add_vline(x=self.time["ekgtime"][pik_index-30].timestamp() * 1000, line_dash="dash", line_color="red", line_width=2, annotation_text="-60 ms", annotation_font_size=15) # 60 ms before peak
                    self.fig.add_vline(x=self.time["ekgtime"][pik_index+30].timestamp() * 1000, line_dash="dash", line_color="red", line_width=2, annotation_text="+60 ms", annotation_font_size=15) # 60 ms after peak

                    self.fig.add_vline(x=self.time["ekgtime"][pik_index-90].timestamp() * 1000, line_dash="dash", line_color="orange", line_width=2, annotation_text="-180 ms", annotation_font_size=15) # 180 ms before peak
                    self.fig.add_vline(x=self.time["ekgtime"][pik_index-140].timestamp() * 1000, line_dash="dash", line_color="orange", line_width=2, annotation_text="-280 ms", annotation_font_size=15) # 280 ms before peak


                    QTc_line1 = round(320 / np.sqrt(self.data["peaks_RR_avg"][cislo_piky]/1000))
                    QTc_line2 = round(450 / np.sqrt(self.data["peaks_RR_avg"][cislo_piky]/1000))

                    QTc_x1 = self.time["ekgtime"][pik_index+(int((QTc_line1)/2))].timestamp() * 1000
                    QTc_x2 = self.time["ekgtime"][pik_index+(int((QTc_line2)/2))].timestamp() * 1000

                    self.fig.add_vline(x=QTc_x1, line_dash="dash", line_color="blue", line_width=2, annotation_text=f"+{QTc_line1} ms", annotation_font_size=15) # 320 ms after peak
                    self.fig.add_vline(x=QTc_x2, line_dash="dash", line_color="blue", line_width=2, annotation_text=f"+{QTc_line2} ms", annotation_font_size=15) # 450 ms after peak

                
                #['ECG_P_Peaks', 'ECG_P_Onsets', 'ECG_P_Offsets', 'ECG_Q_Peaks', 'ECG_R_Onsets', 'ECG_R_Offsets', 'ECG_S_Peaks', 'ECG_T_Peaks', 'ECG_T_Onsets', 'ECG_T_Offsets']

                if self.zobraz_cary[0] == True:
                    for i in self.Piky_points_names:
                        if self.data[i][cislo_piky] != 0:
                            self.fig.add_vline(x=self.data[i][cislo_piky] * 1000, line_dash="dash", line_color="pink", line_width=2, annotation_text=i.replace("ECG_", ""))

                for index, i in enumerate(self.P_prominence_data[cislo_piky][0]):
                    print(i)
                    self.fig.add_vline(x=i * 1000, line_dash="dot", line_color="yellow", line_width=2, 
                                       annotation_text=f"Prom [{round(self.P_prominence_data[cislo_piky][1][index])}]", annotation_font_size=15)
                    

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

            print(ctx.triggered_id, selected_rows[0]['Číslo piku'])

            # Determine which button was clicked
            category = None
            if ctx.triggered_id == "piky_category_a":
                category = 'A'
            elif ctx.triggered_id == "piky_category_s":
                category = 'S'
            elif ctx.triggered_id == "piky_category_n":
                category = 'N'
                
            # Update the category in the selected row
            row_data[selected_rows[0]['Číslo piku'] - 1]["hodnoceni"] = category
            
            # Find the index of the selected row in the current sorted order
            cislo_piku = selected_rows[0]["Číslo piku"]
            selected_index = next((i for i, item in enumerate(virtualRowData) if item['Číslo piku'] == cislo_piku), None) # Zjisti index vybraného řádku v tabulce pomocí virtualRowData

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
                row_data[row["Číslo piku"] - 1] = row
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