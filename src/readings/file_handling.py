class NeededFiles:
    def __init__(self):
        self.files = {
            "net": open("/proc/net/dev", "r"),
            "stat": open("/proc/stat", "r"),
            "mem_pressure": open("/proc/pressure/memory", "r"),
            "cpu_pressure": open("/proc/pressure/cpu", "r"),
            "meminfo": open("/proc/meminfo", "r"),
            "disk_info": open("/proc/diskstats", "r")
        }

    def get_file(self, name):
        f = self.files[name]
        f.seek(0)
        return f

    def close_all(self):
        for f in self.files.values():
            f.close()
        self.files.clear()
