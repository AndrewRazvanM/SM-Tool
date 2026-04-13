from core.formatter_thresholds import *

def time_formatter(sec:float) -> str:
    """
    Formats process up time to HH:MM:SS
    """
    sec= int(sec)
    h, remainder = divmod(sec, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02}:{m:02}:{s:02} "

def classify(value, thresholds:tuple) -> int:
    """
    Gives a curse color based on the value.
    """
    if value == "N/A":
        return 3
    for limit, state in thresholds:
        if value < limit:
            return state

class TextStyle:
    __slots__ = ("value", "style", "bar_width")

    def __init__(self, text: str, style: int, bar_width= 0):
        self.value = text
        self.style = style
        self.bar_width= bar_width

class CPUPressureFormatter:
    __slots__ = ("formatted_output",)

    def __init__(self):
        self.formatted_output = [TextStyle("N/A", 3) for _ in range(5)]

    def format(self, system_pressure_readings: object, schedule: dict):
        if not schedule["cpu"]:
            return

        out = self.formatted_output
        txt_max_len= 5 

        cpu_avg10 = system_pressure_readings.cpu_avg10
        cpu_avg60 = system_pressure_readings.cpu_avg60
        cpu_avg300 = system_pressure_readings.cpu_avg300

        # --- Compute health ---
        if cpu_avg10 == "N/A":
            cpu_pressure_health = "N/A"
            cpu_pressure_bar_width = 0
            cpu_pressure_state = 3
        else:
            penalty = cpu_avg10 * 2.0 + cpu_avg60 * 6.0 + cpu_avg300 * 50.0
            cpu_pressure_health = max(0.0, 100.0 - penalty)

            cpu_pressure_bar_width = int(cpu_pressure_health // 4.3)
            cpu_pressure_bar_width = max(1, min(cpu_pressure_bar_width, 23))

            cpu_pressure_state = classify(cpu_pressure_health, PRESSURE_HEALTH_THRESHOLDS)

        # --- Classify averages ---
        avg10_state = classify(cpu_avg10, CPU_AVG10_THRESHOLDS)
        avg60_state = classify(cpu_avg60, CPU_AVG60_THRESHOLDS)
        avg300_state = classify(cpu_avg300, CPU_AVG300_THRESHOLDS)

        # --- Write output ---
        out[0].value = f"{cpu_avg10:<{txt_max_len}}"
        out[0].style = avg10_state

        out[1].value = f"{cpu_avg60:<{txt_max_len}}"
        out[1].style = avg60_state

        out[2].value = f"{cpu_avg300:<{txt_max_len}}"
        out[2].style = avg300_state

        out[3].value = f"{cpu_pressure_health:<{txt_max_len}.1f}" if cpu_pressure_health != "N/A" else "N/A"
        out[3].style = cpu_pressure_state

        out[4].bar_width = cpu_pressure_bar_width
        out[4].style = cpu_pressure_state

        self.formatted_output = out

MEM_MAX_BAR_WIDTH = 30

class MemoryPressureFormatter:
    __slots__ = ("formatted_output",)

    def __init__(self):
        self.formatted_output = [TextStyle("N/A", 3) for _ in range(8)]


    def format_mem(self, system_pressure_readings: object, schedule: dict) -> list:
        if not schedule["memory"]:
            return

        txt_max_len= 5
        memory_some = system_pressure_readings.memory_some
        memory_full = system_pressure_readings.memory_full

        out = self.formatted_output

        s10, s60, s300 = memory_some
        f10, f60, f300 = memory_full

        # --- classify states ---
        s10_state = classify(s10, SOME_THRESHOLDS)
        s60_state = classify(s60, SOME_THRESHOLDS)
        s300_state = classify(s300, SOME_300_THRESHOLDS)

        f10_state = classify(f10, FULL_THRESHOLDS)
        f60_state = classify(f60, FULL_THRESHOLDS)
        f300_state = classify(f300, FULL_300_THRESHOLDS)

        # --- health classification ---
        penalty= (s10 + s60 * 2.00 + s300 * 3.00 + f10 * 20.00 + f60 * 40.00 + f300 * 60.00)
        health_score= max(0,100 - penalty)
        health_bar_width= min(MEM_MAX_BAR_WIDTH, int(health_score/3.2))

        if health_score == "N/A":
            score_state = 3
            bar_state = 3
        else:
            score_state = 0 if health_score > 80 else 1 if health_score > 60 else 2
            bar_state = score_state

        # --- write output ---
        out[0].value, out[0].style = f"{s10:<{txt_max_len}}", s10_state
        out[1].value, out[1].style = f"{s60:<{txt_max_len}}", s60_state
        out[2].value, out[2].style = f"{s300:<{txt_max_len}}", s300_state

        out[3].value, out[3].style = f"{f10:<{txt_max_len}}", f10_state
        out[4].value, out[4].style = f"{f60:<{txt_max_len}}", f60_state
        out[5].value, out[5].style = f"{f300:<{txt_max_len}}", f300_state

        out[6].value = f"{health_score:.1f}" if health_score != "N/A" else "N/A"
        out[6].style = score_state

        out[7].bar_width = health_bar_width
        out[7].style = bar_state

        self.formatted_output= out

class MemoryFormatter:
    """
    Formats text and decides state (0=good, 1=warning, 2=critical, 3=muted, 4= none) for:
        Memory Information
    """

    __slots__ = (
        "formatted_output",
    )

    def __init__(self):
        self.formatted_output= [TextStyle("N/A", 3) for _ in range(4)]

    def format(self, memory_info_readings: object, schedule: dict) -> list:
        if schedule["memory"] is False:
            return

        mem_total= memory_info_readings.MemTotal
        mem_available= memory_info_readings.MemAvailable
        swap_total= memory_info_readings.SwapTotal
        swap_free= memory_info_readings.SwapFree
        memory_info_formatted_output= self.formatted_output

        if mem_total < 1000:
            mem_total= f"{mem_total} kB"
            mem_total_style= 2
        elif mem_total < 1000000:
            mem_total= f"{mem_total//1000} MB"
            mem_total_style= 1
        else:
            mem_total= f"{mem_total//1000000} GB"
            mem_total_style= 0

        if mem_available < 1000:
            mem_available= f"{mem_available} kB"
            mem_available_style= 2
        elif mem_available < 1000000:
            mem_available= f"{mem_available//1000} MB"
            mem_available_style= 1
        else:
            mem_available= f"{mem_available//1000000} GB"
            mem_available_style= 0

        if swap_total < 1000:
            swap_total= f"{swap_total} kB"
            swap_total_style= 2
        elif swap_total < 1000000:
            swap_total= f"{swap_total//1000} MB"
            swap_total_style= 1
        else:
            swap_total= f"{swap_total//1000000} GB"
            swap_total_style= 0

        if swap_free < 1000:
            swap_free= f"{swap_free} kB"
            swap_free_style= 2
        elif swap_free < 1000000:
            swap_free= f"{swap_free//1000} MB"
            swap_free_style= 1
        else:
            swap_free= f"{swap_free//1000000} GB"
            swap_free_style= 0
        
        memory_info_formatted_output[0].value= mem_total[:6] 
        memory_info_formatted_output[0].style= mem_total_style
        memory_info_formatted_output[1].value= mem_available[:6] 
        memory_info_formatted_output[1].style= mem_available_style
        memory_info_formatted_output[2].value= swap_total[:6] 
        memory_info_formatted_output[2].style= swap_total_style
        memory_info_formatted_output[3].value= swap_free[:6] 
        memory_info_formatted_output[3].style= swap_free_style

        self.formatted_output= memory_info_formatted_output

class CPUTempFormatter:
    """
    Formats CPU temperature and fan info into TextStyle objects.
    """

    __slots__ = ("formatted_cpu_readings",)

    def __init__(self):
        # Initial placeholder values
        self.formatted_cpu_readings = [
            TextStyle("N/A", 3),
            TextStyle(" ", 3, 1),
            TextStyle("N/A", 3),
            TextStyle(" ", 3, 1),
            TextStyle("N/A", 3),
            TextStyle("N/A", 3),
        ]

    def format_info(self, cpu_readings: object, schedule: dict):
        if not schedule.get("cpu", True):
            return

        cpu_temp_dict = cpu_readings.cpu_temp
        formatted = self.formatted_cpu_readings

        if cpu_temp_dict is None:
            return

        cpu_temp_dict_length = len(cpu_temp_dict)
        num_cpu_core_state = 0

        # Package id 0
        if "Package id 0" in cpu_temp_dict:
            cpu_temp_dict_length -= 1
            die_temp_val = cpu_temp_dict["Package id 0"].temp
            die_temp = f"{die_temp_val:>3} °C"
            die_temp_state = classify(die_temp_val, CPU_TEMP_THRESHOLDS)
            die_temp_bar_state = die_temp_state
            die_temp_bar_width = min(24, die_temp_val // 4)
        else:
            die_temp = "N/A   "
            die_temp_state = die_temp_bar_state = 3
            die_temp_bar_width = 0

        # Average
        if "Average" in cpu_temp_dict:
            cpu_temp_dict_length -= 1
            avg_val = cpu_temp_dict["Average"]
            average_temp = f"{avg_val:>3} °C"
            average_temp_state = classify(avg_val, CPU_TEMP_THRESHOLDS)
            average_temp_bar_state = average_temp_state
            average_temp_bar_width = min(23, avg_val // 4)
        else:
            average_temp = "N/A   "
            average_temp_state = average_temp_bar_state = 3
            average_temp_bar_width = 0

        num_cpu_threads = f" {(cpu_temp_dict_length * 2):<4}"
        num_cpu_core = f" {cpu_temp_dict_length:<4}"

        # Update formatted TextStyle objects
        formatted[0].value, formatted[0].style = die_temp, die_temp_state
        formatted[1].bar_width, formatted[1].style = die_temp_bar_width, die_temp_bar_state
        formatted[2].value, formatted[2].style = average_temp, average_temp_state
        formatted[3].bar_width, formatted[3].style = average_temp_bar_width, average_temp_bar_state
        formatted[4].value, formatted[4].style = num_cpu_core, num_cpu_core_state
        formatted[5].value, formatted[5].style = num_cpu_threads, num_cpu_core_state

        self.formatted_cpu_readings = formatted

class CPULoadFormatter:
    """
    Formats CPU load into TextStyle objects.
    """

    __slots__ = ("formatted_cpu_load",)

    def __init__(self):
        self.formatted_cpu_load = []

    def format_load(self, raw_cpu_load: object, cpu_load_bar_ratio: int, schedule: dict) -> list:
        if not schedule.get("cpu", True):
            return

        cpu_load = raw_cpu_load.cpu_load
        formatted = self.formatted_cpu_load

        if not formatted:
            formatted = [TextStyle("N/A", 3) for _ in cpu_load]

        symbol_str = f"{"%":<{cpu_load_bar_ratio}}"

        for idx, cpu in enumerate(cpu_load):
            val = cpu_load[cpu]
            text = f"{cpu}: {val} {symbol_str}"[:cpu_load_bar_ratio - 2]  # Truncate if necessary
            formatted[idx].value = text
            formatted[idx].style = 0

            if val in (None, "N/A"):
                formatted[idx].bar_width = 0
            else:
                formatted[idx].bar_width = int((val / 100) * cpu_load_bar_ratio)

        self.formatted_cpu_load = formatted

class NetworkFormatter:

    __slots__= (
        "formatted_network_output"
    )

    def __init__(self):
        self.formatted_network_output= [TextStyle(" ", 0) for _ in range(10)]

    def format(self, network_readings: dict, schedule: dict):
        if schedule["network"] is False:
            return
        
        network_throughput= network_readings
        formatted_network_output= self.formatted_network_output

        total_received= 0
        total_received_dropp= 0
        total_sent= 0
        total_sent_dropp= 0

        total_up_txt_max_len= 8
        total_down_txt_max_len= 10
        per_interface_txt_max_len= 13
        
        formatted_output_index= 3 #reserves the first 4 positions for the totals

        for interface in network_throughput:
            if network_throughput[interface].Type != "Physical":
                continue
            
            if formatted_output_index >= len(formatted_network_output):
                break
            
            received= network_throughput[interface].Received_bytes
            sent= network_throughput[interface].Transmitted_bytes
            interface_string_length= len(interface)

            r_bits= received * 8
            if r_bits < 1000000:
                received_string= f"Dw: {round((r_bits)/1000, 3):>{per_interface_txt_max_len - interface_string_length}} Kb/s"
            elif r_bits < 1000000000:
                received_string= f"Dw: {round((r_bits)/1000000, 3):{per_interface_txt_max_len - interface_string_length}} Mb/s"
            else:
                received_string= f"Dw: {round((r_bits)/1000000000, 3):{per_interface_txt_max_len - interface_string_length}} Gb/s"

            up_bits= sent * 8
            if up_bits < 1000000:
                sent_string= f"Up: {round((up_bits)/1000, 3):>{per_interface_txt_max_len}.{per_interface_txt_max_len}} Kb/s"
            elif up_bits < 1000000000:
                sent_string= f"Up: {round((up_bits)/1000000, 3):>{per_interface_txt_max_len}.{per_interface_txt_max_len}} Mb/s"
            else:
                sent_string= f"Up: {round((up_bits)/1000000000, 3):>{per_interface_txt_max_len}.{per_interface_txt_max_len}} Gb/s"

            formatted_network_output[formatted_output_index].value= f"{interface}: {received_string} | {sent_string}"[:49]
            formatted_output_index+= 1

            total_received+= received
            total_received_dropp+= network_throughput[interface].Received_drop
            total_sent+= sent
            total_sent_dropp+= network_throughput[interface].Transmitted_drop
        
        received_bits = total_received * 8
        if received_bits < 1000000:
            formatted_network_output[0].value= f"{round((total_received)/1000, 3):>{total_down_txt_max_len}.{total_down_txt_max_len}} Kb/s"
        elif received_bits < 1000000000:
            formatted_network_output[0].value= f"{round((total_received)/1000000, 3):>{total_down_txt_max_len}.{total_down_txt_max_len}} Mb/s"
        else:
            formatted_network_output[0].value= f"{round((total_received)/1000000000, 3):>{total_down_txt_max_len}.{total_down_txt_max_len}} Gb/s"

        r_dropp_bits= total_received_dropp * 8
        if r_dropp_bits < 1000000:
            formatted_network_output[1].value= f"{round((r_dropp_bits)/1000, 3):>{total_down_txt_max_len}.{total_down_txt_max_len}} Kb/s"
        elif r_dropp_bits < 1000000000:
            formatted_network_output[1].value= f"{round((r_dropp_bits)/1000000, 3):>{total_down_txt_max_len}.{total_down_txt_max_len}} Mb/s"
        else:
            formatted_network_output[1].value= f"{round((r_dropp_bits)/1000000000, 3):>{total_down_txt_max_len}.{total_down_txt_max_len}} Gb/s"

        up_bits= total_sent * 8
        if up_bits < 1000000:
            formatted_network_output[2].value= f"{round((up_bits)/1000, 3):>{total_up_txt_max_len}.{total_up_txt_max_len}} Kb/s"
        elif up_bits < 1000000000:
            formatted_network_output[2].value= f"{round((up_bits)/1000000, 3):>{total_up_txt_max_len}.{total_up_txt_max_len}} Mb/s"
        else:
            formatted_network_output[2].value= f"{round((up_bits)/1000000000, 3):>{total_up_txt_max_len}.{total_up_txt_max_len}} Gb/s"

        up_dropp_bits= total_sent_dropp * 8
        if up_dropp_bits < 1000000:
            formatted_network_output[3].value= f"{round((up_dropp_bits)/1000, 3):>{total_up_txt_max_len}.{total_up_txt_max_len}} Kb/s"
        elif up_dropp_bits < 1000000000:
            formatted_network_output[3].value= f"{round((up_dropp_bits)/1000000, 3):>{total_up_txt_max_len}.{total_up_txt_max_len}} Mb/s"
        else:
            formatted_network_output[3].value= f"{round((up_dropp_bits)/1000000000, 3):>{total_up_txt_max_len}.{total_up_txt_max_len}} Gb/s"

class NvidiaFormatter:

    __slots__= (
        "formatted_nvidia_output"
    )

    def __init__(self):
        self.formatted_nvidia_output= [TextStyle(" ", 3) for _ in range(7)] #will cause a crash on systems with multiple gpus. Need to fix at some point

    def format(self, nvidia_readings: list, schedule: dict) -> list:
        if schedule["nvidia"] is False:
            return
        
        gpu_readings= nvidia_readings
        formatted_nvidia_output= self.formatted_nvidia_output

        text_max_size= 20
        
        for gpu_index in gpu_readings:
            gpu_temp= gpu_readings[gpu_index]["Temperature"]
            if gpu_temp == "N/A":
                formatted_temp= f"{gpu_temp:<{text_max_size}.{text_max_size}}"
                gpu_temp_bar_width= 3
            else:
                formatted_temp= f"{gpu_temp} {"°C":<{text_max_size}.{text_max_size}}"
                gpu_temp_bar_width= min(49, int((gpu_temp /100) * 49))
            
            formatted_temp_attr= classify(gpu_temp, GPU_TEMP_THRESHOLDS)

            formatted_nvidia_output[0].value= formatted_temp
            formatted_nvidia_output[0].style= formatted_temp_attr
            formatted_nvidia_output[1].bar_width= gpu_temp_bar_width
            formatted_nvidia_output[1].style=formatted_temp_attr

            if gpu_readings[gpu_index]["GPU Clock Speed"] == "N/A":
                formatted_clock_speed= f"{gpu_readings[gpu_index]["GPU Clock Speed"]:<{text_max_size}}"
                formatted_clock_speed_attr= 3
            else:
                formatted_clock_speed= f"{gpu_readings[gpu_index]["GPU Clock Speed"]} {"Mhz":<{text_max_size}.{text_max_size}}"
                formatted_clock_speed_attr= 0

            formatted_nvidia_output[2].value= formatted_clock_speed
            formatted_nvidia_output[2].style= formatted_clock_speed_attr

            if gpu_readings[gpu_index]["Fan Speed"] == "N/A":
                formatted_fan_speed= f"{gpu_readings[gpu_index]["Fan Speed"]:<{text_max_size}}"
                formatted_fan_speed_attr= 3
            else:
                formatted_fan_speed= f"{gpu_readings[gpu_index]["Fan Speed"]} {"RPM":<{text_max_size}.{text_max_size}}"
                formatted_fan_speed_attr= 0

            formatted_nvidia_output[3].value= formatted_fan_speed
            formatted_nvidia_output[3].style= formatted_fan_speed_attr
    
            mem_load= gpu_readings[gpu_index]["Memory Load"]
            formatted_memory_load= f"{mem_load} {"%":<{text_max_size}.{text_max_size}}"
            formatted_memory_load_attr= classify(mem_load, GPU_LOAD_THRESHOLDS)
            

            formatted_nvidia_output[4].value= formatted_memory_load
            formatted_nvidia_output[4].style= formatted_memory_load_attr

            gpu_load= gpu_readings[gpu_index]["GPU Load"]

            if gpu_readings[gpu_index]["GPU Load"] == "N/A":
                formatted_gpu_load= f"{gpu_load:<{text_max_size}.{text_max_size}}"
                gpu_load_bar_width = 0
            else:
                formatted_gpu_load= f"{gpu_readings[gpu_index]["GPU Load"]} {"%":<{text_max_size}.{text_max_size}}"
                gpu_load_bar_width = min(49, int((gpu_load / 100) * 49))

            formatted_gpu_load_attr= classify(gpu_load, GPU_LOAD_THRESHOLDS)

            formatted_nvidia_output[5].value= formatted_gpu_load
            formatted_nvidia_output[5].style= formatted_gpu_load_attr
            formatted_nvidia_output[6].bar_width= gpu_load_bar_width
            formatted_nvidia_output[6].style= formatted_gpu_load_attr

class ProcessFormatter:
    __slots__ = ("formatted_processes_output")

    def __init__(self):
        self.formatted_processes_output = []

    def format(self, processes: list, processes_readings: object, schedule: dict) -> list:
        if not schedule["processes"]:
            return

        out = self.formatted_processes_output
        usernames = processes_readings.user_list
        current_users = set(processes_readings.current_user)

        # Trim excess rows
        if len(out) > len(processes):
            del out[len(processes):]

        for idx, (pid, process) in enumerate(processes.items()):

            if idx >= len(out):
                out.append([TextStyle("N/A", 3) for _ in range(13)])

            row = out[idx]
            proc_user = usernames.get(process.uid, str(process.uid))
                        
            row[0].value = f"{pid:<10}"
            row[0].style = 0

            row[1].value = f"{process.ppid:<10}"
            row[1].style = 5

            row[2].value = f"{proc_user:<14.14}"
            row[2].style = 0 if proc_user in current_users else (5 if proc_user == "root" else 3)

            row[3].value = f"{process.priority:<5}"
            row[3].style = 3

            row[4].value = f"{process.state:<7}"
            row[4].style = 0

            row[5].value = time_formatter(process.process_up_time)
            row[5].style = 0

            row[6].value = f"{process.num_threads:<9}"
            row[6].style = 0

            cpu = process.cpu_load
            row[7].value = f"{cpu:<6.6}"
            row[7].style = 0 if cpu < 50.0 else 1 if cpu < 80.0 else 2

            #converst from MiB to GB or MB
            if process.vsize > 1024:
                row[8].value = f"{(process.vsize // 1024) * 1.048576:<1.0f} {'GB':<6}"
            else:
                row[8].value = f"{process.vsize * 1.048576:<1.0f} {'MB':<6}"
            row[8].style = 0

            #converst from MiB to GB or MB
            if process.rss > 1024:
                row[9].value = f"{(process.rss // 1024) * 1.048576:<1.0f} {'GB':<6}"
            else:
                row[9].value = f"{process.rss * 1.048576:<1.0f} {'MB':<6}"
            row[9].style = 0

            row[10].value = f"{process.name:<19.19}"
            row[10].style = 4

            row[11].value= f"{process.command:<150}"
            row[11].style= 4

            row[12].value= process.starttime #used by ContentDiff to check if process changed

# Tunables
FIELDS_PER_DEVICE = 4  # name, read, write, iops
TXT_MAX_LEN = 9

class IOTotalFormatter:
    __slots__ = ("formatted_io_output",)

    def __init__(self):
        self.formatted_io_output = []

    def format(self, io_tot_readings, schedule):
        if not schedule["io"]:
            return

        devices = io_tot_readings.devices_total_io
        out = self.formatted_io_output

        required_len = len(devices) * FIELDS_PER_DEVICE

        # resize
        if len(out) < required_len:
            for _ in range(len(out), required_len):
                out.append(TextStyle(" ", 3))
        elif len(out) > required_len:
            del out[required_len:]

        for idx, (name, dev) in enumerate(devices.items()):
            base = idx * FIELDS_PER_DEVICE

            read = dev.read_throughput
            write = dev.write_throughput
            iops = dev.iops

            out[base + 0].value = f"{name:<{TXT_MAX_LEN}.{TXT_MAX_LEN}}"
            out[base + 1].value = f"{read:<{TXT_MAX_LEN}.1f}" if read != "N/A" else "N/A"
            out[base + 2].value = f"{write:<{TXT_MAX_LEN}.1f}" if write != "N/A" else "N/A"
            out[base + 3].value = f"{iops:<{TXT_MAX_LEN}.1f}" if iops != "N/A" else "N/A"

        self.formatted_io_output = out
        
# Tunables
IO_HEALTH_SCALE = 1.5
IO_MAX_BAR_WIDTH = 30


class IOPressureFormatter:
    __slots__ = ("formatted_io_output",)

    def __init__(self):
        self.formatted_io_output = [TextStyle("N/A", 3) for _ in range(8)]

    def format(self, io_pressure_readings: object, schedule: dict) -> list:
        if not schedule["io"]:
            return

        out = self.formatted_io_output
        txt_max_len = 5

        some = io_pressure_readings.io_some
        full = io_pressure_readings.io_full

        s10, s60, s300, _ = some
        f10, f60, f300, _ = full

        # --- Classification ---
        s10_state = classify(s10, IO_PRESSURE_THRESHOLDS)
        s60_state = classify(s60, IO_PRESSURE_THRESHOLDS)
        s300_state = classify(s300, IO_PRESSURE_THRESHOLDS)

        f10_state = classify(f10, IO_PRESSURE_THRESHOLDS)
        f60_state = classify(f60, IO_PRESSURE_THRESHOLDS)
        f300_state = classify(f300, IO_PRESSURE_THRESHOLDS)

        # --- Health computation ---
        if s10 == "N/A":
            health = "N/A"
            bar_width = 0
            health_state = 3
        else:
            penalty = (s10 * 2.0 + s60 * 5.0 + s300 * 10.0 +
                       f10 * 10.0 + f60 * 20.0 + f300 * 50.0)

            health = max(0.0, 100.0 - penalty * IO_HEALTH_SCALE)
            bar_width = min(IO_MAX_BAR_WIDTH, int(health / 3.2))
            health_state = classify(health, PRESSURE_HEALTH_THRESHOLDS)

        # --- Write output ---
        out[0].value, out[0].style = f"{s10:<{txt_max_len}.{txt_max_len}}", s10_state
        out[1].value, out[1].style = f"{s60:<{txt_max_len}.{txt_max_len}}", s60_state
        out[2].value, out[2].style = f"{s300:<{txt_max_len}.{txt_max_len}}", s300_state

        out[3].value, out[3].style = f"{f10:<{txt_max_len}.{txt_max_len}}", f10_state
        out[4].value, out[4].style = f"{f60:<{txt_max_len}.{txt_max_len}}", f60_state
        out[5].value, out[5].style = f"{f300:<{txt_max_len}.{txt_max_len}}", f300_state

        out[6].value = f"{health:<{txt_max_len}.1f}" if health != "N/A" else "N/A  " #manually padding
        out[6].style = health_state

        out[7].bar_width = bar_width
        out[7].style = health_state

        self.formatted_io_output = out
        
