from callbacks.form_callbacks import FormCallbacks
from callbacks.vyhodnoceni_callbacks import VyhodnoceniCallbacks
from callbacks.vysledky_callbacks import VysledkyCallbacks
from callbacks.epochy_callbacks import EpochyCallbacks

from components.layout_content import layout_content
from dash import Output, Input, State, no_update

class DashCallbacks(FormCallbacks, VyhodnoceniCallbacks, VysledkyCallbacks, EpochyCallbacks):
    def register_callbacks(self):
        self.form_callbacks()
        self.vyhodnoceni_callbacks()
        self.vysledky_callbacks()
        self.epochy_callbacks()
        
        # Callback pro větvení stránek
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
                        return layout_content.decoding_done(self.args)
                    
                    elif pathname == '/vysledky':
                        return layout_content.chart_vysledky(self.args)
                    
                    elif pathname == '/epochy':
                        if self.args["epocha"] == True:
                            return layout_content.epochy()
                        else:
                            return layout_content.decoding_done(self.args)
                    
                    elif pathname == '/piky':
                        if self.args["piky"] == True:
                            return layout_content.epochy()
                        else:
                            return layout_content.decoding_done(self.args)
                    
                    else:
                        return layout_content.decoding_done(self.args)

            else:
                return no_update
            
        