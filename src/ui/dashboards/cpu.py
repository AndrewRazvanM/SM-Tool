import curses

class CPUDashboard:

    __slots__= (
        "cpu_dashboard",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "__cpu_info_content_diff",
        "__cpu_pressure_content_diff",
        "__dashboard_disabled",
        "__cpu_name",
        "__sensor_name"
    )

    def __init__(self, stdscr: curses.window, content_diff_engine: object, cpu_name: str, sensor_name: str) -> object:
        self.cpu_dashboard = stdscr
        
        self.start_y= 3
        self.start_x= 0

        #max text width
        window_max_lines, window_max_columns= stdscr.getmaxyx()

        #if window is too small, disables the dashboard
        if window_max_lines >= 13 + self.start_y and window_max_columns >= 51 + self.start_x:
            self.__dashboard_disabled= False
        else:
            self.__dashboard_disabled= True

        self.__cpu_info_content_diff= content_diff_engine()
        self.__cpu_pressure_content_diff= content_diff_engine()

        self.__cpu_name= cpu_name
        self.__sensor_name= sensor_name

    def resize(self, stdscr: curses.window):
        self.cpu_dashboard= stdscr
        window_max_lines, window_max_columns= stdscr.getmaxyx()

        if window_max_lines >= 13 + self.start_y and window_max_columns >= 51 + self.start_x:
            self.__dashboard_disabled= False
            self.draw_static_interface()
            self.__cpu_info_content_diff.force_write= True
            self.__cpu_pressure_content_diff.force_write= True

        else:
            self.__dashboard_disabled= True
    
    def assing_style(self):
        from .style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_style_map= bar_map

    def draw_static_interface(self):

        if self.__dashboard_disabled:
            return
        
        cpu_name= self.__cpu_name
        sensor_name= self.__sensor_name
        cpu_dashboard= self.cpu_dashboard

        #starting position
        start_y= self.start_y 
        start_x= self.start_x

        #build the borders
        # Draw corners first
        cpu_dashboard.addch(start_y, start_x, curses.ACS_ULCORNER)
        cpu_dashboard.addch(start_y, start_x+ 50, curses.ACS_URCORNER)
        cpu_dashboard.addch(start_y+ 11, start_x, curses.ACS_LLCORNER)
        cpu_dashboard.addch(start_y+ 11, start_x+ 50, curses.ACS_LRCORNER)

        # Draw horizontal edges (width-1)
        cpu_dashboard.hline(start_y, start_x+1, curses.ACS_HLINE, 49)
        cpu_dashboard.hline(start_y+ 11, start_x+1, curses.ACS_HLINE, 49)

        # Draw vertical edges (height-1)
        cpu_dashboard.vline(start_y+1, start_x, curses.ACS_VLINE, 10)
        cpu_dashboard.vline(start_y+1, start_x+ 50, curses.ACS_VLINE, 10)
        #add title
        cpu_dashboard.addstr(start_y+ 0, start_x+ 15, "CPU Dashboard", curses.A_BOLD)

        #add CPU name
        cpu_dashboard.addstr(1 + start_y, max(1,48 - len(cpu_name)) + start_x, cpu_name[:48])

        cpu_dashboard.addstr(2 + start_y, 7 + start_x, "CPU Cores:")
        cpu_dashboard.addstr(2 + start_y, 31 + start_x, "CPU Threads:")
        cpu_dashboard.hline(3+ start_y, 1 + start_x, "=" , 49)

        cpu_dashboard.addstr(4 + start_y, 11 + start_x, "PSI:")
        cpu_dashboard.addstr(4 + start_y, 34 + start_x, "PSI Health:")
        cpu_dashboard.vline(4 + start_y, 26 + start_x, "|", 7)

        cpu_dashboard.addstr(5 + start_y, 1 + start_x, "Avg10:")
        cpu_dashboard.addstr(5 + start_y, 8 + start_x, "| Avg60:")
        cpu_dashboard.addstr(5 + start_y, 17 + start_x, "| Avg300:")
        cpu_dashboard.hline(7 + start_y, 1 + start_x, "-", 49)

        cpu_dashboard.addstr(8 + start_y, 13 + start_x, f"Temp sensor is {sensor_name}"[:36])
        cpu_dashboard.addstr(9 + start_y, 7 + start_x, "CPU Die:")
        cpu_dashboard.addstr(9 + start_y, 34 + start_x, "CPU Avg:")
        
        cpu_dashboard.noutrefresh()

    def check_content_diff(self, formatted_cpu_readings: list, formatted_cpu_pressure: list):
        self.__cpu_info_content_diff.check_differences(formatted_cpu_readings)
        self.__cpu_pressure_content_diff.check_differences(formatted_cpu_pressure)

    def render(self):
        if self.__dashboard_disabled:
            return
        
        cpu_dashboard= self.cpu_dashboard

        cpu_info= self.__cpu_info_content_diff.is_content_diff
        cpu_pressure= self.__cpu_pressure_content_diff.is_content_diff

        start_y= self.start_y 
        start_x= self.start_x

        style_map= self.style_map
        bar_style_map= self.bar_style_map

        if cpu_info[0].changed:
            style= cpu_info[0].content.style
            attr= style_map[style]
            cpu_dashboard.addstr(9 + start_y, 16 + start_x, cpu_info[0].content.value, attr)

        if cpu_info[1].changed:
            style= cpu_info[1].content.style
            attr= bar_style_map[style]
            width= min(24, cpu_info[1].content.bar_width)
            cpu_dashboard.hline(10 + start_y, 1 + start_x, " ", width, attr)
            cpu_dashboard.hline(10 + start_y, 1 + start_x + width, " ", 24 - width)

        if cpu_info[2].changed:
            style= cpu_info[2].content.style
            attr= style_map[style]
            cpu_dashboard.addstr(9 + start_y, 43 + start_x, cpu_info[2].content.value, attr)

        if cpu_info[3].changed:
            style= cpu_info[3].content.style
            attr= bar_style_map[style]
            width= min(23, cpu_info[3].content.bar_width)
            cpu_dashboard.hline(10 + start_y, 27 + start_x, " ", width, attr)
            cpu_dashboard.hline(10 + start_y, 27 + start_x + width, " ", 23 - width)

        if cpu_info[4].changed:
            style= cpu_info[4].content.style
            attr= style_map[style]
            cpu_dashboard.addstr(2 + start_y, 17 + start_x, cpu_info[4].content.value, attr)

        if cpu_info[5].changed:
            style= cpu_info[5].content.style
            attr= style_map[style]
            cpu_dashboard.addstr(2 + start_y, 43 + start_x, cpu_info[5].content.value, attr)

        if cpu_pressure[0].changed:
            style= cpu_pressure[0].content.style
            attr= style_map[style]
            cpu_dashboard.addstr(6 + start_y, 2 + start_x, cpu_pressure[0].content.value, attr)

        if cpu_pressure[1].changed:
            style= cpu_pressure[1].content.style
            attr= style_map[style]
            cpu_dashboard.addstr(6 + start_y, 11 + start_x, cpu_pressure[1].content.value, attr)

        if cpu_pressure[2].changed:
            style= cpu_pressure[2].content.style
            attr= style_map[style]
            cpu_dashboard.addstr(6 + start_y, 20 + start_x, cpu_pressure[2].content.value, attr)

        if cpu_pressure[3].changed:
            style= cpu_pressure[3].content.style
            attr= style_map[style]
            cpu_dashboard.addstr(5 + start_y, 39 + start_x, cpu_pressure[3].content.value, attr)

        if cpu_pressure[4].changed:
            style= cpu_pressure[4].content.style
            attr= bar_style_map[style]
            width= min(23, cpu_pressure[4].content.bar_width)
            cpu_dashboard.hline(6 + start_y, 27 + start_x, " ", width, attr)
            cpu_dashboard.hline(6 + start_y, 27 + start_x + width, " ", 23 - width)

        cpu_dashboard.noutrefresh()

class CPULoadDashboard:

    __slots__= (
        "cpu_load_dashboard",
        "nr_of_threads",
        "window_max_columns",
        "window_max_lines",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "__cpu_load_content_list",
        "max_bar_width",
        "__cpu_load_positions",
        "__dashboard_disabled"
    )

    def __init__(self, stdscr: curses.window, formatted_content_list: object, nr_of_threads: int) -> object:
        self.cpu_load_dashboard = stdscr
        
        self.start_y= 14
        self.start_x= 0

        self.nr_of_threads= nr_of_threads
        self.max_bar_width= 1

        #max text width
        window_max_lines, window_max_columns= stdscr.getmaxyx()

        self.window_max_columns= window_max_columns - 1  - self.start_x#leaves space for edge
        self.window_max_lines= min(24, window_max_lines - self.start_y) #leaves space for the CPU Dashboard and Processes Dashboard
        #if there's noe enough vertical space, disable it. +3 leaves space for the tytle
        if window_max_lines < self.start_y + 3:
            self.__dashboard_disabled= True
        else:
            self.__dashboard_disabled= False

        self.__cpu_load_content_list= formatted_content_list

    def assing_style(self):
        from .style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_style_map= bar_map

    def resize(self, stdscr: curses.window):
        self.cpu_load_dashboard= stdscr
        window_max_lines, window_max_columns= stdscr.getmaxyx()

        start_y= self.start_y

        self.window_max_lines= min(24, window_max_lines  - start_y) #leaves space for the CPU Dashboard and process window
        self.window_max_columns= window_max_columns - 1 - self.start_x

        if window_max_lines < start_y + 3:
            self.__dashboard_disabled= True
        else:
            self.__dashboard_disabled= False

        self.draw_static_interface()

    def draw_static_interface(self):

        if self.__dashboard_disabled:
            return

        cpu_load_dashboard = self.cpu_load_dashboard
        start_y = self.start_y
        start_x = self.start_x
        threads = self.nr_of_threads

        # Usable space
        header_space = 4       # space for title
        row_height = 2         # height of each CPU bar row
        min_bar_width = 3      # minimum width per bar
        usable_width = self.window_max_columns
        usable_height = self.window_max_lines - header_space

        # Draw dashboard title
        cpu_load_dashboard.addstr(start_y + 1, start_x + 15, "CPU Load Dashboard", curses.A_BOLD)

        # Compute maximum rows that can fit
        max_rows = max(1, usable_height // row_height)

        # Decide number of rows and columns
        rows = min(threads, max_rows)
        columns = -(-threads // rows)  # ceil division

        # Compute column width to evenly fill horizontal space
        col_width = max(min_bar_width, usable_width // columns)
        self.max_bar_width = col_width - 2

        # Draw total CPU bar at top
        cpu_load_positions = []
        cpu_load_dashboard.addch(start_y + 2, start_x, "[")
        cpu_load_dashboard.addch(start_y + 2, start_x + col_width, "]")
        cpu_load_positions.append((start_y + 2, start_x))

        # Draw per-core CPU bars row by row
        for idx in range(threads - 1):
            row = idx // columns
            col = idx % columns

            y = start_y + header_space + row * row_height
            x = start_x + col * col_width

            if y >= start_y + usable_height:
                break  # don’t draw outside available vertical space

            cpu_load_dashboard.addch(y, x, "[")
            cpu_load_dashboard.addch(y, x + col_width, "]")
            cpu_load_positions.append((y, x))

        self.__cpu_load_positions = cpu_load_positions
        cpu_load_dashboard.noutrefresh()

    def render(self):
        if self.__dashboard_disabled:
            return
        
        #assign local references
        cpu_load_dashboard= self.cpu_load_dashboard
        cpu_load_positions= self.__cpu_load_positions
        content_list= self.__cpu_load_content_list.formatted_cpu_load
        bar_style_map= self.bar_style_map
        max_bar_width= self.max_bar_width

        for idx, content_obj in enumerate(content_list):
            style= content_obj.style
            attr_bar= bar_style_map[style]

            if idx > len(cpu_load_positions) - 1:
                break
            
            cpu_load_bar_width= content_obj.bar_width
            #the bar is "overlayed" over the text
            cpu_load_dashboard.addnstr(cpu_load_positions[idx][0], cpu_load_positions[idx][1] + 1, content_obj.value[:cpu_load_bar_width], max_bar_width, attr_bar)  #write text until content[cpu].bar_width
            cpu_load_dashboard.addnstr(cpu_load_positions[idx][0], cpu_load_positions[idx][1] + cpu_load_bar_width + 1, content_obj.value[cpu_load_bar_width:], max(1, max_bar_width - cpu_load_bar_width))      

        cpu_load_dashboard.noutrefresh()