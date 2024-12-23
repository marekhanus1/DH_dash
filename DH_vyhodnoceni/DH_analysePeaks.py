import numpy as np
import neurokit2 as nk # type: ignore
from scipy import signal



class AnalysePeaks:
    def peak_analysis(self):
        start_file_ekg, end_file_ekg = self.get_time_range(self.ekg_casova_znacka, self.args["pik_range"])
        print(start_file_ekg, end_file_ekg)

        
        ekg_pik_values = self.ekg_values[start_file_ekg:end_file_ekg]
        ekg_pik_casova_znacka = self.ekg_casova_znacka[start_file_ekg:end_file_ekg]


        peaks, _ = signal.find_peaks(ekg_pik_values, height=int(self.args["limit"]), distance=75)

        print("PEAKS: ", len(peaks))
        
        peaks_in_ms = [ekg_pik_casova_znacka[j] for j in peaks] # .timestamp()

        RR_avg = np.average(np.diff(peaks_in_ms)) # RR interval in seconds
                            
        _, ecg_peak_values = nk.ecg_delineate(ekg_pik_values, peaks, sampling_rate=self.vzorkovaci_frekvence, method="dwt")

        #print(ecg_peak_values)

        
        # convert all data in dict to datetime
        for key in ecg_peak_values:
            for i in ecg_peak_values[key]:
                print(i)
            ecg_peak_values[key] = [ekg_pik_casova_znacka[i] for i in ecg_peak_values[key] if str(i) != "nan"]
        
        
        
        # Print lenght of each list in dict
        for key in ecg_peak_values:
            print(f"{key}: {len(ecg_peak_values[key])}")



        #print(len(ecg_peak_values['ECG_P_Offsets']))
        


        P_distance = []
        PR_distance = []
        Q_distance = []
        QTc_distance = []
        flex_der = []
        for i in range(len(peaks)-1):

            if ecg_peak_values['ECG_P_Onsets'][i] != "nan" or ecg_peak_values['ECG_P_Offsets'][i] != "nan":
                P_distance = np.append(P_distance, ecg_peak_values['ECG_P_Offsets'][i] - ecg_peak_values['ECG_P_Onsets'][i])
            else:
                P_distance = np.append(P_distance, "NaN")

            if ecg_peak_values['ECG_R_Onsets'][i] != "nan" or ecg_peak_values['ECG_P_Onsets'][i] != "nan":
                PR_distance = np.append(PR_distance, ecg_peak_values['ECG_R_Onsets'][i] - ecg_peak_values['ECG_P_Onsets'][i])
            else:
                PR_distance = np.append(PR_distance, "NaN")
            
            if ecg_peak_values['ECG_R_Onsets'][i] != "nan" or ecg_peak_values['ECG_Q_Peaks'][i] != "nan":
                Q_distance = np.append(Q_distance, ecg_peak_values['ECG_Q_Peaks'][i] - ecg_peak_values['ECG_R_Onsets'][i])
            else:
                Q_distance = np.append(Q_distance, "NaN")

            if ecg_peak_values['ECG_T_Offsets'][i] != "nan" or ecg_peak_values['ECG_R_Onsets'][i] != "nan":            
                QTc = round((ecg_peak_values['ECG_T_Offsets'][i] - ecg_peak_values['ECG_R_Onsets'][i])/np.sqrt(RR_avg/1000))
                QTc_distance = np.append(QTc_distance, QTc)
            else:
                QTc_distance = np.append(QTc_distance, "NaN")



        self.peaks_stats = {
            "time":peaks_in_ms,
            "P": P_distance,
            "PR": PR_distance,
            "Q": Q_distance,
            "QTc": QTc_distance
        }

        #print(self.peaks_stats)