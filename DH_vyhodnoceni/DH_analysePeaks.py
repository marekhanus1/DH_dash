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
            ecg_peak_values[key] = [ekg_pik_casova_znacka[i] for i in ecg_peak_values[key] if str(i) != "nan"]
        
        
        
        # Print lenght of each list in dict
        for key in ecg_peak_values:
            print(f"{key}: {len(ecg_peak_values[key])}")



        #print(len(ecg_peak_values['ECG_P_Offsets']))
        
        print("RR_avg: ", RR_avg)

        P_distance = []
        PR_distance = []
        Q_distance = []
        QTc_distance = []
        flex_der = []
        for i in range(len(peaks)-2):
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
                    QTc = round(((ecg_peak_values['ECG_T_Offsets'][i] - ecg_peak_values['ECG_R_Onsets'][i])) * 1000 / np.sqrt(RR_avg * 1000))
                    QTc_distance.append(QTc)
                else:
                    QTc_distance.append(None)
            except:
                QTc_distance.append(None)


        self.peaks_stats = {
            "time":peaks_in_ms[:-2],
            "P": P_distance,
            "PR": PR_distance,
            "Q": Q_distance,
            "QTc": QTc_distance
        }

        #print(self.peaks_stats)