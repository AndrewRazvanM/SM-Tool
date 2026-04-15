import curses
from readings.process_monitor import ProcessMonitor
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
        "__diff_engine",
        "positions_list",
        "process_list",
        "process_services",
        "process_formatter",
        "sorter",
    )

    def __init__(self, stdscr: curses.window, file_path: object) -> object:
        self.process_dashboard = stdscr
        self.process_services= ProcessMonitor(file_path)
        self.process_formatter= ProcessFormatter()
        self.__diff_engine= ScrollWinContentDiff()
        self.sorter= sorter
        self.process_list= {}
        
        self.start_y= 0
        self.start_x= 0
        self.window_max_lines= 0
        self.window_max_columns= 0
        self.__dashboard_disabled= True
        self.__sorted_process_content_list= []
        self.positions_list= []
        self.header_format= ""

    def update_data_pipeline(self, schedule: dict):
        self.process_services.update(schedule, self.process_list)
        self.sorter(self.process_list, schedule)
        self.process_formatter.format(self.process_list, self.process_services, schedule)

    def assign_style(self):
        from core.style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_map= bar_map

    def resize(self, stdscr: curses.window, dash_coordinates: object):
        self.process_dashboard= stdscr
        self.__diff_engine.force_write= True

        self.draw_static_interface(dash_coordinates)

    def visible_content(self, scroll_pos: int) -> list:
        process_list= self.process_formatter.formatted_processes_output
        list_length= len(process_list) - 1

        if scroll_pos > list_length:
            scroll_pos= list_length

        self.__sorted_process_content_list= process_list[scroll_pos: scroll_pos + self.window_max_lines]

        self.__diff_engine.check_differences(self.__sorted_process_content_list)

        return scroll_pos

    def draw_static_interface(self, dash_coordinates: object):

        window_max_columns = self.window_max_columns = dash_coordinates.max_x - 1
        self.window_max_lines = dash_coordinates.max_y

        if dash_coordinates.sys_disabled is True:
            self.__dashboard_disabled= True
            return

        self.__dashboard_disabled= False

        start_y = self.start_y = dash_coordinates.start_y
        start_x = self.start_x = dash_coordinates.start_x

        process_dashboard = self.process_dashboard

        # Column widths 
        __widths = [
            10,   # PID
            10,   # PPID
            14,  # RunningUnder
            5,   # Priority
            7,   # State
            10,  # UpTime
            9,   # Threads
            6,   # Cpu %
            10,  # VirtMem
            10,  # Memory
            20,  # Name 
            0,   # Command (0 means no truncation / rest of line)
        ]

        headers = (
            "PID",
            "PPID",
            "RunningUnder",
            "Prio",
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
        header_parts = []
        for w in __widths[:-1]:
            position_idx+= w
            positions_list.append(position_idx)

            header_parts.append(f"{{:<{w}}}")

        remaining_window_columns = max(0, window_max_columns - position_idx)
        header_parts.append(f"{{:<{remaining_window_columns}}}")  # last column expands

        self.positions_list= positions_list
        self.header_format= header_format = "".join(header_parts)
        header_line = header_format.format(*headers)

        process_dashboard.addnstr(start_y, start_x, header_line, window_max_columns, self.bar_map[4])
        process_dashboard.noutrefresh()

    def render(self):

        if self.__dashboard_disabled:
            return
        
        highlight_columns= (3, 4, 5, 7, 8, 9)
        
        start_y = self.start_y + 1 #leave space for header
        start_x = self.start_x

        positions_list= self.positions_list

        window_max_columns= self.window_max_columns - 2

        style_map= self.style_map

        content= self.__diff_engine.is_content_diff
        process_dashboard= self.process_dashboard

        for row_idx, process_obj in enumerate(content):
            process_row= process_obj.row_content

            if process_obj.row_changed:

                attr= style_map[process_row[0].style]
                process_dashboard.addnstr(start_y + row_idx, start_x, process_row[0].value, window_max_columns, attr)
                
                for col in range(0, 11):
                    col_position= positions_list[col]

                    max_col_width= window_max_columns - col_position
                    if max_col_width < 1:
                        break

                    attr= style_map[process_row[col + 1].style]
                    process_dashboard.addnstr(start_y + row_idx, start_x + col_position, process_row[col + 1].value, max_col_width, attr)

            #updates only cpu, time, priority, state, virt mem, mem
            elif process_obj.row_update_values:
                for idx in highlight_columns:
                    text= process_row[idx].value
                    style= process_row[idx].style
                    col_position= positions_list[idx - 1]
                    max_width= window_max_columns - col_position
                    if max_width >= 1:
                    
                        attr= style_map[style]
                        process_dashboard.addnstr(start_y + row_idx, start_x + col_position, text, max_width, attr)
                