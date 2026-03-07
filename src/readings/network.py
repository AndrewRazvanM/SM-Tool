from time import monotonic
import os


def network_traffic(file_path, previous_data= None, previous_time= None):
    if previous_data is None:
        previous_data={}
    if previous_time is None:
        previous_time= monotonic()
    data={}
    network_data= {}
    current_time= monotonic()
    try:
        for line in file_path.get_file("net"):
                if ":" not in line:
                    continue
                interface, stats = line.split(":", 1)
                interface = interface.strip()
                if (previous_data is not None) and (interface in previous_data):
                    interface_type= previous_data[interface]["Type"]
                elif os.path.exists(f"/sys/class/net/{interface}/device"):
                    interface_type= "Physical"
                else:
                    interface_type= "Virtual"

                fields = stats.split()
                received_bytes = int(fields[0])
                received_packets= int(fields[1])
                received_error= int(fields[2])
                received_drop= int(fields[3])
                received_fifo= int(fields[4])
                received_frame= int(fields[5])
                transmitted_bytes = int(fields[8])
                transmitted_packets= int(fields[9])
                transmitted_error= int(fields[10])
                transmitted_drop= int(fields[11])
                transmitted_fifo= int(fields[12])
                transmitted_frame= int(fields[13])
                data[interface] = {"Received bytes": received_bytes, 
                                   "Received packets": received_packets, 
                                   "Received error": received_error,
                                   "Received drop": received_drop,
                                   "Received fifo": received_fifo,
                                   "Received frame": received_frame,
                                   "Transmitted bytes": transmitted_bytes, 
                                   "Transmitted packets": transmitted_packets, 
                                   "Transmitted error": transmitted_error,
                                   "Transmitted drop": transmitted_drop,
                                    "Transmitted fifo": transmitted_fifo,
                                    "Transmitted frame": transmitted_frame,
                                    "Type": interface_type
                                   }
    
    except FileNotFoundError:
        data={"No Interface": {
                    "Type": "N/A"
        }}
    
    if ((previous_data != {}) and (data != {})):
        time_delta= max(current_time - previous_time, 0.001)
        network_data["Total"]={
            reading: 0 for reading in data[next(iter(data))] if reading != "Type"
        }        
        for interface in data:
            if interface not in previous_data:
                continue
            network_data[interface]= {}
            for reading in data[interface]:
                if reading == "Type":
                    network_data[interface][reading]= data[interface][reading]
                else:
                    network_data[interface][reading]= (data[interface][reading] - previous_data[interface][reading])/time_delta
                    
        for readings in network_data["Total"]:
            for interface in network_data:
                if interface not in previous_data:
                    continue
                if interface == "Total":
                    continue
                elif network_data[interface]["Type"] == "Physical":
                    network_data["Total"][readings]+= network_data[interface][readings]

    return data, network_data, current_time