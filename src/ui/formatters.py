class TextStyle:
    __slots__ = ("value", "style", "bar_width")

    def __init__(self, text: str, style: int, bar_width= 0):
        self.value = text
        self.style = style
        self.bar_width= bar_width

def time_formatter(sec:float) -> str:
    """
    Formats process up time to HH:MM:SS
    """
    sec= int(sec)
    h, remainder = divmod(sec, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02}:{m:02}:{s:02} "

class PressureFormatter:
    """
    Formats text and decides the state (0=good, 1=warning, 2=critical, 3=muted, 4=blue) for:
     cpu pressure
     memory pressure
     io pressure
    """
    __slots__= (
        "cpu_formatted_output",
        "memory_formatted_output",
        "io_formatted_output",
    )
    
    def __init__(self):
        self.cpu_formatted_output= [TextStyle("N/A", 3) for _ in range(5)]

        self.memory_formatted_output= [TextStyle("N/A", 3) for _ in range(8)]

        self.io_formatted_output= [TextStyle("N/A", 3) for _ in range(3)]

    def format_cpu(self, system_pressure_readings: object, schedule: dict) -> list:
        """
        Formats the cpu pressure and determines reading state(0=good, 1=warning, 2=critical, 3=muted, 4=none) if they did.
        """
        if schedule["cpu"] is False:
            return
        cpu_formatted_output= self.cpu_formatted_output
        cpu_avg10= system_pressure_readings.cpu_avg10
        cpu_avg60= system_pressure_readings.cpu_avg60
        cpu_avg300= system_pressure_readings.cpu_avg300

        if cpu_avg10 == "N/A":
            cpu_pressure_health= "N/A"
            cpu_pressure_bar_width= 0
            cpu_pressure_health_state= 3
            cpu_pressure_bar_state= 3

        else:
            penalty_cpu= cpu_avg10 * 2.0 + cpu_avg60 * 6.0 + cpu_avg300 * 50.0
            cpu_pressure_health= max(0, 100 - penalty_cpu)
            cpu_pressure_bar_width= int(cpu_pressure_health//4.3)

            if cpu_pressure_bar_width < 1:
                cpu_pressure_bar_width= 1
            elif cpu_pressure_bar_width > 23:
                cpu_pressure_bar_width= 23

            if cpu_pressure_health > 90:
                cpu_pressure_health_state= 0
                cpu_pressure_bar_state= 0
            elif cpu_pressure_health > 80:
                cpu_pressure_health_state= 1
                cpu_pressure_bar_state= 1
            else:
                cpu_pressure_health_state= 2
                cpu_pressure_bar_state= 2

        #determine the cpu state
        if cpu_avg10 == "N/A":
            cpu_avg10_state= 3
        elif cpu_avg10 <= 1.0:
            cpu_avg10_state= 0
        elif cpu_avg10 < 5.0:
            cpu_avg10_state= 1
        else:
            cpu_avg10_state= 2

        if cpu_avg60 == "N/A":
            cpu_avg60_state= 3
        elif cpu_avg60 <= 1.0:
            cpu_avg60_state= 0
        elif cpu_avg60 < 3.0:
            cpu_avg60_state= 1
        else:
            cpu_avg60_state= 2

        if cpu_avg300 == "N/A":
            cpu_avg300_state= 3
        elif cpu_avg300 <= 0.5:
            cpu_avg300_state= 0
        elif cpu_avg300 < 1.0:
            cpu_avg300_state= 1
        else:
            cpu_avg300_state= 2


        cpu_formatted_output[0].value = f"{cpu_avg10:<5}"
        cpu_formatted_output[0].style = cpu_avg10_state
        cpu_formatted_output[1].value = f"{cpu_avg60:<5}"
        cpu_formatted_output[1].style = cpu_avg60_state
        cpu_formatted_output[2].value = f"{cpu_avg300:<5}"
        cpu_formatted_output[2].style = cpu_avg300_state
        cpu_formatted_output[3].value= f"{cpu_pressure_health:<5.1f}"
        cpu_formatted_output[3].style= cpu_pressure_health_state
        cpu_formatted_output[4].bar_width= cpu_pressure_bar_width
        cpu_formatted_output[4].style= cpu_pressure_bar_state

        self.cpu_formatted_output= cpu_formatted_output

    def format_mem(self, system_pressure_readings:object, schedule: dict) -> list:
        if schedule["memory"] is False:
            return
        
        memory_some= system_pressure_readings.memory_some
        memory_full= system_pressure_readings.memory_full
        memory_formatted_output= self.memory_formatted_output
        memory_health= system_pressure_readings.memory_health

        some_avg10= memory_some[0]
        some_avg60= memory_some[1]
        some_avg300= memory_some[2]

        full_avg10= memory_full[0]
        full_avg60= memory_full[1]
        full_avg300= memory_full[2]

        if some_avg10 == "N/A":
            some_avg10_state= 3
        elif some_avg10 < 1.0:
            some_avg10_state= 0
        elif some_avg10 < 5.0:
            some_avg10_state= 1
        else:
            some_avg10_state= 2

        if some_avg60 == "N/A":
            some_avg60_state= 3
        elif some_avg60 < 1.0:
            some_avg60_state= 0
        elif some_avg60 < 5.0:
            some_avg60_state= 1
        else:
            some_avg60_state= 2

        if some_avg300 == "N/A":
            some_avg300_state= 3
        elif some_avg300 < 0.5:
            some_avg300_state= 0
        elif some_avg300 < 2.0:
            some_avg300_state= 1
        else:
            some_avg300_state= 2

        if full_avg10 == "N/A":
            full_avg10_state= 3
        elif full_avg10 < 0.5:
            full_avg10_state= 0
        elif full_avg10 < 1.0:
            full_avg10_state= 1
        else:
            full_avg10_state= 2

        if full_avg60 == "N/A":
            full_avg60_state= 3
        elif full_avg60 < 0.5:
            full_avg60_state= 0
        elif full_avg60 < 1.0:
            full_avg60_state= 1
        else:
            full_avg60_state= 2

        if full_avg300 == "N/A":
            full_avg300_state= 3
        elif full_avg300 < 0.1:
            full_avg300_state= 0
        elif full_avg300 < 0.5:
            full_avg300_state= 1
        else:
            full_avg300_state= 2

        if memory_health[0] == "N/A":
            mem_score_state= 3
            mem_bar_state= 3
        elif memory_health[0] >80:
            mem_score_state= 0
            mem_bar_state= 0
        elif memory_health[0] >60:
            mem_score_state= 1
            mem_bar_state= 1
        else:
            mem_score_state= 2
            mem_bar_state= 2

        memory_formatted_output[0].value= f"{some_avg10:<5}"
        memory_formatted_output[0].style= some_avg10_state
        memory_formatted_output[1].value= f"{some_avg60:<5}"
        memory_formatted_output[1].style= some_avg60_state
        memory_formatted_output[2].value= f"{some_avg300:<5}"
        memory_formatted_output[2].style= some_avg300_state
        memory_formatted_output[3].value= f"{full_avg10:<5}"
        memory_formatted_output[3].style= full_avg10_state
        memory_formatted_output[4].value= f"{full_avg60:<5}"
        memory_formatted_output[4].style= full_avg60_state
        memory_formatted_output[5].value= f"{full_avg300:<5}"
        memory_formatted_output[5].style= full_avg300_state
        memory_formatted_output[6].value= f"{memory_health[0]:<5.1f}"
        memory_formatted_output[6].style= mem_score_state
        memory_formatted_output[7].bar_width= memory_health[1]
        memory_formatted_output[7].style= mem_bar_state

        self.memory_formatted_output= memory_formatted_output

class MemoryFormatter:
    """
    Formats text and decides state (0=good, 1=warning, 2=critical, 3=muted, 4= none) for:
        Memory Information
    """

    __slots__ = (
        "memory_info_formatted_output",
    )

    def __init__(self):
        self.memory_info_formatted_output= [TextStyle("N/A", 3) for _ in range(4)]

    def format(self, memory_info_readings: object, schedule: dict) -> list:
        if schedule["memory"] is False:
            return

        mem_total= memory_info_readings.MemTotal
        mem_available= memory_info_readings.MemAvailable
        swap_total= memory_info_readings.SwapTotal
        swap_free= memory_info_readings.SwapFree
        memory_info_formatted_output= self.memory_info_formatted_output

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

class CPUFormatter:
    """
    Formats text and decides state (0=good, 1=warning, 2=critical, 3=muted, 4=blue) for:
        cpu_readings: Temp and Fan
        cpu_load
    """

    __slots__=("formatted_cpu_readings", "formatted_cpu_load")

    def __init__(self):
        self.formatted_cpu_readings= []
        self.formatted_cpu_readings.extend([
                TextStyle("N/A", 3),
                TextStyle(" ", 3, 1),
                TextStyle("N/A", 3),
                TextStyle(" ", 3, 1),
                TextStyle("N/A", 3),
                TextStyle("N/A", 3),
            ])
        self.formatted_cpu_load= []

    def format_info(self, cpu_readings: object, schedule: dict) -> list:
        if schedule["cpu"] is False:
            return
        
        cpu_temp_dict= cpu_readings.cpu_temp
        cpu_fan_dict= cpu_readings.cpu_fan
        formatted_cpu_readings= self.formatted_cpu_readings

        if cpu_readings.cpu_load_raw_data is not None:
            num_threads= len(cpu_readings.cpu_load_raw_data) - 1
            num_cpu_threads_state= 0

        else:
            num_threads= "N/A"
            num_cpu_threads_state= 3

        if cpu_temp_dict is None:
            cpu_temp_dict= {}
            return
        
        cpu_temp_dict_length= len(cpu_temp_dict)
        num_cpu_core_state=  0

        if "Package id 0" in cpu_temp_dict:
            cpu_temp_dict_length-= 1
            die_temperature_val= cpu_temp_dict["Package id 0"].temp
            die_temp= f"{die_temperature_val:>3} °C"

            if die_temperature_val <70:
                die_temp_state= 0
                die_temp_bar_state= 0
            elif die_temperature_val <85:
                die_temp_state= 1
                die_temp_bar_state= 1
            else:
                die_temp_state= 2
                die_temp_bar_state= 2
            
            die_temp_bar_width= min(24, die_temperature_val//4)

        else:
            die_temp= "N/A   " #padding with extra spaces manually
            die_temp_state= 3
            die_temp_bar_width= 0
            die_temp_bar_state= 3

        if "Average" in cpu_temp_dict:
            cpu_temp_dict_length-= 1
            average_temp_val= cpu_temp_dict["Average"]
            average_temp= f"{average_temp_val:>3} °C"

            if average_temp_val <70:
                average_temp_state= 0
                average_temp_bar_state= 0
            elif average_temp_val <85:
                average_temp_state= 1
                average_temp_bar_state= 1
            else:
                average_temp_state= 2
                average_temp_bar_state= 2

            average_temp_bar_width= min(23, average_temp_val//4)

        else:
            average_temp= "N/A   " #padding with extra spaces manually
            average_temp_state= 3
            average_temp_bar_width= 0
            average_temp_bar_state= 0

        num_cpu_threads= f" {num_threads:<4}"
        num_cpu_core= f" {cpu_temp_dict_length:<4}"
        formatted_cpu_readings[0].value= die_temp 
        formatted_cpu_readings[0].style= die_temp_state
        formatted_cpu_readings[1].bar_width = die_temp_bar_width
        formatted_cpu_readings[1].style= die_temp_bar_state
        formatted_cpu_readings[2].value= average_temp
        formatted_cpu_readings[2].style=average_temp_state
        formatted_cpu_readings[3].bar_width= average_temp_bar_width
        formatted_cpu_readings[3].style= average_temp_bar_state
        formatted_cpu_readings[4].value= num_cpu_core
        formatted_cpu_readings[4].style= num_cpu_core_state
        formatted_cpu_readings[5].value= num_cpu_threads
        formatted_cpu_readings[5].style= num_cpu_threads_state

        self.formatted_cpu_readings= formatted_cpu_readings
        
    def format_load(self, raw_cpu_load: object, cpu_load_bar_ratio: int, schedule: dict) -> list:
        if schedule["cpu"] is False:
            return
        
        cpu_load= raw_cpu_load.cpu_load
        formatted_cpu_load= self.formatted_cpu_load

        if formatted_cpu_load == []:
            formatted_cpu_load= [TextStyle("N/A", 3) for _ in cpu_load]

        for index, cpu in enumerate(cpu_load):
            cpu_load_value= cpu_load[cpu]
                
            text= f"{cpu}: {cpu_load_value} {"%":<{cpu_load_bar_ratio}}"[:cpu_load_bar_ratio - 1]
            formatted_cpu_load[index].value= text
            formatted_cpu_load[index].style= 0

            if cpu_load_value == "N/A" or cpu_load_value is None:
                formatted_cpu_load[index].bar_width= 0
            else:
                formatted_cpu_load[index].bar_width= int((cpu_load_value / 100) * cpu_load_bar_ratio)

        self.formatted_cpu_load= formatted_cpu_load

class NetworkFormatter:

    __slots__= (
        "formatted_network_output"
    )

    def __init__(self):
        self.formatted_network_output= [TextStyle(" ", 0) for _ in range(10)]

    def format(self, network_readings: object, schedule: dict) -> list:
        if schedule["network"] is False:
            return
        
        network_throughput= network_readings.throughput
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

    def format(self, nvidia_readings: object, schedule: dict) -> list:
        if schedule["nvidia"] is False:
            return
        
        gpu_readings= nvidia_readings.gpus_readings
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
                out.append([TextStyle("N/A", 3) for _ in range(12)])

            row = out[idx]
            proc_user = usernames[process.uid]
                        
            row[0].value = f"{pid:<10}"
            row[0].style = 0

            row[1].value = f"{process.ppid:<10}"
            row[1].style = 5

            row[2].value = f"{proc_user:<16.16}"
            row[2].style = 0 if proc_user in current_users else (5 if proc_user == "root" else 3)

            row[3].value = f"{process.priority:<9}"
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

            row[10].value = f"{process.name:<50}"
            row[10].style = 4

            row[11].value= process.starttime