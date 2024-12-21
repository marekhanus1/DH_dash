import numpy as np
import neurokit2 as nk # type: ignore
from scipy import signal



class AnalysePeaks:
    def peak_analysis(self):
        
        peaks, _ = signal.find_peaks(self.ekg_values, height=int(self.args["limit"]), distance=75)
        peaks_in_ms = [self.ekg_casova_znacka[j] for j in peaks] # .timestamp()

        _, ecg_peak_values = nk.ecg_delineate(self.ekg_values, peaks, sampling_rate=self.vzorkovaci_frekvence, method="dwt")

        #print(ecg_peak_values)

        
        # convert all data in dict to datetime
        for key in ecg_peak_values:
            for i in ecg_peak_values[key]:
                print(i)
            ecg_peak_values[key] = [self.ekg_casova_znacka[i] for i in ecg_peak_values[key] if str(i) != "nan"]
        print(len(peaks))
        print(len(ecg_peak_values['ECG_P_Offsets']))
        


        P_distance = []
        PR_distance = []
        Q_distance = []
        QTc_distance = []

        for i in range(len(peaks)):
            np.append(P_distance, ecg_peak_values['ECG_P_Onsets'][i] - ecg_peak_values['ECG_P_Offsets'][i])
            np.append(PR_distance, ecg_peak_values['ECG_P_Offsets'][i] - ecg_peak_values['ECG_R_Peaks'][i])
            np.append(Q_distance, ecg_peak_values['ECG_R_Peaks'][i] - ecg_peak_values['ECG_Q_Points'][i])

            QTc = ecg_peak_values['ECG_R_Peaks'][i] - ecg_peak_values['ECG_T_Offsets'][i]
            np.append(QTc_distance, )

