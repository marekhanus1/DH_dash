from dash import Dash
from components.layout import create_layout
from components.utils import Utils
from callbacks.main_callbacks import DashCallbacks
from dash import _dash_renderer

from DH_vyhodnoceni.DH_main import DecodeHolter
import dash_mantine_components as dmc

import multiprocessing

from plotly_resampler import FigureResampler
from plotly.subplots import make_subplots

_dash_renderer._set_react_version("18.2.0")
#register_plotly_resampler(mode='auto')


class DashMain(DashCallbacks):
    def __init__(self):
        self.app = Dash(__name__, external_stylesheets=dmc.styles.ALL, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=2"},])
        self.app.config.suppress_callback_exceptions = True

        
        manager = multiprocessing.Manager()
        self.shared_data = manager.dict()
        self.decode_holter = DecodeHolter(self.shared_data)

        self.stage_num = 0
        self.path_name = ""
        
        # Init Plotly Resampler 
        self.fig = FigureResampler(
            make_subplots(specs=[[{"secondary_y": True}]]),
            default_n_shown_samples=1_000,
            verbose=False,
        )

        self.config_file = 'components/DH_config.json'
        self.disable_components = False
        
        # Set layout
        self.app.layout = create_layout()
        
        # Register callbacks
        self.register_callbacks()

        self.fig.register_update_graph_callback(app=self.app, graph_id="graph-id")
        self.fig.register_update_graph_callback(app=self.app, graph_id="epochy_graph")


        if __name__ == '__main__':
            self.app.run_server(debug=True, port=5001) #,dev_tools_ui=False,dev_tools_props_check=False

DashMain()


# TODO
# POHYB V TABULCE JE K HOVNU - done!!!!!
# Zvětšit labely v grafu - done
# Přidat funkci zobrazit poslední měření - done, junky
# Pík analyzér
    # Přidat do nastavení pík analyzér - range slider a switch - done
    # Přidat do nastavení možnost zapnutí/vypnutí pík analyzéru a epoch analyzéru - done
    #   - Když jsou vypnuté, změnit zobrazení karet - done


