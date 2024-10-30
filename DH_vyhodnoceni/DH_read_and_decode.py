from datetime import datetime, timedelta, time
import sys
from scipy import signal
import os
import shutil
import numpy as np
import lzma

class ReadAndDecode:
    ################################################### READ EKG #########################################################
    ################################################### READ EKG #########################################################
    ################################################### READ EKG #########################################################
    ################################################### READ EKG #########################################################
    def read_ekg(self): 
        self.file_skip = False
        dta = []
        self.ekg_casova_znacka = []

        for cislo_souboru in range(len(self.ekg_files)):
            with open(self.ekg_files[cislo_souboru], "rb") as f:
                data = f.read() # přečti zkomprimované data EKG souboru

            print("Soubor byl přečten")

            dta_part = self.decompress_lzma(data).decode("utf-8").split(",") # dekomprimuj data souboru
            dta_part = dta_part[:-1] # poslední index je prázdný
            
            
            print(f"Počet zápisů v souboru č.{cislo_souboru+1}: {len(dta_part)}")
            print("Data dekomprimovány")

            # určení časové značky celého souboru
            ekg_casova_znacka = [float(value.split(";")[0]) for value in dta_part]
            
            start_time = datetime.strptime(self.args["date"], "%y%m%d") - timedelta(minutes=5)
            end_time = start_time+timedelta(days=1) + timedelta(minutes=5)
            # zjištění správnost dat a konverze na 
            
            ekg_casova_znacka2 = []
            for i, cas in enumerate(ekg_casova_znacka):
                if start_time <= datetime.fromtimestamp(cas) <= end_time:
                    ekg_casova_znacka2.append(cas) #ekg_casova_znacka2.append(datetime.fromtimestamp(cas))
                else: 
                    [print("ERROR V ČASOVÉ ZNAČCE") for i in range(5)]
                    print(datetime.fromtimestamp(cas))
                    dta_part = dta_part[:i]
                    break
            
            self.ekg_casova_znacka += ekg_casova_znacka2
            dta += dta_part

        print(f"Počet použitelných dat: {len(dta)}")
        print(self.ekg_casova_znacka[-1])

        # Vypočítej množství dat v datovém souboru
        mozny_pocet_minut = len(dta)/(500*60)
        self.shared_data["pocet_minut"] = mozny_pocet_minut

        print(f"Naměřený počet minut datového souboru: {mozny_pocet_minut}")
        
        # Určení, z kolika různých měření se výsledkový soubor skládá
        measurement_periods = []
        current_period_start = self.ekg_casova_znacka[0]
        current_period_end = self.ekg_casova_znacka[0]

        # Loop through the self.ekg_casova_znacka to find measurement periods
        for i in range(1, len(self.ekg_casova_znacka)):
            if (self.ekg_casova_znacka[i] - self.ekg_casova_znacka[i-1]) < 1:
                # Extend the current measurement period
                current_period_end = self.ekg_casova_znacka[i]
            else:
                # Save the current period and start a new one
                measurement_periods.append((current_period_start, current_period_end))
                current_period_start = self.ekg_casova_znacka[i]
                current_period_end = self.ekg_casova_znacka[i]

        # Append the last period
        
        measurement_periods.append((current_period_start, current_period_end))
        self.shared_data["measurement_periods"] = measurement_periods


        # nastavení rozmezí vyhodnocení podle časové značky
        if(self.args["range"] != None):
            start_file_ekg, end_file_ekg = self.get_time_range(self.ekg_casova_znacka)
            if self.file_skip == True:
                return
            

            dta = dta[start_file_ekg:end_file_ekg]
            self.ekg_casova_znacka = self.ekg_casova_znacka[start_file_ekg:end_file_ekg]

            self.pocet_minut = int(len(dta)/(500*60))

            print(f"POCET MINUT {self.pocet_minut}")
        
        else:
            self.pocet_minut = int(mozny_pocet_minut)
        
        self.pocet_souboru = int(self.pocet_minut/5)

        print("Vytvoření datových proměnných")
        self.ekg_values_raw = np.array([int(value.split(";")[1]) for value in dta])
        self.ekg_values = self.ekg_values_raw
        
        # EKG FILTRY
        if self.args["vrubovy"] != None:
            b, a = signal.iirnotch(self.args["vrubovy"], 50, fs=500)  # notch filter
            self.ekg_values = list(signal.filtfilt(b, a, self.ekg_values))

        if self.args["butterworth"] != None:
            sos = signal.butter(4, self.args["butterworth"], btype="highpass", fs=500, output="sos")  # Butterworth filter
            self.ekg_values = list(signal.sosfiltfilt(sos, self.ekg_values))


    ################################################### READ FLEX #########################################################
    ################################################### READ FLEX #########################################################
    ################################################### READ FLEX #########################################################
    ################################################### READ FLEX #########################################################
    def read_flex(self):
        dta = []
        self.flex_casova_znacka = []

        for cislo_souboru in range(len(self.flex_files)):
            with open(self.flex_files[cislo_souboru], "rb") as f:
                data = f.read()

            dta_part = self.decompress_lzma(data).decode("utf-8").split(",") # dekomprimuj data souboru
            dta_part = dta_part[:-1] # poslední index je prázdný

            # nastavení rozmezí vyhodnocení podle časové značky
            flex_casova_znacka = [float(value.split(";")[0]) for value in dta_part]
            print(len(flex_casova_znacka))
            flex_casova_znacka2 = []
            start_time = datetime.strptime(self.args["date"], "%y%m%d") - timedelta(minutes=5)
            end_time = start_time+timedelta(days=1) + timedelta(minutes=5)
            for i, cas in enumerate(flex_casova_znacka):
                if start_time <= datetime.fromtimestamp(cas) <= end_time:
                    flex_casova_znacka2.append(cas) # datetime.fromtimestamp(cas)
                else: 
                    [print("ERROR V ČASOVÉ ZNAČCE FLEX") for i in range(5)]
                    dta_part = dta_part[:i]
                    break
            
            
            dta += dta_part
            self.flex_casova_znacka += flex_casova_znacka2
        
        print("Datový soubor přečten")

        if(self.args["range"] != None):
            start_file_flex, end_file_flex = self.get_time_range(self.flex_casova_znacka)
            dta = dta[start_file_flex:end_file_flex]
            self.flex_casova_znacka = self.flex_casova_znacka[start_file_flex:end_file_flex]

        self.flex_values = [int(value.split(";")[1]) for value in dta]
        
        self.flex_values_raw = self.flex_values

        if self.args["flexbutter"] != None:
            sos = signal.butter(4, self.args["flexbutter"], btype="lowpass", fs=49, output="sos")  # Butterworth filter
            self.flex_values = signal.sosfiltfilt(sos, self.flex_values)
        
        print("Filtry nastaveny")


        self.flex_derivace = []
        for i in range(1, len(self.flex_values)):
            self.flex_derivace.append(self.flex_values[i] - self.flex_values[i-1])
        
        self.flex_peaks, _ = signal.find_peaks(self.flex_values, prominence=self.args["flexprom"], distance=30)
        self.flex_diff = np.diff(self.flex_peaks)

        print("Flex konec")





    def get_time_range(self, data): # NAJDI ČASOVÝ ÚSEK PRO VYHODNOCENÍ
        start_time_str, end_time_str = self.args["range"].split('-')
        start_time = time.fromisoformat(start_time_str)
        end_time = time.fromisoformat(end_time_str)

        


        start_index = None
        end_index = None

        for i, dt in enumerate(data):
            if start_time <= datetime.fromtimestamp(dt).time() <= end_time:
                if start_index is None:
                    start_index = i
                end_index = i
        print(start_index, end_index)
        if start_index is not None and end_index is not None:
            return start_index, end_index
        else:
            print("Error určení rozmezí souboru")
            # Časové rozmezí se nenachází v tomto souboru => přesuň se na další soubor
            self.file_skip = True
            
            return None, None


    def export_EKG(self):
        # Vytvoř výsledkové soubory pro EKG ANALYTIK
        try:
            shutil.rmtree(self.filename)
        except:
            print("slozka neexistuje")

        os.mkdir(self.filename)
        for i in range(self.pocet_souboru):
            with open(self.filename+"/"+self.filename+"_"+str(i+1)+'.holter', 'w+') as outfile:
                outfile.write('\n'.join(str(i) for i in self.ekg_values_raw[i*(60*5*500):i*(60*5*500)+(60*5*500)]))

    
    def decompress_lzma(self, data):
        # Dekomprese souboru, i když je nedokončený 
        # https://stackoverflow.com/questions/37400583/python-lzma-compressed-data-ended-before-the-end-of-stream-marker-was-reached
        results = []
        while True:
            decomp = lzma.LZMADecompressor(lzma.FORMAT_AUTO, None, None)
            try:
                res = decomp.decompress(data)
            except lzma.LZMAError:
                if results:
                    break  # Leftover data is not a valid LZMA/XZ stream; ignore it.
                else:
                    raise  # Error on the first iteration; bail out.
                
                
            results.append(res)
            data = decomp.unused_data
            if not data:
                break
            if not decomp.eof:
                raise lzma.LZMAError("Compressed data ended before the end-of-stream marker was reached")
        return b"".join(results)