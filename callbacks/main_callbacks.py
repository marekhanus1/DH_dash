from callbacks.form_callbacks import FormCallbacks
from callbacks.vyhodnoceni_callbacks import VyhodnoceniCallbacks
from callbacks.vysledky_callbacks import VysledkyCallbacks
from callbacks.epochy_callbacks import EpochyCallbacks

class DashCallbacks(FormCallbacks, VyhodnoceniCallbacks, VysledkyCallbacks, EpochyCallbacks):
    def register_callbacks(self):
        self.form_callbacks()
        self.vyhodnoceni_callbacks()
        self.vysledky_callbacks()
        self.epochy_callbacks()
        
            
        