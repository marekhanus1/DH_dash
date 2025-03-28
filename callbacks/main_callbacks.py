from callbacks.form_callbacks import FormCallbacks
from callbacks.vyhodnoceni_callbacks import VyhodnoceniCallbacks
from callbacks.vysledky_callbacks import VysledkyCallbacks
from callbacks.epochy_callbacks import EpochyCallbacks
from callbacks.piky_callbacks import PikyCallbacks 


from components.layout_content import layout_content
from dash import Output, Input, State, no_update

class DashCallbacks(FormCallbacks, VyhodnoceniCallbacks, VysledkyCallbacks, EpochyCallbacks, PikyCallbacks):
    def register_callbacks(self):
        self.form_callbacks()
        self.vyhodnoceni_callbacks()
        self.vysledky_callbacks()
        self.epochy_callbacks()
        self.piky_callbacks()

        
        # Callback pro větvení stránek
        @self.app.callback(
            Output('main-div', 'children'),
            Input('url', 'pathname')
        )
        
        def display_page(pathname):
            print(f"Current pathname: {pathname}")
            if self.stage_num >= 3 and self.path_name != pathname:
                    self.path_name = pathname
                    if pathname == '/':
                        return layout_content.decoding_done(self.args)
                    
                    elif pathname == '/vysledky':
                        return layout_content.chart_vysledky(self.args)
                    
                    elif pathname == '/epochy':
                        if self.args["epocha"] != None:
                            return layout_content.epochy()
                        else:
                            return layout_content.decoding_done(self.args)
                    
                    elif pathname == '/piky':
                        if self.args["pik_range"] != None:
                            return layout_content.piky()
                        else:
                            return layout_content.decoding_done(self.args)
                    
                    else:
                        return layout_content.decoding_done(self.args)

            else:
                return no_update
            
        