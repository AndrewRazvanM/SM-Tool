import curses
from readings.memory import MemoryInfo
from readings.system_pressure import CPUPressure
from readings.cpu import CPUInfoLoad, CPUInfoTemp
from ui.formatters import CPUTempFormatter, CPULoadFormatter, CPUPressureFormatter
from ui.contentdiff import ContentDiff

class CPUDashboard:
    __slots__ = (
        "cpu_dashboard",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "cpu_temp_readings",
        "cpu_pressure",
        "temp_formatter",
        "pressure_formatter",
        "__diff_engine_temp",
        "__diff_engine_pressure",
        "__dashboard_disabled",
        "__cpu_name",
        "__sensor_name",
        "last_line_y",
    )

    def __init__(self, stdscr: curses.window, file_path: object):
        self.cpu_dashboard = stdscr
        self.cpu_temp_readings = CPUInfoTemp(file_path)
        self.cpu_pressure = CPUPressure(file_path)
        self.temp_formatter = CPUTempFormatter()
        self.pressure_formatter= CPUPressureFormatter()
        self.__diff_engine_temp = ContentDiff()
        self.__diff_engine_pressure = ContentDiff()

        self.__cpu_name = self.cpu_temp_readings.cpu_name
        self.__sensor_name = self.cpu_temp_readings.sensor_name

    def resize(self, stdscr: curses.window, dash_coordinates: object):
        self.cpu_dashboard = stdscr
        self.__diff_engine_temp.force_write = True
        self.__diff_engine_pressure.force_write = True

        self.draw_static_interface(dash_coordinates)

    def assign_style(self):
        from core.style_maps import text_map, bar_map
        self.style_map = text_map
        self.bar_style_map = bar_map

    def update_data_pipeline(self, schedule: dict):
        disable_cpu_check=False
        cpu_temp_readings= self.cpu_temp_readings
        cpu_pressure= self.cpu_pressure
        temp_formatter= self.temp_formatter
        pressure_formatter= self.pressure_formatter

        # Update CPU temperature readings
        cpu_temp_readings.get_cpu_temp(disable_cpu_check, schedule)
        temp_formatter.format_info(cpu_temp_readings, schedule)
        self.__diff_engine_temp.check_differences(temp_formatter.formatted_cpu_readings)

        # Update CPU pressure readings
        cpu_pressure.read_cpu(disable_cpu_check, schedule)
        pressure_formatter.format(cpu_pressure, schedule)
        self.__diff_engine_pressure.check_differences(pressure_formatter.formatted_output)

    def draw_static_interface(self, dash_coordinates: object):
        # Check initial window size
        start_y = self.start_y = dash_coordinates.start_y
        start_x = self.start_x = dash_coordinates.start_x

        if dash_coordinates.sys_disabled is True:
            self.last_line_y = 0
            self.__dashboard_disabled= True
            return
        else:
            self.last_line_y = 13
            self.__dashboard_disabled= False

        dash = self.cpu_dashboard
        cpu_name, sensor_name = self.__cpu_name, self.__sensor_name

        # Draw borders
        dash.addch(start_y, start_x, curses.ACS_ULCORNER)
        dash.addch(start_y, start_x + 50, curses.ACS_URCORNER)
        dash.addch(start_y + 11, start_x, curses.ACS_LLCORNER)
        dash.addch(start_y + 11, start_x + 50, curses.ACS_LRCORNER)
        dash.hline(start_y, start_x + 1, curses.ACS_HLINE, 49)
        dash.hline(start_y + 11, start_x + 1, curses.ACS_HLINE, 49)
        dash.vline(start_y + 1, start_x, curses.ACS_VLINE, 10)
        dash.vline(start_y + 1, start_x + 50, curses.ACS_VLINE, 10)

        # Titles and labels
        dash.addstr(start_y, start_x + 15, "CPU Dashboard", curses.A_BOLD)
        dash.addstr(1 + start_y, max(1, 48 - len(cpu_name)) + start_x, cpu_name[:48])
        dash.addstr(2 + start_y, 7 + start_x, "CPU Cores:")
        dash.addstr(2 + start_y, 31 + start_x, "CPU Threads:")
        dash.hline(3 + start_y, 1 + start_x, "=", 49)

        # CPU temperature labels
        dash.addstr(8 + start_y, 13 + start_x, f"Temp sensor is {sensor_name}"[:36])
        dash.addstr(9 + start_y, 7 + start_x, "CPU Die:")
        dash.addstr(9 + start_y, 34 + start_x, "CPU Avg:")

        # CPU pressure labels
        dash.addstr(4 + start_y, 11 + start_x, "PSI:")
        dash.addstr(4 + start_y, 34 + start_x, "PSI Health:")
        dash.vline(4 + start_y, 26 + start_x, "|", 7)
        dash.addstr(5 + start_y, 1 + start_x, "Avg10:")
        dash.addstr(5 + start_y, 8 + start_x, "| Avg60:")
        dash.addstr(5 + start_y, 17 + start_x, "| Avg300:")
        dash.hline(7 + start_y, 1 + start_x, "-", 49)

        dash.noutrefresh()

    def render(self):
        if self.__dashboard_disabled:
            return

        dash = self.cpu_dashboard
        start_y, start_x = self.start_y, self.start_x
        style_map, bar_style_map = self.style_map, self.bar_style_map

        # CPU Temperature
        temp_list = self.__diff_engine_temp.is_content_diff
        if temp_list[0].changed:
            dash.addstr(9 + start_y, 16 + start_x,
                        temp_list[0].content.value,
                        style_map[temp_list[0].content.style])

        if temp_list[1].changed:
            width = min(24, temp_list[1].content.bar_width)
            dash.hline(10 + start_y, 1 + start_x, " ", width,
                       bar_style_map[temp_list[1].content.style])
            dash.hline(10 + start_y, 1 + start_x + width, " ", 24 - width)

        if temp_list[2].changed:
            dash.addstr(9 + start_y, 43 + start_x,
                        temp_list[2].content.value,
                        style_map[temp_list[2].content.style])

        if temp_list[3].changed:
            width = min(23, temp_list[3].content.bar_width)
            dash.hline(10 + start_y, 27 + start_x, " ", width,
                       bar_style_map[temp_list[3].content.style])
            dash.hline(10 + start_y, 27 + start_x + width, " ", 23 - width)

        if temp_list[4].changed:
            dash.addstr(2 + start_y, 17 + start_x,
                        temp_list[4].content.value,
                        style_map[temp_list[4].content.style])

        if temp_list[5].changed:
            dash.addstr(2 + start_y, 43 + start_x,
                        temp_list[5].content.value,
                        style_map[temp_list[5].content.style])

        # CPU Pressure
        pressure_list = self.__diff_engine_pressure.is_content_diff
        if pressure_list[0].changed:
            dash.addstr(6 + start_y, 2 + start_x,
                        pressure_list[0].content.value,
                        style_map[pressure_list[0].content.style])
        if pressure_list[1].changed:
            dash.addstr(6 + start_y, 11 + start_x,
                        pressure_list[1].content.value,
                        style_map[pressure_list[1].content.style])
        if pressure_list[2].changed:
            dash.addstr(6 + start_y, 20 + start_x,
                        pressure_list[2].content.value,
                        style_map[pressure_list[2].content.style])
        if pressure_list[3].changed:
            dash.addstr(5 + start_y, 39 + start_x,
                        pressure_list[3].content.value,
                        style_map[pressure_list[3].content.style])
        if pressure_list[4].changed:
            width = min(23, pressure_list[4].content.bar_width)
            dash.hline(6 + start_y, 27 + start_x, " ", width,
                       bar_style_map[pressure_list[4].content.style])
            dash.hline(6 + start_y, 27 + start_x + width, " ", 23 - width)

        dash.noutrefresh()

class CPULoadDashboard:
    __slots__ = (
        "cpu_load_dashboard",
        "nr_of_threads",
        "window_max_columns",
        "window_max_lines",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "cpu_info_load",
        "formatter",
        "__diff_engine",
        "__dashboard_disabled",
        "max_bar_width",
        "__cpu_load_positions",
        "last_line_y",
    )

    def __init__(self, stdscr: curses.window, file_path: object):
        self.cpu_load_dashboard = stdscr
        self.cpu_info_load = CPUInfoLoad(file_path)
        self.formatter = CPULoadFormatter()
        self.__diff_engine = ContentDiff()

        self.nr_of_threads = len(self.cpu_info_load.cpu_load_raw_data)

        self.max_bar_width = 1
        self.__cpu_load_positions = []

    def assign_style(self):
        from core.style_maps import text_map, bar_map
        self.style_map = text_map
        self.bar_style_map = bar_map

    def resize(self, stdscr: curses.window, dash_coordinates: object):
        self.cpu_load_dashboard = stdscr

        self.draw_static_interface(dash_coordinates)

    def update_data_pipeline(self, schedule: dict):
        disable_cpu_check= False
        # Update CPU load readings
        self.cpu_info_load.get_cpu_load(disable_cpu_check, schedule)
        # Format the CPU load
        self.formatter.format_load(self.cpu_info_load, self.max_bar_width, schedule)
        # Update differences for rendering
        self.__diff_engine.check_differences(self.formatter.formatted_cpu_load)

    def draw_static_interface(self, dash_coordinates: object):

        if dash_coordinates.sys_disabled is True:
            self.last_line_y= 0
            self.__dashboard_disabled= True
            return
        else:
            self.__dashboard_disabled= False

        start_y = self.start_y = dash_coordinates.start_y
        start_x = self.start_x = dash_coordinates.start_x
        dash = self.cpu_load_dashboard

        window_max_lines = min(24, dash_coordinates.max_y - start_y)
        window_max_columns = dash_coordinates.max_x - 1 - start_x

        threads = self.nr_of_threads

        header_space = 4
        row_height = 2
        min_bar_width = 3
        usable_width = window_max_columns
        usable_height = window_max_lines - header_space

        dash.addstr(start_y + 1, start_x + 15, "CPU Load Dashboard", curses.A_BOLD)

        max_rows = max(1, usable_height // row_height)
        rows = min(threads, max_rows)
        columns = -(-threads // rows)  # ceil division
        col_width = max(min_bar_width, usable_width // columns)
        self.max_bar_width = col_width - 2

        cpu_load_positions = []

        # Draw total CPU bar
        dash.addch(start_y + 2, start_x, "[")
        dash.addch(start_y + 2, start_x + col_width, "]")
        cpu_load_positions.append((start_y + 2, start_x))

        # Draw per-core bars
        for idx in range(threads - 1):
            row = idx // columns
            col = idx % columns
            y = start_y + header_space + row * row_height
            x = start_x + col * col_width
            last_line_y = start_y + header_space + row * row_height
            if y >= start_y + usable_height:
                break
            dash.addch(y, x, "[")
            dash.addch(y, x + col_width, "]")
            cpu_load_positions.append((y, x))

        self.last_line_y= last_line_y
        self.__cpu_load_positions = cpu_load_positions
        dash.noutrefresh()

    def render(self):
        if self.__dashboard_disabled:
            return

        dash = self.cpu_load_dashboard
        positions = self.__cpu_load_positions
        content_list = self.formatter.formatted_cpu_load
        bar_map = self.bar_style_map
        max_width = self.max_bar_width

        for idx, content in enumerate(content_list):
            if idx >= len(positions):
                break
            width = content.bar_width
            dash.addnstr(positions[idx][0], positions[idx][1] + 1,
                         content.value[:width], max_width, bar_map[content.style])
            dash.addnstr(positions[idx][0], positions[idx][1] + width + 1,
                         content.value[width:], max(1, max_width - width))

        dash.noutrefresh()