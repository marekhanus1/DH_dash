import os

def download_files(file_prefix):
    # SSH connection details
    hostname = "192.168.4.1"
    username = "pi"
    password = "raspberry"

    ekg_files = []
    flex_files = []

    # Remote directory to search and download from
    remote_directory = "/home/pi/Holter_bluetooth/holter_vysledky/"
    # Local directory to save files
    local_directory = "holter_vysledky/"

    # Create local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    # SSH command to list files
    ssh_command = f"sshpass -p '{password}' ssh {username}@{hostname} ls {remote_directory}" 

    # Get the list of files
    file_list = os.popen(ssh_command).read().splitlines()

    # Filter files that start with the specified prefix
    filtered_files = [file for file in file_list if file.startswith(file_prefix)]

    # Download each filtered file
    for file_name in filtered_files:
        remote_file_path = os.path.join(remote_directory, file_name)
        local_file_path = os.path.join(local_directory, file_name)
        
        scp_command = f"sshpass -p '{password}' scp {username}@{hostname}:{remote_file_path} {local_file_path}"
        os.system(scp_command)
        print(f"Downloaded: {file_name}")

        if file_name.endswith(".ekg"):
            ekg_files.append(file_name)
        else:
            flex_files.append(file_name)


    # Output the number of files that match the criteria
    print(f"Total files with prefix '{file_prefix}': {len(filtered_files)}")

    file_name = file_prefix.replace("Holter", "logfile") + ".log"
    remote_file_path = os.path.join(remote_directory, file_name)
    print(remote_file_path)
    os.system(f"sshpass -p '{password}' scp {username}@{hostname}:{remote_file_path}  {local_directory}")

    


    
