from os import scandir, path as os_path, open as os_open, O_RDONLY as os_O_RDONLY, pread as os_pread, close as os_close

class CPUFan:
    __slots__=(
        "fan_file",
        "rpm"
    )

    def __init__(self, rpm, fan_file: bytes):
        self.fan_file= fan_file
        self.rpm= rpm

    def update(self):
        file_read= os_pread(self.fan_file, 16, 0)
        self.rpm= int(file_read)

class CPUTemp:
    __slots__= (
        "temp_file",
        "temp",
    )

    def __init__(self, temperature: int, temp_file_descriptor):
        self.temp_file= temp_file_descriptor
        self.temp= temperature//1000
        
    def update(self):
        file = os_pread(self.temp_file, 16, 0)
        self.temp= int(file)//1000

    def close(self):
        os_close(self.temp_file)

class CPUInfo:
    """
    Collects CPU information (Temperature, Load, Fan). Also caches the path for the temperature files.
        The available functions are:
            get_cpu_temp()
            get_cpu_load()
    """
    __slots__= (
        "file_path",
        "cpu_name",
        "sensor_name",
        "cpu_sensor_path",
        "cpu_temp",
        "cpu_fan",
        "cpu_load",
        "cpu_load_deltas",
        "cpu_load_raw_data",
        "cpu_load_raw_data_prev",
    )

    def __init__(self, file_path: object):

        self.sensor_name, self.cpu_sensor_path= self.__probe_cpu_sensors()

        self.file_path= file_path
        self.cpu_temp= None
        self.cpu_load= None
        self.cpu_load_deltas= None
        self.cpu_load_raw_data= None
        self.cpu_load_raw_data_prev= None
        self.cpu_fan= None
        self.cpu_name= self.__get_cpu_name()
        self.get_cpu_load(False, {"cpu": True})

    def __get_cpu_name(self):
        path= "/proc/cpuinfo"
        try:
            with open(path) as f:
                for line in f:
                    if line.startswith("model name"):
                        _, cpu_name = line.strip().split(":")
                        return cpu_name
                    else:
                        continue
    
        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            self.cpu_name= "N/A"

    def __probe_cpu_sensors(self):
        path= "/sys/class/hwmon"
        sensors= (
        "x86_pkg_temp",
        "coretemp",
        "cpu_thermal",
        "tcpu",
        "acpitz",
        )
        sensor_name= "N/A"
        temp_sensors= {}        

        try:
            for sensor_file in scandir(path):
                sensor_folder_path= os_path.join(path, sensor_file)
                sensor_type_file= os_path.join(sensor_folder_path, "name")

                if not os_path.isdir(sensor_folder_path):
                    continue
                if not os_path.isfile(sensor_type_file):
                    continue

                with open(sensor_type_file) as t:
                    sensor_name= t.read().strip()
                
                temp_sensors[sensor_name]= sensor_folder_path

        except FileNotFoundError:
            return

        for match in sensors:
            if match in temp_sensors:
                return match, temp_sensors[match]

    def get_cpu_temp(self, disable_cpu_check: bool, schedule: dict):
        if schedule["cpu"] is False:
            return
        
        if disable_cpu_check is False:
            cpu_sensor_path= self.cpu_sensor_path
            cpu_temp= self.cpu_temp
            cpu_fan= self.cpu_fan
            label=-1 #CPU label files are optional. Adding this as an alternative when it's not available
            fan_label= -1 #same as above
            
            if cpu_sensor_path is None:
                return 

            average_temp= 0
            temp_index= 0

            if cpu_temp is None:
                cpu_temp= {}
                cpu_fan= {}
                

                for hwon_folder in scandir(cpu_sensor_path):
                    file_name= hwon_folder.name
                    
                    if file_name.startswith("temp"):
                        if file_name.endswith("input"):
                            file_path= hwon_folder.path
                            temp_file_descriptor= os_open(file_path, os_O_RDONLY)
                            temp_file= os_pread(temp_file_descriptor, 16, 0)
                            temperature= int(temp_file)

                            file_label_path= file_path[:-5] + "label"
                            try:
                                with open(file_label_path) as l:
                                    label= str(l.read().strip())
                            except FileNotFoundError:
                                label+= 1

                            cpu_temp[label]= CPUTemp(temperature, temp_file_descriptor)

                            if label != "Package id 0":
                                average_temp+= temperature//1000
                                temp_index+= 1
                                
                    elif file_name.startswith("fan"):
                        if file_name.endswith("input"):
                            fan_file_path= hwon_folder.path
                            fan_file= os_open(fan_file_path, os_O_RDONLY)
                            fan_rpm= fan_file.read().strip()

                            fan_file_label_path= fan_file_path[:-5] + "label"
                                
                            try:
                                with open(fan_file_label_path) as l:
                                    fan_label= str(l.read().strip())

                            except FileNotFoundError:
                                fan_label+= 1

                            fan_readings= CPUFan(fan_rpm, fan_file)
                            cpu_fan[fan_label]= fan_readings

                average_temp= average_temp//temp_index
                cpu_temp["Average"]= average_temp
                self.cpu_temp= cpu_temp
                self.cpu_fan= cpu_fan

            else:
                for new_reading in cpu_temp:
                    if new_reading != "Average":
                        cpu_temp[new_reading].update()
                        if new_reading != "Package id 0":
                            average_temp+= cpu_temp[new_reading].temp
                            temp_index+= 1

                average_temp= average_temp//temp_index
                cpu_temp["Average"]= average_temp

                self.cpu_temp= cpu_temp

                if cpu_fan is not None and cpu_fan != {}:
                    for new_reading in cpu_fan:
                        cpu_fan[new_reading].update()
                
                self.cpu_fan= cpu_fan

    def get_cpu_load(self, disable_cpu_check:bool, schedule: dict):
        if schedule["cpu"] is False:
            return
        
        values = ("user", "nice", "system", "idle", "iowait", "irq",
                "softirq", "steal", "guest", "guest_nice")

        if disable_cpu_check:
            return

        cpu_load = self.cpu_load or {}
        cpu_load_deltas = self.cpu_load_deltas or {}
        cpu_load_raw_data = self.cpu_load_raw_data or {}
        file_path = self.file_path

        try:
            for line in file_path.get_file("stat"):
                if line.startswith("cpu"):
                    parts = line.strip().split()
                    cpu_field = parts[0]

                    # Determine CPU identifier
                    if cpu_field == "cpu":
                        identifier = "Total"
                    else:
                        identifier = f"CPU {cpu_field[3:]}"  # Remove "cpu" prefix

                    # Initialize per-CPU dict
                    cpu_load_raw_data[identifier] = {}

                    # Populate values
                    for i, key in enumerate(values):
                        cpu_load_raw_data[identifier][key] = int(parts[i + 1])
            file_read = True
            
        except FileNotFoundError:
            self.cpu_load = {"CPU": "N/A", "CPU 0": "N/A"}
            file_read = False

        if file_read:
            if self.cpu_load_raw_data_prev:
                # Initialize deltas if empty
                if not cpu_load_deltas:
                    cpu_load_deltas = {cpu: {} for cpu in cpu_load_raw_data}

                for cpu in cpu_load_raw_data:
                    sum_deltas = 0
                    for key in values:
                        delta = cpu_load_raw_data[cpu][key] - self.cpu_load_raw_data_prev[cpu][key]
                        cpu_load_deltas[cpu][key] = delta
                        sum_deltas += delta

                    if sum_deltas <= 0:
                        break
                    
                    idle_time = cpu_load_deltas[cpu]["idle"] + cpu_load_deltas[cpu]["iowait"]
                    cpu_load[cpu] = round(((sum_deltas - idle_time) / sum_deltas) * 100, 1)

                self.cpu_load = cpu_load
                self.cpu_load_deltas = cpu_load_deltas
            else:
                # No previous data yet
                self.cpu_load = {cpu: "N/A" for cpu in cpu_load_raw_data}

            # Save raw data for next calculation
            self.cpu_load_raw_data_prev = cpu_load_raw_data.copy()

        self.cpu_load_raw_data = cpu_load_raw_data
            
    def close_temp_files(self):
        cpu_temp= self.cpu_temp
        if cpu_temp is not None:
            for cpu in cpu_temp:
                cpu_temp[cpu].close()
