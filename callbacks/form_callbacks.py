from dash import Output, Input, State, no_update, callback_context, ALL
from components.layout_content import layout_content
import multiprocessing

from components.utils import Utils


class FormCallbacks(Utils):
    def form_callbacks(self):
        ##################################### FORM ##################################### 
        ##################################### FORM ##################################### 
        ##################################### FORM ##################################### 


        @self.app.callback(
            [Output('time_range_div', 'hidden')]+
            [Output({"type": "nastaveni_inputSW","index":component_id}, 'darkHidden') for component_id in ['arg_butter', 'arg_vrub', 'arg_butterflex', 'epoch_delka']] +
            [Output('pik_time_range_div', 'hidden')],

            
            Input({"type": "nastaveni_switch", "index": ALL}, "checked"),
        )
        def toggle_visibility(*switches):
            return [not switch for switch in switches[0]]

        @self.app.callback(Output("datum_div", "children"),Output({"type": "nastaveni_checkbox","index":"chbox_SSH"}, "checked"), Input("datum_radio", "value"))
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
            return f"Časové rozmezí vyhodnocení souboru: {start_time} - {end_time}"
        
        @self.app.callback(
            Output('pik_output-time-range', 'children'),
            [Input('pik_time-range-slider', 'value')]
        )
        def update_output_time_range(value):
            start_time = self.minutes_to_time(value[0])
            end_time = self.minutes_to_time(value[1])
            return f"Časové rozmezí vyhodnocení píků: {start_time} - {end_time}"

        
        @self.app.callback(
            Output('posledni_vyhodnoceni_button', 'disabled'),
            Input({"type": "nastaveni_switch", "index": ALL}, "checked"),
            Input({"type": "nastaveni_input", "index": ALL}, "value"),
            Input({"type": "nastaveni_checkbox", "index": ALL}, "checked"),
            Input({"type": "nastaveni_inputSW", "index": ALL}, "value"),
        )
        def disable_posledni_mereni(*inputs):
            config = Utils.read_config()
            config_names = ["rangeSW",  "butter_SW", "vrub_SW", "flexbutter_sw", "epoch_switch" , "pik_switch",
                                    "date", "pik_limit", "flex_prom", 
                                    "ssh", "exportEKG", 
                                    "rangeMax", "rangeMin", "butter_val", "vrub_val",  "flexbutter_val", "epoch_delka",  "pik_rangeStart", "pik_rangeEnd"]
            index = 0
            for i in inputs:
                for j in i:
                    if type(j) == list:
                        if config[config_names[index]] != j[1]:
                            return True
                        index+=1
                        if config[config_names[index]] != j[0]:
                            return True
                        
                    else:
                        if j != None:
                            if config[config_names[index]] != j:
                                return True
                    index+=1

            return False

        @self.app.callback(
            Output('main-div', 'children', allow_duplicate=True),
            [Input('submit-button', 'n_clicks'),Input('posledni_vyhodnoceni_button', 'n_clicks')],
            
            State({"type": "nastaveni_switch", "index": ALL}, "checked"),
            State({"type": "nastaveni_input", "index": ALL}, "value"),
            State({"type": "nastaveni_checkbox", "index": ALL}, "checked"),
            State({"type": "nastaveni_inputSW", "index": ALL}, "value"),
            
            prevent_initial_call=True
        )
        def update_output(*inputs):
            if inputs[0] > 0 or inputs[1] > 0:
                print(callback_context.triggered[0]["prop_id"])
                

                # (n_clicks, n_clicks2 , [rangeSW, butterSW, vrubSW, flexbutterSW, epochySW, pikySW], [date, limit, flex_prom], [ssh, export], [range_val, butter_val, vrub_val, flexbutter_val, epoch_delka, pik_rangeStart, pik_rangeStop])
                
                inputs = inputs[2:]
                
                
                if callback_context.triggered[0]["prop_id"] == "submit-button.n_clicks":
                    if len(inputs[1][0]) > 6:
                        inputs[1][0] = inputs[1][0][2:].replace("-", "") # Nastav formát datumu

                    config_names = ["rangeSW",  "butter_SW", "vrub_SW", "flexbutter_sw", "epoch_switch" , "pik_switch",
                                    "date", "pik_limit", "flex_prom", 
                                    "ssh", "exportEKG", 
                                    "rangeMax", "rangeMin", "butter_val", "vrub_val",  "flexbutter_val", "epoch_delka",  "pik_rangeStart", "pik_rangeEnd"]
                    
                    config = Utils.read_config()
                    
                    index = 0
                    for i in inputs:
                        for j in i:
                            if type(j) == list:
                                config[config_names[index]] = j[1]
                                index+=1
                                config[config_names[index]] = j[0]
                                
                            else:
                                if j != None:
                                    config[config_names[index]] = j
                            index+=1

                    self.write_config(config)

                
                for index, i in enumerate(inputs[3]):
                    if type(i) == list:
                        start_time = self.minutes_to_time(i[0])
                        end_time = self.minutes_to_time(i[1])
                        inputs[3][index] = f"{start_time}-{end_time}"

                print(inputs)
                inputs[3][-2] = f"{inputs[3][-2]}-{inputs[3][-1]}"
                
                inputs = list(inputs)
                inputs[-1] = inputs[-1][:-1]

                print(inputs)
                for index, i in enumerate(inputs[0]):
                    if i != True:
                        inputs[3][index] = None

                print(inputs[1:])
                inputs = inputs[1:]

                # Vytvoř spouštěcí argumenty pro vyhodnocovací program
                arg_names = ["date", "limit", "flexprom",
                             "ssh", "export",
                             "range", "butterworth", "vrubovy", "flexbutter", "epocha", "pik_range"]
                
                self.create_args(arg_names) # Nastav hodnoty všech argumentů na None

                index = 0
                for i in inputs:
                    for j in i:
                        self.args[arg_names[index]] = j
                        index+=1

                print(self.args)



                if callback_context.triggered[0]["prop_id"] == "submit-button.n_clicks":
                    self.process = multiprocessing.Process(target=self.decode_holter.main, args=(self.args,)) # Spusť vyhodnocovací program přes Multiprocessing
                    self.process.start()
                    self.disable_components = True

                    return layout_content.after_start()
                else:
                    self.shared_data["stage"] = 999
                    return layout_content.after_start()
              
            return no_update