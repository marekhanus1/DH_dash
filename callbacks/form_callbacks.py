from dash import Output, Input, State, no_update, callback_context
from components.layout_content import layout_content
import multiprocessing

from components.utils import Utils


class FormCallbacks(Utils):
    def form_callbacks(self):
        ##################################### FORM ##################################### 
        ##################################### FORM ##################################### 
        ##################################### FORM ##################################### 


        @self.app.callback(
            [Output(component_id, 'darkHidden') for component_id in ['arg_butter', 'arg_vrub', 'arg_butterflex', 'epoch_delka']] +
            [Output('time_range_div', 'hidden'), Output('pik_time_range_div', 'hidden')],
            [Input(switch_id, 'checked') for switch_id in ['butter_switch', 'vrub_switch', 'butterflex_switch', "epoch_switch", 'range_switch', "pik_switch"]]
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
            Output('main-div', 'children', allow_duplicate=True),
            Input('submit-button', 'n_clicks'),Input('posledni_vyhodnoceni_button', 'n_clicks'),
            
            [State(switch_id, 'checked') for switch_id in ['range_switch', 'vrub_switch', 'butter_switch', 'butterflex_switch']]+ # Switche určující platnost argumentů
            [State('datum_input', 'value'), State('chbox_SSH', 'checked'), State('time-range-slider', 'value')]+ # Soubory
            [State('arg_limit', 'value'), State('arg_vrub', 'value'), State('arg_butter', 'value'), State('arg_flexprom', 'value'), State('arg_butterflex', 'value')]+ # filtry a limity
            [State('chbox_export', 'checked')]+
            [State('epoch_delka', 'value'),  State('pik_time-range-slider', 'value'), State('epoch_switch', 'checked'),  State('pik_switch', 'checked')], # epochy a píky
            #[State('epochy_RRmin', 'checked'), State('epochy_RRmax', 'checked'),State('epochy_SDNN', 'checked'), State('epochy_RMSSD', 'checked')],
            
            prevent_initial_call=True
        )
        def update_output(*inputs):
            if inputs[0] > 0 or inputs[1] > 0:
                print(callback_context.triggered[0]["prop_id"])
                print(inputs)

                print(len(inputs))
                                      #    0        1        2          3         4         5       6       
                inputs = list(inputs) # n_clicks rangeSW, butterSW, vrubSW, flexbutterSW, date,    ssh, 
                                      #     7        8        9          10         11          12
                                      # range_val, limit, butter_val, vrub_val, frex_prom, flexbutter_val
                                      #   13        14        15         16             17         
                                      # export,  epoch_delka pik_range, epoch_switch, pik_switch
                # definice indexů
                date_index = 6
                range_index = 8
                pik_range_index = 16
                
                butter_index = 10
                vrub_index = 11
                butterflex_index = 13
                
                if callback_context.triggered[0]["prop_id"] == "submit-button.n_clicks":
                    if len(inputs[date_index]) > 6:
                        inputs[date_index] = inputs[date_index][2:].replace("-", "") # Nastav formát datumu

                    config_names = ["rangeSW", "vrub_SW", "butter_SW", "flexbutter_sw",
                                    "date", "ssh", "rangeMax", "rangeMin", 
                                    "pik_limit", "butter_val", "vrub_val", "flex_prom", "flexbutter_val",
                                    "exportEKG", "epoch_delka",  "pik_rangeMax", "pik_rangeMin", "epoch_switch" , "pik_switch"]
                    
                    config = Utils.read_config()
                    
                    
                    index_push = 0
                    for i in range(len(config_names)-2):
                        if i == range_index-2 or i == pik_range_index-2: # TIME RANGE
                            if inputs[i+index_push] != None:
                                print(config_names[i+index_push])
                                print(inputs[i+2])
                                config[config_names[i+index_push]] = inputs[i+2][1]
                                config[config_names[i+index_push+1]] = inputs[i+2][0]
                            
                            index_push += 1

                        else:
                            if(inputs[i+2] != None):
                                config[config_names[i+index_push]] = inputs[i+2]



                    self.write_config(config)


                # Hodnoty time_range, arg_butterworth, arg_vrub, arg_butterflex a epochy jsou neplatné jestli jejich switch není kladný
                indexy_neplatnych_hodnot = [range_index, butter_index, vrub_index, butterflex_index]

                for i, index in enumerate(indexy_neplatnych_hodnot):
                    if inputs[i+2] != True:
                        inputs[index] = None

                if inputs[pik_range_index+1] != True:
                    inputs[pik_range_index-1] = None
                
                if inputs[pik_range_index+2] != True:
                    inputs[pik_range_index] = None
                
                for i in [range_index, pik_range_index]:
                    if inputs[i] != None:
                        start_time = self.minutes_to_time(inputs[i][0])
                        end_time = self.minutes_to_time(inputs[i][1])
                        inputs[i] = f"{start_time}-{end_time}"



                # Vytvoř spouštěcí argumenty pro vyhodnocovací program
                arg_names = ["date", "ssh", "range",
                    "limit", "vrubovy", "butterworth", "flexprom", "flexbutter",
                    "export",
                    "epocha", "pik_range"]
                
                self.create_args(arg_names) # Nastav hodnoty všech argumentů na None

                for i, name in enumerate(arg_names):
                    self.args[name] = inputs[i+6]

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