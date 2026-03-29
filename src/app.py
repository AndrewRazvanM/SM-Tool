from core import scheduler, file_handling, layout_manager
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
        "mem_dashboard",
        "cpu_dashboard",
        "cpu_load_dashboard",
        "network_dashboard",
        "nvidia_dashboard",
        "process_dashboard",
        "scroll_pos",
        "layout_controller",
        "dashboard_dict"
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
        self.mem_dashboard = memory.MemoryDashboard(stdscr, self.files_path)

        #cpu dashboard
        self.cpu_dashboard= cpu.CPUDashboard(stdscr, self.files_path)

        #cpu load dashboard
        self.cpu_load_dashboard= cpu.CPULoadDashboard(stdscr, self.files_path)

        #for network dashboard
        self.network_dashboard= network.NetworkDashboard(stdscr, self.files_path)

        #for nvidia dashboard
        self.nvidia_dashboard= nvidia.NvidiaDashboard(stdscr)

        #for process window
        self.scroll_pos= 0
        self.process_dashboard= processes.ProcessDashboard(stdscr, self.files_path)

        #initialize the layout manager
        self.dashboard_dict= {
            "cpu": self.cpu_dashboard,
            "cpu_load": self.cpu_load_dashboard,
            "mem": self.mem_dashboard,
            "net": self.network_dashboard,
            "nvidia": self.nvidia_dashboard,
            "process": self.process_dashboard,
        }
        self.layout_controller = layout_manager.LayoutController(stdscr)

    def handle_input(self, stdscr):

        while True:
            key= stdscr.getch()

            if key == curses.KEY_UP:
                self.scroll_pos -= 1
                self.scroll_pos= max(0, self.scroll_pos)
                    
            if key == curses.KEY_DOWN:
                self.scroll_pos += 1
            
            if key == curses.KEY_RESIZE:
                stdscr= self.stdscr
                stdscr.clear()
                self.layout_controller.calculate_layout(self.dashboard_dict)
                self.layout_controller.on_resize(stdscr, self.dashboard_dict)
            
            if key == ord("q"):
                self.running= False
                self.files_path.close_all()
                self.cpu_dashboard.cpu_temp_readings.close_temp_files()
                self.nvidia_dashboard.nvidia_service.close_nvidia_drivers()

            if key == -1:
                break  # no key

    def run(self):
        #create local references
        stdscr= self.stdscr
        scheduler= self.scheduler
        layout_controller= self.layout_controller
        dashboard_dict= self.dashboard_dict

        #mem
        mem_dashboard= self.mem_dashboard

        #cpu
        cpu_dashboard= self.cpu_dashboard
        cpu_load_dashboard= self.cpu_load_dashboard

        #network
        network_dashboard= self.network_dashboard

        #nvidia
        nvidia_dashboard= self.nvidia_dashboard

        #processes
        process_dashboard= self.process_dashboard

        #create variable
        memory_check_disable= False #need to implement in the MemInfo readings too. Needs to implement toggle for the user
        disable_cpu_check= False

        #assing the styles
        mem_dashboard.assign_style()
        cpu_dashboard.assign_style()
        cpu_load_dashboard.assign_style()
        network_dashboard.assign_style()
        nvidia_dashboard.assign_style()
        process_dashboard.assign_style()

        layout_controller.calculate_layout(dashboard_dict)
        layout_controller.apply_layout(dashboard_dict)

        while self.running:

            self.handle_input(stdscr)

            schedule = scheduler.should_run()

            #get system readings and format them
            cpu_dashboard.update_data_pipeline(schedule)
            cpu_load_dashboard.update_data_pipeline(schedule)
            mem_dashboard.update_data_pipeline(schedule)
            network_dashboard.update_data_pipeline(schedule)
            nvidia_dashboard.update_data_pipeline(schedule)
            process_dashboard.update_data_pipeline(schedule)

            #handles scrolling through the process list
            self.scroll_pos= process_dashboard.visible_content(self.scroll_pos)

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

