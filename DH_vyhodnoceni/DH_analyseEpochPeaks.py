import numpy as np
import neurokit2 as nk # type: ignore
from scipy import signal
from datetime import datetime

class EpochPeaksAnalyser:
    def __init__(self, piky_shared_dict):
        self.piky_shared_dict = piky_shared_dict

    def run_epoch_piky(self, ekg_pik_values, ekg_pik_casova_znacka, args, RR_avg):
        print("ANALYZE PEAKS...")
        vzorkovaci_frekvence = 500


        ekg_pik_casova_znacka = [i.timestamp() for i in ekg_pik_casova_znacka] # Převeď časovou značku na UNIX timestampy


        self.piky_shared_dict["stage"] = 6
        peaks, _ = signal.find_peaks(ekg_pik_values, height=int(args["limit"]), distance=75) # Najdi R píky v EKG
        print("PEAKS: ", len(peaks))
        
        
        
        peaks_in_ms = [ekg_pik_casova_znacka[j] for j in peaks] # .timestamp() # Časová značka R píků v sekundách

        
                            
        _, ecg_peak_values = nk.ecg_delineate(ekg_pik_values, peaks, sampling_rate=vzorkovaci_frekvence, method="dwt") # Najdi všechny důležité body na EKG

        for key in ecg_peak_values:
            ecg_peak_values[key] = [ekg_pik_casova_znacka[i] for i in ecg_peak_values[key] if str(i) != "nan"] # Převeď indexy na UNIX timestampy
        
        keys = list(ecg_peak_values.keys()) # Názvy klíčů v dictionary
        
        # Projdi všechny hodnoty a urči, jestli nějaké nechybí. Pokud ano, přidej 0 před další hodnotu
        for cislo_piku in range(len(peaks)-1):
            try:
            
                for i in keys[:5]:
                    if ecg_peak_values[i][cislo_piku] > peaks_in_ms[cislo_piku]:
                        ecg_peak_values[i] = np.insert(ecg_peak_values[i], cislo_piku, 0)
                        print(f"MOVED P {i} - {cislo_piku}")  
                                
                for i in keys[5:]:
                    if ecg_peak_values[i][cislo_piku] > peaks_in_ms[cislo_piku+1]:
                        ecg_peak_values[i] = np.insert(ecg_peak_values[i], cislo_piku, 0)
                        print(f"MOVED T {i} - {cislo_piku}")

                    elif ecg_peak_values[i][cislo_piku] < peaks_in_ms[cislo_piku]:
                        ecg_peak_values[i] = np.delete(ecg_peak_values[i], cislo_piku)
                        print(f"DELETED T {i} - {cislo_piku}")

            
            except: 
                print("INDEX ERROR IN PEAKS")
        



        P_distance = []
        PR_distance = []
        QRS_distance = []
        QTc_distance = []
        flex_der = []
        RR_avg = []
        P_peaks = []

        index_epochy = 1

        vzorky_za_ms = int(vzorkovaci_frekvence/1000)

        for i in range(len(peaks)-1):
            
            if peaks[i] - 300*vzorky_za_ms < 0:
                zacatek_hledani = 0
            else:
                zacatek_hledani =peaks[i]-250 # 300 ms před R píkem



            find_P_peaks, prominence = signal.find_peaks(ekg_pik_values[zacatek_hledani:peaks[i]-30], prominence=int(args["pik_prominenceP"])) # 

            prominence = list(prominence["prominences"])

            P_peaks_in_ms = [ekg_pik_casova_znacka[zacatek_hledani:peaks[i]-30][j] for j in find_P_peaks] # Časová značka P píků v sekundách 
            P_peaks.append([P_peaks_in_ms, prominence])

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


        max_length = max(max(len(inner_list) for inner_list in pair) for pair in P_peaks)
        padded_data = []
        for pair in P_peaks:
            padded_pair = [inner_list + [0] * (max_length - len(inner_list)) for inner_list in pair]
            padded_data.append(padded_pair)


        self.P_peaks = np.array(padded_data).astype(np.float64)

        self.peaks_stats = {
            "time":np.array(peaks_in_ms[:-1]).astype(np.float64),
            "P": np.array(P_distance).astype(np.float64),
            "PR": np.array(PR_distance).astype(np.float64),
            "QRS": np.array(QRS_distance).astype(np.float64),
            "QTc": np.array(QTc_distance).astype(np.float64),
            "FlexDer": np.array(flex_der).astype(np.float64)
        }
