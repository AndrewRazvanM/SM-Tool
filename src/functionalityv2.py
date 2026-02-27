import pynvml
import os
import time

class NeededFiles:
    def __init__(self):
        self.files = {
            "net": open("/proc/net/dev", "r"),
            "stat": open("/proc/stat", "r"),
            "mem_pressure": open("/proc/pressure/memory", "r"),
            "cpu_pressure": open("/proc/pressure/cpu", "r"),
            "meminfo": open("/proc/meminfo", "r"),
        }

    def get_file(self, name):
        f = self.files[name]
        f.seek(0)
        return f

    def close_all(self):
        for f in self.files.values():
            f.close()
        self.files.clear()

def nvidia_gpu_name(gpu_check_disable):
    gpu_handles= None
    if gpu_check_disable is False:
            data= []
            gpu_handles= []
            gpu_count= pynvml.nvmlDeviceGetCount()
            for gpu in range(gpu_count):
                gpu_handles.append(pynvml.nvmlDeviceGetHandleByIndex(gpu))
                gpu_name= pynvml.nvmlDeviceGetName(gpu_handles[gpu])
                data.append(gpu_name)
    else:
        data= ["Disabled on this system"]
    
    return data, gpu_handles

def nvidia_gpu_readings(gpu_check_disable, gpu_handles, gpu_fan_disabled= False,gpu_mem_disabled= False):

    try:
        if gpu_check_disable is False:
            data= []
            for gpu in gpu_handles:
                gpu_temp= pynvml.nvmlDeviceGetTemperature(gpu, pynvml.NVML_TEMPERATURE_GPU)
                gpu_stats= pynvml.nvmlDeviceGetUtilizationRates(gpu)
                        #not supported on all cards
                if gpu_fan_disabled == False:
                    try:
                        gpu_fan= pynvml.nvmlDeviceGetFanSpeed(gpu)

                    except pynvml.NVMLError:
                        gpu_fan = "N/A"
                        gpu_fan_disabled= True
                else:
                    gpu_fan = "N/A"

                gpu_core= pynvml.nvmlDeviceGetClockInfo(gpu, pynvml.NVML_CLOCK_GRAPHICS)
                #it's not supported on all graphic cards
                if gpu_mem_disabled == False:
                    try:

                        gpu_core_mem= pynvml.nvmlDeviceGetClockInfo(gpu, pynvml.NVML_CLOCK_MEM)

                    except pynvml.NVMLError:
                        gpu_core_mem= "N/A"
                        gpu_mem_disabled= True
                else:
                    gpu_core_mem= "N/A"

                data.append({
                    "Temperature": gpu_temp,
                    "GPU Clock Speed": gpu_core,
                    "Fan Speed": gpu_fan,
                    "Memory Load": gpu_stats.memory,
                    "GPU Load": gpu_stats.gpu,
                    "GPU Mem Clock": gpu_core_mem
                })
        
        else:
            data= [{
                "Temperature": "N/A",
                "GPU Clock Speed": "N/A",
                "Fan Speed": "N/A",
                "Memory Load": "N/A",
                "GPU Load":"N/A",
            }]

    except (pynvml.NVMLError_LibraryNotFound, OSError, pynvml.NVMLError, RuntimeError):
                data= [{
            "Temperature": 0,
            "GPU Clock Speed": 0,
            "Fan Speed": 0,
            "Memory Load": 0,
            "GPU Load":0,
            }]
    return data, gpu_fan_disabled, gpu_mem_disabled

def get_cpu_name(cpu_check_disable= bool):
    try:
        path= "/proc/cpuinfo"

        if cpu_check_disable is False:
                with open(path) as f:
                    for line in f:
                        if ":" not in line:
                            continue
                        name, value = line.strip().split(":")
                        if "model name" in name:
                            cpu_name= value
                            break

        else:
            cpu_name= "Check disabled"
    
    except (RuntimeError, UnboundLocalError, FileNotFoundError):
        cpu_name= "Not Available"

    return cpu_name

def probe_cpu_sensors(cpu_check_disable):
    path= "/sys/class/hwmon"
    preferred = (
    "x86_pkg_temp",
    "coretemp",
    "cpu_thermal",
    "tcpu",
    "acpitz",
    )
    sensor_name= "Not Found"
    folder_path= "N/A"

    try:
        if cpu_check_disable is False:
            found_sensor= False
            for sensor_check in preferred:
                if found_sensor is False:
                    for sensor_file in os.listdir(path):
                        folder_path= os.path.join(path, sensor_file)
                        sensor_type_file= os.path.join(folder_path, "name")

                        if not os.path.isdir(folder_path):
                            continue
                        if not os.path.isfile(sensor_type_file):
                            continue

                        with open(sensor_type_file) as t:
                            sensor_name= t.read().strip()

                        if sensor_name == sensor_check:
                            found_sensor= True
                            break
    except FileNotFoundError:
        sensor_name= "N/A"

    return sensor_name, folder_path

def cpu_readings(cpu_check_disable= bool,folder_path=str, temperature_folder_path= None):

    if cpu_check_disable is False:
        if temperature_folder_path is None:
            temperature_folder_path={}
            cpu_data= {}
            try:
                for find_temperatures in os.scandir(folder_path):
                    temp_name= find_temperatures.name
                    if "temp" in temp_name:
                        if "input" in temp_name: 
                            sensor_temp_path= find_temperatures.path
                            cpu_label= int("".join(ch for ch in temp_name if ch.isdigit()))     
                            cpu_number= os.path.join(folder_path,f"temp{cpu_label}_label")                   
                            t= open((sensor_temp_path))
                            temperature= int(t.read().strip())
                            with open(cpu_number) as l:
                                label=  str(l.read().strip())
                                cpu_data[label]= (int(temperature)//1000)
                            temperature_folder_path[label]= t #cache the CPU label and folder path

     
                    if (("input" in temp_name) and ("fan" in temp_name)):
                        fan_speed_file= os.path.join(folder_path, temp_name)
                        f= open(fan_speed_file)
                        fan_speed= f.read().strip()
                        cpu_data["CPU Fan"]= fan_speed
                        temperature_folder_path["CPU Fan"]= f #cache the fan file path

                if "CPU Fan" not in cpu_data:
                    cpu_data["CPU Fan"]= "N/A"

            except (RuntimeError, UnboundLocalError, FileNotFoundError):
                    cpu_data= {
                        "Core": "N/A",
                        "Package id 0": "N/A",
                        "CPU Fan": "N/A"
                    }            
        else:
            cpu_data = {label: 0 for label in temperature_folder_path}
            for key in temperature_folder_path:
                t= temperature_folder_path[key]
                t.seek(0)
                reading= int(t.read().strip())
                cpu_data[key] = (int(reading)//1000)

            if "CPU Fan" not in temperature_folder_path:
                cpu_data["CPU Fan"]= "N/A"

    else:
        cpu_data= {
            "Core": "N/A",
            "Package id 0": "N/A",
            "CPU Fan": "N/A"
            }

    return cpu_data, temperature_folder_path

def memory_readings(memory_disable, path):
    data={}
    if memory_disable is False:
        try:
            for line in path.get_file("meminfo"):
                    if (("MemTotal" not in line) and ("MemAvailable" not in line) and ("SwapTotal" not in line) and ("SwapFree" not in line)):
                        continue #skips lines that are not relevant
                    key, value= line.split(":", 1)
                    value= int(value.strip().split()[0])
                    data[key]= int(value)
                
        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            data= {
            "MemTotal": "N/A",
            "MemAvailable": "N/A",
            "SwapTotal": "N/A",
            "SwapFree": "N/A"
        }
    
    else:
        data= {
            "MemTotal": "N/A",
            "MemAvailable": "N/A",
            "SwapTotal": "N/A",
            "SwapFree": "N/A"
        }

    return data

def system_pressure(cpu_disable,memory_disable,file_paths):
    data_memory={
        "some": {},
        "full": {}
    }
    data_cpu={}
    if cpu_disable is False:
        try:
            for line in file_paths.get_file("cpu_pressure"):
                    if "full" in line:
                        break
                    line= line.strip()
                    for i, token in enumerate(line.split()):
                        if token == "some":
                            continue
                        key, value= token.split("=", 1)
                        value= round(float(value.strip()), 1)
                        data_cpu[key]= value
                            
        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            data_cpu["avg10"]= "N/A"
            data_cpu["avg60"]= "N/A"
            data_cpu["avg300"]= "N/A"
            data_cpu["total"]= "N/A"
    else:
            data_cpu["avg10"]= "N/A"
            data_cpu["avg60"]= "N/A"
            data_cpu["avg300"]= "N/A"
            data_cpu["total"]= "N/A"

    if memory_disable is False:
        try:
            for line in file_paths.get_file("mem_pressure"):
                    split= line.strip().split(" ")
                    if "some" in line:
                        for _, token in enumerate(split):
                            if token == "some":
                                    continue
                            key, value= token.split("=", 1)
                            value= value.strip()
                            data_memory["some"][key]= float(value)
                    if "full" in line:
                        for _, token in enumerate(split):
                            if token == "full":
                                    continue
                            key, value= token.split("=", 1)
                            value= value.strip()
                            data_memory["full"][key]= float(value)

        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            data_memory["some"]["avg10"]= "N/A"
            data_memory["some"]["avg60"]= "N/A"
            data_memory["some"]["avg300"]= "N/A"
            data_memory["some"]["total"]= "N/A"
            data_memory["full"]["avg10"]= "N/A"
            data_memory["full"]["avg60"]= "N/A"
            data_memory["full"]["avg300"]= "N/A"
            data_memory["full"]["total"]= "N/A"
    else:
            data_memory["some"]["avg10"]= "N/A"
            data_memory["some"]["avg60"]= "N/A"
            data_memory["some"]["avg300"]= "N/A"
            data_memory["some"]["total"]= "N/A"
            data_memory["full"]["avg10"]= "N/A"
            data_memory["full"]["avg60"]= "N/A"
            data_memory["full"]["avg300"]= "N/A"
            data_memory["full"]["total"]= "N/A"

    return data_cpu, data_memory
              
def get_cpu_load(cpu_check_disable, file_path, previous_data= None):
    if previous_data is None:
        previous_data={}
    load_usage= {}
    data= {}
    deltas={}
    #values below should be in predefined positions and they should all exist for modern kernels
    #https://man7.org/linux/man-pages/man5/proc_stat.5.html
    values = ["user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal", "guest", "guest_nice"]

    if cpu_check_disable is False:
        try:
            for line in file_path.get_file("stat"):
                    if line.startswith("cpu"):
                        split= line.strip()
                        split= split.split()
                        for i in range(len(split)):
                            if "cpu" in split[i]:
                                if "cpu" == split[i]:
                                    identifier= "CPU"
                                    data[identifier]= {}
                                else:
                                    identifier= f"CPU {split[i].strip("cpu")}"
                                    data[identifier]= {}
                            else:
                                data[identifier][values[i-1]]= int(split[i].strip())
                    else:
                        continue

        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            load_usage={
                    "CPU": "N/A",
                    "CPU 0": "N/A",
                    }
            
        if previous_data != {}:
            # for cpu, fields in data.items():
            #     prev_fields = previous_data[cpu]

            #     sum_deltas = 0
            #     for i in values:
            #         delta = fields[i] - prev_fields[i]   # already ints
            #         sum_deltas += delta

            #     if cpu == "CPU":
            #         total_cpu_load_delta = sum_deltas
                
            #     idle_time = prev_fields["idle"] + prev_fields["iowait"]
            #     load_usage[cpu]= round(((sum_deltas - idle_time)/sum_deltas * 100), 1)

            for cpu in data:
                deltas[cpu]= {}
                sum_deltas= 0

                for i in values:
                    deltas[cpu][i]= data[cpu][i] - previous_data[cpu][i]
                    sum_deltas= sum_deltas + deltas[cpu][i]
                
                idle_time = deltas[cpu]["idle"] + deltas[cpu]["iowait"]
                load_usage[cpu]= round(((sum_deltas - idle_time)/sum_deltas * 100), 1)
        else:
            load_usage={
                "CPU": 0,
                "CPU 0": 0,
                }
    return data,load_usage

def network_traffic(file_path, previous_data= None, previous_time= None):
    if previous_data is None:
        previous_data={}
    if previous_time is None:
        previous_time= time.monotonic()
    data={}
    network_data= {}
    current_time= time.monotonic()
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

class ProcessStat:
    """Is a single process' essential stats."""

    __slots__ = (
        "name",
        "utime",
        "stime",
        "process_time",
        "num_threads",
        "vsize",
        "rss",
        "starttime",
        "state",
        "priority",
    )
    #need to offset stat_list by 3
    def __init__(self, name, stats_list):
        self.name = name
        self.state= stats_list[0]
        self.utime = int(stats_list[11])
        self.stime = int(stats_list[12])
        self.process_time = self.utime + self.stime
        self.num_threads = int(stats_list[17])
        self.vsize = int(stats_list[20])//1048576
        self.rss = int(stats_list[21])
        self.starttime = int(stats_list[19])
        self.priority= int(stats_list[15])

class ProcessStatus:

    __slots__ = (
            "PPid",
            "Uid",
            "Gid",
    )

    def __init__(self):
        pass

def current_processes(prev_stat_data= None, data_length= 300, status_index= 0,prev_time= None, ticks_per_second= None):
    #https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
    if ticks_per_second is None:
        ticks_per_second = os.sysconf(os.sysconf_names["SC_CLK_TCK"]) #used for process load calculation
    current_time = time.monotonic() #used to calculate the difference in time between current and last calculation
    if prev_time is not None:
        time_delta= current_time - prev_time
    else:
        time_delta= -1
    path= "/proc"
    stat_data = {} #process cpu load and mem consumption
    status_data={} #process info and mem consumption

    process_cpu_load= {}
    data_length_index=0
    if status_index == 2:
        status_scan= True
        status_index= 0
    else:
        status_scan= False
        status_index+= 1

    for proc_folder_path in os.scandir(path):
        if not proc_folder_path.name.isdigit():
            continue  

        PID= int(proc_folder_path.name)
        if data_length_index < data_length:
            data_length_index+= 1
            stat_file= f"{path}/{PID}/stat"
            try:
                with open(stat_file) as f:
                    line= f.readline()
                    _, _, rest = line.partition("(")
                    name, _, stats = rest.partition(")")
                    stats_list= stats.split()
                    process= ProcessStat(name,stats_list)
                    stat_data[PID]= process
            except FileNotFoundError:
                #handles exception for new processes that are killed while I'm reading them
                try:
                    del stat_data[PID]
                except:
                    continue

            #does the calculation only once every 2 times
            if status_scan is True:
                status_file= f"{path}/{PID}/status"
                proc_status= ProcessStatus()
                try:
                    with open(status_file) as f:
                        for line in f:
                            key, value= line.split(":", 1)
                            key= key.strip()
                            if key in ProcessStatus.__slots__:
                                setattr(proc_status, key, value.strip())
                            
                        status_data[PID]= proc_status

                except FileNotFoundError:
                    #handles exception for new processes that are killed while I'm reading them
                    try:
                        del status_data[PID]
                    except:
                        continue
    
    if (prev_stat_data is not None) and (time_delta > 0):
        common_pids = prev_stat_data.keys() & stat_data.keys()
        for PID in common_pids:
                #PID reuse handling 
                if stat_data[PID].starttime != prev_stat_data[PID].starttime: 
                   continue

                #handling process restart
                process_time_delta= stat_data[PID].process_time- prev_stat_data[PID].process_time
                if process_time_delta < 0: 
                     continue
                
                process_time_delta_sec= process_time_delta / ticks_per_second
                cpu_load_percetange= round((process_time_delta_sec / time_delta)* 100, 1) #normalizez based on the number of threads
                process_cpu_load[PID]= cpu_load_percetange

    return stat_data, status_data, process_cpu_load, status_index, current_time, ticks_per_second


# def main():
#     status_index= 2
#     stat_data, status_data, process_cpu_load, status_index= current_processes()
#     print(process_cpu_load)
    

# if __name__ == "__main__":
#      raise SystemExit(main())