from scipy import signal
import numpy as np
import openpyxl

class AnalyseHR:
    def analyze_HR(self):
        
        self.avg_HR_RESP = {
            "time": [],
            "HR": [],
            "RESP": []
        }
        
        print(len(self.flex_values), len(self.flex_casova_znacka))
        for i in range(self.pocet_minut*60-5):
            ekg_sekunda = self.ekg_values[i*500:i*500+500*5]
            ekg_sekunda_CZ = self.ekg_casova_znacka[i*500:i*500+500*5]

            flex_sekunda = self.flex_values[i*49:i*49+(49*60)]
            flex_sekunda_CZ = self.flex_casova_znacka[i*49:i*49+(49*60)]

            peaks, _ = signal.find_peaks(ekg_sekunda, height=int(self.args["limit"]), distance=150)
            peaks_in_ms = [ekg_sekunda_CZ[j] for j in peaks] # .timestamp()


            self.avg_HR_RESP["time"].append(ekg_sekunda_CZ[0])


            dif = np.diff(peaks_in_ms)
            if len(dif) == 0:
                self.avg_HR_RESP["HR"].append(0)
            else:
                self.avg_HR_RESP["HR"].append(1 / np.average(dif) * 60)

            flex_peaks, _ = signal.find_peaks(flex_sekunda, prominence=self.args["flexprom"])
            flex_peaks=np.array(flex_peaks)



            flex_peaks_in_ms = [flex_sekunda_CZ[j] for j in flex_peaks] # .timestamp()
            flex_dif = list(np.diff(flex_peaks_in_ms))

            if len(flex_dif) == 0:
                self.avg_HR_RESP["RESP"].append(0)
            else:
                self.avg_HR_RESP["RESP"].append(1 / np.average(flex_dif) * 60)


    def analyze_epochs(self):
        delka_epochy_s = int(self.args["epocha"])
        pocet_epoch = int(self.pocet_minut/(delka_epochy_s/60)) #int(len(self.ekg_values)/(500*delka_epochy_s))

        self.epoch_stats = {
            "time": [],
            "HR": [],
            "RR-min": [],
            "RR-max": [],
            "RMSSD": [],
            "SDNN": [],
            "RESP": [],
            "FlexDer": [],
            "RR_avg": []
        }
        

        for epoch_num in range(pocet_epoch):

            ekg_epocha = self.ekg_values[epoch_num*500*delka_epochy_s:epoch_num*500*delka_epochy_s+500*delka_epochy_s]
            ekg_epocha_cz = self.ekg_casova_znacka[epoch_num*500*delka_epochy_s:epoch_num*500*delka_epochy_s+500*delka_epochy_s]
            
            
            peaks, _ = signal.find_peaks(ekg_epocha, height=int(self.args["limit"]), distance=150)
            peaks_in_ms = [ekg_epocha_cz[j]*1000 for j in peaks] #.timestamp()

            ekg_dif = np.diff(peaks_in_ms)

            RMSSD = 0
            SDNN = 0
            HR = 0
            RESP = 0

            if(len(ekg_dif) > 1):
            
                for i in range(1, len(ekg_dif)):
                    RMSSD += (np.power((ekg_dif[i]-ekg_dif[i-1]),2))
                        
                RMSSD = np.sqrt((1/(len(ekg_dif)-1))*RMSSD)
                
                for i in range(len(ekg_dif)):
                    SDNN += np.power((ekg_dif[i]-np.average(ekg_dif)),2)
                SDNN = np.sqrt(1/((len(ekg_dif)-1)) * SDNN)
                
                HR = round(1000 / np.average(ekg_dif) * 60)
                RR_avg = np.average(ekg_dif)
            # Zapiš data do dictionary
            self.epoch_stats["time"].append(ekg_epocha_cz[0])

            if len(ekg_dif) == 0:
                self.epoch_stats["HR"]    .append(0)
                self.epoch_stats["RR-min"].append(0)
                self.epoch_stats["RR-max"].append(0)
                self.epoch_stats["RMSSD"] .append(0)
                self.epoch_stats["SDNN"]  .append(0)
                self.epoch_stats["RR_avg"].append(0)
            else:
                self.epoch_stats["HR"]    .append(HR)
                self.epoch_stats["RR_avg"].append(RR_avg)
                self.epoch_stats["RR-min"].append(round(np.min(ekg_dif),2))


                # Nastav limity statistik
                if np.max(ekg_dif) > 5000:
                    self.epoch_stats["RR-max"].append(0)
                else:
                    self.epoch_stats["RR-max"].append(round(np.max(ekg_dif),2))
                
                if RMSSD > 5000 or SDNN > 5000:
                    self.epoch_stats["RMSSD"] .append(0)
                    self.epoch_stats["SDNN"]  .append(0)

                else:
                    self.epoch_stats["RMSSD"] .append(round(RMSSD,2))
                    self.epoch_stats["SDNN"]  .append(round(SDNN,2))



            flex_epocha = self.flex_values[epoch_num*49*delka_epochy_s:epoch_num*49*delka_epochy_s+(49*delka_epochy_s)]

            self.epoch_stats["FlexDer"].append(round(max(np.diff(flex_epocha)), 2))


            #flex_epocha_cz = self.flex_casova_znacka[epoch_num*49*delka_epochy_s:epoch_num*49*delka_epochy_s+(49*delka_epochy_s)]

            flex_peaks, _ = signal.find_peaks(flex_epocha, prominence=self.args["flexprom"])
            
            

            self.epoch_stats["RESP"].append(len(flex_peaks))
