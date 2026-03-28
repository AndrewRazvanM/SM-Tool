from core.formatter_threshdolds import SOME_THRESHOLDS, SOME_300_THRESHOLDS, FULL_THRESHOLDS, FULL_300_THRESHOLDS, CPU_AVG10_THRESHOLDS, CPU_AVG300_THRESHOLDS, CPU_AVG60_THRESHOLDS, CPU_HEALTH_THRESHOLDS

def time_formatter(sec:float) -> str:
    """
    Formats process up time to HH:MM:SS
    """
    sec= int(sec)
    h, remainder = divmod(sec, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02}:{m:02}:{s:02} "

def classify_pressure(value, thresholds):
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

            cpu_pressure_state = classify_pressure(cpu_pressure_health, CPU_HEALTH_THRESHOLDS)

        # --- Classify averages ---
        avg10_state = classify_pressure(cpu_avg10, CPU_AVG10_THRESHOLDS)
        avg60_state = classify_pressure(cpu_avg60, CPU_AVG60_THRESHOLDS)
        avg300_state = classify_pressure(cpu_avg300, CPU_AVG300_THRESHOLDS)

        # --- Write output ---
        out[0].value = f"{cpu_avg10:<5}"
        out[0].style = avg10_state

        out[1].value = f"{cpu_avg60:<5}"
        out[1].style = avg60_state

        out[2].value = f"{cpu_avg300:<5}"
        out[2].style = avg300_state

        out[3].value = f"{cpu_pressure_health:<5.1f}" if cpu_pressure_health != "N/A" else "N/A"
        out[3].style = cpu_pressure_state

        out[4].bar_width = cpu_pressure_bar_width
        out[4].style = cpu_pressure_state

        self.formatted_output = out

class MemoryPressureFormatter:
    __slots__ = ("formatted_output",)

    def __init__(self):
        self.formatted_output = [TextStyle("N/A", 3) for _ in range(8)]


    def format_mem(self, system_pressure_readings: object, schedule: dict) -> list:
        if not schedule["memory"]:
            return

        memory_some = system_pressure_readings.memory_some
        memory_full = system_pressure_readings.memory_full
        memory_health = system_pressure_readings.memory_health

        out = self.formatted_output

        s10, s60, s300 = memory_some
        f10, f60, f300 = memory_full

        # --- classify states ---
        s10_state = classify_pressure(s10, SOME_THRESHOLDS)
        s60_state = classify_pressure(s60, SOME_THRESHOLDS)
        s300_state = classify_pressure(s300, SOME_300_THRESHOLDS)

        f10_state = classify_pressure(f10, FULL_THRESHOLDS)
        f60_state = classify_pressure(f60, FULL_THRESHOLDS)
        f300_state = classify_pressure(f300, FULL_300_THRESHOLDS)

        # --- health classification ---
        health_score = memory_health[0]
        if health_score == "N/A":
            score_state = 3
            bar_state = 3
        else:
            score_state = 0 if health_score > 80 else 1 if health_score > 60 else 2
            bar_state = score_state

        # --- write output ---
        out[0].value, out[0].style = f"{s10:<5}", s10_state
        out[1].value, out[1].style = f"{s60:<5}", s60_state
        out[2].value, out[2].style = f"{s300:<5}", s300_state

        out[3].value, out[3].style = f"{f10:<5}", f10_state
        out[4].value, out[4].style = f"{f60:<5}", f60_state
        out[5].value, out[5].style = f"{f300:<5}", f300_state

        out[6].value = f"{health_score:<5.1f}" if health_score != "N/A" else "N/A"
        out[6].style = score_state

        out[7].bar_width = memory_health[1]
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
            die_temp_state = 0 if die_temp_val < 70 else 1 if die_temp_val < 85 else 2
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
            average_temp_state = 0 if avg_val < 70 else 1 if avg_val < 85 else 2
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
        formatted[5].value, formatted[5].style = num_cpu_threads, 3

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

        for idx, cpu in enumerate(cpu_load):
            val = cpu_load[cpu]
            text = f"{cpu}: {val}%"[:cpu_load_bar_ratio - 1]  # Truncate if necessary
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
                received_string= f"Dw: {round((r_bits)/1000, 3):>{13- interface_string_length}} Kb/s"
            elif r_bits < 1000000000:
                received_string= f"Dw: {round((r_bits)/1000000, 3):{13- interface_string_length}} Mb/s"
            else:
                received_string= f"Dw: {round((r_bits)/1000000000, 3):{13- interface_string_length}} Gb/s"

            up_bits= sent * 8
            if up_bits < 1000000:
                sent_string= f"Up: {round((up_bits)/1000, 3):>13.13} Kb/s"
            elif up_bits < 1000000000:
                sent_string= f"Up: {round((up_bits)/1000000, 3):>13.13} Mb/s"
            else:
                sent_string= f"Up: {round((up_bits)/1000000000, 3):>13.13} Gb/s"

            formatted_network_output[formatted_output_index].value= f"{interface}: {received_string} | {sent_string}"[:49]
            formatted_output_index+= 1

            total_received+= received
            total_received_dropp+= network_throughput[interface].Received_drop
            total_sent+= sent
            total_sent_dropp+= network_throughput[interface].Transmitted_drop
        
        received_bits = total_received * 8
        if received_bits < 1000000:
            formatted_network_output[0].value= f"{round((total_received)/1000, 3):>10.10} Kb/s"
        elif received_bits < 1000000000:
            formatted_network_output[0].value= f"{round((total_received)/1000000, 3):>10.10} Mb/s"
        else:
            formatted_network_output[0].value= f"{round((total_received)/1000000000, 3):>10.10} Gb/s"

        r_dropp_bits= total_received_dropp * 8
        if r_dropp_bits < 1000000:
            formatted_network_output[1].value= f"{round((r_dropp_bits)/1000, 3):>10.10} Kb/s"
        elif r_dropp_bits < 1000000000:
            formatted_network_output[1].value= f"{round((r_dropp_bits)/1000000, 3):>10.10} Mb/s"
        else:
            formatted_network_output[1].value= f"{round((r_dropp_bits)/1000000000, 3):>10.10} Gb/s"

        up_bits= total_sent * 8
        if up_bits < 1000000:
            formatted_network_output[2].value= f"{round((up_bits)/1000, 3):>8.8} Kb/s"
        elif up_bits < 1000000000:
            formatted_network_output[2].value= f"{round((up_bits)/1000000, 3):>8.8} Mb/s"
        else:
            formatted_network_output[2].value= f"{round((up_bits)/1000000000, 3):>8.8} Gb/s"

        up_dropp_bits= total_sent_dropp * 8
        if up_dropp_bits < 1000000:
            formatted_network_output[3].value= f"{round((up_dropp_bits)/1000, 3):>8.8} Kb/s"
        elif up_dropp_bits < 1000000000:
            formatted_network_output[3].value= f"{round((up_dropp_bits)/1000000, 3):>8.8} Mb/s"
        else:
            formatted_network_output[3].value= f"{round((up_dropp_bits)/1000000000, 3):>8.8} Gb/s"

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
        
        for gpu_index in gpu_readings:

            if gpu_readings[gpu_index]["Temperature"] == "N/A":
                formatted_temp= f"{gpu_readings[gpu_index]["Temperature"]:<30.30}"
                formatted_temp_attr= 3
                gpu_temp_bar_width= 3
            elif gpu_readings[gpu_index]["Temperature"] < 70:
                formatted_temp= f"{gpu_readings[gpu_index]['Temperature']} °C".ljust(30)[:30]
                formatted_temp_attr= 0
                gpu_temp_bar_width= min(49, int((gpu_readings[gpu_index]["Temperature"] /100) * 49))
            elif gpu_readings[gpu_index]["Temperature"] < 80:
                formatted_temp= f"{gpu_readings[gpu_index]["Temperature"]} {"°C":<30.30}"
                formatted_temp_attr= 1
                gpu_temp_bar_width= min(49, int((gpu_readings[gpu_index]["Temperature"] /100) * 49))
            else:
                formatted_temp= f"{gpu_readings[gpu_index]["Temperature"]} {"°C":<30.30}"
                formatted_temp_attr= 2
                gpu_temp_bar_width= min(49, int((gpu_readings[gpu_index]["Temperature"] /100) * 49))

            formatted_nvidia_output[0].value= formatted_temp
            formatted_nvidia_output[0].style= formatted_temp_attr
            formatted_nvidia_output[1].bar_width= gpu_temp_bar_width
            formatted_nvidia_output[1].style=formatted_temp_attr

            if gpu_readings[gpu_index]["GPU Clock Speed"] == "N/A":
                formatted_clock_speed= f"{gpu_readings[gpu_index]["GPU Clock Speed"]:<30.30}"
                formatted_clock_speed_attr= 3
            else:
                formatted_clock_speed= f"{gpu_readings[gpu_index]["GPU Clock Speed"]} {"Mhz":<30.30}"
                formatted_clock_speed_attr= 0

            formatted_nvidia_output[2].value= formatted_clock_speed
            formatted_nvidia_output[2].style= formatted_clock_speed_attr

            if gpu_readings[gpu_index]["Fan Speed"] == "N/A":
                formatted_fan_speed= f"{gpu_readings[gpu_index]["Fan Speed"]:<30.30}"
                formatted_fan_speed_attr= 3
            else:
                formatted_fan_speed= f"{gpu_readings[gpu_index]["Fan Speed"]} {"RPM":<30.30}"
                formatted_fan_speed_attr= 0

            formatted_nvidia_output[3].value= formatted_fan_speed
            formatted_nvidia_output[3].style= formatted_fan_speed_attr

            if gpu_readings[gpu_index]["Memory Load"] == "N/A":
                formatted_memory_load= f"{gpu_readings[gpu_index]["Memory Load"]:<30.30}"
                formatted_memory_load_attr= 3
            elif gpu_readings[gpu_index]["Memory Load"] < 60:
                formatted_memory_load= f"{gpu_readings[gpu_index]["Memory Load"]} {"%":<30.30}"
                formatted_memory_load_attr= 0
            elif gpu_readings[gpu_index]["Memory Load"] < 90:
                formatted_memory_load= f"{gpu_readings[gpu_index]["Memory Load"]} {"%":<30.30}"
                formatted_memory_load_attr= 1
            else:
                formatted_memory_load= f"{gpu_readings[gpu_index]["Memory Load"]} {"%":<30.30}"
                formatted_memory_load_attr= 2

            formatted_nvidia_output[4].value= formatted_memory_load
            formatted_nvidia_output[4].style= formatted_memory_load_attr

            if gpu_readings[gpu_index]["GPU Load"] == "N/A":
                formatted_gpu_load= f"{gpu_readings[gpu_index]["GPU Load"]:<30.30}"
                formatted_gpu_load_attr= 3
                gpu_load_bar_width= 1
            elif gpu_readings[gpu_index]["GPU Load"] < 60:
                formatted_gpu_load= f"{gpu_readings[gpu_index]["GPU Load"]} {"%":<30.30}"
                formatted_gpu_load_attr= 0
                gpu_load_bar_width= min(49, int((gpu_readings[gpu_index]["GPU Load"] / 100) * 49))
            elif gpu_readings[gpu_index]["GPU Load"] < 90:
                formatted_gpu_load= f"{gpu_readings[gpu_index]["GPU Load"]} {"%":<30.30}"
                formatted_gpu_load_attr= 1
                gpu_load_bar_width= min(49, int((gpu_readings[gpu_index]["GPU Load"] / 100) * 49))
            else:
                formatted_gpu_load= f"{gpu_readings[gpu_index]["GPU Load"]} {"%":<30.30}"
                formatted_gpu_load_attr= 2
                gpu_load_bar_width= min(49, int((gpu_readings[gpu_index]["GPU Load"] / 100) * 49))

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
            proc_user = usernames[process.uid]
                        
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
            row[7].style = 0 if cpu < 50 else 1 if cpu < 80 else 2

            if process.vsize > 1024:
                row[8].value = f"{(process.vsize // 1024) * 1.048576:<1.0f} {'GB':<6}"
            else:
                row[8].value = f"{process.vsize * 1.048576:<1.0f} {'MB':<6}"
            row[8].style = 0

            if process.rss > 1024:
                row[9].value = f"{(process.rss // 1024) * 1.048576:<1.0f} {'GB':<6}"
            else:
                row[9].value = f"{process.rss * 1.048576:<1.0f} {'MB':<6}"
            row[9].style = 0

            row[10].value = f"{process.name:<19.19}"
            row[10].style = 4

            row[11].value= f"{process.command:<150}"
            row[11].style= 4

            row[12].value= process.starttime