import curses

class ProcessDashboard:

    __slots__= (
        "process_dashboard",
        "window_max_lines",
        "window_max_columns",
        "header_format",
        "start_y",
        "start_x",
        "style_map",
        "bar_map",
        "__sorted_process_content_list",
        "__dashboard_disabled",
        "__widths",
        "positions_list"
    )

    def __init__(self, stdscr: curses.window, cpu_load_max_y: int) -> object:
        self.process_dashboard = stdscr
        
        self.start_y= cpu_load_max_y + 2
        self.start_x= 0 #other dashboard column width

        #max text width
        window_max_lines, self.window_max_columns= stdscr.getmaxyx()
        self.window_max_lines= max(0, window_max_lines - 1 - self.start_y)

        #if there's not enough vertical space, disable it. 
        if self.window_max_lines > 3:
            self.__dashboard_disabled= False
        else:
            self.__dashboard_disabled= True

        self.__widths = [
            10,   # PID
            10,   # PPID
            16,  # RunningUnder
            9,   # Priority
            7,   # State
            10,  # UpTime
            9,   # Threads
            6,   # Cpu %
            10,  # VirtMem
            10,  # Memory
            0,   # Name (0 means no truncation / rest of line)
        ]

    def assing_style(self):
        from .style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_map= bar_map

    def resize(self, stdscr: curses.window, cpu_load_max_y: int):
        self.process_dashboard= stdscr
        self.start_y= cpu_load_max_y + 2

        window_max_lines, self.window_max_columns= stdscr.getmaxyx()
        self.window_max_lines= max(0, window_max_lines - 1 - self.start_y)
        
        if self.window_max_lines > 3:
            self.__dashboard_disabled= False
        else:
            self.__dashboard_disabled= True

        self.draw_static_interface()

    def visible_content(self, scroll_pos: int, sorted_process_list: list) -> list:
        list_length= len(sorted_process_list) - 1

        if scroll_pos > list_length:
            scroll_pos= list_length

        self.__sorted_process_content_list= sorted_process_list[scroll_pos: scroll_pos + self.window_max_lines]

    def draw_static_interface(self):

        if self.__dashboard_disabled:
            return

        process_dashboard = self.process_dashboard
        start_y = self.start_y

        # Column widths 
        __widths= self.__widths

        headers = (
            "PID",
            "PPID",
            "RunningUnder",
            "Priority",
            "State",
            "UpTime",
            "Threads",
            "CPU %",
            "VirtMem",
            "Memory",
            "Name",
        )
        
        #pre-calculate the positions
        positions_list= []
        position_idx= 0
        # Build format string dynamically
        fmt_parts = []
        for w in __widths[:-1]:
            position_idx+= w
            positions_list.append(position_idx)

            fmt_parts.append(f"{{:<{w}}}")

        fmt_parts.append(f"{{:<{self.window_max_columns}}}")  # last column expands

        self.positions_list= positions_list
        self.header_format= header_format = "".join(fmt_parts)
        header_line = header_format.format(*headers)

        process_dashboard.addnstr(start_y, 0, header_line, self.window_max_columns, self.bar_map[4])
        process_dashboard.noutrefresh()

    def render(self):

        if self.__dashboard_disabled:
            return
        
        start_y= self.start_y + 1 #leave space for header

        positions_list= self.positions_list

        window_max_columns= self.window_max_columns - 2

        style_map= self.style_map

        __sorted_process_content_list= self.__sorted_process_content_list
        process_dashboard= self.process_dashboard

        for row_idx, process in enumerate(__sorted_process_content_list):

            attr= style_map[process[0].style]

            process_dashboard.addnstr(start_y + row_idx, 0, process[0].value, window_max_columns, attr)
            
            for col in range(0, 10):
                col_position= positions_list[col]

                max_col_width= window_max_columns - col_position
                if max_col_width < 1:
                    break

                attr= style_map[process[col + 1].style]
                process_dashboard.addnstr(start_y + row_idx, col_position, process[col + 1].value, max_col_width, attr)