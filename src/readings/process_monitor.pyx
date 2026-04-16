# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

from os import scandir, sysconf, sysconf_names
from time import monotonic
import cython

from posix.fcntl cimport open as c_open, O_RDONLY
from posix.unistd cimport close as c_close, pread as c_pread
from libc.stdlib cimport atoi, atol

cdef class ProcessInfo:

    cdef public:
        int uid, ppid, utime, stime, num_threads, priority
        long vsize, rss, process_time
        long long starttime
        double cpu_load, process_up_time
        str name, state, command        
    
    def __cinit__(self, name, starttime, uid=None):
        self.name = name.decode()
        self.cpu_load = 0
        self.uid = int(uid)
        self.ppid = 0
        self.utime = 0
        self.stime = 0
        self.process_time = 0
        self.process_up_time = 0.0
        self.num_threads = 0
        self.vsize = 0
        self.rss = 0
        self.starttime = starttime
        self.priority = 0
        self.command = " "


cdef class SystemUsername:

    cdef public:
        str name
        int UID

    def __cinit__(self, line):
        self.name, _, uid, _ = line.strip().split(":", 3)
        self.UID = int(uid)


cdef class ProcessMonitor:

    cdef public:
        int __page_size, ticks_per_second
        double __prev_process_time
        str __proc_path
        object __sys_up_time_file
        dict user_list, current_user

    def __cinit__(self, file_path: object):
        self.__page_size = sysconf("SC_PAGE_SIZE")
        self.ticks_per_second = sysconf(sysconf_names["SC_CLK_TCK"])
        self.__prev_process_time = monotonic()
        self.__proc_path = "/proc"
        self.__sys_up_time_file = file_path
        self.user_list, self.current_user = self.__get_process_username()

    def __get_process_username(self):

        path = "/etc/passwd"
        current_user_path = "/var/run/user"
        username_data = {}
        current_user_data = {}

        try:
            with open(path) as f:
                for line in f:
                    username_object = SystemUsername(line)
                    username_data[int(username_object.UID)] = username_object.name
        except FileNotFoundError:
            username_data[0] = "root"
        
        try:
            for username_folder in scandir(current_user_path):
                username_string = username_data[int(username_folder.name)]
                current_user_data[username_string] = True
        except FileNotFoundError:
            pass

        return username_data, current_user_data

    def update(self, schedule: dict, process_list: dict, data_length=30000) -> dict: 
        if schedule["processes"] is False:
            return

        cdef int PID, utime, stime, num_threads, priority
        cdef long vsize, rss, starttime, process_time, delta
        cdef double time_delta, sys_up_time, process_up_time, raw_load
        cdef int file_descriptor
        cdef char stat_buf[512]
        cdef Py_ssize_t nread

        current_time = monotonic()
        time_delta = current_time - self.__prev_process_time
        self.__prev_process_time = current_time

        cdef int page_size = self.__page_size
        cdef int ticks = self.ticks_per_second
        cdef set current_pids = set()

        data_length_index = 0
        sys_up_time = float(self.__sys_up_time_file.get_file("system_up_time").read().split()[0])

        for proc_folder_path in scandir(self.__proc_path):

            pid_proc_path = proc_folder_path.path.encode()
            pid_proc_string = proc_folder_path.name

            try:
                PID = int(pid_proc_string)
            except ValueError:
                continue
            
            if data_length_index >= data_length:
                break

            data_length_index += 1
            current_pids.add(PID)

            stat_file_bytes = pid_proc_path + b"/stat"

            try:
                file_descriptor = c_open(stat_file_bytes, O_RDONLY)
                if file_descriptor == -1:
                    continue

                nread = c_pread(file_descriptor, stat_buf, 512, 0)
                c_close(file_descriptor)

                if nread <= 0:
                    continue

                py_line = bytes(stat_buf[:nread])

                name_start = py_line.index(b"(")
                name_end = py_line.index(b") ", name_start)
                name = py_line[name_start + 1:name_end]
                stats_list = py_line[name_end + 2:].split(None, 22)

                ppid = stats_list[1]
                state = stats_list[0].decode()
                utime = atoi(stats_list[11])
                stime = atoi(stats_list[12])
                process_time = utime + stime
                num_threads = atoi(stats_list[17])
                vsize = atol(stats_list[20]) >> 20
                rss = (atol(stats_list[21]) * page_size) >> 20
                starttime = atol(stats_list[19])
                priority = atoi(stats_list[15])
                process_up_time = sys_up_time - (starttime / ticks)

            except FileNotFoundError:
                continue

            uid = None

            if PID not in process_list or process_list[PID].starttime != starttime:

                status_file = pid_proc_path + b"/status"
                cmdline_file = pid_proc_path + b"/cmdline"

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
                    with open(status_file, "rb") as f:
                        for status_line in f:
                            if status_line.startswith(b"Uid"):  
                                uid = status_line.split()[1]
                                uid = uid.decode()
                            if uid:
                                break

                except FileNotFoundError:
                    continue

                process = ProcessInfo(name, starttime, uid)
                process.utime = utime
                process.ppid = int(ppid)
                process.state = state
                process.stime = stime
                process.priority = priority
                process.vsize = vsize
                process.num_threads = num_threads
                process.rss = rss
                process.process_up_time = process_up_time
                process.command = comm

                process_list[PID] = process

            else:
                process = process_list[PID]
                process.utime = utime
                process.stime = stime
                process.vsize = vsize
                process.rss = rss
                process.state = state
                process.num_threads = num_threads
                process.priority = priority
                process.process_up_time = sys_up_time - (starttime / ticks)

            if time_delta > 0:
                delta = process_time - process.process_time
                process.process_time = process_time

                if delta >= 0:
                    raw_load = (<double>delta / ticks / time_delta) * 100.0
                    process.cpu_load = <int>(raw_load * 10 + 0.5) / 10.0

        dead_processes = process_list.keys() - current_pids
        for remove_pid in dead_processes:
            del process_list[remove_pid]