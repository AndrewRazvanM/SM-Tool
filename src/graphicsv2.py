import curses
from functionalityv2 import *
import time

def invalidate_windows(stdscr, *windows):
    stdscr.clear()
    stdscr.touchwin()
    for w in windows:
        if w != None:
            w.touchwin()
            w.clear()

def generate_windows(stdscr):
    lines, columns = stdscr.getmaxyx()

    # Fixed layout 
    cpu_h, cpu_w = 12, 51
    mem_h, mem_w = 10, 51
    net_h, net_w = 6,  51
    gpu_h, gpu_w = 11, 51

    start_x = 0
    start_y = 1  # leave space for title

    #cpu load window
    if columns > 105 and lines >= 12:
        cpu_load_window_h= min(cpu_h+mem_h,lines)
        cpu_load_window= curses.newwin(cpu_load_window_h, columns-cpu_w, start_y, cpu_w + 1)
    else:
        stdscr.addstr(2, cpu_w+5, "Window too small", curses.A_BLINK)
        cpu_load_window= None
        cpu_load_window_h= 0

    #processes window layout
    if columns >105 and lines > max(12, cpu_load_window_h+2):
        process_h, process_w= (lines-cpu_load_window_h), (columns-cpu_w)
        process_window= curses.newwin(process_h, process_w, cpu_load_window_h + 1, cpu_w+1)
    else:
        process_window= None

    cpu_window = curses.newwin(cpu_h, cpu_w, start_y, start_x)
    memory_window = curses.newwin(mem_h, mem_w, start_y + cpu_h, start_x)
    network_window = curses.newwin(net_h, net_w, start_y + cpu_h + mem_h, start_x)
    gpu_window = curses.newwin(gpu_h, gpu_w, start_y + cpu_h + mem_h + net_h, start_x)
        
    return cpu_window, memory_window, network_window, gpu_window, cpu_load_window, process_window

def static_interface(
    stdscr,
    cpu_name,
    cpu_load_raw_data,
    cpu_temp_data,
    cpu_sensor,
    gpu_name,
    cpu_window,
    memory_window,
    network_window,
    gpu_window,
    cpu_load_window,
    cpu_load_window_ratio,
    process_window,
    stat_data
):
    normal_text= 4
    green_text= 5
    _, columns = stdscr.getmaxyx()
    stdscr.addstr(0, columns // 2 - 11, "System Monitoring Tool", curses.A_BOLD)

    #setting Backgrounds
    stdscr.bkgd(" ", curses.color_pair(normal_text))
    cpu_window.bkgd(" ", curses.color_pair(normal_text))
    memory_window.bkgd(" ", curses.color_pair(normal_text))
    network_window.bkgd(" ", curses.color_pair(normal_text))
    gpu_window.bkgd(" ", curses.color_pair(normal_text))
    if cpu_load_window is not None:
        cpu_load_window.bkgd(" ", curses.color_pair(normal_text))
    if process_window is not None:
        process_window.bkgd(" ", curses.color_pair(normal_text))

    # ---- CPU WINDOW ----
    cpu_window.box()
    cpu_window.addstr(0, 15, "CPU Dashboard", curses.A_BOLD)
    cpu_window.addstr(1, 48 - len(cpu_name), cpu_name)

    cpu_window.addstr(2, 7, "CPU Cores:")
    cpu_window.addstr(2, 18, f"{len(cpu_temp_data) - 2}")
    cpu_window.addstr(2, 31, "CPU Threads:")
    cpu_window.addstr(2, 44, f"{len(cpu_load_raw_data) - 1}")
    cpu_window.addstr(3, 1, "=" * 49)

    cpu_window.addstr(4, 11, "PSI:")
    cpu_window.addstr(4, 34, "PSI Health:")
    cpu_window.vline(4, 26, "|", 3)

    cpu_window.addstr(5, 1, "Avg10:")
    cpu_window.addstr(5, 8, "| Avg60:")
    cpu_window.addstr(5, 17, "| Avg300:")
    cpu_window.addstr(7, 1, "-" * 49)

    cpu_window.addstr(8, 13, f"Temp sensor is {cpu_sensor}")
    cpu_window.addstr(9, 7, "CPU Die:")
    cpu_window.addstr(9, 34, "CPU Avg:")
    cpu_window.vline(9, 26, "|", 2)

    # ---- MEMORY WINDOW ----
    memory_window.box()
    memory_window.addstr(0, 15, "Memory Dashboard", curses.A_BOLD)

    memory_window.addstr(1, 12, "PSI")
    memory_window.addstr(3, 2, "Some")
    memory_window.addstr(2, 8, "|  Avg 10:")
    memory_window.addstr(3, 8, "|  Avg 60:")
    memory_window.addstr(4, 8, "| Avg 300:")

    memory_window.addstr(7, 2, "Full")
    memory_window.addstr(6, 8, "|  Avg 10:")
    memory_window.addstr(7, 8, "|  Avg 60:")
    memory_window.addstr(8, 8, "| Avg 300:")
    memory_window.vline(1, 26, "|", 8)
    memory_window.addstr(5, 1, "-" * 49)

    memory_window.addstr(1, 28, "Total Memory:")
    memory_window.addstr(2, 28, " Free Memory:")
    memory_window.addstr(3, 28, "  Total SWAP:")
    memory_window.addstr(4, 28, "   Free SWAP:")
    memory_window.addstr(6, 31, "Health Score:")

    # ---- NETWORK WINDOW ----
    network_window.box()
    network_window.addstr(0, 15, "Network Dashboard", curses.A_BOLD)
    network_window.addstr(1,1, "  Upload:")
    network_window.addstr(2,1, "Up dropp:")
    network_window.addstr(3,1, "Download:")
    network_window.addstr(4,1, "Dw dropp:")
    network_window.vline(1,26, "|", 4)
    network_window.addstr(1,31, "Interfaces:")

    # ---- GPU WINDOW ----
    gpu_window.box()
    gpu_window.addstr(0, 15, "GPU Dashboard", curses.A_BOLD)
    gpu_window.addstr(1, (51-len(gpu_name[0]))//2, gpu_name[0])
    gpu_window.addstr(2, 2, "  GPU Clock:")
    gpu_window.addstr(3, 2, "  Mem Clock:")
    gpu_window.addstr(4, 2, "        Fan:")
    gpu_window.addstr(5, 2, "Memory Load:")
    gpu_window.addstr(6, 2, "   GPU Load:")
    gpu_window.addstr(8, 2, "Temperature:")

    # ---- CPU Load Window ----
    if cpu_load_window is not None:
        lines_cpu_w, columns_cpu_w = cpu_load_window.getmaxyx()
        cpu_load_window.addstr(0, 20, "CPU Load Dashboard", curses.A_BOLD)
        boxes_per_columns= (lines_cpu_w-4)//3
        boxes_nr_columns= columns_cpu_w//cpu_load_window_ratio
        box_row_index= 1
        box_column_index= 1
        cpu_index_lines= 4
        cpu_index_columns= 0        
        #per core load
        for _ in range(len(cpu_load_raw_data)-1):
            if box_row_index > boxes_per_columns:
                box_row_index = 1
                box_column_index += 1
                cpu_index_lines = 4
                cpu_index_columns += cpu_load_window_ratio

            if box_column_index > boxes_nr_columns:
                break

            cpu_load_window.addch(cpu_index_lines,cpu_index_columns, "[")                          #left side
            cpu_load_window.addch(cpu_index_lines,cpu_index_columns+cpu_load_window_ratio-1, "]")  #right side
            box_row_index += 1
            cpu_index_lines += 3

    # ---- Processes List Window ----
    if process_window is not None:
        proc_win_lines, proc_win_columns= process_window.getmaxyx()
        prev_PID= 0
        name_max= 0
        for PID in stat_data:
            name= len(stat_data[PID].name)
            if PID > prev_PID:
                prev_PID = PID
            if name > name_max:
                name_max= name
            
        max_pid_width= len(str(prev_PID))
        process_window_avail_columns= (proc_win_columns - max_pid_width - name_max)//8
        ppid_position=  max_pid_width + name_max
        priority_position= ppid_position + process_window_avail_columns
        state_position= priority_position + process_window_avail_columns
        total_time_position= state_position + process_window_avail_columns
        cpu_position= total_time_position + process_window_avail_columns
        threads_position= cpu_position + process_window_avail_columns
        vMem_position= threads_position + process_window_avail_columns
        pMem_position= vMem_position + process_window_avail_columns
        
        process_window.hline(0,0, " ", proc_win_columns, curses.color_pair(green_text) | curses.A_REVERSE)
        process_window.addstr(0, 0, f"{"PID":<{max_pid_width}}", curses.color_pair(green_text) | curses.A_REVERSE)
        process_window.addstr(0, max_pid_width, f"{"Name":>{name_max/2}}", curses.color_pair(green_text) | curses.A_REVERSE)
        process_window.addstr(0, ppid_position, f"{"PPID":<{max_pid_width}}", curses.color_pair(green_text) | curses.A_REVERSE)
        process_window.addstr(0, priority_position, "Priority", curses.color_pair(green_text) | curses.A_REVERSE | curses.A_BOLD)
        process_window.addstr(0, state_position, "State", curses.color_pair(green_text) | curses.A_REVERSE | curses.A_BOLD)
        process_window.addstr(0, total_time_position, "Up Time", curses.color_pair(green_text) | curses.A_REVERSE | curses.A_BOLD)
        process_window.addstr(0, cpu_position, "CPU %", curses.color_pair(green_text) | curses.A_REVERSE | curses.A_BOLD)
        process_window.addstr(0, threads_position, "Threads", curses.color_pair(green_text) | curses.A_REVERSE | curses.A_BOLD)
        process_window.addstr(0, vMem_position, "Virt Mem", curses.color_pair(green_text) | curses.A_REVERSE | curses.A_BOLD)
        process_window.addstr(0, pMem_position, "RSS", curses.color_pair(green_text) | curses.A_REVERSE | curses.A_BOLD)

    else:
        max_pid_width= 0
        name_max= 0
        ppid_position= 0
        priority_position= 0
        state_position= 0
        total_time_position= 0
        cpu_position= 0
        threads_position= 0
        vMem_position= 0
        pMem_position= 0
        process_window_avail_columns= 0

    #schedule refreshes
    stdscr.noutrefresh()
    cpu_window.noutrefresh()
    memory_window.noutrefresh()
    network_window.noutrefresh()
    gpu_window.noutrefresh()
    if cpu_load_window is not None:
        cpu_load_window.noutrefresh()
    if process_window is not None:
        process_window.noutrefresh()
    
    return max_pid_width, ppid_position, priority_position, state_position, total_time_position, cpu_position, threads_position, vMem_position, pMem_position, process_window_avail_columns, name_max

def scrollable_window (window, content, scroll_pos, window_nr_lines,  max_pid_width):
    white_green= 8
    window.touchwin()
    #first line is reserved for the static interface
    visible_content= content[scroll_pos:scroll_pos + window_nr_lines- 1]

    for i, (PID, string) in enumerate(visible_content):
        window.addstr(1+i, 0, f"{PID:>{max_pid_width}}", curses.color_pair(white_green) | curses.A_BOLD)
        window.addstr(1+i, max_pid_width, f"{string}")
    
    window.noutrefresh()

def main(stdscr):
    #open static files
    file_path= NeededFiles()
    #to implement check disable in the TUI later
    memory_check_disable= False
    cpu_check_disable= False
    gpu_check_disable= False
    gpu_fan_disabled= False
    gpu_mem_disabled= False
    try:
        pynvml.nvmlInit()
    except (pynvml.NVMLError_LibraryNotFound,
        pynvml.NVMLError_DriverNotLoaded,
        pynvml.NVMLError_NoPermission) as error:
        gpu_check_disable= True

    #collect initial readings needed to initialize the interface
    cpu_sensor, cpu_sensor_path= probe_cpu_sensors(cpu_check_disable)
    cpu_temp_data, cpu_temp_path= cpu_readings(cpu_check_disable, cpu_sensor_path)
    cpu_name= get_cpu_name(cpu_check_disable)
    gpu_name, gpu_handles= nvidia_gpu_name(gpu_check_disable)
    cpu_load_raw_data_prev, cpu_calc_load = get_cpu_load(cpu_check_disable, file_path)
    stat_data, status_data, process_cpu_load, status_index, prev_time, ticks_per_second= current_processes(prev_stat_data= None, data_length= 150, status_index= 0, prev_time= None, ticks_per_second= None)

    network_raw_data= None
    time_netw= None

    stdscr.clear()
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(True)
        
    #for status bars
    status_bar_ok= 1
    status_bar_warning= 2
    status_bar_critical= 3
    #for text
    normal_text= 4
    green_text= 5
    yellow_text= 6
    red_text= 7
            
    curses.curs_set(0) #set cursor to invisible
    stdscr.keypad(True)
    stdscr.nodelay(True)
    #initialize the content windows and static interfaces
    cpu_window, memory_window, network_window, gpu_window, cpu_load_window, process_window= generate_windows(stdscr)
        ##calculates how to fit all cpus loads in the cpu load window
    if cpu_load_window != None:
            lines_cpu_w, columns_cpu_w = cpu_load_window.getmaxyx()
            displayed_lines= (lines_cpu_w-4)//3
            columns_needed= int(((len(cpu_load_raw_data_prev)-1) + displayed_lines)/displayed_lines)
            cpu_load_window_ratio= (columns_cpu_w-2)//columns_needed
    else:
        cpu_load_window_ratio= 1

    max_pid_width, ppid_position, priority_position, state_position, total_time_position, cpu_position, threads_position, vMem_position, pMem_position, process_window_avail_columns, name_max= static_interface(stdscr,cpu_name,cpu_load_raw_data_prev,cpu_temp_data,cpu_sensor,gpu_name, cpu_window, memory_window, network_window, gpu_window,cpu_load_window,cpu_load_window_ratio, process_window, stat_data)
    if process_window is not None:
        process_window_lenght, process_window_columns = process_window.getmaxyx()

    #initialize colors, assign pairs, set default colors and set default background
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED,  curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_GREEN)

    #initialize static variables
        #for cpu
    next_temp_net_read= 0 #will scan for temperatures once a second
    next_load_read= 0 #will calculate the cpu load 2 times a second
    cpu_average_temp= 0
    cpu_load_raw_data= {}
        #for monotonic time measuring
    interval = 0.2
    interface_refresh = time.monotonic()
        #for processes
    next_process_scan= 2 # will scan the processes once every 2 seconds
    stat_data= None
    status_index= 0
    data_length= 500 #will make this changable by the user in the future
    process_window_content= []
    scroll_pos = 0
    if process_window is not None:
        process_window_lenght, process_window_columns = process_window.getmaxyx()
        #for gpu
    next_gpu_read= 1 #reads every 1 sec
        #for memory
    next_pressure_mem_read= 0 #reads every sec

    while True:
        data_collection= time.monotonic()
        key_press= stdscr.getch()
        cpu_average_temp= 0 #resets to avoid weird errors
        #redraws content windows on resize
        if key_press == curses.KEY_RESIZE:
            invalidate_windows(stdscr, cpu_window, memory_window, network_window, gpu_window,cpu_load_window, process_window)
            cpu_window, memory_window, network_window, gpu_window, cpu_load_window, process_window= generate_windows(stdscr)
            #calculate how many processes can fit in the window
            if process_window is not None:
                process_window_lenght, _= process_window.getmaxyx()
            if cpu_load_window is not None:
                lines_cpu_w, columns_cpu_w = cpu_load_window.getmaxyx()
                #calculates how to fit all cpus loads in the cpu load window
                displayed_lines= (lines_cpu_w-4)//3
                columns_needed= int(((len(cpu_load_raw_data)-1) + displayed_lines)/displayed_lines)
                cpu_load_window_ratio= (columns_cpu_w-2)//columns_needed 
            max_pid_width, ppid_position, priority_position, state_position, total_time_position, cpu_position, threads_position, vMem_position, pMem_position, process_window_avail_columns, name_max= static_interface(stdscr,cpu_name,cpu_load_raw_data,cpu_temp_data,cpu_sensor,gpu_name,cpu_window,memory_window,network_window,gpu_window, cpu_load_window, cpu_load_window_ratio, process_window, stat_data)
            if process_window is not None:
                process_window_lenght, process_window_columns = process_window.getmaxyx()

        #collect readings - decoupled them from the interface refresh
        if data_collection > next_temp_net_read:
            cpu_temp_data, cpu_temp_path= cpu_readings(cpu_check_disable, cpu_sensor_path, cpu_temp_path)
            network_raw_data, network_data, time_netw= network_traffic(file_path, network_raw_data, time_netw)
            next_temp_net_read= data_collection + 1

        if data_collection > next_load_read:
            cpu_load_raw_data, cpu_calc_load= get_cpu_load(cpu_check_disable, file_path, cpu_load_raw_data)
            next_load_read= data_collection + 1

        if data_collection > next_pressure_mem_read:
            cpu_pressure, memory_pressure= system_pressure(cpu_check_disable,memory_check_disable, file_path)
            memory_total= memory_readings(memory_check_disable, file_path)
            next_pressure_mem_read= data_collection + 1.5

        if data_collection > next_gpu_read:
            gpu_data, gpu_fan_disabled, gpu_mem_disabled= nvidia_gpu_readings(gpu_check_disable, gpu_handles, gpu_fan_disabled, gpu_mem_disabled)
            next_gpu_read= data_collection + 1

        if data_collection > next_process_scan:
            stat_data, status_data, process_cpu_load, status_index, prev_time, ticks_per_second= current_processes(stat_data, data_length, status_index, prev_time, ticks_per_second)
            next_process_scan= data_collection + 2

        #CPU window dinamic data render
        cpu_window.addstr(6,2, f"{cpu_pressure["avg10"]:>4}")
        cpu_window.addstr(6,11, f"{cpu_pressure["avg60"]:>4}")
        cpu_window.addstr(6,21, f"{cpu_pressure["avg300"]:>4}")
        if cpu_pressure["avg60"] != "N/A":
            penalty_cpu= cpu_pressure["avg10"] *2.0 + cpu_pressure["avg60"] * 6.0 + cpu_pressure["avg300"] * 50.0
            cpu_health_bar= max(0,100- penalty_cpu)
            cpu_health_bar_ratio= int(cpu_health_bar//4.34)
            if ((cpu_pressure["avg10"] <1.0) or (cpu_pressure["avg60"] <1.0) or (cpu_pressure["avg300"] <0.5)):
                cpu_window.addstr(5,35, "Healthy ", curses.color_pair(green_text))
                #status bar - green
                #22 is the usable window width
                cpu_window.hline(6, 27, " ", cpu_health_bar_ratio, curses.color_pair(status_bar_ok) | curses.A_REVERSE)
                cpu_window.hline(6, 27+ cpu_health_bar_ratio , " ", 22- cpu_health_bar_ratio)
                
            elif ((cpu_pressure["avg10"] <5.0) or (cpu_pressure["avg60"] <5.0) or (cpu_pressure["avg300"] <2.0)):
                cpu_window.addstr(5, 35, "Degraded", curses.color_pair(yellow_text))
                #status bar - yellow
                cpu_window.hline(6, 27, " ", cpu_health_bar_ratio, curses.color_pair(status_bar_warning) | curses.A_REVERSE)
                cpu_window.hline(6, 27+ cpu_health_bar_ratio, " ", 22- cpu_health_bar_ratio)
            else:
                cpu_window.addstr(5, 35, "Critical", curses.color_pair(red_text))
                #status bar - critical
                cpu_window.hline(6, 27, " ", cpu_health_bar_ratio, curses.color_pair(status_bar_critical) | curses.A_REVERSE)
                cpu_window.hline(6, 27+ cpu_health_bar_ratio, " ", 22-cpu_health_bar_ratio)
        else:
            cpu_window.addstr(5,35, "N/A")

        #average temp calc
        if cpu_sensor_path != "N/A":
            cpu_window.addstr(9,15, f"{cpu_temp_data["Package id 0"]:>3} °C")
            if cpu_temp_data["Package id 0"] != "N/A":
                temp_index= 0
                for core in sorted(cpu_temp_data):
                    if ((core != "Package id 0") and (core != "CPU Fan")):
                        temp_index+= 1
                        cpu_average_temp+= cpu_temp_data[core]
                cpu_average_temp= cpu_average_temp//temp_index
            else:
                cpu_average_temp= "N/A"

            cpu_window.addstr(9,42, f"{cpu_average_temp:>3} °C")
            #die temp bars
            if cpu_temp_data["Package id 0"] != "N/A":
                if cpu_temp_data["Package id 0"] < 75:
                    #column lenght is 24 - add the bar and remove any previous columns
                    cpu_window.hline(10, 1, " ", cpu_temp_data["Package id 0"]//5, curses.color_pair(status_bar_ok) | curses.A_REVERSE)
                    cpu_window.hline(10, min(24, 1+ cpu_temp_data["Package id 0"]//5), " ", max(0, 24-cpu_temp_data["Package id 0"]//5))
                elif cpu_temp_data["Package id 0"] < 90:
                    cpu_window.hline(10, 1, " ", cpu_temp_data["Package id 0"]//5, curses.color_pair(status_bar_warning) | curses.A_REVERSE)
                    cpu_window.hline(10, min(24, 1+ cpu_temp_data["Package id 0"]//5), " ", max(0, 24-cpu_temp_data["Package id 0"]//5))
                else:
                    cpu_window.hline(10, 1, " ", cpu_temp_data["Package id 0"]//5, curses.color_pair(status_bar_critical) | curses.A_REVERSE)
                    cpu_window.hline(10, min(24, 1+ cpu_temp_data["Package id 0"]//5), " ", max(0, 24-cpu_temp_data["Package id 0"]//5))

            #avg temp bars - max width is 23
            if cpu_average_temp != "N/A":
                if cpu_average_temp <75:
                    cpu_window.hline(10, 27, " ", int(cpu_average_temp//4.34), curses.color_pair(status_bar_ok) | curses.A_REVERSE)
                    cpu_window.hline(10, 27+ int(cpu_average_temp//4.34), " ", 23-int(cpu_average_temp//4.34))
                elif cpu_average_temp <90:
                    cpu_window.hline(10, 27, " ", int(cpu_average_temp//4.34), curses.color_pair(status_bar_warning) | curses.A_REVERSE)
                    cpu_window.hline(10, 27+ int(cpu_average_temp//4.34), " ", 23-int(cpu_average_temp//4.34))
                else:
                    cpu_window.hline(10, 27, " ", int(cpu_average_temp//4.34), curses.color_pair(status_bar_critical) | curses.A_REVERSE)
                    cpu_window.hline(10, 27+ int(cpu_average_temp//4.34), " ", 23-int(cpu_average_temp//4.34))
        else:
            cpu_window.addstr(9,42, "N/A")
            cpu_window.addstr(9,15, "N/A")


        cpu_window.noutrefresh()

        #Memory Dashboard dinamic content
        memory_window.addstr(2, 19, f"{memory_pressure["some"]["avg10"]:>6} ")
        memory_window.addstr(3, 19, f"{memory_pressure["some"]["avg60"]:>6} ")
        memory_window.addstr(4, 19, f"{memory_pressure["some"]["avg300"]:>6} ")
        memory_window.addstr(6, 19, f"{memory_pressure["full"]["avg10"]:>6} ")
        memory_window.addstr(7, 19, f"{memory_pressure["full"]["avg60"]:>6} ")
        memory_window.addstr(8, 19, f"{memory_pressure["full"]["avg300"]:>6} ")
        memory_window.addstr(1, 42, f"{round(memory_total["MemTotal"]/1048576, 1):>5} GB")
        memory_window.addstr(2, 42, f"{round(memory_total["MemAvailable"]/1048576, 1):>5} GB")
        memory_window.addstr(3, 42, f"{round(memory_total["SwapTotal"]/1048576, 1):>5} GB")
        memory_window.addstr(4, 42, f"{round(memory_total["SwapFree"]/1048576, 1):>5} GB")
        #memory health calc and bar
        penalty_mem= (memory_pressure["some"]["avg10"] + memory_pressure["some"]["avg60"]* 2.00 + memory_pressure["some"]["avg300"]* 3.00 + memory_pressure["full"]["avg10"]* 20.00 + memory_pressure["full"]["avg60"]* 40.00 + memory_pressure["full"]["avg300"]* 60.00)
        mem_health_bar= max(0,100- penalty_mem)
        memory_window.addstr(7, 35, f"{mem_health_bar}    ")
        mem_health_bar_ratio= int(mem_health_bar//4.34)
        if mem_health_bar > 80.0:
            #available width is 23
            memory_window.hline(8, 27, " ", mem_health_bar_ratio, curses.color_pair(status_bar_ok) | curses.A_REVERSE)
            memory_window.hline(8, 27 + mem_health_bar_ratio, " ", 23- mem_health_bar_ratio)
        elif mem_health_bar > 60:
            memory_window.hline(8, 27, " ", mem_health_bar_ratio, curses.color_pair(status_bar_warning) | curses.A_REVERSE)
            memory_window.hline(8, 27 + mem_health_bar_ratio, " ", 23- mem_health_bar_ratio)
        else:
            memory_window.hline(8, 27, " ", mem_health_bar_ratio, curses.color_pair(status_bar_critical) | curses.A_REVERSE)
            memory_window.hline(8, 27 + mem_health_bar_ratio, " ", 23- mem_health_bar_ratio)

        memory_window.noutrefresh()

        #Network Dashboard dinamic content
        if network_data != {}:
            #converts to MB/s + string
            total_trans= f"{round((network_data["Total"]["Transmitted bytes"]* 8)/ 1000000, 3)} MB/s"
            total_received= f"{round((network_data["Total"]["Received bytes"]* 8)/ 1000000, 3)} MB/s"
            total_tr_dropped= f"{round((network_data["Total"]["Transmitted drop"]* 8)/ 1000000, 3)} MB/s"
            total_re_dropped= f"{round((network_data["Total"]["Received drop"]* 8)/ 1000000, 3)} MB/s"

            network_window.addstr(1, 11, f"{total_trans:>15}")
            network_window.addstr(2, 11, f"{total_tr_dropped:>15}")
            network_window.addstr(3, 11, f"{total_received:>15}")
            network_window.addstr(4, 11, f"{total_re_dropped:>15}")
            window_limit_counter=0
            for interface in network_data:
                if interface != "Total":
                    if network_data[interface]["Type"] == "Physical":
                        network_window.addstr(2+ window_limit_counter,31, f"{interface:>8}")
                        window_limit_counter+= 1
                    if window_limit_counter == 3:
                        break
        
        else:
            network_window.addstr(1, 11, "N/A")
            network_window.addstr(2, 11, "N/A")
            network_window.addstr(3, 11, "N/A")
            network_window.addstr(4, 11, "N/A")
            network_window.addstr(2, 36, "N/A")

        network_window.noutrefresh()

        #GPU Window Dinamic content
        if gpu_handles is not None:
            if gpu_check_disable is not True:
                gpu_window.addstr(2, 14, f"{gpu_data[0]["GPU Clock Speed"]:>6} MHz")
                gpu_window.addstr(3, 14, f"{gpu_data[0]["GPU Mem Clock"]:>6} Mhz")

            else:
                gpu_window.addstr(2, 14, f"{gpu_data[0]["GPU Clock Speed"]:>6}")
                gpu_window.addstr(3, 14, f"{gpu_data[0]["GPU Mem Clock"]:>6} Mhz")

            gpu_window.addstr(4, 15, f"{gpu_data[0]["Fan Speed"]:>5}")
            gpu_window.addstr(5, 14, f"{gpu_data[0]["Memory Load"]:>6}")
            gpu_window.addstr(6, 14, f"{gpu_data[0]["GPU Load"]:>6}")
            #available width is 49
            max_bar_width_l= min(49, (gpu_data[0]["GPU Load"]//2)) #guards agains random errors
            max_bar_width_t= min(49, (gpu_data[0]["Temperature"]//2)) ##guards agains random errors
            if gpu_check_disable is not True:
                #gpu load bar
                gpu_window.hline(7, 1, " ", max_bar_width_l,curses.color_pair(status_bar_ok) | curses.A_REVERSE)
                gpu_window.hline(7, 1 + max_bar_width_l, " ", 49 - max_bar_width_l)
                #gpu temp + TEMP bar
                gpu_window.addstr(8, 14, f"{gpu_data[0]["Temperature"]:>6} °C")
                if gpu_data[0]["Temperature"] < 75:
                    gpu_window.hline(9, 1, " ", max_bar_width_t,curses.color_pair(status_bar_ok) | curses.A_REVERSE)
                    gpu_window.hline(9, 1 + max_bar_width_t, " ", 49 - max_bar_width_t)
                elif gpu_data[0]["Temperature"] < 87:
                    gpu_window.hline(9, 1, " ", max_bar_width_t,curses.color_pair(status_bar_warning) | curses.A_REVERSE)
                    gpu_window.hline(9, 1 + max_bar_width_t, " ", 49 - max_bar_width_t)
                else:
                    gpu_window.hline(9, 1, " ", max_bar_width_t,curses.color_pair(status_bar_critical) | curses.A_REVERSE)
                    gpu_window.hline(9, 1 + max_bar_width_t, " ", 49 - max_bar_width_t)
        else:
             gpu_window.addstr(2, 14, "N/A")
             gpu_window.addstr(3, 14, "N/A")
             gpu_window.addstr(4, 14, "N/A")
             gpu_window.addstr(5, 14, "N/A")
             gpu_window.addstr(6, 14, "N/A")

        gpu_window.noutrefresh()

        #cpu load window dinamic render
        if cpu_load_window is not None:
            lines_cpu_w, columns_cpu_w = cpu_load_window.getmaxyx()
            if cpu_calc_load != {}:
                cpu_index_lines= 4
                cpu_index_columns= 1
                #total load status bar
                total_bar= min(columns_cpu_w-2,100)
                total_bar_ratio= 100/total_bar #calculates lenght for the bar, when at 100% -> this is the maximum of characters I should ever have
                total_bar_length= int(cpu_calc_load["CPU"]//total_bar_ratio)
                cpu_load_window.hline(1, 1, " ", total_bar)
                cpu_load_window.hline(1, 1, " ", total_bar_length, curses.color_pair(status_bar_ok) | curses.A_REVERSE)

                #overlays text for total load over status bar => ensures each letter has the proper background 
                tot_text_to_add= f"Total Load: {cpu_calc_load["CPU"]:>5} %"
                for i, ch in enumerate(tot_text_to_add):
                    if i <= total_bar_length:
                        cpu_load_window.addch(1, 1+i, ch, curses.color_pair(status_bar_ok) | curses.A_REVERSE | curses.A_BOLD)
                    else:
                        cpu_load_window.addch(1, 1+i, ch, curses.color_pair(normal_text) | curses.A_BOLD)

                #per core load
                for cpu in cpu_calc_load:
                    if cpu == "CPU":
                        continue

                    if cpu_index_lines > (lines_cpu_w-2):
                        cpu_index_lines= 4
                        cpu_index_columns+= cpu_load_window_ratio

                    if cpu_index_columns >= (columns_cpu_w-(cpu_load_window_ratio-2)): 
                        break
                    #status bar showing current per core load
                    per_core_bar_ratio= 100//cpu_load_window_ratio # calculates the ratio for 100% LOAD -> this is the maxiumu possible load
                    bar_length= min(cpu_load_window_ratio, int(cpu_calc_load[cpu]//per_core_bar_ratio)) #guards against random errors
                    cpu_load_window.hline(cpu_index_lines, cpu_index_columns, " ", bar_length, curses.color_pair(status_bar_ok) | curses.A_REVERSE)
                    cpu_load_window.hline(cpu_index_lines, cpu_index_columns+ bar_length, " ", (cpu_load_window_ratio - bar_length-2))
                   
                    #overlays text over the status bar -> keeps backgrounds color
                    text_to_add= f"{cpu}: {cpu_calc_load[cpu]:>5} %"
                    for i, ch in enumerate(text_to_add):
                        if i <= bar_length:
                            cpu_load_window.addch(cpu_index_lines, cpu_index_columns+i, f"{ch}", curses.color_pair(status_bar_ok) | curses.A_REVERSE | curses.A_BOLD) 
                        else:
                            cpu_load_window.addch(cpu_index_lines, cpu_index_columns+i, f"{ch}", curses.A_BOLD)
                    cpu_index_lines += 3

            cpu_load_window.noutrefresh()

        # Process Window dinamic render
        #supports scrolling through the process list
        if process_window is not None:

            process_window_content= [None] * len(stat_data) #small optimization -> pre-allocates list-size
            
            if process_cpu_load != {}:
                last_column= (process_window_columns- max_pid_width)
                sorted_processes= sorted(process_cpu_load.items(), key= lambda item:item[1], reverse= True)
                for i, tuplet in enumerate(sorted_processes):
                    PID, cpu_load = tuplet
                    #create the strings 
                    empty_string= list(" " * last_column)
                    name_string= list(f"{stat_data[PID].name:<{name_max}}")
                    priority_string= list(f"{stat_data[PID].priority:>4}")
                    state_string= list(f"{stat_data[PID].state:<{process_window_avail_columns}}")
                    process_uptime_seconds= (stat_data[PID].process_time/ticks_per_second) #coverts the process time to seconds
                    if process_uptime_seconds >60:
                        process_uptime_values= f"{process_uptime_seconds//60} M" #converts the time to minute and makes it a string
                    else:
                        process_uptime_values= f"{process_uptime_seconds} S" #makes it into a string and keeps it as seconds

                    process_uptime_string= list(f"{process_uptime_values:<{process_window_avail_columns}}") 
                    cpu_string= list(f"{cpu_load:<{process_window_avail_columns}}")
                    if PID in status_data:
                        ppid_string= list(f"{status_data[PID].PPid:>{max_pid_width}}")
                    else:
                        ppid_string= list("N/A")
                    threads_string= list(f"{stat_data[PID].num_threads:<{process_window_avail_columns}}")
                    vMem_value= f"{stat_data[PID].vsize} GB"
                    vMem_string= list(f"{vMem_value:<{process_window_avail_columns}}")
                    pMem_string= list(f"{stat_data[PID].rss:<{process_window_avail_columns}}")

                    #add the strings in a list on specific positions
                    empty_string[0:ppid_position]= name_string
                    empty_string[ppid_position - max_pid_width:priority_position - 1]= ppid_string
                    empty_string[priority_position - max_pid_width:state_position-1]= priority_string[-process_window_avail_columns:]
                    empty_string[state_position - max_pid_width:total_time_position-1]= state_string[-process_window_avail_columns:]
                    empty_string[total_time_position - max_pid_width:cpu_position-1]= process_uptime_string[-process_window_avail_columns:]
                    empty_string[cpu_position - max_pid_width:threads_position-1]= cpu_string[-process_window_avail_columns:]
                    empty_string[threads_position - max_pid_width:vMem_position-1]= threads_string[-process_window_avail_columns:]
                    empty_string[vMem_position - max_pid_width:pMem_position-1]= vMem_string[-process_window_avail_columns:]
                    empty_string[pMem_position - max_pid_width:last_column]= pMem_string[-process_window_avail_columns:]
                    #combine them into a single one
                    content= "".join(empty_string)
                    process_window_content[i] = (PID, content) #build content list

            else:
                for i, PID in enumerate(stat_data):
                    content= f"{stat_data[PID].name:>{max_pid_width}}"
                    content= content+ " "* process_window_avail_columns
                    process_window_content[i] =  (PID, content) #build content list

            if key_press == curses.KEY_DOWN:
                scroll_pos = min(scroll_pos + 1, len(process_window_content) - (process_window_lenght-1))
            elif key_press == curses.KEY_UP:
                scroll_pos = max(scroll_pos - 1, 0)

            scrollable_window (process_window, process_window_content, scroll_pos, (process_window_lenght - 1), max_pid_width)

            process_window.noutrefresh()

        curses.doupdate()

        #enforicng updates at monotonic intervals
        interface_refresh += interval
        sleep_time = interface_refresh - time.monotonic()
        if sleep_time > 0:
            time.sleep(sleep_time)

        if key_press == ord("q"):
            file_path.close_all
            for file in cpu_temp_path:
                cpu_temp_path[file].close()

            if gpu_check_disable is False:
                try:
                    pynvml.nvmlShutdown()
                except pynvml.NVML_ERROR_UNINITIALIZED:
                    pass
            print("Program was stopped by the user.")
            break

if __name__ == "__main__":
    curses.wrapper(main)