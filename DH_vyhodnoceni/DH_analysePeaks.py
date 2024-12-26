import numpy as np
import neurokit2 as nk # type: ignore
from scipy import signal



class AnalysePeaks:
    def peak_analysis(self):
        start_file_ekg, end_file_ekg = self.get_time_range(self.ekg_casova_znacka, self.args["pik_range"])
        

        
        ekg_pik_values = self.ekg_values[start_file_ekg:end_file_ekg] # Rozmezí EKG, které se bude analyzovat
        ekg_pik_casova_znacka = self.ekg_casova_znacka[start_file_ekg:end_file_ekg] # Rozmezí časové značky EKG, která se bude analyzovat


        peaks, _ = signal.find_peaks(ekg_pik_values, height=int(self.args["limit"]), distance=75) # Najdi R píky v EKG
        print("PEAKS: ", len(peaks))
        
        peaks_in_ms = [ekg_pik_casova_znacka[j] for j in peaks] # .timestamp() # Časová značka R píků v sekundách

        
                            
        _, ecg_peak_values = nk.ecg_delineate(ekg_pik_values, peaks, sampling_rate=self.vzorkovaci_frekvence, method="dwt") # Najdi všechny důležité body na EKG

        for key in ecg_peak_values:
            ecg_peak_values[key] = [ekg_pik_casova_znacka[i] for i in ecg_peak_values[key] if str(i) != "nan"] # Převeď indexy na UNIX timestampy
        
        keys = list(ecg_peak_values.keys()) # Názvy klíčů v dictionary
        

        # Projdi všechny hodnoty a urči, jestli nějaké nechybí. Pokud ano, přidej 0 před další hodnotu
        for cislo_piku in range(len(peaks)-1):
            for i in keys[:5]:
                if ecg_peak_values[i][cislo_piku] > peaks_in_ms[cislo_piku]:
                    ecg_peak_values[i] = np.insert(ecg_peak_values[i], cislo_piku, 0)
                    print(f"MOVED P {i} - {cislo_piku}")  
                            
            for i in keys[5:]:
                if ecg_peak_values[i][cislo_piku] > peaks_in_ms[cislo_piku+1]:
                    ecg_peak_values[i] = np.insert(ecg_peak_values[i], cislo_piku, 0)
                    print(f"MOVED T {i} - {cislo_piku}")

        
        



        P_distance = []
        PR_distance = []
        QRS_distance = []
        QTc_distance = []
        flex_der = []
        RR_avg = []

        index_epochy = 1

        for i in range(len(peaks)-1):
            while self.epoch_stats["time"][index_epochy] <= peaks_in_ms[i]: # Najdi epochu, ve které se nachází R pík pro určení RR_avg a FlexDer
                index_epochy += 1
                if index_epochy == len(self.epoch_stats["time"]): # Zajisti, aby nedošlo k přetečení
                    break
            
            index_epochy -= 1 # Vrať se o jednu epochu zpět (Tam se R pík nachází)

            flex_der.append(self.epoch_stats["FlexDer"][index_epochy])
            RR_avg = self.epoch_stats["RR_avg"][index_epochy]

            try:
                if ecg_peak_values['ECG_P_Onsets'][i] != 0 and ecg_peak_values['ECG_P_Offsets'][i] != 0:
                    P = (ecg_peak_values['ECG_P_Offsets'][i] - ecg_peak_values['ECG_P_Onsets'][i])*1000
                    P_distance.append(round(P, 2))

                else:
                    P_distance.append(None)
            except:
                P_distance.append(None)

            try:
                if ecg_peak_values['ECG_R_Onsets'][i] != 0 and ecg_peak_values['ECG_P_Onsets'][i] != 0:
                    PR = (ecg_peak_values['ECG_R_Onsets'][i] - ecg_peak_values['ECG_P_Onsets'][i]) * 1000
                    PR_distance.append(round(PR, 2))
                else:
                    PR_distance.append(None)
            except:
                PR_distance.append(None)
            
            try:
                if ecg_peak_values['ECG_R_Onsets'][i] != 0 and ecg_peak_values['ECG_R_Offsets'][i] != 0:
                    QRS = (ecg_peak_values['ECG_R_Offsets'][i] - ecg_peak_values['ECG_R_Onsets'][i]) * 1000
                    QRS_distance.append(round(QRS, 2))
                else:
                    QRS_distance.append(None)
            except:
                QRS_distance.append(None)

            try:
                if ecg_peak_values['ECG_T_Offsets'][i] != 0 and ecg_peak_values['ECG_R_Onsets'][i] != 0:  
                    QT = (ecg_peak_values['ECG_T_Offsets'][i] - ecg_peak_values['ECG_R_Onsets'][i]) * 1000  
                            
                    QTc = round(QT / np.sqrt(RR_avg/1000),2)
                    QTc_distance.append(QTc)
                else:
                    QTc_distance.append(None)
            except:
                QTc_distance.append(None)


        #convert ecg_peak_values dtype
        for key in ecg_peak_values:
            ecg_peak_values[key] = np.array(ecg_peak_values[key]).astype(np.float64)


        self.ecg_peak_values = ecg_peak_values
        

        self.peaks_stats = {
            "time":np.array(peaks_in_ms[:-1]).astype(np.float64),
            "P": np.array(P_distance).astype(np.float64),
            "PR": np.array(PR_distance).astype(np.float64),
            "QRS": np.array(QRS_distance).astype(np.float64),
            "QTc": np.array(QTc_distance).astype(np.float64),
            "FlexDer": np.array(flex_der).astype(np.float64)

        }

        #print(self.peaks_stats)