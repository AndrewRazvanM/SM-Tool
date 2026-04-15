from os import scandir, sysconf, sysconf_names, open as os_open, O_RDONLY as os_O_RDONLY, pread, close as os_close
from time import monotonic
import cython

cdef class ProcessInfo:

    cdef public:
        int uid, ppid, utime, stime, num_threads, priority
        long vsize, rss, starttime, process_time
        double cpu_load, process_up_time
        str name, state, command        
    
    #need to offset stat_list by 3
    def __init__(self, name, starttime, uid=None):
        self.name = name.decode()
        self.cpu_load= 0
        self.uid= int(uid)
        self.ppid= 0
        self.utime = 0
        self.stime = 0
        self.process_time = 0
        self.num_threads = 0
        self.vsize = 0
        self.rss = 0
        self.starttime = starttime
        self.priority= 0
        self.command= " "

class SystemUsername:

    __slots__ = (
        "name", # This is the user's login name
        "UID" # This is the user's ID
    )

    def __init__ (self, line):
        self.name, _, self.UID, _= line.strip().split(":", 3)

class ProcessMonitor:
    """
    Stores and updates the process lists.
     The update method can take a maximum number of processes scanned.
    """
    __slots__=(
        "__page_size",
        "ticks_per_second",
        "__prev_process_time",
        "__proc_path",
        "__sys_up_time_file",
        "user_list",
        "current_user",
    )

    def __init__(self, file_path: object):
        self.__page_size = sysconf("SC_PAGE_SIZE") #for calculating consumed memory
        self.ticks_per_second = sysconf(sysconf_names["SC_CLK_TCK"]) #used for process load calculation
        self.__prev_process_time= monotonic()
        self.__proc_path= "/proc"
        self.__sys_up_time_file= file_path
        self.user_list, self.current_user= self.__get_process_username()

    def _get_system_uptime(self):
       
        up_time= float(self.__sys_up_time_file.get_file("system_up_time").read().split()[0])

        return up_time

    def __get_process_username(self):

        path= "/etc/passwd"
        current_user_path= "/var/run/user"
        username_data= {}
        current_user_data= {}

        try:
            with open(path) as f:
                for line in f:
                    username_object= SystemUsername(line)
                    username_data[int(username_object.UID)]= username_object.name

        except FileNotFoundError:
            username_data[0]= "root"
        
        try:
            for username_folder in scandir(current_user_path):
                username_string= username_data[int(username_folder.name)]
                current_user_data[username_string]= True
        
        except FileNotFoundError:
            pass

        return username_data, current_user_data

    #tested with 30.000 dummy processes on my machine. So that data_length should be fine. 
    def update(self, schedule: dict, process_list: dict, data_length=30000) -> dict: 
        if schedule["processes"] is False:
            return
        
        current_time= monotonic()
        time_delta= current_time - self.__prev_process_time
        self.__prev_process_time= current_time
        data_length_index= 0
        current_pids= set() #used to remove old entires in process_list
        sys_up_time= self._get_system_uptime()

        for proc_folder_path in scandir(self.__proc_path):
            
            pid_proc_path= proc_folder_path.path
            pid_proc_string= proc_folder_path.name
            if not pid_proc_string.isdigit():
                    continue  
            
            if data_length_index < data_length:
                data_length_index+= 1
            else:
                break
                
            PID= int(pid_proc_string)
            current_pids.add(PID)
            stat_file= pid_proc_path + "/stat"

            try:
                file_descriptor = os_open(stat_file, os_O_RDONLY)
                line= pread(file_descriptor, 512, 0)
                name_start = line.index(b"(")
                name_end = line.index(b") ", name_start) #edge case handling
                name = line[name_start + 1:name_end]
                stats_list= line[name_end + 2:].split(None, 22)

                ppid= stats_list[1]
                state= stats_list[0].decode()
                utime = int(stats_list[11])
                stime = int(stats_list[12])
                process_time = utime + stime
                num_threads = int(stats_list[17])
                vsize = int(stats_list[20]) >> 20 #Converts to MiB
                rss = (int(stats_list[21]) * self.__page_size) >> 20 #converts to bytes then MiB
                starttime = int(stats_list[19])
                priority= int(stats_list[15])
                process_up_time= sys_up_time - (starttime/self.ticks_per_second)
                os_close(file_descriptor)

            except FileNotFoundError:
                #handles exception for new processes that are killed while I'm reading them. 
                continue

            #scan for process UID and comm only when it's a new process or the process restarted
            uid= None
            if PID not in process_list or process_list[PID].starttime != starttime:
                status_file= pid_proc_path + "/status"
                cmdline_file= pid_proc_path + "/cmdline"
                try:
                    with open(cmdline_file, "rb") as f:
                        raw = f.read()

                    if raw:
                        comm = raw.replace(b"\x00", b" ").decode().strip()
                    else:
                        comm = " "

                except FileNotFoundError:
                    continue

                try:
                    with open(status_file) as f:
                        for line in f:
                            if line.startswith("Uid"):  
                                uid= line.split()[1]
                                        
                            if uid:
                                break

                except FileNotFoundError:
                #handles exception for new processes that are killed while I'm reading them.
                    continue

                process = ProcessInfo(name, starttime, uid)
                process.utime = utime
                process.ppid= int(ppid)
                process.state= state
                process.stime = stime
                process.priority= priority
                process.vsize = vsize
                process.num_threads= num_threads
                process.rss = rss
                process.process_up_time= process_up_time
                process.command= comm
                process_list[PID] = process

            else:
                process = process_list[PID]
                process.utime = utime
                process.stime = stime
                process.vsize = vsize
                process.rss = rss
                process.state= state
                process.num_threads= num_threads
                process.priority= priority
                process.process_up_time= sys_up_time - (starttime/self.ticks_per_second)

            #handles edges cases for CPU Load calculation
            if time_delta > 0:
                #handles process restart
                delta = process_time - process.process_time
                process.process_time= process_time
                if delta >= 0:  # ignore negative deltas due to PID reuse
                    process.cpu_load = round((delta / self.ticks_per_second / time_delta) * 100, 1)

        dead_processes= process_list.keys() - current_pids
        for remove_pid in dead_processes:
            del process_list[remove_pid]
