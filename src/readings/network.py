from time import monotonic
from os import path as os_path

class Interface:
    __slots__= (
        "Received_bytes",
        "Received_packets",
        "Received_error",
        "Received_drop",
        "Transmitted_bytes", 
        "Transmitted_packets", 
        "Transmitted_error",
        "Transmitted_drop",
        "Type"
    )

    def __init__(self):
        self.Received_bytes= "N/A"
        self.Received_packets= "N/A"
        self.Received_error= "N/A"
        self.Received_drop= "N/A"
        self.Transmitted_bytes= "N/A"
        self.Transmitted_packets= "N/A"
        self.Transmitted_error= "N/A"
        self.Transmitted_drop= "N/A"
        self.Type= "N/A"

class NetworkTraffic:
    """
    Collects the network traffic data.
    """
    __slots__= (
        "file_path",
        "raw_readings",
        "prev_time",
        "throughput"
    )

    def __init__(self, file_path: object):
        self.file_path= file_path
        self.raw_readings= {}
        self.prev_time= None
        self.throughput= {}

    def update(self, schedule):

        if schedule["network"] is False:
            return
        
        previous_time= self.prev_time

        if previous_time is None:
            previous_time= monotonic()

        current_time= monotonic()
        time_delta= max(current_time - previous_time, 0.001)
        raw_readings= self.raw_readings
        throughput= self.throughput 
        current_networks= {}
        
        try:
            for line in self.file_path.get_file("net"):
                if ":" not in line:
                    continue

                fields= line.split(None, 13)

                interface= fields[0].rstrip(":")
                if interface not in raw_readings:
                    if os_path.exists(f"/sys/class/net/{interface}/device"):
                        interface_type= "Physical"

                    else:
                        interface_type= "Virtual"
                else:
                    interface_type= raw_readings[interface].Type

                received_bytes = int(fields[1])
                received_packets= int(fields[2])
                received_error= int(fields[3])
                received_drop= int(fields[4])
                transmitted_bytes = int(fields[9])
                transmitted_packets= int(fields[10])
                transmitted_error= int(fields[11])
                transmitted_drop= int(fields[12])

                current_networks[interface]= True

                if interface in raw_readings:

                    if interface not in throughput:
                        #create the object and assign it in the dict
                        interface_throughput= Interface()
                        interface_throughput.Received_bytes= (received_bytes - raw_readings[interface].Received_bytes)/ time_delta
                        interface_throughput.Received_packets= (received_packets- raw_readings[interface].Received_packets)/ time_delta
                        interface_throughput.Received_error= (received_error - raw_readings[interface].Received_error)/ time_delta
                        interface_throughput.Received_drop= (received_drop - raw_readings[interface].Received_drop)/ time_delta
                        interface_throughput.Transmitted_bytes= (transmitted_bytes - raw_readings[interface].Transmitted_bytes) / time_delta
                        interface_throughput.Transmitted_packets= (transmitted_packets - raw_readings[interface].Transmitted_packets)/ time_delta
                        interface_throughput.Transmitted_error= (transmitted_error - raw_readings[interface].Transmitted_error)/ time_delta
                        interface_throughput.Transmitted_drop= (transmitted_drop - raw_readings[interface].Transmitted_drop)/ time_delta
                        interface_throughput.Type= interface_type
        
                        throughput[interface]= interface_throughput

                    else:
                        #if object exist, just update the values
                        throughput[interface].Received_bytes= (received_bytes - raw_readings[interface].Received_bytes)/ time_delta
                        throughput[interface].Received_packets= (received_packets- raw_readings[interface].Received_packets)/ time_delta
                        throughput[interface].Received_error= (received_error - raw_readings[interface].Received_error)/ time_delta
                        throughput[interface].Received_drop= (received_drop - raw_readings[interface].Received_drop)/ time_delta
                        throughput[interface].Transmitted_bytes= (transmitted_bytes - raw_readings[interface].Transmitted_bytes) / time_delta
                        throughput[interface].Transmitted_packets= (transmitted_packets - raw_readings[interface].Transmitted_packets)/ time_delta
                        throughput[interface].Transmitted_error= (transmitted_error - raw_readings[interface].Transmitted_error)/ time_delta
                        throughput[interface].Transmitted_drop= (transmitted_drop - raw_readings[interface].Transmitted_drop)/ time_delta

                    #assign new value to the existing object
                    raw_readings[interface].Received_bytes= received_bytes
                    raw_readings[interface].Received_packets= received_packets
                    raw_readings[interface].Received_error= received_error
                    raw_readings[interface].Received_drop= received_drop
                    raw_readings[interface].Transmitted_bytes= transmitted_bytes
                    raw_readings[interface].Transmitted_packets= transmitted_packets
                    raw_readings[interface].Transmitted_error= transmitted_error
                    raw_readings[interface].Transmitted_drop= transmitted_drop

                else:
                    #create object and assign it to the dict
                    interface_raw_readings= Interface()
                    raw_readings[interface]= interface_raw_readings
                    raw_readings[interface].Received_bytes= received_bytes
                    raw_readings[interface].Received_packets= received_packets
                    raw_readings[interface].Received_error= received_error
                    raw_readings[interface].Received_drop= received_drop
                    raw_readings[interface].Transmitted_bytes= transmitted_bytes
                    raw_readings[interface].Transmitted_packets= transmitted_packets
                    raw_readings[interface].Transmitted_error= transmitted_error
                    raw_readings[interface].Transmitted_drop= transmitted_drop
                    raw_readings[interface].Type= interface_type

        except FileNotFoundError:
            throughput["N/A"]= Interface()
            throughput["N/A"].Type= "Physical"
            
        removed_networks= raw_readings.keys() - current_networks.keys()
        for to_delete in removed_networks:
            del raw_readings[to_delete]
            
