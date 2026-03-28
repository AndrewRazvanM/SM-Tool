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

    def close(self):
        os_close(self.fan_file)

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

class CPUInfoTemp:
    """
    Handles CPU Temperature and Fan readings only.
    """
    __slots__ = (
        "file_path",
        "cpu_name",
        "sensor_name",
        "cpu_sensor_path",
        "cpu_temp",
        "cpu_fan"
    )

    def __init__(self, file_path: object):
        self.file_path = file_path
        self.sensor_name, self.cpu_sensor_path = self.__probe_cpu_sensors()
        self.cpu_name = self.__get_cpu_name()
        self.cpu_temp = None
        self.cpu_fan = None

    def __get_cpu_name(self):
        path = "/proc/cpuinfo"
        try:
            with open(path) as f:
                for line in f:
                    if line.startswith("model name"):
                        _, cpu_name = line.strip().split(":", 1)
                        return cpu_name.strip()
        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            return "N/A"

    def __probe_cpu_sensors(self):
        path = "/sys/class/hwmon"
        sensors = ("x86_pkg_temp", "coretemp", "cpu_thermal", "tcpu", "acpitz")
        temp_sensors = {}
        sensor_name, cpu_sensor_path = "N/A", "N/A"

        try:
            for sensor_file in scandir(path):
                sensor_folder_path = os_path.join(path, sensor_file)
                sensor_type_file = os_path.join(sensor_folder_path, "name")

                if not os_path.isdir(sensor_folder_path) or not os_path.isfile(sensor_type_file):
                    continue

                with open(sensor_type_file) as t:
                    temp_sensors[t.read().strip()] = sensor_folder_path

            for match in sensors:
                if match in temp_sensors:
                    return match, temp_sensors[match]

            return sensor_name, cpu_sensor_path

        except FileNotFoundError:
            return sensor_name, cpu_sensor_path

    def get_cpu_temp(self, disable_cpu_check: bool, schedule: dict):
        if schedule.get("cpu") is False or disable_cpu_check:
            return
        
        cpu_sensor_path = self.cpu_sensor_path
        if cpu_sensor_path == "N/A":
            return

        cpu_temp = self.cpu_temp or {}
        cpu_fan = self.cpu_fan or {}
        average_temp = 0
        temp_index = 0
        cpu_label_index = -1
        fan_label = -1

        if not cpu_temp:
            for hwon_folder in scandir(cpu_sensor_path):
                file_name = hwon_folder.name

                if file_name.startswith("temp") and file_name.endswith("input"):
                    file_path = hwon_folder.path
                    temp_file_descriptor = os_open(file_path, os_O_RDONLY)
                    temp_bytes = os_pread(temp_file_descriptor, 16, 0)
                    temperature = int(temp_bytes)

                    file_label_path = file_path[:-5] + "label"
                    try:
                        with open(file_label_path) as l:
                            label = l.read().strip()
                    except FileNotFoundError:
                        cpu_label_index += 1
                        label = f"CPU {cpu_label_index}"

                    cpu_temp[label] = CPUTemp(temperature, temp_file_descriptor)
                    if label != "Package id 0":
                        average_temp += temperature // 1000
                        temp_index += 1

                elif file_name.startswith("fan") and file_name.endswith("input"):
                    fan_file_path = hwon_folder.path
                    fan_file_descriptor = os_open(fan_file_path, os_O_RDONLY)
                    fan_bytes = os_pread(fan_file_descriptor, 16, 0)
                    fan_rpm = int(fan_bytes.strip())

                    fan_label_path = fan_file_path[:-5] + "label"
                    try:
                        with open(fan_label_path) as l:
                            fan_label = l.read().strip()
                    except FileNotFoundError:
                        fan_label += 1

                    cpu_fan[fan_label] = CPUFan(fan_rpm, fan_file_descriptor)

            average_temp = average_temp // max(1, temp_index)
            cpu_temp["Average"] = average_temp
            self.cpu_temp = cpu_temp
            self.cpu_fan = cpu_fan
        else:
            # Update existing readings
            for key, reading in cpu_temp.items():
                if key != "Average":
                    reading.update()
                    if key != "Package id 0":
                        average_temp += reading.temp
                        temp_index += 1
            cpu_temp["Average"] = average_temp // max(1, temp_index)
            self.cpu_temp = cpu_temp

            if cpu_fan:
                for fan in cpu_fan.values():
                    fan.update()
            self.cpu_fan = cpu_fan

    def close_temp_files(self):
        if self.cpu_temp:
            for key, temp_obj in self.cpu_temp.items():
                if key != "Average":
                    temp_obj.close()
        if self.cpu_fan:
            for fan_obj in self.cpu_fan.values():
                fan_obj.close()

class CPUInfoLoad:
    """
    Handles CPU Load readings only.
    """
    __slots__ = (
        "file_path",
        "cpu_load",
        "cpu_load_deltas",
        "cpu_load_raw_data",
        "cpu_load_raw_data_prev"
    )

    def __init__(self, file_path):
        self.file_path = file_path
        self.cpu_load = None
        self.cpu_load_deltas = None
        self.cpu_load_raw_data = None
        self.cpu_load_raw_data_prev = None
        self.get_cpu_load(False, {"cpu": True}) #needed to initialyze the CPU dashboard in the TUI

    def get_cpu_load(self, disable_cpu_check: bool, schedule: dict):
        if schedule.get("cpu") is False or disable_cpu_check:
            return

        values = ("user", "nice", "system", "idle", "iowait", "irq",
                  "softirq", "steal", "guest", "guest_nice")

        cpu_load = self.cpu_load or {}
        cpu_load_deltas = self.cpu_load_deltas or {}
        cpu_load_raw_data = self.cpu_load_raw_data or {}
        file_path = self.file_path

        try:
            for line in file_path.get_file("stat"):
                if line.startswith("cpu"):
                    parts = line.strip().split()
                    cpu_field = parts[0]

                    identifier = "Total" if cpu_field == "cpu" else f"CPU {cpu_field[3:]}"
                    cpu_load_raw_data[identifier] = {k: int(parts[i + 1]) for i, k in enumerate(values)}
            file_read = True
        except FileNotFoundError:
            self.cpu_load = {"CPU": "N/A", "CPU 0": "N/A"}
            file_read = False

        if file_read:
            if self.cpu_load_raw_data_prev:
                if not cpu_load_deltas:
                    cpu_load_deltas = {cpu: {} for cpu in cpu_load_raw_data}

                for cpu in cpu_load_raw_data:
                    sum_deltas = 0
                    for key in values:
                        delta = cpu_load_raw_data[cpu][key] - self.cpu_load_raw_data_prev[cpu][key]
                        cpu_load_deltas[cpu][key] = delta
                        sum_deltas += delta

                    if sum_deltas > 0:
                        idle_time = cpu_load_deltas[cpu]["idle"] + cpu_load_deltas[cpu]["iowait"]
                        cpu_load[cpu] = round(((sum_deltas - idle_time) / sum_deltas) * 100, 1)
            else:
                cpu_load = {cpu: "N/A" for cpu in cpu_load_raw_data}

            self.cpu_load = cpu_load
            self.cpu_load_deltas = cpu_load_deltas
            self.cpu_load_raw_data_prev = cpu_load_raw_data.copy()
        self.cpu_load_raw_data = cpu_load_raw_data