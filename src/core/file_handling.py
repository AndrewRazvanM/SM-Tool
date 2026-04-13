class NeededFiles:
    def __init__(self):
        self.files = {}

        # always expected
        self.files["net"] = open("/proc/net/dev", "r")
        self.files["stat"] = open("/proc/stat", "r")
        self.files["meminfo"] = open("/proc/meminfo", "r")
        self.files["disk_info"] = open("/proc/diskstats", "r")
        self.files["system_up_time"] = open("/proc/uptime", "r")

        try:
            self.files["cpu_pressure"] = open("/proc/pressure/cpu", "r")
        except FileNotFoundError:
            self.files["cpu_pressure"] = None  # could also log a warning

        try:
            self.files["io_pressure"] = open("/proc/pressure/io", "r")
        except FileNotFoundError:
            self.files["io_pressure"] = None

        try:
            self.files["mem_pressure"] = open("/proc/pressure/memory", "r")
        except FileNotFoundError:
            self.files["mem_pressure"] = None

    def get_file(self, name: str):
        f = self.files[name]
        if f is None:
            raise FileNotFoundError(f"{name} not available")
        f.seek(0)
        return f

    def close_all(self):
        for f in self.files.values():
            f.close()
        self.files.clear()
