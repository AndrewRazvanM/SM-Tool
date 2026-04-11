from readings.io import ReadTotalIO
from ui.formatters import IOTotalFormatter
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
        self.io_tot_formatter = IOTotalFormatter()
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

        #starting position
        start_y = self.start_y = dash_coordinates.start_y 
        start_x = self.start_x = dash_coordinates.start_x
        max_x= dash_coordinates.max_x

        #build the borders
        # Draw corners first
        io_tot_dashboard.addch(start_y, start_x, curses.ACS_ULCORNER)
        io_tot_dashboard.addch(start_y, start_x + max_x - 1, curses.ACS_URCORNER)
        io_tot_dashboard.addch(start_y+ 11, start_x, curses.ACS_LLCORNER)
        io_tot_dashboard.addch(start_y+ 11, start_x + max_x - 1, curses.ACS_LRCORNER)

        # Draw horizontal edges (width-1)
        io_tot_dashboard.hline(start_y, start_x+1, curses.ACS_HLINE, max_x - 2)
        io_tot_dashboard.hline(start_y+ 11, start_x+1, curses.ACS_HLINE, max_x - 2)

        # Draw vertical edges (height-1)
        io_tot_dashboard.vline(start_y + 1, start_x, curses.ACS_VLINE, 10)
        io_tot_dashboard.vline(start_y + 1, start_x + max_x - 1, curses.ACS_VLINE, 10)
        #add title
        io_tot_dashboard.addstr(start_y+ 0, start_x+ 15, "IO Totals Dashboard", curses.A_BOLD)

         # CPU pressure labels
        io_tot_dashboard.addstr(start_y+ 1, start_x+ 2, "Some  |  Avg 10:")
        io_tot_dashboard.addstr(start_y+ 2, start_x+ 8, "|  Avg 60:")
        io_tot_dashboard.addstr(start_y+ 3, start_x+ 8, "| Avg 300:")
        io_tot_dashboard.hline(start_y+ 4, start_x+ 1, "-", 23)
        
        io_tot_dashboard.addstr(start_y+ 5, start_x+ 2, "Full  |  Avg 10:")
        io_tot_dashboard.addstr(start_y+ 6, start_x+ 8, "|  Avg 60:")
        io_tot_dashboard.addstr(start_y+ 7, start_x+ 8, "| Avg 300:")
        io_tot_dashboard.hline(start_y+ 8, start_x+ 1, "-", 23)

        io_tot_dashboard.addstr(start_y+ 9, start_x+ 7, "PSI Health:")
        io_tot_dashboard.vline(start_y+ 1, start_x+ 24, "|", 10)

    def render(self):

        if self.__dashboard_disabled:
                return
        
        io_tot_dashboard = self.io_tot_dashboard

        content_list_io = self.__diff_engine_io.is_content_diff

        start_y = self.start_y 
        start_x = self.start_x

        style_map = self.style_map

    def update_data_pipeline(self, schedule: dict) -> list:
        io_tot_service = self.io_tot_service
        io_tot_formatter = self.io_tot_formatter

        io_tot_service.read_io_totals(schedule)
        io_tot_formatter.format(io_tot_service.devices_total_io, schedule)

        self.__diff_engine_io.check_differences(io_tot_formatter.formatted_io_output)