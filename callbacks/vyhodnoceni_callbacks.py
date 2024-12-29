from dash import Output, Input, State, no_update
from components.utils import Utils
from components.layout_content import layout_content


import pandas as pd
import numpy as np

class VyhodnoceniCallbacks(Utils):
    def vyhodnoceni_callbacks(self):

        self.folder_names = ["EKG", "FLEX", "HR A RESP", "EPOCHY"]
        self.HR_names = np.array(["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDer"], dtype=object)
        self.Piky_names = np.array(["peaks_P", "peaks_PR", "peaks_QRS", "peaks_QTc", "peaks_FlexDer"], dtype=object)
        self.Piky_points_names = np.array(['ECG_P_Peaks', 'ECG_P_Onsets', 'ECG_P_Offsets', 'ECG_Q_Peaks', 'ECG_R_Onsets', 'ECG_R_Offsets', 'ECG_S_Peaks', 'ECG_T_Peaks', 'ECG_T_Onsets', 'ECG_T_Offsets'], dtype=object)


        self.data_names = np.array([["ekg", "ekgraw"],
                                    ["flex", "flexraw"],                             
                                    ["HR", "RESP"]], dtype=object)
        self.time_names = ["ekgtime", "flextime", "HR_RESP_time"]

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
                try:
                    print(self.process.is_alive())
                    if self.process.is_alive():
                        self.process.terminate()
                        self.process.join()
                except:
                    print("Process does not exist")

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
                    
                    
                    
                   
                    if self.args["epocha"] != None:
                        self.data_names = np.array([["ekg", "ekgraw"],
                                ["flex", "flexraw"], 
                                ["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDer"],                            
                                ["HR", "RESP"]], dtype=object)
                                                        #np.array(self.data_names.tolist() + [self.HR_names.tolist()], dtype=object)
                        self.time_names = ["ekgtime", "flextime", "epochy_time", "HR_RESP_time"]
                    
                    
                    data_names = self.data_names
                    time_names = self.time_names

                    

                    if self.args["pik_range"] != None:
                        Piky_points_names = np.append(self.Piky_points_names, "peaks_P_prominence")
                        data_names = np.array(data_names.tolist() + [self.Piky_names.tolist()]+ [Piky_points_names.tolist()], dtype=object)
                        time_names = np.array(time_names + ["peaks_time"], dtype=object)

                    

                    print(data_names, time_names)
                    self.data, self.time = self.read_hdf5_data(data_names, time_names)
                    if self.args["epocha"] != None:
                        self.epochy_data = pd.DataFrame({k: self.data[k] for k in self.HR_names})
                        cas_epochy = [i.strftime("%H:%M:%S") for i in self.time["epochy_time"]]
                        self.epochy_data.insert(0, "Čas epochy", cas_epochy)
                        self.epochy_data.insert(0, "Číslo epochy", range(1, len(self.epochy_data) + 1))
                    
                    if self.args["pik_range"] != None:
                        self.piky_data = pd.DataFrame({k: self.data[k] for k in self.Piky_names})
                        print(self.piky_data)
                        cas_piky = [i.strftime("%H:%M:%S")+ f".{i.microsecond // 100000}" for i in self.time["peaks_time"]]

                        self.data["peaks_P_prominence"] = [[item for item in sublist if item != 0] for sublist in self.data["peaks_P_prominence"]]


                        pocet_P_piku = [len(i) for i in self.data["peaks_P_prominence"]]
                        self.piky_data.insert(0, "peaks_P_prominence", pocet_P_piku)

                        self.piky_data.insert(0, "Čas piku", cas_piky)
                        self.piky_data.insert(0, "Číslo piku", range(1, len(self.piky_data) + 1))

                    return layout_content.decoding_done(self.args)
                    
                else:
                    return no_update
            else:
                return no_update
            

        @self.app.callback(
        #[Output('output-div', 'children'), ],
        
        [Output('my-interval2', 'disabled'), Output("fileinfo_div", "children", allow_duplicate=True)],
        Input('my-interval2', 'n_intervals'),
        prevent_initial_call=True, 
        suppress_callback_exceptions=True
            
        )
        def interval_callback(n_clcik):
            infodiv_content = self.handle_info()

                
            return True, infodiv_content