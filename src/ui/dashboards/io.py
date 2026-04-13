from readings.io import ReadTotalIO
from readings.system_pressure import IOPressure
from ui.formatters import IOTotalFormatter, IOPressureFormatter
from ui.contentdiff import ContentDiff
import curses
class IOTotals:
    """IO Totals Dashboard monitor. It's 11 lines and 51 columns."""
    __slots__= (
        "io_tot_dashboard",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "__dashboard_disabled",
        "__diff_engine_io",
        "__diff_engine_pressure",
        "io_tot_service",
        "io_pressure_service",
        "io_tot_formatter",
        "io_pressure_formatter"
    )

    def __init__(self, stdscr: curses.window, file_path: object) -> object:
        self.io_tot_dashboard = stdscr

        self.io_tot_service = ReadTotalIO(file_path)
        self.io_pressure_service = IOPressure(file_path)

        self.io_tot_formatter = IOTotalFormatter()
        self.io_pressure_formatter = IOPressureFormatter()

        self.__diff_engine_io = ContentDiff() 
        self.__diff_engine_pressure = ContentDiff()

    def assign_style(self):
        from core.style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_style_map= bar_map

    def resize(self, stdscr, dash_coordinates: object):
        self.io_tot_dashboard= stdscr

        self.draw_static_interface(dash_coordinates)
        self.__diff_engine_io.force_write = True
        self.__diff_engine_pressure.force_write = True

    def draw_static_interface(self, dash_coordinates: object):
        if dash_coordinates.sys_disabled is True:
            self.__dashboard_disabled = True
            return
        else:
            self.__dashboard_disabled = False
        
        io_tot_dashboard= self.io_tot_dashboard

        start_y = self.start_y = dash_coordinates.start_y 
        start_x = self.start_x = dash_coordinates.start_x
        max_x= dash_coordinates.max_x

        # borders
        io_tot_dashboard.addch(start_y, start_x, curses.ACS_ULCORNER)
        io_tot_dashboard.addch(start_y, start_x + max_x - 1, curses.ACS_URCORNER)
        io_tot_dashboard.addch(start_y+ 11, start_x, curses.ACS_LLCORNER)
        io_tot_dashboard.addch(start_y+ 11, start_x + max_x - 1, curses.ACS_LRCORNER)

        io_tot_dashboard.hline(start_y, start_x+1, curses.ACS_HLINE, max_x - 2)
        io_tot_dashboard.hline(start_y+ 11, start_x+1, curses.ACS_HLINE, max_x - 2)

        io_tot_dashboard.vline(start_y + 1, start_x, curses.ACS_VLINE, 10)
        io_tot_dashboard.vline(start_y + 1, start_x + max_x - 1, curses.ACS_VLINE, 10)

        # title
        io_tot_dashboard.addstr(start_y, start_x + 15, "IO Totals Dashboard", curses.A_BOLD)

        # PSI section
        io_tot_dashboard.addstr(start_y + 1, start_x + 2, "Some 10:")
        io_tot_dashboard.addstr(start_y + 2, start_x + 2, "Some 60:")
        io_tot_dashboard.addstr(start_y + 3, start_x + 2, "Some300:")

        #separator
        io_tot_dashboard.vline(start_y + 1, start_x + 20, "|", 3)

        io_tot_dashboard.addstr(start_y + 1, start_x + 26, "Full 10:")
        io_tot_dashboard.addstr(start_y + 2, start_x + 26, "Full 60:")
        io_tot_dashboard.addstr(start_y + 3, start_x + 26, "Full300:")

        io_tot_dashboard.addstr(start_y + 4, start_x + 3, "Health:")

        # separator
        io_tot_dashboard.hline(start_y + 5, start_x + 1, "-", max_x - 2)
        io_tot_dashboard.addstr(start_y + 5, start_x + 10, "PSI")
        io_tot_dashboard.addch(curses.ACS_UARROW)
        io_tot_dashboard.addstr(" - IO")
        io_tot_dashboard.addch(curses.ACS_DARROW)

        # device section header
        io_tot_dashboard.addstr(start_y + 6, start_x + 2, "Devices:")
        io_tot_dashboard.addstr(start_y + 6, start_x + 12, "Read")
        io_tot_dashboard.addstr(start_y + 6, start_x + 24, "Write")
        io_tot_dashboard.addstr(start_y + 6, start_x + 36, "IOPS")

        io_tot_dashboard.noutrefresh()

    def render(self):

        if self.__dashboard_disabled:
            return
        
        io_tot_dashboard = self.io_tot_dashboard

        content_list_io = self.__diff_engine_io.is_content_diff
        content_list_pressure = self.__diff_engine_pressure.is_content_diff

        start_y = self.start_y 
        start_x = self.start_x

        style_map = self.style_map
        bar_style_map = self.bar_style_map

        # -------------------------
        # PSI PRESSURE (top)
        # -------------------------
        # Some
        for i in range(3):
            entry = content_list_pressure[i]
            if entry.changed:
                attr = style_map[entry.content.style]
                io_tot_dashboard.addstr(start_y + 1 + i, start_x + 12, entry.content.value, attr)

        # Full
        for i in range(3):
            entry = content_list_pressure[3 + i]
            if entry.changed:
                attr = style_map[entry.content.style]
                io_tot_dashboard.addstr(start_y + 1 + i, start_x + 36, entry.content.value, attr)

        # Health
        health = content_list_pressure[6]
        if health.changed:
            attr = style_map[health.content.style]
            io_tot_dashboard.addstr(start_y + 4, start_x + 12, health.content.value, attr)

        # Health bar
        bar = content_list_pressure[7]
        if bar.changed:
            attr = bar_style_map[bar.content.style]
            io_tot_dashboard.hline(start_y + 4, start_x + 20, " ", bar.content.bar_width, attr)
            io_tot_dashboard.hline(start_y + 4, start_x + 20 + bar.content.bar_width, " ", 31 - bar.content.bar_width)

        # -------------------------
        # IO TOTALS (bottom)
        # -------------------------
        FIELDS_PER_DEVICE = 4
        row_index = 0

        for idx in range(0, len(content_list_io), FIELDS_PER_DEVICE):
            y = start_y + 7 + row_index

            # name
            entry = content_list_io[idx + 0]
            if entry.changed:
                attr = style_map[entry.content.style]
                io_tot_dashboard.addstr(y, start_x + 2, entry.content.value, attr)

            # read
            entry = content_list_io[idx + 1]
            if entry.changed:
                attr = style_map[entry.content.style]
                io_tot_dashboard.addstr(y, start_x + 12, entry.content.value, attr)

            # write
            entry = content_list_io[idx + 2]
            if entry.changed:
                attr = style_map[entry.content.style]
                io_tot_dashboard.addstr(y, start_x + 24, entry.content.value, attr)

            # iops
            entry = content_list_io[idx + 3]
            if entry.changed:
                attr = style_map[entry.content.style]
                io_tot_dashboard.addstr(y, start_x + 36, entry.content.value, attr)

            row_index += 1

        io_tot_dashboard.noutrefresh()

    def update_data_pipeline(self, schedule: dict) -> list:
        io_tot_service = self.io_tot_service
        io_pressure_service = self.io_pressure_service
        io_tot_formatter = self.io_tot_formatter
        io_pressure_formatter = self.io_pressure_formatter

        io_tot_service.read_io_totals(schedule)
        io_pressure_service.read_io(schedule)
        io_tot_formatter.format(io_tot_service, schedule)
        io_pressure_formatter.format(io_pressure_service, schedule)

        self.__diff_engine_io.check_differences(io_tot_formatter.formatted_io_output)
        self.__diff_engine_pressure.check_differences(io_pressure_formatter.formatted_io_output)