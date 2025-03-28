import os
import numpy as np
import h5py
from datetime import datetime
import json
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import subprocess
import paramiko
import platform

class Utils():
    def minutes_to_time(self,minutes):
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    def create_args(self, arg_name):
         
        self.args = {}
        
        value = None

        #setattr(self.args, arg_name[0], value)
        for i in arg_name:
            self.args[i] = value

    def set_arg_function(self, arg_name, value):
        setattr(self.args, arg_name, value)

    def get_dataset_size(self, filename, dtype):
        # Get the size of the file in bytes
        file_size = os.path.getsize(filename)
        # Calculate the number of elements in the array
        return file_size // np.dtype(dtype).itemsize
    
    def read_hdf5_data(self,names, time_names):
        with h5py.File(self.hdf5_filename, 'r') as f:
            decoded_data = {}
            decoded_time = {}

            for i in names:
                for j in i:
                    decoded_data[j] = f[j][:]

            for i in time_names:
                a = f[i][:]
                decoded_time[i] = [datetime.fromtimestamp(ts) for ts in a]

        return decoded_data, decoded_time
    
    def find_name_index(self, array, index):
        current_index = 0
        num_rows = array.shape[0]  # Total number of rows
        
        for row_idx in range(num_rows):
            row_length = len(array[row_idx])  # Length of the current row
            if current_index + row_length > index:
                col_idx = index - current_index  # Calculate the column index
                return row_idx, col_idx
            current_index += row_length
            
        return None  # If index is out of bounds
    
    def read_config():
        with open('components/DH_config.json', 'r') as f:
            return json.load(f)

        # Function to write to config file
    def write_config(self, data):
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=4)

    def handle_progressbar(self):
        progressbar_content = []
        print(self.shared_data["stage"])
        if self.shared_data["stage"] >= 2:
            progressbar_content += [dmc.ProgressSection(dmc.ProgressLabel("EKG"), value=30, color="red"),]
        
        if self.shared_data["stage"] >= 3:
            progressbar_content += [dmc.ProgressSection(dmc.ProgressLabel("FLEX"), value=10, color="orange"),]
        
        if self.shared_data["stage"] >= 4:
            progressbar_content += [dmc.ProgressSection(dmc.ProgressLabel("EPOCHY"), value=10, color="pink"),]
        
        if self.shared_data["stage"] >= 5:
            progressbar_content += [dmc.ProgressSection(dmc.ProgressLabel("HR A RESP"), value=10, color="cyan"),]

        if self.shared_data["stage"] >= 6:
            progressbar_content += [dmc.ProgressSection(dmc.ProgressLabel("PÍKY"), value=30, color="blue"),]
        return progressbar_content
    
    def handle_info(self):
        info_content = []
        if "pocet_souboru" in self.shared_data:
            info_content += [dmc.Group([f"Počet souborů: {self.shared_data['pocet_souboru']}"])]
        else:
            info_content += [dmc.Group(["Počet souborů: ", dmc.Loader(color="red", size="md", type="dots")]),]
        
        if "pocet_minut" in self.shared_data:
            info_content += [dmc.Group([f"Počet naměřených minut: {int(self.shared_data['pocet_minut'])}"]),]
        else:
            info_content += [dmc.Group(["Počet naměřených minut:", dmc.Loader(color="red", size="md", type="dots")]),]

        if "measurement_periods" in self.shared_data:

            cas_od = datetime.fromtimestamp(self.shared_data['measurement_periods'][0][0]).strftime("%H:%M")
            cas_do = datetime.fromtimestamp(self.shared_data['measurement_periods'][0][1]).strftime("%H:%M")
            info_content += [dmc.Group([f"Úseky měření: od {cas_od} do {cas_do}"]),]
            
            for i in range(1,len(self.shared_data["measurement_periods"])):
                cas_od = datetime.fromtimestamp(self.shared_data['measurement_periods'][i][0]).strftime("%H:%M")
                cas_do = datetime.fromtimestamp(self.shared_data['measurement_periods'][i][1]).strftime("%H:%M")
                info_content += [dmc.Group([dmc.Space(w="10.25%"), 
                                f"od {cas_od} do {cas_do}"]),]
        else:
            info_content += [dmc.Group(["Úseky měření: ", dmc.Loader(color="red", size="md", type="dots")]),]

        if "pik_range_error" in self.shared_data:

            info_content += [dmc.Alert(self.shared_data["pik_range_error"], title="Špatně zadané rozmezí souboru!", color="yellow"),]
            self.args["pik_range"] = None
        
        if "error" in self.shared_data:
            info_content += [dmc.Alert(self.shared_data["error"], title="Error!", color="red"),]

        return info_content
    

    def get_dates_from_filenames(typ, files=None):
        dates = {}
        
        if typ == "local":
            folder_path = "holter_vysledky"
            files = os.listdir(folder_path)

        
        month_names = {
            1: "Leden", 2: "Únor", 3: "Březen", 4: "Duben",
            5: "Květen", 6: "Červen", 7: "Červenec", 8: "Srpen",
            9: "Září", 10: "Říjen", 11: "Listopad", 12: "Prosinec"
        }

        for filename in sorted(files, reverse=True):
            # Check if the filename matches the expected format
            if filename.startswith("Holter_"):
                # Extract the YYMMDD part
                try:
                    date_part = filename.split("_")[1]
                    date_obj = datetime.strptime(date_part, "%y%m%d").date()
                    
                    # Format date for display
                    label = date_obj.strftime("%d. %-m. %Y")
                    month_name = month_names[date_obj.month]
                    
                    # Create the month group if it doesn't exist
                    if month_name not in dates:
                        dates[month_name] = []
                    
                    # Add the date entry to the month's list if it's unique
                    select_obj = {"label": label, "value": date_part}
                    if select_obj not in dates[month_name]:
                        dates[month_name].append(select_obj)
                except ValueError:
                    # If filename format doesn't match, skip it
                    pass
    
        # Convert to desired grouped format
        grouped_dates = [{"group": month, "items": items} for month, items in dates.items()]
        
        return grouped_dates

    def choose_date_input(self, value, disabled):
        datum_content = []
        if value == "normal":
            config = Utils.read_config()
            

            datum_content = dmc.Group(
                [
                    dmc.Select(
                                id={"type": "nastaveni_input", "index":"datum_input"},
                                data=Utils.get_dates_from_filenames("local"),
                                value=config.get("date"),
                                leftSection=DashIconify(icon="clarity:date-line"),
                                w=300,
                                withScrollArea=False,
                                styles={"dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                                disabled=disabled,
                                mb=10
                        ),
                    
                    #dmc.Button("Zobrazit logfile", id="logfile_button", n_clicks=0, color="blue", disabled=disabled),

                ]
            )
                        
        
            return datum_content
        elif value == "jine":

            host = "192.168.4.1"  # Raspberry Pi's IP address

            if self.can_ping(host, timeout=0.5):
                
                print(f"Connected to RPi")
                # Configuration
                
                username = "pi"       # Pi's username
                password = "raspberry"  # Pi's password
                remote_path = "/home/pi/Holter_bluetooth/holter_vysledky"

                # List files in the remote directory
                files = self.list_remote_directory(host, username, password, remote_path)


                datum_content = dmc.Select(
                        id={"type": "nastaveni_input", "index":"datum_input"},
                        data=Utils.get_dates_from_filenames("RPi",files=files),
                        leftSection=DashIconify(icon="clarity:date-line"),
                        w=300,
                        withScrollArea=False,
                        styles={"dropdown": {"maxHeight": 200, "overflowY": "auto"}},
                        disabled=disabled,
                        mb=10),
            else:
                print(f"Cannot connect to RPi")


                datum_content = dmc.Alert("Nelze se připojit k RPi", title="Error!", color="red"),
            

            return datum_content
        
        else:
            return None
        
    def create_folder(folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    
    def validate_time(self, time):
        try:
            datetime.strptime(time, '%H:%M')
            return True
        except ValueError:
            return False
        
    def compare_time(self, time1, time2):
        return datetime.strptime(time1, '%H:%M') < datetime.strptime(time2, '%H:%M')
    
    """
    def is_connected_to_ap(self, target_ssid):
        try:
            # Use nmcli to get the name of the currently connected Wi-Fi network
            result = subprocess.run(
                ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse the output
            active_networks = [
                line.split(":")[1] for line in result.stdout.splitlines() if line.startswith("yes")
            ]
            return target_ssid in active_networks
        except subprocess.CalledProcessError as e:
            print(f"Error while checking network: {e}")
            return False
    """

    def can_ping(self, ip, timeout=1):
        try:
            # Determine the OS
            if platform.system().lower() == "windows":
                # Windows ping command
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
            else:
                # Linux/macOS ping command
                cmd = ["ping", "-c", "1", "-W", str(timeout), ip]
            
            # Execute the ping command
            result = subprocess.run(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
            return False
     

    def list_remote_directory(self,host, username, password, remote_path):
        try:
            # Establish an SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=username, password=password)

            # Execute the ls command on the remote directory
            stdin, stdout, stderr = ssh.exec_command(f"ls -1 {remote_path}")
            # Read the output and split by lines
            files = stdout.read().decode().splitlines()

            ssh.close()
            return files
        except Exception as e:
            print(f"Error: {e}")
            return []
        
    
    def read_log(self, filename):
        filename = f"holter_vysledky/logfile_{filename}.log"
        try:
            with open(filename, "r") as f:
                return dmc.Textarea(value=f.read(), autosize=True)
        except:
            return dmc.Alert("Logfile nebyl nalezen", title="Error!", color="red")
        