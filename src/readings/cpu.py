from os import scandir
from os import path as os_path

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
                    for sensor_file in scandir(path):
                        folder_path= os_path.join(path, sensor_file)
                        sensor_type_file= os_path.join(folder_path, "name")

                        if not os_path.isdir(folder_path):
                            continue
                        if not os_path.isfile(sensor_type_file):
                            continue

                        with open(sensor_type_file) as t:
                            sensor_name= t.read().strip()

                        if sensor_name == sensor_check:
                            found_sensor= True
                            break
    except FileNotFoundError:
        sensor_name= "N/A"

    return sensor_name, folder_path

def get_cpu_temp(cpu_check_disable= bool,folder_path=str, temperature_folder_path= None):

    if cpu_check_disable is False:
        if temperature_folder_path is None:
            temperature_folder_path={}
            cpu_data= {}
            try:
                for find_temperatures in scandir(folder_path):
                    temp_name= find_temperatures.name
                    if "temp" in temp_name:
                        if "input" in temp_name: 
                            sensor_temp_path= find_temperatures.path
                            cpu_label= int("".join(ch for ch in temp_name if ch.isdigit()))     
                            cpu_number= os_path.join(folder_path,f"temp{cpu_label}_label")                   
                            t= open((sensor_temp_path))
                            temperature= int(t.read().strip())
                            with open(cpu_number) as l:
                                label=  str(l.read().strip())
                                cpu_data[label]= (int(temperature)//1000)
                            temperature_folder_path[label]= t #cache the CPU label and folder path

     
                    if (("input" in temp_name) and ("fan" in temp_name)):
                        fan_speed_file= os_path.join(folder_path, temp_name)
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
                        break

        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            load_usage={
                    "CPU": "N/A",
                    "CPU 0": "N/A",
                    }
            
        if previous_data != {}:

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

