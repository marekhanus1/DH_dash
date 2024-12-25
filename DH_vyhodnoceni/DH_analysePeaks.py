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

        RR_avg = np.average(np.diff(peaks_in_ms)) # RR interval in seconds
                            
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

        
        print("RR_avg: ", RR_avg)
        self.shared_data["RR_avg"] = RR_avg


        P_distance = []
        PR_distance = []
        Q_distance = []
        QTc_distance = []
        flex_der = []
        for i in range(len(peaks)-1):
            try:
                if ecg_peak_values['ECG_P_Onsets'][i] != "nan" or ecg_peak_values['ECG_P_Offsets'][i] != "nan":
                    P = (ecg_peak_values['ECG_P_Offsets'][i] - ecg_peak_values['ECG_P_Onsets'][i])*1000
                    P_distance.append(round(P, 2))

                else:
                    P_distance.append(None)
            except:
                P_distance.append(None)

            try:
                if ecg_peak_values['ECG_R_Onsets'][i] != "nan" or ecg_peak_values['ECG_P_Onsets'][i] != "nan":
                    PR = (ecg_peak_values['ECG_R_Onsets'][i] - ecg_peak_values['ECG_P_Onsets'][i]) * 1000
                    PR_distance.append(round(PR, 2))
                else:
                    PR_distance.append(None)
            except:
                PR_distance.append(None)
            
            try:
                if ecg_peak_values['ECG_R_Onsets'][i] != "nan" or ecg_peak_values['ECG_Q_Peaks'][i] != "nan":
                    Q = (ecg_peak_values['ECG_Q_Peaks'][i] - ecg_peak_values['ECG_R_Onsets'][i]) * 1000
                    Q_distance.append(round(Q, 2))
                else:
                    Q_distance.append(None)
            except:
                Q_distance.append(None)

            try:
                if ecg_peak_values['ECG_T_Offsets'][i] != "nan" or ecg_peak_values['ECG_R_Onsets'][i] != "nan":            
                    QTc = round(((ecg_peak_values['ECG_T_Offsets'][i] - ecg_peak_values['ECG_R_Onsets'][i])) * 1000 / np.sqrt(RR_avg * 1000),2)
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
            "Q": np.array(Q_distance).astype(np.float64),
            "QTc": np.array(QTc_distance).astype(np.float64),

        }

        #print(self.peaks_stats)