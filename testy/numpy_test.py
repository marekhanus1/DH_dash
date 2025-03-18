import numpy as np

# Initial data
a = ([False, False, True, True, True, True], ['241129', 3000, 10], [False, False], [[480, 1020], 2, 4, 4, 30, [1410, 1420]])

for element in a:
    for j in element:
        print(j)
        print(type(j))

a = ([False, False, True, True, True, True], ['241129', 3000, 10], [False, False], ['08:00-17:00', 2, 4, 4, 30, '23:50-23:59', '23:59'])
# remove last element: '23:59'

a = list(a)
a[-1] = a[-1][:-1]
print(a)



import subprocess
import platform

def can_ping(ip, timeout=1):
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

# Example usage
if can_ping("192.168.4.1", timeout=0.5):  # 0.5 seconds timeout
    print("Connected to the network!")
else:
    print("Not connected to the network.")

