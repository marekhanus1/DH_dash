import numpy as np
import neurokit2 as nk # type: ignore
from scipy import signal



class AnalysePeaks:
    def peak_analysis(self):
        
        peaks, _ = signal.find_peaks(self.ekg_values, height=int(self.args["limit"]), distance=75)

        
        peaks_in_ms = [self.ekg_casova_znacka[j] for j in peaks] # .timestamp()

        RR_avg = np.average(np.diff(peaks_in_ms)) # RR interval in seconds
                            
        _, ecg_peak_values = nk.ecg_delineate(self.ekg_values, peaks, sampling_rate=self.vzorkovaci_frekvence, method="dwt")

        #print(ecg_peak_values)

        
        # convert all data in dict to datetime
        for key in ecg_peak_values:
            for i in ecg_peak_values[key]:
                print(i)
            ecg_peak_values[key] = [self.ekg_casova_znacka[i] for i in ecg_peak_values[key] if str(i) != "nan"]
        print(len(peaks))
        
        
        # Print lenght of each list in dict
        for key in ecg_peak_values:
            print(f"{key}: {len(ecg_peak_values[key])}")



        #print(len(ecg_peak_values['ECG_P_Offsets']))
        


        P_distance = []
        PR_distance = []
        Q_distance = []
        QTc_distance = []

        for i in range(len(peaks)-1):

            if ecg_peak_values['ECG_P_Onsets'][i] != "nan" or ecg_peak_values['ECG_P_Offsets'][i] != "nan":
                np.append(P_distance, ecg_peak_values['ECG_P_Offsets'][i] - ecg_peak_values['ECG_P_Onsets'][i])
            else:
                np.append(P_distance, "NaN")

            if ecg_peak_values['ECG_R_Onsets'][i] != "nan" or ecg_peak_values['ECG_P_Onsets'][i] != "nan":
                np.append(PR_distance, ecg_peak_values['ECG_R_Onsets'][i] - ecg_peak_values['ECG_P_Onsets'][i])
            else:
                np.append(PR_distance, "NaN")
            
            if ecg_peak_values['ECG_R_Onsets'][i] != "nan" or ecg_peak_values['ECG_Q_Peaks'][i] != "nan":
                np.append(Q_distance, ecg_peak_values['ECG_Q_Peaks'][i] - ecg_peak_values['ECG_R_Onsets'][i])
            else:
                np.append(Q_distance, "NaN")

            if ecg_peak_values['ECG_T_Offsets'][i] != "nan" or ecg_peak_values['ECG_R_Onsets'][i] != "nan":            
                QTc = round((ecg_peak_values['ECG_T_Offsets'][i] - ecg_peak_values['ECG_R_Onsets'][i])/np.sqrt(RR_avg/1000))
                np.append(QTc_distance, QTc)
            else:
                np.append(QTc_distance, "NaN")

        self.peaks_stats = {
            "P": P_distance,
            "PR": PR_distance,
            "Q": Q_distance,
            "QTc": QTc_distance
        }

        print(self.peaks_stats)