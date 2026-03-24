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
        if scroll_pos <0:
            scroll_pos= 0

        if scroll_pos > list_length:
            scroll_pos= list_length

        self.__sorted_process_content_list= sorted_process_list[scroll_pos: scroll_pos + self.window_max_lines]

    def draw_static_interface(self):

        if self.__dashboard_disabled:
            return

        process_dashboard = self.process_dashboard
        start_y = self.start_y

        # Column widths 
        widths = (
            7,   # PID
            7,   # PPID
            14,  # RunningUnder
            9,   # Priority
            7,   # State
            10,  # UpTime
            9,   # Threads
            10,  # VirtMem
            10,  # Memory
            0,   # Name (0 means no truncation / rest of line)
        )

        headers = (
            "PID",
            "PPID",
            "RunningUnder",
            "Priority",
            "State",
            "UpTime",
            "Threads",
            "VirtMem",
            "Memory",
            "Name",
        )

        # Build format string dynamically
        fmt_parts = []
        for w in widths[:-1]:
            fmt_parts.append(f"{{:<{w}}}")
        fmt_parts.append(f"{{:<{self.window_max_columns}}}")  # last column expands

        self.header_format= header_format = "".join(fmt_parts)
        header_line = header_format.format(*headers)

        process_dashboard.addnstr(start_y, 0, header_line, self.window_max_columns, self.bar_map[4])
        process_dashboard.noutrefresh()

    def render(self):

        if self.__dashboard_disabled:
            return