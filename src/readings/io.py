from time import monotonic

class DeviceIO:
    """
    Stores information about individual devices
    """
    __slots__ = (
        "major_id",
        "sectors_read",
        "sectors_written",
        "reads_completed",
        "writes_completed",
        "ios_in_progress",
        "time_doing_ios_ms",
        "read_throughput",
        "write_throughput",
        "iops",
        "time_busy"
    )

    def __init__ (self, list):
        self.major_id= int(list[0])
        self.reads_completed= int(list[3])
        self.sectors_read= int(list[5])
        self.writes_completed= int(list[7])
        self.sectors_written= int(list[9])
        self.ios_in_progress= int(list[11])
        self.time_doing_ios_ms= int(list[12])
        self.read_throughput= None
        self.write_throughput= None
        self.iops= None
        self.time_busy= None

    def update(self, list, time_delta, sectors_size):
        
        sectors_read= int(list[5])
        sectors_written= int(list[9])
        reads_completed= int(list[3])
        time_doing_ios_ms= int(list[12])

        self.read_throughput = ((sectors_read - self.sectors_read) * sectors_size) / time_delta
        self.write_throughput= ((sectors_written - self.sectors_written) * sectors_size) / time_delta
        self.iops= (reads_completed - self.reads_completed) / time_delta
        self.time_busy= (time_doing_ios_ms - self.time_doing_ios_ms) / time_delta

        self.reads_completed= reads_completed
        self.sectors_read= sectors_read
        self.writes_completed= int(list[7])
        self.sectors_written= sectors_written
        self.ios_in_progress= int(list[11])
        self.time_doing_ios_ms= time_doing_ios_ms
        
class ReadTotalIO:

    def __init__(self, file_path: object):
        self.file_path= file_path
        self.sectors_size= 512 #to implement actual check later
        self.devices_total_io= {}
        self.prev_time= monotonic()

    def read_io_totals(self):
        """
        Gets the current readings for I/O Totals and updates the calculations where needed.
        """
        current_time= monotonic()
        time_delta= current_time - self.prev_time
        self.prev_time= current_time
        sectors_size= self.sectors_size

        for line in self.file_path.get_file("disk_info"):
            list= line.split(None, 13)
            name= list[2]
            
            #check for devices that matter
            if name.startswith(("loop", "ram")):
                continue

            if name.startswith("sd") and  name[-1].isdigit():
                continue

            if "p" in name and name[-1].isdigit():
                continue
            
            if name not in self.devices_total_io:
                self.devices_total_io[name]= DeviceIO(list)
            
            else:
                self.devices_total_io[name].update(list, time_delta, sectors_size)
