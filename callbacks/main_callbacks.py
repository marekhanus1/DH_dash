from dash import Output, Input, State, no_update, callback_context


from components.utils import Utils
from components.layout_content import layout_content
from components.vysledky_chart_content import data_names, time_names
from components.epochy_content import columnDefs

import multiprocessing

from plotly.subplots import make_subplots
import plotly.graph_objects as go

import pandas as pd
import dash_mantine_components as dmc

class DashCallbacks(Utils):
    def register_callbacks(self):
        ##################################### FORM ##################################### 
        ##################################### FORM ##################################### 
        ##################################### FORM ##################################### 
        @self.app.callback(
            [Output(component_id, 'darkHidden') for component_id in ['arg_butter', 'arg_vrub', 'arg_butterflex']] +
            [Output('time_range_div', 'hidden')],
            [Input(switch_id, 'checked') for switch_id in ['butter_switch', 'vrub_switch', 'butterflex_switch', 'range_switch']]
        )
        def toggle_visibility(*switches):
            return [not switch for switch in switches]

        @self.app.callback(Output("datum_div", "children"),Output("chbox_SSH", "checked"), Input("datum_radio", "value"))
        def date_input_callback(value):

            date_content = self.choose_date_input(value, self.disable_components)

            if date_content == None:
                return no_update
            else:
                if value == "normal":
                    return date_content, False
                else:
                    return date_content, True

    

        @self.app.callback(
            Output('output-time-range', 'children'),
            [Input('time-range-slider', 'value')]
        )
        def update_output_time_range(value):
            start_time = self.minutes_to_time(value[0])
            end_time = self.minutes_to_time(value[1])
            return f"Selected Time Range: {start_time} - {end_time}"

        @self.app.callback(
            Output('main-div', 'children', allow_duplicate=True),
            Input('submit-button', 'n_clicks'),
            
            [State(switch_id, 'checked') for switch_id in ['range_switch', 'vrub_switch', 'butter_switch', 'butterflex_switch']]+ # Switche určující platnost argumentů
            [State('datum_input', 'value'), State('chbox_SSH', 'checked'), State('time-range-slider', 'value')]+ # Soubory
            [State('arg_limit', 'value'), State('arg_vrub', 'value'), State('arg_butter', 'value'), State('arg_flexprom', 'value'), State('arg_butterflex', 'value')]+ # filtry a limity
            [State('chbox_export', 'checked')]+
            [State('epoch_delka', 'value')],
            #[State('epochy_RRmin', 'checked'), State('epochy_RRmax', 'checked'),State('epochy_SDNN', 'checked'), State('epochy_RMSSD', 'checked')],
            
            prevent_initial_call=True
        )
        def update_output(*inputs):
            if inputs[0] > 0:
                                      #    0        1        2          3         4         5       6       
                inputs = list(inputs) # n_clicks rangeSW, butterSW, vrubSW, flexbutterSW, date,    ssh, 
                                      #     7        8        9          10         11          12
                                      # range_val, limit, butter_val, vrub_val, frex_prom, flexbutter_val
                                      #   
                                      # export,    epoch_delka
                date_index = 5
                range_index = 7

                if len(inputs[date_index]) > 6:
                    inputs[date_index] = inputs[date_index][2:].replace("-", "") # Nastav formát datumu

                config_names = ["rangeSW", "vrub_SW", "butter_SW", "flexbutter_sw",
                                "date", "ssh", "rangeMax", "rangeMin", 
                                "pik_limit", "butter_val", "vrub_val", "flex_prom", "flexbutter_val",
                                "exportEKG", "epoch_delka"]
                
                config = Utils.read_config()
                
                
                index_push = 0
                for i in range(len(config_names)-1):
                    if i == range_index-1: # TIME RANGE
                        if inputs[i+index_push] != None:
                            config[config_names[i]] = inputs[range_index][1]
                            config[config_names[i+1]] = inputs[range_index][0]
                        
                        index_push = 1

                    else:
                        if(inputs[i+1] != None):
                            config[config_names[i+index_push]] = inputs[i+1]



                self.write_config(config)


                # Hodnoty time_range, arg_butterworth, arg_vrub, arg_butterflex a epochy jsou neplatné jestli jejich switch není kladný
                indexy_neplatnych_hodnot = [range_index, 9, 10, 12]
                

                for i, index in enumerate(indexy_neplatnych_hodnot):
                    if inputs[i+1] != True:
                        inputs[index] = None


                

                if inputs[range_index] != None:
                    start_time = self.minutes_to_time(inputs[range_index][0])
                    end_time = self.minutes_to_time(inputs[range_index][1])
                    inputs[range_index] = f"{start_time}-{end_time}"
                #print(inputs)



                # Vytvoř spouštěcí argumenty pro vyhodnocovací program
                arg_names = ["date", "ssh", "range",
                    "limit", "vrubovy", "butterworth", "flexprom", "flexbutter",
                    "export",
                    "epocha"]
                
                self.create_args(arg_names) # Nastav hodnoty všech argumentů na None

                for i, name in enumerate(arg_names):
                    self.args[name] = inputs[i+5]

                print(self.args)
                self.process = multiprocessing.Process(target=self.decode_holter.main, args=(self.args,)) # Spusť vyhodnocovací program přes Multiprocessing
                self.process.start()
                self.disable_components = True

                return layout_content.after_start()
            
            return no_update

        ##################################### VYHODNOCENI ##################################### 
        ##################################### VYHODNOCENI ##################################### 
        ##################################### VYHODNOCENI ##################################### 
        @self.app.callback(
            #[Output('output-div', 'children'), ],
            
            Output('main-div', 'children', allow_duplicate=True),
            Input('reset-button', 'n_clicks'),
            prevent_initial_call=True
        )
        def reset_vyhodnoceni(n_clicks):
            if n_clicks > 0:
                # Vynuluj proces
                print(self.process.is_alive())
                if self.process.is_alive():
                    self.process.terminate()
                    self.process.join()
                
                self.disable_components = False

                return layout_content.before_start()
            
            return no_update

        

        @self.app.callback(
            #[Output('output-div', 'children'), ],
            
            [Output('stage-store', 'data'), Output('my-interval', 'disabled'), Output("vyhodnoceni_progress", "children"), Output("fileinfo_div", "children")],
            Input('my-interval', 'n_intervals'),
            prevent_initial_call=True, 
            suppress_callback_exceptions=True
            
        )
        def interval_callback(n_clcik):
            progressbar_content = self.handle_progressbar()
            infodiv_content = self.handle_info()


            if self.shared_data["stage"] == 999:
                stage_id = 3
                disable_interval = True
            else:
                stage_id = 2
                disable_interval = False
                
            return stage_id, disable_interval, progressbar_content, infodiv_content
            


        @self.app.callback(
            Output('main-div', 'children', allow_duplicate=True),
            [Input('stage-store', 'data')],
            prevent_initial_call=True
        )

        def update_layout(stage):
            # Return the layout corresponding to the current stage
            if self.stage_num != stage and stage != None:
                interval_disabled = True
                print("SOM? TU")
                self.stage_num = stage
                if stage >= 3:
                    print("START")
                    self.hdf5_filename = "DH_data.h5"
                    
                    
                    
                    self.data, self.time = self.read_hdf5_data(data_names, time_names)

                    self.epochy_data = pd.DataFrame({k: self.data[k] for k in data_names[2]})
                    cas_epochy = [i.strftime("%H:%M:%S") for i in self.time["epochy_time"]]
                    self.epochy_data.insert(0, "Čas epochy", cas_epochy)
                    self.epochy_data.insert(0, "Číslo epochy", range(1, len(self.epochy_data) + 1))
                    
                    return layout_content.decoding_done()
                    
                else:
                    return no_update
            else:
                return no_update
        

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
                                        )
                                    )

                
                return self.fig
            else:
                return no_update