from core import scheduler, file_handling, layout_controller
from ui.dashboards import memory, cpu, network, nvidia, processes, io
from ui.button import Button, EnableDashButton
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
        "io_tot_dashboard",
        "scroll_pos",
        "layout_controller",
        "dashboard_dict",
        "dash_buttons",
        "global_buttons"
    )

    def __init__ (self, stdscr):
        #cursor is invisible
        curses.curs_set(0)
        #capture mouse clicks 
        curses.mousemask(curses.BUTTON1_CLICKED | curses.BUTTON4_PRESSED | curses.BUTTON5_PRESSED)

        #initialize colors
        curses.start_color()
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)
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

        #for IO totals dashboard
        self.io_tot_dashboard = io.IOTotals(stdscr, self.files_path)

        #initialize the layout manager
        self.layout_controller = layout_controller.LayoutController(stdscr)
        self.dashboard_dict= {
            "cpu": self.cpu_dashboard,
            "cpu_load": self.cpu_load_dashboard,
            "mem": self.mem_dashboard,
            "net": self.network_dashboard,
            "nvidia": self.nvidia_dashboard,
            "process": self.process_dashboard,
            "io_tot": self.io_tot_dashboard,
        }

         #initialize the buttons
        from core.style_maps import button_map
        button_style_map = button_map
        self.global_buttons = {
            "settings": Button("| Settings |", button_style_map),
            "dash_toggle": EnableDashButton("Dashboards", button_style_map)
        }
        self.dash_buttons = {
            "cpu": Button("| Disable |", button_style_map),
            "mem": Button("| Disable |", button_style_map),
            "net": Button("| Disable |", button_style_map),
            "nvidia": Button("| Disable |", button_style_map),
            "process": Button("| Disable |", button_style_map),
            "cpu_load": Button("| Disable |", button_style_map),
            "io_tot": Button("| Disable |", button_style_map),
        }
    @staticmethod
    def clear_region_clrtoeol(win: curses.window, y: int, x: int, height: int):
        for row in range(height):
            win.move(y + row, x)
            win.clrtoeol()

    def handle_input(self, stdscr: curses.window):

        while True:
            key= stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                self.layout_controller.on_resize(stdscr, self.dashboard_dict, self.dash_buttons, self.global_buttons)
                return
            
            if key == ord("q"):
                self.running= False
                self.files_path.close_all()
                self.cpu_dashboard.cpu_temp_readings.close_temp_files()
                self.nvidia_dashboard.nvidia_service.close_nvidia_drivers()
                return

            if key == curses.KEY_UP:
                self.scroll_pos = max(0, self.scroll_pos - 1)

            elif key == curses.KEY_DOWN:
                self.scroll_pos += 1

            elif key == curses.KEY_MOUSE:
                dash_buttons = self.dash_buttons
                layout_controller = self.layout_controller
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                except curses.error:
                    return

                if bstate & curses.BUTTON4_PRESSED:
                    self.scroll_pos = max(0, self.scroll_pos - 1)

                elif bstate & curses.BUTTON5_PRESSED:
                    self.scroll_pos += 1

                for btn in dash_buttons:
                    if dash_buttons[btn].is_clicked(my, mx):
                        layout_controller.usr_dash_disabled[btn] = True

                        #clear only affected dashboards
                        if btn in layout_controller.static_layout:
                            clr_y = layout_controller.static_layout[btn].start_y
                            clr_x = layout_controller.static_layout[btn].start_x
                            clr_height = layout_controller.static_layout[btn].max_y
                            self.clear_region_clrtoeol(stdscr, clr_y, clr_x, clr_height)
                        else:
                            clr_y = layout_controller.dynamic_layout[btn].start_y
                            clr_x = layout_controller.dynamic_layout[btn].start_x
                            #for dynamic dashboards, starting from the dashboard y pos, everything needs to be cleared. Doing just the dashboard height, might caused visual artifacts
                            clr_height = layout_controller.window_max_lines - layout_controller.dynamic_layout[btn].start_y
                            self.clear_region_clrtoeol(stdscr, clr_y, clr_x, clr_height)

                        layout_controller.on_resize(stdscr, self.dashboard_dict, self.dash_buttons, self.global_buttons)
                        return
                    
                if self.global_buttons["dash_toggle"].is_clicked(my, mx):
                    stdscr.clear()
                    for dash in layout_controller.usr_dash_disabled:
                        layout_controller.usr_dash_disabled[dash] = False

                    layout_controller.calculate_layout(self.dashboard_dict, self.dash_buttons, self.global_buttons)
                    layout_controller.on_resize(stdscr, self.dashboard_dict, self.dash_buttons, self.global_buttons)
                    return

            if key == -1:
                break  # no key

    def run(self):
        
        #create local references
        stdscr = self.stdscr
        scheduler = self.scheduler
        layout_controller = self.layout_controller
        dashboard_dict = self.dashboard_dict
        dash_buttons = self. dash_buttons
        global_buttons = self.global_buttons

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

        #io_tot
        io_tot_dashboard = self.io_tot_dashboard

        #assing the styles
        mem_dashboard.assign_style()
        cpu_dashboard.assign_style()
        cpu_load_dashboard.assign_style()
        network_dashboard.assign_style()
        nvidia_dashboard.assign_style()
        process_dashboard.assign_style()
        io_tot_dashboard.assign_style()

        layout_controller.calculate_layout(dashboard_dict, dash_buttons, global_buttons)
        layout_controller.apply_layout(dashboard_dict, dash_buttons, global_buttons, stdscr)

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
            io_tot_dashboard.update_data_pipeline(schedule)

            #handles scrolling through the process list
            self.scroll_pos= process_dashboard.visible_content(self.scroll_pos)

            #render differences
            mem_dashboard.render()
            cpu_dashboard.render()
            cpu_load_dashboard.render()
            network_dashboard.render()
            nvidia_dashboard.render()
            process_dashboard.render()
            io_tot_dashboard.render()

            curses.doupdate()
            #refresh rate of 10 hz
            sleep(0.1)

