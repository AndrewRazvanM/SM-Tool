import curses
from functionalityv2 import *
import time

class StaticInterface():

    def global_win(self, stdscr):
        _, columns = stdscr.getmaxyx()
        stdscr.addstr(0, columns // 2 - 11, "System Monitoring Tool", curses.A_BOLD)
        stdscr.noutrefresh()

    def cpu(self, cpu_window, cpu_sensor, cpu_name, cpu_temp_data, cpu_load_raw_data):
        cpu_window.box()
        cpu_window.addstr(0, 15, "CPU Dashboard", curses.A_BOLD)
        cpu_window.addstr(1, max(0,48 - len(cpu_name)), cpu_name)

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
        cpu_window.noutrefresh()

    def memory(self, memory_window):
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
        memory_window.noutrefresh()

    def network(self, network_window):
        network_window.box()
        network_window.addstr(0, 15, "Network Dashboard", curses.A_BOLD)
        network_window.addstr(1,1, "  Upload:")
        network_window.addstr(2,1, "Up dropp:")
        network_window.addstr(3,1, "Download:")
        network_window.addstr(4,1, "Dw dropp:")
        network_window.vline(1,26, "|", 4)
        network_window.addstr(1,31, "Interfaces:")
        network_window.noutrefresh()

    def gpu(self, gpu_window, gpu_name):
        gpu_window.box()
        gpu_window.addstr(0, 15, "GPU Dashboard", curses.A_BOLD)
        gpu_window.addstr(1, (51-len(gpu_name[0]))//2, gpu_name[0])
        gpu_window.addstr(2, 2, "  GPU Clock:")
        gpu_window.addstr(3, 2, "  Mem Clock:")
        gpu_window.addstr(4, 2, "        Fan:")
        gpu_window.addstr(5, 2, "Memory Load:")
        gpu_window.addstr(6, 2, "   GPU Load:")
        gpu_window.addstr(8, 2, "Temperature:")
        gpu_window.noutrefresh()

    def cpu_load(self, cpu_load_window, cpu_load_raw_data, cpu_load_window_ratio):
        if cpu_load_window is not None:
            cpu_window_lines, cpu_window_columns = cpu_load_window.getmaxyx()
            cpu_load_window.addstr(0, 20, "CPU Load Dashboard", curses.A_BOLD)
            boxes_per_columns= (cpu_window_lines-4)//3
            boxes_nr_columns= cpu_window_columns//cpu_load_window_ratio
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

            cpu_load_window.noutrefresh()

    def processes(self, process_window, process_stat_data, proc_win_columns, green_text= 5):
        if process_window is not None:
            
            prev_PID= 0
            for PID in process_stat_data:
                if PID > prev_PID:
                    prev_PID = PID

            ppid_max_length= max(3,len(str(prev_PID)))
            user_max_length= 13 #len(RunningUnder) + 1 // will need to implement a check for max size; PID example above
            priority_max_length= 10 #len(Priority) + 2 (space between text)
            state_max_length= 4 #len(ST) + 2
            total_time_max_length= 9 #len(up-time) +2
            threads_max_length= 9 #len(Threads) + 2
            cpu_max_length= 6 #len(100.0) + 2
            vMem_max_length= 10 #len(99999 MB) + 2 
            pMem_max_length= 8 #len(999 MB) + 2 // currently doesn't convert to MB
            process_text_lengths= (ppid_max_length, user_max_length, priority_max_length, state_max_length, total_time_max_length, threads_max_length, cpu_max_length, vMem_max_length, pMem_max_length)
            #buid the static interface as a single line
            line= f"{"PID":<{ppid_max_length}}{"PPID":>{ppid_max_length}}{"RunningUnder":>{user_max_length}}{"Priority":>{priority_max_length}}{"ST":>{state_max_length}}{"Up-Time":>{total_time_max_length}}{"Threads":>{threads_max_length}}{"CPU%":>{cpu_max_length}}{"VMem":>{vMem_max_length}}{"RSS":>{pMem_max_length}}{"Name":>6}{" ":>{proc_win_columns}}"
            process_window.addnstr(0,0, f"{line}", proc_win_columns, curses.color_pair(green_text) | curses.A_REVERSE)

        else:
            process_text_lengths= (0,0,0,0,0,0,0,0,0)

        process_window.noutrefresh()
        
        return process_text_lengths

class ContentDiff:
    def __init__(self, win):
        self.win= win
        self.prev_lines= []
        self.current_lines= []
        _, self.window_max_width= win.getmaxyx()

    def resize (self, win):
        self.prev_lines= []
        _, self.window_max_width= win.getmaxyx()

    def render(self):
        prev= self.prev_lines
        current= self.current_lines
        prev_len= len(prev)
        window_max_width= self.window_max_width
        for i, line in enumerate(current):
            if i >= prev_len or line != prev[i]:
                text, text_max_length, (is_bar, bar_length, bar_max), attribute, y, x= current[i]
                if is_bar is False:
                    if attribute is None:
                        self.win.addnstr(y, x, text, text_max_length - 1)
                    else:
                        self.win.addnstr(y, x, text, text_max_length - 1, attribute)
                else:
                    max_width= min(window_max_width - x, bar_max)
                    filled= min(bar_length, max_width)
                    empty= max_width - filled
                    self.win.hline(y, x, text, filled, attribute)
                    self.win.hline(y, x + filled, text, empty)

        self.prev_lines= self.current_lines.copy()
        self.win.noutrefresh()

class CpuDashboard():
    def __init__(self, win):
        self.view= ContentDiff(win)

    def update(self, cpu_temp_data, cpu_pressure_data, cpu_sensor_path):
        temp_state, pressure_state= cpu_dashboard_state(cpu_temp_data, cpu_pressure_data, cpu_sensor_path)
        self.view.current_lines= cpu_dashboard_layout(temp_state, pressure_state)

    def render(self):
        self.view.render()

class MemoryDashboard():
    def __init__(self, win):
        self.view= ContentDiff(win)
        
    def update(self, memory_data, memory_pressure_data):
        memory_state, memory_pressure_state= memory_dashboard_state(memory_data, memory_pressure_data)
        self.view.current_lines= memory_dashboard_layout(memory_state, memory_pressure_state)

    def render(self):
        self.view.render()

class NetworkDashboard():
    def __init__(self, win):
        self.view= ContentDiff(win)

    def update(self, network_data):
        total_trans, total_received, total_tr_dropped, total_re_dropped, interfaces_list= network_dashboard_state(network_data)
        self.view.current_lines= network_dashboard_layout(total_trans, total_received, total_tr_dropped, total_re_dropped, interfaces_list)

    def render(self):
        self.view.render()

class CpuLoadDashboard():
    def __init__(self, win):
        self.view= ContentDiff(win)

    def update(self, cpu_load_data, cpu_load_window_ratio, cpu_window_lines, cpu_window_columns):
        load_state_total, load_state= cpu_load_state(cpu_load_data, cpu_load_window_ratio, cpu_window_lines, cpu_window_columns)
        self.view.current_lines= cpu_load_layout(load_state_total, load_state)

    def render(self):
        self.view.render()

class GpuDashboard():
    def __init__(self, win):
        self.view= ContentDiff(win)

    def update(self, gpu_data, gpu_check_disable, status_bar_ok= 1, status_bar_warning= 2, status_bar_critical= 3):
        state= gpu_dashboard_state(gpu_data, gpu_check_disable, status_bar_ok, status_bar_warning, status_bar_critical)
        self.view.current_lines= gpu_dashboard_layout(state)

    def render(self):
        self.view.render()

class ProcessDashboard():

    def __init__(self, height, width, pad_start_y, pad_start_x):
        # Visible window size (NOT pad size)
        self.height = height - 2 #For header and end of stdscr 
        self.width = width - 1 

        # Screen coordinates where the pad will be displayed
        self.y = pad_start_y
        self.x = pad_start_x

        # Scrolling state
        self.scroll_pos = 0

        # Pad state
        self.pad = None
        self.total_rows = 0  # total rows inside the pad

    def rebuild_pad(self, process_window_content):
        """
        Rebuilds the entire pad using full process content.
        Should only be called when process data refreshes (every 2s).
        """

        # Total rows equals number of lines in content
        self.total_rows = max(2, len(process_window_content))

        # Create pad large enough to hold ALL rows
        normal_text= 4 #white fgd - black bkgd
        self.pad = curses.newpad(self.total_rows, self.width)
        self.pad.bkgd(" ", curses.color_pair(normal_text))

        # Fill pad
        for _, line in enumerate(process_window_content):
            text, text_max_length, _, attribute, y, x = line

            try:
                if attribute is None:
                    self.pad.addnstr(y, x, text, text_max_length - 1)
                else:
                    self.pad.addnstr(y, x, text, text_max_length - 1, attribute)
            except curses.error:
                # Ignore drawing errors caused by edge clipping
                pass

        self._clamp_scroll()

    def _clamp_scroll(self):
        """
        Ensures scroll_pos is always within legal bounds.
        """
        max_scroll = max(0, self.total_rows - self.height)

        if self.scroll_pos > max_scroll:
            self.scroll_pos = max_scroll
        if self.scroll_pos < 0:
            self.scroll_pos = 0

    def render(self):
        """
        Displays the visible portion of the pad onto the screen.
        Called every UI refresh.
        """

        if self.pad is None:
            return

        self._clamp_scroll()

        lower_y = self.y + self.height - 1
        lower_x = self.x + self.width - 1

        try:
            self.pad.noutrefresh(
                self.scroll_pos,  # pad row start
                0,                # pad column start
                self.y,           # screen top-left y
                self.x,           # screen top-left x
                lower_y,          # screen bottom-right y
                lower_x           # screen bottom-right x
            )
        except curses.error:
            # Prevent crash if resize happens mid-refresh
            pass

    def scroll_input(self, key):
        """
        Handles arrow key scrolling.
        """

        if key == curses.KEY_DOWN:
            if self.scroll_pos < self.total_rows - self.height:
                self.scroll_pos += 1

        elif key == curses.KEY_UP:
            if self.scroll_pos > 0:
                self.scroll_pos -= 1

def cpu_dashboard_state(cpu_temp_data, cpu_pressure_data, cpu_sensor_path, status_bar_ok= 1, status_bar_warning= 2, status_bar_critical= 3, green_text=5, yellow_text= 6, red_text= 7):
        #perssure state
        avg10= cpu_pressure_data["avg10"]
        avg60= cpu_pressure_data["avg60"]
        avg300= cpu_pressure_data["avg300"]
        if avg60 != "N/A":
            penalty_cpu= avg10 * 2.0 + avg60 * 6.0 + avg300 * 50.0
            cpu_health_bar= max(0,100- penalty_cpu)
            cpu_pressure_bar_length= int(cpu_health_bar//4.34)
            #calculate pressure bar. 22 is the usable window width
            if ((avg10 <1.0) or (avg60 <1.0) or (avg300 <0.5)):
                pressure_health_text= f"{"Healthy":>8}"
                pressure_health_attr= curses.color_pair(green_text) 
                pressure_bar_attr= curses.color_pair(status_bar_ok) | curses.A_REVERSE 
                
            elif ((avg10 <5.0) or (avg60 <5.0) or (avg300 <2.0)):
                pressure_health_text= "Degraded"
                pressure_health_attr= curses.color_pair(yellow_text) 
                pressure_bar_attr= curses.color_pair(status_bar_warning) | curses.A_REVERSE 
 
            else:
                pressure_health_text= "Critical"
                pressure_health_attr= curses.color_pair(red_text)
                pressure_bar_attr= curses.color_pair(status_bar_critical) | curses.A_REVERSE 
                
        else:
            pressure_health_text= "N/A"
            pressure_health_attr= curses.A_DIM
            pressure_bar_attr= curses.A_DIM
            cpu_pressure_bar_length= 0

        if avg60 != "N/A":
            if avg10 < 1.0:
                avg10_attr= curses.color_pair(green_text) 
            elif avg10 <5.0:
                avg10_attr= curses.color_pair(yellow_text) 
            else:
                avg10_attr= curses.color_pair(red_text) 

            if avg60 < 1.0:
                avg60_attr= curses.color_pair(green_text) 
            elif avg60 <5.0:
                avg60_attr= curses.color_pair(yellow_text) 
            else:
                avg60_attr= curses.color_pair(red_text) 

            if avg300 < 1.0:
                avg300_attr= curses.color_pair(green_text) 
            elif avg300 <5.0:
                avg300_attr= curses.color_pair(yellow_text) 
            else:
                avg300_attr= curses.color_pair(red_text) 

        else:
            avg10_attr= curses.A_DIM
            avg60_attr= curses.A_DIM
            avg300_attr= curses.A_DIM

        avg10= f"{avg10:>4}"
        avg60= f"{avg60:>4}"
        avg300= f"{avg300:>4}"

        pressure_state= ((avg10, avg10_attr), (avg60, avg60_attr), (avg300, avg300_attr), (pressure_health_text, pressure_health_attr), (cpu_pressure_bar_length, pressure_bar_attr)) #just for readability

        #temperature state
        
        cpu_die_temp= cpu_temp_data["Package id 0"]
        cpu_average_temp= 0
        if cpu_sensor_path != "N/A":
            cpu_die_temp_text= f"{cpu_die_temp:>3} °C"
            cpu_die_bar_length= int(cpu_die_temp//5)
            #calc average temp
            if cpu_die_temp != "N/A":
                temp_index= 0
                for core in cpu_temp_data:
                    if ((core != "Package id 0") and (core != "CPU Fan")):
                        temp_index+= 1
                        cpu_average_temp+= cpu_temp_data[core]

                cpu_average_temp= cpu_average_temp//temp_index
                cpu_average_bar_length= int(cpu_average_temp // 4.34)
                cpu_average_temp_text= f"{cpu_average_temp:>3} °C"
            else:
                cpu_average_temp_text= f"{"N/A":<6}"

            #die temp bars. usable width is 24
            if cpu_die_temp != "N/A":
                if cpu_die_temp < 75:
                    cpu_die_bar_attr= curses.color_pair(status_bar_ok) | curses.A_REVERSE
                    cpu_die_temp_attr= curses.color_pair(green_text)
                elif cpu_die_temp < 90:
                    cpu_die_bar_attr= curses.color_pair(status_bar_warning) | curses.A_REVERSE
                    cpu_die_temp_attr= curses.color_pair(yellow_text)
                else:
                    cpu_die_bar_attr= curses.color_pair(status_bar_critical) | curses.A_REVERSE
                    cpu_die_temp_attr= curses.color_pair(red_text)

            #avg temp bars. usable width is 23
            if cpu_average_temp != "N/A":
                if cpu_average_temp <75:
                    cpu_avgerage_bar_attr= curses.color_pair(status_bar_ok) | curses.A_REVERSE
                    cpu_average_text_attr= curses.color_pair(green_text)
                elif cpu_average_temp <90:
                    cpu_avgerage_bar_attr= curses.color_pair(status_bar_warning) | curses.A_REVERSE
                    cpu_average_text_attr= curses.color_pair(yellow_text)
                else:
                    cpu_avgerage_bar_attr= curses.color_pair(status_bar_critical) | curses.A_REVERSE
                    cpu_average_text_attr= curses.color_pair(red_text)

        else:
            cpu_die_temp_text= cpu_die_temp
            cpu_die_temp_attr= curses.A_DIM
            cpu_die_bar_length= 0
            cpu_die_bar_attr= curses.A_DIM
            cpu_average_temp_text= f"{"N/A":<6}"
            cpu_average_text_attr= curses.A_DIM
            cpu_avgerage_bar_attr= curses.A_DIM
            cpu_average_bar_length= 0

        cpu_state= ((cpu_die_temp_text, cpu_die_temp_attr), (cpu_average_temp_text, cpu_average_text_attr), (cpu_die_bar_length, cpu_die_bar_attr), (cpu_average_bar_length, cpu_avgerage_bar_attr))

        return pressure_state, cpu_state

def cpu_dashboard_layout(pressure_state, cpu_state):
    lines= []
    (avg10, avg10_attr), (avg60, avg10_attr), (avg300, avg300_attr), (pressure_health_text, pressure_health_attr), (cpu_pressure_bar_length, pressure_bar_attr)= pressure_state
    (cpu_die_temp_text, cpu_die_temp_attr), (cpu_average_temp_text, cpu_average_text_attr), (cpu_die_bar_length, cpu_die_bar_attr), (cpu_average_bar_length, cpu_avgerage_bar_attr)= cpu_state

    #build the content, line by line
    lines.append((avg10, 8, (False, 0, 0), avg10_attr, 6, 2)) #this represents the text, text_max_length, (is_bar, bar_length, bar_max), attribute, y, x
    lines.append((avg60, 8, (False, 0, 0), avg10_attr, 6, 11))
    lines.append((avg300, 8, (False, 0, 0), avg300_attr, 6, 21))
    lines.append((pressure_health_text, 8, (False, 0, 0), pressure_health_attr, 5, 35))
    lines.append((" ", 8, (True, cpu_pressure_bar_length, 22), pressure_bar_attr, 6, 27)) #22 is the max available width for the bar
    lines.append((cpu_die_temp_text, 8, (False, 0, 0), cpu_die_temp_attr, 9, 15))
    lines.append((cpu_average_temp_text, 8, (False, 0, 0), cpu_average_text_attr, 9, 42))
    lines.append((" ", 8, (True, cpu_die_bar_length, 23), cpu_die_bar_attr, 10, 1)) #24 is the max available width for the bar
    lines.append((" ", 8, (True, cpu_average_bar_length, 23), cpu_avgerage_bar_attr, 10, 27)) #23 is the max available width for the bar

    return lines

def memory_dashboard_state(memory_data, memory_pressure_data, status_bar_ok= 1, status_bar_warning= 2, status_bar_critical= 3, green_text=5, yellow_text= 6, red_text= 7):
    some_avg10= memory_pressure_data["some"]["avg10"]
    some_avg60= memory_pressure_data["some"]["avg60"]
    some_avg300= memory_pressure_data["some"]["avg300"]
    full_avg10= memory_pressure_data["full"]["avg10"]
    full_avg60= memory_pressure_data["full"]["avg60"]
    full_avg300= memory_pressure_data["full"]["avg300"]
    total_memory= f"{round(memory_data["MemTotal"]/1048576, 1):>5} GB"
    free_memory= f"{round(memory_data["MemAvailable"]/1048576, 1):>5} GB"
    total_swap= f"{round(memory_data["SwapTotal"]/1048576, 1):>5} GB"
    free_swap= f"{round(memory_data["SwapTotal"]/1048576, 1):>5} GB"

    memory_state= total_memory, free_memory, total_swap, free_swap

    #health score calculation
    penalty= (some_avg10 + some_avg60 * 2.00 + some_avg300 * 3.00 + full_avg10 * 20.00 + full_avg60 * 40.00 + full_avg300 * 60.00)
    health_score= max(0,100- penalty)
    health_bar_width= int(health_score//4.34)
    #attribute for both health score and health score bar
    if health_score > 80:
        health_bar_attr= curses.color_pair(status_bar_ok) | curses.A_REVERSE
        health_score_attr= curses.color_pair(green_text)
    elif health_score > 60:
        health_bar_attr= curses.color_pair(status_bar_warning) | curses.A_REVERSE
        health_score_attr= curses.color_pair(yellow_text)
    else:
        health_bar_attr= curses.color_pair(status_bar_critical) | curses.A_REVERSE
        health_score_attr= curses.color_pair(red_text)

    #calculate what attribute to use for the pressure readings
    #some averages
    if some_avg10 < 5.0:
        some_avg10_attr= curses.color_pair(green_text)
    elif some_avg10 < 10.0:
        some_avg10_attr= curses.color_pair(yellow_text)
    else:
        some_avg10_attr= curses.color_pair(red_text)

    if some_avg60 < 3.0:
        some_avg60_attr= curses.color_pair(green_text)
    elif some_avg60 < 6.0:
        some_avg60_attr= curses.color_pair(yellow_text)
    else:
        some_avg60_attr= curses.color_pair(red_text)

    if some_avg300 < 1.0:
        some_avg300_attr= curses.color_pair(green_text)
    elif some_avg300 < 2.0:
        some_avg300_attr= curses.color_pair(yellow_text)
    else:
        some_avg300_attr= curses.color_pair(red_text)

    #full averages
    if full_avg10 < 0.5:
        full_avg10_attr= curses.color_pair(green_text)
    elif full_avg10 < 1.0:
        full_avg10_attr= curses.color_pair(yellow_text)
    else:
        full_avg10_attr= curses.color_pair(red_text)

    if full_avg60 < 0.5:
        full_avg60_attr= curses.color_pair(green_text)
    elif full_avg60 < 1.0:
        full_avg60_attr= curses.color_pair(yellow_text)
    else:
        full_avg60_attr= curses.color_pair(red_text)

    if full_avg300 < 0.1:
        full_avg300_attr= curses.color_pair(green_text)
    elif full_avg300 < 0.5:
        full_avg300_attr= curses.color_pair(yellow_text)
    else:
        full_avg300_attr= curses.color_pair(red_text)

    some_avg10= f"{some_avg10:>6}"
    some_avg60= f"{some_avg60:>6}"
    some_avg300= f"{some_avg300:>6}"
    full_avg10= f"{full_avg10:>6}"
    full_avg60= f"{full_avg60:>6}"
    full_avg300= f"{full_avg300:>6}"
    health_score= f"{health_score:>6}"

    pressure_state= (some_avg10, some_avg10_attr), (some_avg60, some_avg60_attr), (some_avg300, some_avg300_attr), (full_avg10, full_avg10_attr), (full_avg60, full_avg60_attr), (full_avg300, full_avg300_attr), (health_score, health_score_attr), (health_bar_width, health_bar_attr)

    return memory_state, pressure_state

def memory_dashboard_layout(memory_state, pressure_state):
    lines= []

    total_memory, free_memory, total_swap, free_swap= memory_state
    (some_avg10, some_avg10_attr), (some_avg60, some_avg60_attr), (some_avg300, some_avg300_attr), (full_avg10, full_avg10_attr), (full_avg60, full_avg60_attr), (full_avg300, full_avg300_attr), (health_score, health_score_attr), (health_bar_width, health_bar_attr) = pressure_state

    #build the content, line by line
    lines.append((some_avg10, 8, (False, 0, 0), some_avg10_attr, 2, 19)) #this represents the text, text_max_length, (not a bar, bar length, max bar length), no color(attribute), y=2, x=19
    lines.append((some_avg60, 8, (False, 0, 0), some_avg60_attr, 3, 19))
    lines.append((some_avg300, 8, (False, 0, 0), some_avg300_attr, 4, 19))
    lines.append((full_avg10, 8, (False, 0, 0), full_avg10_attr, 6, 19))
    lines.append((full_avg60, 8, (False, 0, 0), full_avg60_attr, 7, 19))
    lines.append((full_avg300, 8, (False, 0, 0), full_avg300_attr, 8, 19))
    lines.append((total_memory, 8, (False, 0, 0), None, 1, 42))
    lines.append((free_memory, 8, (False, 0, 0), None, 2, 42))
    lines.append((total_swap, 8, (False, 0, 0), None, 3, 42))
    lines.append((free_swap, 8, (False, 0, 0), None, 4, 42))
    lines.append((health_score, 8, (False, 0, 0), health_score_attr, 7, 35))
    lines.append((" ", 8, (True, health_bar_width, 23), health_bar_attr, 8, 27))

    return lines

def network_dashboard_state(network_data):
    #converts from bytes to mb/s
    if network_data != {}:
        total_trans= f"{round((network_data["Total"]["Transmitted bytes"]* 8)/ 1000000, 3)} MB/s"
        total_received= f"{round((network_data["Total"]["Received bytes"]* 8)/ 1000000, 3)} MB/s"
        total_tr_dropped= f"{round((network_data["Total"]["Transmitted drop"]* 8)/ 1000000, 3)} MB/s"
        total_re_dropped= f"{round((network_data["Total"]["Received drop"]* 8)/ 1000000, 3)} MB/s"
        
        total_trans= f"{total_trans:>15}"
        total_received= f"{total_received:>15}"
        total_tr_dropped= f"{total_tr_dropped:>15}"
        total_re_dropped= f"{total_re_dropped:>15}"

        window_limit_counter= 0
        interfaces_list= []
        for interface in network_data:
            if interface != "Total":
                if network_data[interface]["Type"] == "Physical":
                    interface_text= f"{interface:>8}"
                    interfaces_list.append(interface_text)
                    window_limit_counter+= 1
                if window_limit_counter == 3:
                    break

    else:
        total_trans= f"{"N/A":>15}"
        total_received= f"{"N/A":>15}"
        total_tr_dropped= f"{"N/A":>15}"
        total_re_dropped= f"{"N/A":>15}"
        interfaces_list= []

    return total_trans, total_received, total_tr_dropped, total_re_dropped, interfaces_list

def network_dashboard_layout(total_trans, total_received, total_tr_dropped, total_re_dropped, interfaces_list):
    lines= []

    #build the content, line by line
    lines.append((total_trans, 49, (False, 0, 0), None, 1, 11)) #this represents the text, text_max_length, (not a bar, bar length, max bar length), no color(attribute), y=1, x=11
    lines.append((total_received, 49, (False, 0, 0), None, 2, 11))
    lines.append((total_tr_dropped, 49, (False, 0, 0), None, 3, 11))
    lines.append((total_re_dropped, 49, (False, 0, 0), None, 4, 11))

    for i, interface in enumerate(interfaces_list):
        lines.append((interface, 15, (False, 0, 0), None, 2 + i, 31))

    return lines

def gpu_dashboard_state(gpu_data, gpu_check_disable, status_bar_ok= 1, status_bar_warning= 2, status_bar_critical= 3):
    if gpu_check_disable is False:
        gpu_clock= f"{gpu_data[0]["GPU Clock Speed"]:>6} MHz"
        gpu_mem= f"{gpu_data[0]["GPU Mem Clock"]:>6} Mhz"
        gpu_load=  f"{gpu_data[0]["GPU Load"]:>6}"
        gpu_fan= f"{gpu_data[0]["Fan Speed"]:>6}"
        gpu_mem_load= f"{gpu_data[0]["Memory Load"]:>6}"
        gpu_temp= f"{gpu_data[0]["Temperature"]:>6} °C"
        #gpu temp attr
        gpu_temp_attr= curses.color_pair(status_bar_ok) | curses.A_REVERSE #this is also re-used for the gpu_load_bar color
        #temp bar attr
        if gpu_data[0]["Temperature"] < 75:
            temp_bar_attr= curses.color_pair(status_bar_ok) | curses.A_REVERSE
        
        elif gpu_data[0]["Temperature"] <87:
            temp_bar_attr= curses.color_pair(status_bar_warning) | curses.A_REVERSE

        else:
            temp_bar_attr= curses.color_pair(status_bar_critical) | curses.A_REVERSE

            #available width is 49
        max_bar_width_l= min(49, (gpu_data[0]["GPU Load"]//2)) #gpu_load_bar length. guards agains random errors
        max_bar_width_t= min(49, (gpu_data[0]["Temperature"]//2)) #gpu_temp_bar length. guards agains random errors
    
    else:
        max_bar_width_l= 0
        max_bar_width_t= 0
        gpu_clock= " N/A"
        gpu_mem= " N/A"
        gpu_fan= " N/A"
        gpu_mem_load= " N/A"
        gpu_load= " N/A"
        gpu_temp= " N/A"
        temp_bar_attr= curses.A_DIM
        gpu_temp_attr= curses.A_DIM

    return (gpu_clock, gpu_mem, gpu_fan, gpu_mem_load, (gpu_load, gpu_temp_attr), (gpu_temp, temp_bar_attr), (max_bar_width_l, max_bar_width_t))

def gpu_dashboard_layout(state):
    lines= []
    gpu_load, gpu_temp_attr= state[4]
    gpu_temp, temp_bar_attr= state[5]
    bar_width_l, bar_width_t= state[6]

    lines.append((state[0], 49, (False, 0, 0), None, 2, 14)) #this represents the gpu_clock (text), (not a bar, bar length, max bar length), no color(attribute), y=2, x=14
    lines.append((state[1], 49, (False, 0, 0), None, 3, 14))
    lines.append((state[2], 49, (False, 0, 0), None, 4, 14))
    lines.append((state[3], 49, (False, 0, 0), None, 5, 14))
    lines.append((gpu_load, 49, (False, 0, 0), None, 6, 14))
    lines.append((" ", 49, (True, bar_width_l, 49), gpu_temp_attr, 7, 1))
    lines.append((gpu_temp, 49, (False, 0, 0), None, 8, 14))
    lines.append((" ", 49, (True, bar_width_t, 49), temp_bar_attr, 9, 1))

    return lines

def cpu_load_state(cpu_load_data, cpu_load_window_ratio, cpu_window_lines, cpu_window_columns, status_bar_ok= 1, status_bar_warning= 2, status_bar_critical= 3):
    string_with_color_attr= curses.color_pair(status_bar_ok) | curses.A_REVERSE
    string_without_color_attr= None
    cpu_index_lines= 4
    cpu_index_columns= 1
    per_core_bar_ratio= 100//cpu_load_window_ratio # calculates the ratio when at 100% LOAD -> this is the maxiumu possible load
    cpu_load_state= []
    max_cpu_load_bar= cpu_load_window_ratio - 2

    if cpu_load_data != {}:
        #total load status bar
        total_bar_max= min(cpu_window_columns - 2, 100)
        total_bar_ratio= 100/total_bar_max #calculates lenght for the bar, when at 100%
        total_bar_length= int(cpu_load_data["CPU"]//total_bar_ratio)

        #build the string and match the color of the letter with the bar color. The text is inside the bar.
        total_bar_text = f"Total Load: {cpu_load_data['CPU']} %"
        total_bar_text = total_bar_text[:total_bar_max].ljust(total_bar_max)
        filled_in= min(total_bar_max, total_bar_length)
        #split it into 2 strings and add the color attributes
        colored_string= total_bar_text[:filled_in] #1st string - filled in with color
        ncolored_string= total_bar_text[filled_in:] #2nd string - not filled in with color

        for cpu in cpu_load_data:
            if cpu == "CPU":
                continue

            if cpu_index_lines > cpu_window_lines - 1:
                cpu_index_lines= 4
                cpu_index_columns+= cpu_load_window_ratio

            if cpu_index_columns >= (cpu_window_columns - max_cpu_load_bar): 
                break
                    #status bar showing current per core load
            bar_length= min(max_cpu_load_bar, int(cpu_load_data[cpu]//per_core_bar_ratio)) #guards against random errors
            text_to_add= f"{cpu}: {cpu_load_data[cpu]:>5}{" %":<{bar_length}}"
            text_to_add= text_to_add[:max_cpu_load_bar].ljust(max_cpu_load_bar)
            colored_string_indv= text_to_add[:bar_length] #1st string - filled in with color
            ncolored_string_indv= text_to_add[bar_length:max_cpu_load_bar] #2nd string - not filled in with color
            cpu_load_state.append((colored_string_indv, string_with_color_attr, ncolored_string_indv, string_without_color_attr, cpu_index_lines, cpu_index_columns, bar_length, max_cpu_load_bar))
            cpu_index_lines += 3

    else:
        colored_string= " "
        ncolored_string= f"Total Load: N/A"
        bar_length= 0
        filled_in= 0
        total_bar_max= 0

    cpu_load_state_total= (colored_string, string_with_color_attr, ncolored_string, string_without_color_attr, filled_in, total_bar_max)

    return cpu_load_state_total, cpu_load_state

def cpu_load_layout(cpu_load_state_total, cpu_load_state):
    lines= []

    #build the content, line by line
    lines.append((cpu_load_state_total[0], cpu_load_state_total[5], (False, 0, 0), cpu_load_state_total[1], 1, 1)) #Represents colored part of the total bar with text
    lines.append((cpu_load_state_total[2], cpu_load_state_total[5], (False, 0, 0), cpu_load_state_total[3], 1, 1 + cpu_load_state_total[4]))
    for i in cpu_load_state:
        lines.append((i[0], i[7], (False, 0, 0), i[1], i[4], i[5])) #Represents colored part of the individual cpu load bar with text. The tuplet == text, text_max_length (is_bar, bar_length, bar_max), attribute, y, x
        lines.append((i[2], i[7], (False, 0, 0), i[3], i[4], i[5] + i[6])) #Represents the part of the bar with text that is not colored
    return lines

def processes_dashboard_state(process_cpu_load_data, process_stat_data, process_status_data, process_text_lengths, process_window_columns, ticks_per_second):
    process_window_content= []
    max_text_width= 0
    max_pid_width= 3
    if process_cpu_load_data != {}:
            max_pid_width= process_text_lengths[0]
            max_text_width= max(0, (process_window_columns- max_pid_width - 1))
            sorted_processes= sorted(process_cpu_load_data.items(), key= lambda item:item[1], reverse= True)

            for i, tuplet in enumerate(sorted_processes):
                PID, cpu_load = tuplet
                #create the strings 
                pid_string= f"{PID:<{max_pid_width}}"
                if PID in process_status_data:
                    ppid_string= f"{process_status_data[PID].PPid:<{max_pid_width}}"
                else:
                    ppid_string= f"{"N/A":<{max_pid_width}}"

                user_string= f"{" ":<{process_text_lengths[1]}}"[:process_text_lengths[1]] #to implement user string later
                priority_string= f" {process_stat_data[PID].priority:<{process_text_lengths[2]}}"[:process_text_lengths[2]]
                state_string= f" {process_stat_data[PID].state:<{process_text_lengths[3]}}"[:process_text_lengths[3]]

                process_uptime_seconds= (process_stat_data[PID].process_time/ticks_per_second) #coverts the process time to seconds
                if process_uptime_seconds >60:
                    process_uptime_values= f"{round(process_uptime_seconds/60,1)} M" #converts the time to minute and makes it a string
                else:
                    process_uptime_values= f"{process_uptime_seconds} S" #makes it into a string and keeps it as seconds

                process_uptime_string= f" {process_uptime_values:<{process_text_lengths[4]}}"[:process_text_lengths[4]]
                threads_string= f" {process_stat_data[PID].num_threads:<{process_text_lengths[5]}}"[:process_text_lengths[5]]
                cpu_string= f"{cpu_load:>{process_text_lengths[6]}}"[:process_text_lengths[6]]
                vMem_value= f"{process_stat_data[PID].vsize}"[:process_text_lengths[7] - 4] #leaves an extra space from the previous column
                vMem_value= f"{vMem_value} GB"
                vMem_string= f"{vMem_value:>{process_text_lengths[7]}}"[:process_text_lengths[7]]
                pMem_string= f"{process_stat_data[PID].rss:>{process_text_lengths[8]}}"[:process_text_lengths[8]] 
                name_string= f" {process_stat_data[PID].name:<{max_text_width}}" 
                #create the process line string
                final_string= f"{ppid_string}{user_string}{priority_string}{state_string}{process_uptime_string}{threads_string}{cpu_string}{vMem_string}{pMem_string}{name_string}"

                process_window_content.append((pid_string, final_string))
            
    return process_window_content, max_text_width, max_pid_width

def process_dashboard_content_scrollable_layout (content,  max_pid_width, max_text_width):
    white_green= 8
    PID_string_attr= curses.color_pair(white_green) | curses.A_BOLD
    process_string_attr= None
    #first line is reserved for the static interface
    padded_content_list= []

    for i, (pid_string, string) in enumerate(content): 
        padded_content_list.append((pid_string, max_pid_width, (False, 0, 0), PID_string_attr, 0 + i, 0)) #The tuplet == text, text_max_length (is_bar, bar_length, bar_max), attribute, y, x
        padded_content_list.append((string, max_text_width, (False, 0, 0), process_string_attr, 0 + i, max_pid_width + 1))

    return padded_content_list

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
        cpu_load_window= None
        cpu_load_window_h= 0

    #processes window layout
    if columns >105 and lines > max(12, cpu_load_window_h+2):
        process_h, process_w= (lines - cpu_load_window_h), (columns - cpu_w)
        process_window= curses.newwin(process_h, process_w, cpu_load_window_h + 1, cpu_w+1)
        process_window_positions= (process_h, process_w, cpu_load_window_h + 1, cpu_w + 1)
    else:
        process_window= None
        process_window_positions= (0,0,0,0)

    cpu_window = curses.newwin(cpu_h, cpu_w, start_y, start_x)
    memory_window = curses.newwin(mem_h, mem_w, start_y + cpu_h, start_x)
    network_window = curses.newwin(net_h, net_w, start_y + cpu_h + mem_h, start_x)
    gpu_window = curses.newwin(gpu_h, gpu_w, start_y + cpu_h + mem_h + net_h, start_x)

    #setting background color for windows and clear the window (curses needs to repaint)
    normal_text= 4
    stdscr.bkgd(" ", curses.color_pair(normal_text))
    stdscr.clear()
    cpu_window.bkgd(" ", curses.color_pair(normal_text))
    cpu_window.clear()
    memory_window.bkgd(" ", curses.color_pair(normal_text))
    memory_window.clear()
    network_window.bkgd(" ", curses.color_pair(normal_text))
    gpu_window.bkgd(" ", curses.color_pair(normal_text))
    if cpu_load_window is not None:
        cpu_load_window.bkgd(" ", curses.color_pair(normal_text))
        cpu_load_window.clear()
    if process_window is not None:
        process_window.bkgd(" ", curses.color_pair(normal_text))
        process_window.clear()
        
    return cpu_window, memory_window, network_window, gpu_window, cpu_load_window, process_window, process_window_positions

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

    cpu_sensor, cpu_sensor_path= probe_cpu_sensors(cpu_check_disable) #check for available temp sensor and cache the path
    cpu_name= get_cpu_name(cpu_check_disable) #check for the CPU name and cache it
    gpu_name, gpu_handles= nvidia_gpu_name(gpu_check_disable) #check for the GPU name and cache it

    if cpu_sensor_path == "N/A":
        cpu_check_disable= True

    #for status bars colors
    status_bar_ok= 1
    status_bar_warning= 2
    status_bar_critical= 3
    #for text colors
    normal_text= 4
    green_text= 5
    yellow_text= 6
    red_text= 7
    white_green= 8 #foreground - background
    
    stdscr.clear()
    curses.curs_set(0) #set cursor to invisible
    stdscr.keypad(True)
    stdscr.nodelay(True)

    #initialize colors, assign color pairs
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
    static_ui= StaticInterface() #used to write the static interface
    initial_read= True #generates the interface only on launch
    interface_refresh= time.monotonic() 
    next_temp_net_read= 0 #to decouple cpu temperature reads from interface
    next_load_read= 0 #to decouple cpu load reads from interface
    next_pressure_mem_read= 0 #to decouple memory reads from interface
    next_gpu_read= 0 #to decouple gpu reads from interface
    #for process reads
    data_length= 1000 #max number of processes read - will make this changeable by the user in the interface
    next_process_scan= 0 #to decouple process reads from interface
    status_index= 0
    process_text_lengths= (0,0,0,0,0,0,0,0,0)
    process_stat_data= None
    prev_time= None
    ticks_per_second= None
    cpu_temp_path= None #for cpu temp reads
    cpu_load_raw_data= None #for cpu load reads
    network_raw_data= None #for network traffic reads
    time_netw= None #for network traffic reads

    while True:
        data_collection= time.monotonic()
        key_press= stdscr.getch()

        #redraws content windows on resize
        if key_press == curses.KEY_RESIZE:
            invalidate_windows(stdscr, cpu_window, memory_window, network_window, gpu_window,cpu_load_window, process_window)
            cpu_window, memory_window, network_window, gpu_window, cpu_load_window, process_window, process_window_positions= generate_windows(stdscr)
            gpu_dashboard= GpuDashboard(gpu_window)
            cpu_dashboard= CpuDashboard(cpu_window)
            memory_dashboard= MemoryDashboard(memory_window)
            network_dashboard= NetworkDashboard(network_window)
            process_dashboard= ProcessDashboard(process_window_positions[0], process_window_positions[1], process_window_positions[2] + 1, process_window_positions[3])

            #write the static interface
            static_ui.global_win(stdscr)
            static_ui.cpu(cpu_window, cpu_sensor, cpu_name, cpu_temp_data, cpu_load_raw_data)
            static_ui.memory(memory_window)
            static_ui.network(network_window)
            static_ui.gpu(gpu_window, gpu_name)
            #writes the static interface for cpu_load and calculates how to fit all cpus loads in the cpu load window 
            if cpu_load_window is not None:
                cpu_window_lines, cpu_window_columns = cpu_load_window.getmaxyx()
                displayed_lines= (cpu_window_lines-4)//3
                columns_needed= max(1, int(((len(cpu_load_raw_data)-1) + displayed_lines)/displayed_lines))
                cpu_load_window_ratio= (cpu_window_columns-2)//columns_needed
                cpu_load_dashboard= CpuLoadDashboard(cpu_load_window)
                static_ui.cpu_load(cpu_load_window, cpu_load_raw_data, cpu_load_window_ratio)
            else:
                cpu_load_window_ratio= 1
            
            if process_window is not None:
                process_text_lengths= static_ui.processes(process_window, process_stat_data, process_window_positions[1])

        #collect readings - decoupled them from the interface refresh
        if data_collection > next_temp_net_read:
            cpu_temp_data, cpu_temp_path= cpu_readings(cpu_check_disable, cpu_sensor_path, cpu_temp_path)
            next_temp_net_read= data_collection + 1.5

        if data_collection > next_load_read:
            cpu_load_raw_data, cpu_load_calc_data= get_cpu_load(cpu_check_disable, file_path, cpu_load_raw_data)
            network_raw_data, network_data, time_netw= network_traffic(file_path, network_raw_data, time_netw)
            next_load_read= data_collection + 1

        if data_collection > next_pressure_mem_read:
            cpu_pressure_data, memory_pressure_data= system_pressure(cpu_check_disable, memory_check_disable, file_path)
            memory_data= memory_readings(memory_check_disable, file_path)
            next_pressure_mem_read= data_collection + 1.5

        if data_collection > next_gpu_read:
            gpu_data, gpu_fan_disabled, gpu_mem_disabled= nvidia_gpu_readings(gpu_check_disable, gpu_handles, gpu_fan_disabled, gpu_mem_disabled)
            next_gpu_read= data_collection + 1

        process_content_refresh= False #decouples content list building from TUI refresh
        if data_collection > next_process_scan:
            process_stat_data, process_status_data, process_cpu_load_data, status_index, prev_time, ticks_per_second= current_processes(process_stat_data, data_length, status_index, prev_time, ticks_per_second)
            next_process_scan= data_collection + 2
            process_content_refresh= True

        #initialize the interface on start-up
        if initial_read is True:
            cpu_window, memory_window, network_window, gpu_window, cpu_load_window, process_window, process_window_positions= generate_windows(stdscr)
            gpu_dashboard= GpuDashboard(gpu_window)
            cpu_dashboard= CpuDashboard(cpu_window)
            memory_dashboard= MemoryDashboard(memory_window)
            network_dashboard= NetworkDashboard(network_window)
            process_dashboard= ProcessDashboard(process_window_positions[0], process_window_positions[1], process_window_positions[2] + 1, process_window_positions[3])
            initial_read= False

            #write the static interface
            static_ui.global_win(stdscr)
            static_ui.cpu(cpu_window, cpu_sensor, cpu_name, cpu_temp_data, cpu_load_raw_data)
            static_ui.memory(memory_window)
            static_ui.network(network_window)
            static_ui.gpu(gpu_window, gpu_name)
            ##writes the static interface for cpu_load and calculates how to fit all cpus loads in the cpu load window 
            if cpu_load_window is not None:
                    cpu_window_lines, cpu_window_columns = cpu_load_window.getmaxyx()
                    displayed_lines= (cpu_window_lines-4)//3
                    columns_needed= max(1, int(((len(cpu_load_raw_data)-1) + displayed_lines)/displayed_lines))
                    cpu_load_window_ratio= (cpu_window_columns-2)//columns_needed
                    cpu_load_dashboard= CpuLoadDashboard(cpu_load_window)
                    static_ui.cpu_load(cpu_load_window, cpu_load_raw_data, cpu_load_window_ratio)
            else:
                cpu_load_window_ratio= 1

            if process_window is not None:
                process_text_lengths= static_ui.processes(process_window, process_stat_data, process_window_positions[1])
               
        #CPU Dashboard dinamic content
        cpu_dashboard.update(cpu_temp_data, cpu_pressure_data, cpu_sensor_path)
        cpu_dashboard.render()

        #Memory Dashboard dinamic content
        memory_dashboard.update(memory_data, memory_pressure_data)
        memory_dashboard.render()

        #Network Dashboard dinamic content
        network_dashboard.update(network_data)
        network_dashboard.render()

        #CPU Load Dashboard dinamic content
        if cpu_load_window is not None:
            cpu_load_dashboard.update(cpu_load_calc_data, cpu_load_window_ratio, cpu_window_lines, cpu_window_columns)
            cpu_load_dashboard.render()

        #Processes Dashboard dinamic content

        if process_content_refresh is True:
            processes_state, max_text_width, max_pid_width= processes_dashboard_state(process_cpu_load_data, process_stat_data, process_status_data, process_text_lengths, process_window_positions[1], ticks_per_second)
            process_window_content= process_dashboard_content_scrollable_layout (processes_state,  max_pid_width, max_text_width)
            if process_window is not None:
                process_dashboard.rebuild_pad(process_window_content)

        if process_window is not None:
            process_dashboard.scroll_input(key_press)
            process_dashboard.render()

        #GPU Dashboard dinamic content
        gpu_dashboard.update(gpu_data, gpu_check_disable)
        gpu_dashboard.render()

        curses.doupdate()

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

        #enforicng updates at monotonic intervals
        interface_refresh += 0.1
        sleep_time = interface_refresh - time.monotonic()
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == "__main__":
    curses.wrapper(main)
