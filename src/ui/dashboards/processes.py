import curses
from readings.processes import ProcessMonitor
from ui.formatters import ProcessFormatter
from core.sorter import sorter
from ui.contentdiff import ScrollWinContentDiff

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
        "content_diff",
        "positions_list",
        "process_list",
        "process_services",
        "process_formatter",
        "sorter",
    )

    def __init__(self, stdscr: curses.window, last_dashboard_max_y: int, file_path: object) -> object:
        self.process_dashboard = stdscr
        self.process_services= ProcessMonitor(file_path)
        self.process_formatter= ProcessFormatter()
        self.content_diff= ScrollWinContentDiff()
        self.sorter= sorter
        self.process_list= {}
        
        self.start_y= last_dashboard_max_y + 2
        self.start_x= 0 #other dashboard column width

        #max text width
        window_max_lines, self.window_max_columns= stdscr.getmaxyx()
        self.window_max_lines= max(0, window_max_lines - 1 - self.start_y)

        #if there's not enough vertical space, disable it. 
        if self.window_max_lines > 3:
            self.__dashboard_disabled= False
        else:
            self.__dashboard_disabled= True

    def update_data_pipeline(self, schedule):
        self.process_services.update(schedule, self.process_list)
        self.sorter(self.process_list, schedule)
        self.process_formatter.format(self.process_list, self.process_services, schedule)

    def assing_style(self):
        from .style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_map= bar_map

    def resize(self, stdscr: curses.window, last_dashboard_max_y: int):
        self.process_dashboard= stdscr
        self.start_y= last_dashboard_max_y + 2

        window_max_lines, self.window_max_columns= stdscr.getmaxyx()
        self.window_max_lines= max(0, window_max_lines - 1 - self.start_y)
        
        if self.window_max_lines > 3:
            self.__dashboard_disabled= False
        else:
            self.__dashboard_disabled= True

        self.draw_static_interface()

    def visible_content(self, scroll_pos: int) -> list:
        process_list= self.process_formatter.formatted_processes_output
        list_length= len(process_list) - 1

        if scroll_pos > list_length:
            scroll_pos= list_length

        self.__sorted_process_content_list= process_list[scroll_pos: scroll_pos + self.window_max_lines]

        self.content_diff.check_differences(self.__sorted_process_content_list)

        return scroll_pos

    def draw_static_interface(self):

        if self.__dashboard_disabled:
            return

        process_dashboard = self.process_dashboard
        start_y = self.start_y

        # Column widths 
        __widths = [
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
            25,  # Name 
            0,   # Command (0 means no truncation / rest of line)
        ]

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
            "Command"
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
        
        highlight_columns= (3, 4, 5, 7, 8, 9)
        
        start_y= self.start_y + 1 #leave space for header

        positions_list= self.positions_list

        window_max_columns= self.window_max_columns - 2

        style_map= self.style_map

        content= self.content_diff.is_content_diff
        process_dashboard= self.process_dashboard

        for row_idx, process_obj in enumerate(content):
            process_row= process_obj.row_content

            if process_obj.row_changed:

                attr= style_map[process_row[0].style]
                process_dashboard.addnstr(start_y + row_idx, 0, process_row[0].value, window_max_columns, attr)
                
                for col in range(0, 10):
                    col_position= positions_list[col]

                    max_col_width= window_max_columns - col_position
                    if max_col_width < 1:
                        break

                    attr= style_map[process_row[col + 1].style]
                    process_dashboard.addnstr(start_y + row_idx, col_position, process_row[col + 1].value, max_col_width, attr)
            #updates only cpu, time, priority, state, virt mem, mem
            elif process_obj.row_update_values:
                for idx in highlight_columns:
                    text= process_row[idx].value
                    style= process_row[idx].style
                    col_position= positions_list[idx - 1]
                    max_width= window_max_columns - col_position
                    if max_width >= 1:
                    
                        attr= style_map[style]
                        process_dashboard.addnstr(start_y + row_idx, col_position, text, max_width, attr)
                