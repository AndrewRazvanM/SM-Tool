from core import scheduler, file_handling, sorter
from readings import memory as reading_mem, system_pressure, cpu as reading_cpu, network as reading_net, processes as reading_proc, nvidia as reading_nvidia
from ui import formatters, contentdiff
from ui.dashboards import memory, cpu, network, nvidia, processes
import curses
from time import sleep

class Application:

    __slots__=(
        "stdscr",
        "running",
        "files_path",
        "scheduler",
        "input_handler",
        "diff_engine",
        "mem_formatter",
        "mem_dashboard",
        "mem_service",
        "pressure_service",
        "pressure_formatter",
        "cpu_formatter",
        "cpu_dashboard",
        "cpu_service",
        "cpu_load_dashboard",
        "network_dashboard",
        "network_formatter",
        "network_service",
        "nvidia_dashboard",
        "nvidia_services",
        "nvidia_formatter",
        "process_dashboard",
        "process_services",
        "process_formatter",
        "scroll_pos",
        "sort"
    )

    def __init__ (self, stdscr):
        curses.curs_set(0)
        
        #initialize colors
        curses.start_color()
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_GREEN)
        #set bkgd
        stdscr.bkgd(" ", curses.color_pair(4))
        stdscr.clear()

        #assing the stdscr
        self.stdscr = stdscr
        self.stdscr.nodelay(True) #non blocking input
        self.stdscr.keypad(True) #accept arrows key etc.

        self.running = True
        self.files_path= file_handling.NeededFiles()
        self.scheduler = scheduler.Scheduler()

        #For memory dashboard
        self.mem_service = reading_mem.MemoryInfo(self.files_path)
        self.mem_formatter = formatters.MemoryFormatter()
        self.mem_dashboard = memory.MemoryDashboard(stdscr, contentdiff.ContentDiff)

        #For system pressure
        self.pressure_service= system_pressure.SystemPressure(self.files_path)
        self.pressure_formatter= formatters.PressureFormatter()

        #for both cpu & cpu load dashboards
        self.cpu_formatter= formatters.CPUFormatter() 
        self.cpu_service= reading_cpu.CPUInfo(self.files_path)

        #cpu dashboard
        self.cpu_dashboard= cpu.CPUDashboard(stdscr, contentdiff.ContentDiff, self.cpu_service.cpu_name, self.cpu_service.sensor_name)

        #cpu load dashboard
        self.cpu_load_dashboard= cpu.CPULoadDashboard(stdscr, self.cpu_formatter, len(self.cpu_service.cpu_load_raw_data))
        processes_start_y= self.cpu_dashboard.last_line_y + self.cpu_load_dashboard.last_line_y

        #for network dashboard
        self.network_service= reading_net.NetworkTraffic(self.files_path)
        self.network_formatter= formatters.NetworkFormatter()
        self.network_dashboard= network.NetworkDashboard(stdscr, contentdiff.ContentDiff)

        #for nvidia dashboard
        self.nvidia_services= reading_nvidia.Nvidia()
        self.nvidia_formatter= formatters.NvidiaFormatter()
        self.nvidia_dashboard= nvidia.NvidiaDashboard(stdscr, contentdiff.ContentDiff, self.nvidia_services.gpu_name_list)

        #for process window
        self.scroll_pos= 0
        self.process_services= reading_proc.ProcessMonitor(self.files_path)
        self.process_formatter= formatters.ProcessFormatter()
        self.process_dashboard= processes.ProcessDashboard(stdscr, processes_start_y)

        #sorter
        self.sort= sorter.sorter

    def handle_input(self, stdscr):

        while True:
            key= stdscr.getch()

            if key == curses.KEY_UP:
                self.scroll_pos += 1
                    
            if key == curses.KEY_DOWN:
                self.scroll_pos -= 1
            
            if key == curses.KEY_RESIZE:
                stdscr= self.stdscr
                stdscr.clear()
                self.mem_dashboard.resize(stdscr)
                self.cpu_dashboard.resize(stdscr)
    
                self.cpu_load_dashboard.resize(stdscr)
                processes_start_y= self.cpu_dashboard.last_line_y + self.cpu_load_dashboard.last_line_y

                self.network_dashboard.resize(stdscr)
                self.nvidia_dashboard.resize(stdscr)

                self.process_dashboard.resize(stdscr, processes_start_y)
            
            if key == ord("q"):
                self.running= False
                self.files_path.close_all()
                self.cpu_service.close_temp_files()
                self.nvidia_services.close_nvidia_drivers()

            if key == -1:
                break  # no key

    def run(self):
        #create local references
        stdscr= self.stdscr
        scheduler= self.scheduler
        sort= self.sort
        #mem
        mem_service= self.mem_service
        mem_formatter= self.mem_formatter
        mem_dashboard= self.mem_dashboard

        #pressure
        pressure_service= self.pressure_service
        pressure_formatter= self.pressure_formatter

        #cpu
        cpu_dashboard= self.cpu_dashboard
        cpu_load_dashboard= self.cpu_load_dashboard
        cpu_service= self.cpu_service
        cpu_formatter= self.cpu_formatter

        #network
        network_dashboard= self.network_dashboard
        network_service= self.network_service
        network_formatter= self.network_formatter

        #nvidia
        nvidia_services= self.nvidia_services
        nvidia_formatter= self.nvidia_formatter
        nvidia_dashboard= self.nvidia_dashboard

        #processes
        process_services= self.process_services
        process_formatter= self.process_formatter
        process_dashboard= self.process_dashboard

        #create variable
        memory_check_disable= False #need to implement in the MemInfo readings too. Needs to implement toggle for the user
        disable_cpu_check= False

        #assing the styles
        mem_dashboard.assing_styles()
        cpu_dashboard.assing_style()
        cpu_load_dashboard.assing_style()
        network_dashboard.assing_style()
        nvidia_dashboard.assing_style()
        process_dashboard.assing_style()

        #generate static interfaces
        mem_dashboard.draw_static_interface()
        cpu_dashboard.draw_static_interface()
        cpu_load_dashboard.draw_static_interface()
        network_dashboard.draw_static_interface()
        nvidia_dashboard.draw_static_interface()
        process_dashboard.draw_static_interface()

        while self.running:

            self.handle_input(stdscr)

            schedule = scheduler.should_run()

            #get system readings
            mem_service.update(schedule)
            memory_check_disable= pressure_service.read_mem(memory_check_disable, schedule)
            pressure_service.read_cpu(disable_cpu_check, schedule)
            cpu_service.get_cpu_temp(disable_cpu_check, schedule)
            cpu_service.get_cpu_load(disable_cpu_check, schedule)
            network_service.update(schedule)
            process_services.update(schedule)
            nvidia_services.get_nvidia_gpu_readings(schedule)

            #format system readings
            mem_formatter.format(mem_service, schedule)
            pressure_formatter.format_mem(pressure_service, schedule)
            pressure_formatter.format_cpu(pressure_service, schedule)
            cpu_formatter.format_info(cpu_service, schedule)
            cpu_formatter.format_load(cpu_service, cpu_load_dashboard.max_bar_width, schedule)
            network_formatter.format(network_service, schedule)
            nvidia_formatter.format(nvidia_services, schedule)
            process_formatter.format(process_services, schedule)

            #sort formatted lists for the process window
            sort(process_formatter.formatted_processes_output, schedule)

            #check if content is different. excludes the CPU Load Dashboard and Processes Dashboard
            mem_dashboard.check_content_diff(mem_formatter.memory_info_formatted_output, pressure_formatter.memory_formatted_output)
            cpu_dashboard.check_content_diff(cpu_formatter.formatted_cpu_readings, pressure_formatter.cpu_formatted_output)
            network_dashboard.check_content_diff(network_formatter.formatted_network_output)
            nvidia_dashboard.check_content_diff(nvidia_formatter.formatted_nvidia_output)

            #handles scrolling through the list
            process_dashboard.visible_content(self.scroll_pos, process_formatter.formatted_processes_output)

            #render differences
            mem_dashboard.render()
            cpu_dashboard.render()
            cpu_load_dashboard.render()
            network_dashboard.render()
            nvidia_dashboard.render()
            process_dashboard.render()

            curses.doupdate()
            #refresh rate of 10 hz
            sleep(0.1)

