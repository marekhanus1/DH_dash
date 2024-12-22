# INICIALIZACE KNIHOVEN
import os
import sys
import glob
import h5py

# INICIALIZACE VEDLEJŠÍCH SOUBOURŮ
from DH_vyhodnoceni.DH_read_and_decode import ReadAndDecode
from DH_vyhodnoceni.DH_analyseHR import AnalyseHR
from DH_vyhodnoceni.DH_analysePeaks import AnalysePeaks
import DH_vyhodnoceni.download_files as download_files

class DecodeHolter(ReadAndDecode, AnalyseHR, AnalysePeaks):
    def __init__(self, shared_data):
        self.shared_data = shared_data


    def main(self, args):
        self.args = args
        self.filename = "Holter_" + self.args["date"] # ČASOVÁ ZNAČKA VÝSLEDKOVÝCH SOUBORŮ
        
        self.vzorkovaci_frekvence = 500 # VZORKOVACÍ FREKVENCE
        
        
        if(self.args["ssh"] == True): # STÁHNI SOUBORY Z RPi
            download_files.download_files(self.filename)
            
        
        # Build the search pattern
        search_pattern = os.path.join("holter_vysledky/", self.filename + "*")

        # Get all files that match the search pattern
        matching_files = glob.glob(search_pattern)

        self.shared_data["pocet_souboru"] = len(matching_files)
        
        # ROZDĚL SOUBORY NA EKG A FLEX
        self.ekg_files = []
        self.flex_files = []

        for i in matching_files:
            if i.endswith(".ekg"):
                self.ekg_files.append(i) 
            elif i.endswith(".flex"):
                self.flex_files.append(i)

        self.ekg_files = sorted(self.ekg_files)
        self.flex_files = sorted(self.flex_files)
        print(self.ekg_files, self.flex_files)

            
        # VYHODNOCENÍ
        print("")
        self.shared_data["stage"] = 1 # Fáze jedna - začátek vyhodnocení -> čtení EKG souborů

        print("EKG READ...")
        self.read_ekg()
        self.shared_data["stage"] = 2 # Fáze dva - EKG přečteno

        if(self.args["export"] == True):
            print("EXPORT DATA TO EKG ANALYTIK...")
            self.export_EKG()
        
        print("FLEX READ...")
        self.read_flex()
        self.shared_data["stage"] = 3 # Fáze tři - FLEX přečten

        print("ANALYZE EPOCHS...")
        if self.args["epocha"] != None:
            self.analyze_epochs() 

        self.shared_data["stage"] = 4 # Fáze čtyři - analýza epoch dokončena

        
        print("ANALYZE HR...")
        self.analyze_HR()
        self.shared_data["stage"] = 5 # Fáze pět - analýza HR dokončena

        print("ANALYZE PEAKS...")
        #self.peak_analysis()
        self.shared_data["stage"] = 6 # Fáze šest - analýza píků dokončena
        
        # Ulož data do paměti pro web
        print("SAVE DATA...")
        with h5py.File("DH_data.h5", 'w') as f:
            # EKG hodnoty 
            f.create_dataset("ekg", data=self.ekg_values, compression="gzip")
            f.create_dataset("ekgraw", data=self.ekg_values_raw, compression="gzip")
            f.create_dataset("ekgtime", data=self.ekg_casova_znacka, compression="gzip")

            # FLEX HODNOTY
            f.create_dataset("flex", data=self.flex_values, compression="gzip")
            f.create_dataset("flexraw", data=self.flex_values_raw, compression="gzip")
            f.create_dataset("flextime", data=self.flex_casova_znacka, compression="gzip")
            f.create_dataset("flexderivace", data=self.flex_derivace, compression="gzip")
            f.create_dataset("flexpeaks", data=self.flex_peaks, compression="gzip")
            f.create_dataset("flexdiff", data=self.flex_diff, compression="gzip")

            # EPOCHY
            if self.args["epocha"] != None:
                f.create_dataset("epochy_HR",     data=self.epoch_stats["HR"],     compression="gzip")
                f.create_dataset("epochy_RESP",   data=self.epoch_stats["RESP"],   compression="gzip")
                f.create_dataset("epochy_RR-min", data=self.epoch_stats["RR-min"], compression="gzip")
                f.create_dataset("epochy_RR-max", data=self.epoch_stats["RR-max"], compression="gzip")
                f.create_dataset("epochy_SDNN",   data=self.epoch_stats["SDNN"],   compression="gzip")
                f.create_dataset("epochy_RMSSD",  data=self.epoch_stats["RMSSD"],  compression="gzip")
                f.create_dataset("epochy_FlexDer",  data=self.epoch_stats["FlexDer"],  compression="gzip")
                f.create_dataset("epochy_time",   data=self.epoch_stats["time"],   compression="gzip")


            # HR ANALÝZA
            f.create_dataset("HR", data=self.avg_HR_RESP["HR"], compression="gzip")
            f.create_dataset("RESP", data=self.avg_HR_RESP["RESP"], compression="gzip")
            f.create_dataset("HR_RESP_time", data=self.avg_HR_RESP["time"], compression="gzip")

            
        print("Done.")
        self.shared_data["stage"] = 999 # konec programu

