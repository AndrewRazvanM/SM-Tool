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
        "time_spent_reading_ms",
        "time_spent_writing_ms",
        "read_throughput",
        "write_throughput",
        "read_iops",
        "write_iops",
        "time_busy",
        "read_latency",
        "write_latency"
    )

    def __init__ (self, fields):
        self.major_id= int(fields[0])
        self.reads_completed= int(fields[3])
        self.sectors_read= int(fields[5])
        self.writes_completed= int(fields[7])
        self.sectors_written= int(fields[9])
        self.ios_in_progress= int(fields[11])
        self.time_doing_ios_ms= int(fields[12])
        self.time_spent_reading_ms = int(fields[6])
        self.time_spent_writing_ms = int(fields[10])
        self.read_throughput= "N/A"
        self.write_throughput= "N/A"
        self.read_iops= "N/A"
        self.write_iops= "N/A"
        self.time_busy= "N/A"
        self.read_latency= "N/A"
        self.write_latency= "N/A"

    def update(self, fields, time_delta, sectors_size):
        
        sectors_read = int(fields[5])
        sectors_written = int(fields[9])
        reads_completed = int(fields[3])
        writes_completed = int(fields[7])
        time_doing_ios_ms = int(fields[12])
        time_spent_reading_ms = int(fields[6])
        time_spent_writing_ms = int(fields[10])

        self.read_throughput = ((sectors_read - self.sectors_read) * sectors_size) / time_delta
        self.write_throughput = ((sectors_written - self.sectors_written) * sectors_size) / time_delta
        self.read_iops = (reads_completed - self.reads_completed) / time_delta
        self.write_iops = (writes_completed - self.writes_completed) / time_delta
        self.time_busy = (((time_doing_ios_ms - self.time_doing_ios_ms)/1000) / time_delta) * 100

        read_ops_delta = reads_completed - self.reads_completed
        read_time_delta = time_spent_reading_ms - self.time_spent_reading_ms
        if read_ops_delta > 0:
            self.read_latency = read_time_delta / read_ops_delta
        else:
            self.read_latency = 0.0

        write_ops_delta = writes_completed - self.writes_completed
        write_time_delta = time_spent_writing_ms - self.time_spent_writing_ms
        if write_ops_delta > 0:
            self.write_latency = write_time_delta / write_ops_delta
        else:
            self.write_latency = 0.0

        self.reads_completed = reads_completed
        self.sectors_read = sectors_read
        self.writes_completed = writes_completed
        self.sectors_written = sectors_written
        self.ios_in_progress = int(fields[11])
        self.time_doing_ios_ms = time_doing_ios_ms
        self.time_spent_reading_ms = time_spent_reading_ms
        self.time_spent_writing_ms = time_spent_writing_ms
        
class ReadTotalIO:

    __slots__ = (
        "file_path",
        "sectors_size",
        "devices_total_io",
        "prev_time"
    )

    def __init__(self, file_path: object):
        self.file_path= file_path
        self.sectors_size= 512 #to implement actual check later
        self.devices_total_io= {}
        self.prev_time= monotonic()

    def read_io_totals(self, schedule: dict):
        """
        Gets the current readings for I/O Totals and updates the calculations where needed.
        """

        if schedule["io"] is False:
            return

        current_time= monotonic()
        time_delta= current_time - self.prev_time
        self.prev_time= current_time
        sectors_size= self.sectors_size

        try:
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

        except FileNotFoundError:
            return
