import curses
from readings.memory import MemoryInfo
from readings.system_pressure import MemPressure
from ui.formatters import MemoryFormatter, MemoryPressureFormatter
from ui.contentdiff import ContentDiff

class MemoryDashboard:
    "Memory Dashboard monitor. It's 9 lines and 51 columns."
    __slots__= (
        "memory_dashboard",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "__dashboard_disabled",
        "__diff_engine_p",
        "__diff_engine_m",
        "mem_service",
        "mem_formatter",
        "mem_p_formatter",
        "mem_pressure_service",
        "mem_check_disable"
    )

    def __init__(self, stdscr: curses.window, file_path: object) -> object:
        self.mem_check_disable= False
        self.memory_dashboard = stdscr
        self.mem_service = MemoryInfo(file_path, self.mem_check_disable)
        self.mem_pressure_service= MemPressure(file_path)
        self.mem_formatter = MemoryFormatter()
        self.mem_p_formatter= MemoryPressureFormatter()
        self.__diff_engine_p= ContentDiff()
        self.__diff_engine_m= ContentDiff()

    def assign_style(self):
        from core.style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_style_map= bar_map

    def resize(self, stdscr, dash_coordinates: object):
        self.memory_dashboard= stdscr

        self.draw_static_interface(dash_coordinates)
        self.__diff_engine_p.force_write= True
        self.__diff_engine_m.force_write= True

    def draw_static_interface(self, dash_coordinates: object):
        if dash_coordinates.sys_disabled is True:
            self.__dashboard_disabled = True
            return
        else:
            self.__dashboard_disabled = False
        
        memory_dashboard= self.memory_dashboard

        start_y= self.start_y = dash_coordinates.start_y 
        start_x= self.start_x = dash_coordinates.start_x
        max_x= dash_coordinates.max_x

        # borders
        memory_dashboard.addch(start_y, start_x, curses.ACS_ULCORNER)
        memory_dashboard.addch(start_y, start_x + max_x - 1, curses.ACS_URCORNER)
        memory_dashboard.addch(start_y+ 11, start_x, curses.ACS_LLCORNER)
        memory_dashboard.addch(start_y+ 11, start_x + max_x - 1, curses.ACS_LRCORNER)

        memory_dashboard.hline(start_y, start_x+1, curses.ACS_HLINE, max_x - 2)
        memory_dashboard.hline(start_y+ 11, start_x+1, curses.ACS_HLINE, max_x - 2)

        memory_dashboard.vline(start_y + 1, start_x, curses.ACS_VLINE, 10)
        memory_dashboard.vline(start_y + 1, start_x + max_x - 1, curses.ACS_VLINE, 10)

        # title
        memory_dashboard.addstr(start_y, start_x + 15, "Memory Dashboard", curses.A_BOLD)

        # PSI section (top)
        memory_dashboard.addstr(start_y + 1, start_x + 2, "Some 10:")
        memory_dashboard.addstr(start_y + 2, start_x + 2, "Some 60:")
        memory_dashboard.addstr(start_y + 3, start_x + 2, "Some300:")

        #separator
        memory_dashboard.vline(start_y + 1, start_x + 20, "|", 3)

        memory_dashboard.addstr(start_y + 1, start_x + 26, "Full 10:")
        memory_dashboard.addstr(start_y + 2, start_x + 26, "Full 60:")
        memory_dashboard.addstr(start_y + 3, start_x + 26, "Full300:")

        memory_dashboard.addstr(start_y + 4, start_x + 3, "Health:")

        # separator
        memory_dashboard.hline(start_y + 5, start_x + 1, "-", max_x - 2)
        memory_dashboard.addstr(start_y + 5, start_x + 10, "PSI")
        memory_dashboard.addch(curses.ACS_UARROW)
        memory_dashboard.addstr(" - Memory")
        memory_dashboard.addch(curses.ACS_DARROW)

        # memory info section
        memory_dashboard.addstr(start_y + 6, start_x + 2, "Total Mem:")
        memory_dashboard.addstr(start_y + 7, start_x + 2, "Free  Mem:")
        memory_dashboard.addstr(start_y + 8, start_x + 2, "Total Swap:")
        memory_dashboard.addstr(start_y + 9, start_x + 2, "Free  Swap:")

        memory_dashboard.noutrefresh()

    def update_data_pipeline(self, schedule: dict):
        mem_service= self.mem_service
        mem_pressure_service= self.mem_pressure_service

        mem_formatter= self.mem_formatter
        mem_p_formatter= self.mem_p_formatter

        mem_service.update(schedule)
        mem_pressure_service.read_mem(self.mem_check_disable, schedule)
        mem_formatter.format(mem_service, schedule)
        mem_p_formatter.format_mem(mem_pressure_service, schedule)

        self.__diff_engine_m.check_differences(mem_formatter.formatted_output)
        self.__diff_engine_p.check_differences(mem_p_formatter.formatted_output)

    def render(self):
        if self.__dashboard_disabled:
            return
        
        memory_dashboard= self.memory_dashboard
        start_y= self.start_y
        start_x= self.start_x
        style_map= self.style_map
        bar_style_map= self.bar_style_map

        mem_info= self.__diff_engine_m.is_content_diff
        mem_pressure= self.__diff_engine_p.is_content_diff

        # -------------------------
        # PSI PRESSURE (top)
        # -------------------------
        # Some
        for i in range(3):
            entry = mem_pressure[i]
            if entry.changed:
                attr = style_map[entry.content.style]
                memory_dashboard.addstr(start_y + 1 + i, start_x + 12, entry.content.value, attr)

        # Full
        for i in range(3):
            entry = mem_pressure[3 + i]
            if entry.changed:
                attr = style_map[entry.content.style]
                memory_dashboard.addstr(start_y + 1 + i, start_x + 36, entry.content.value, attr)

        # Health
        health = mem_pressure[6]
        if health.changed:
            attr = style_map[health.content.style]
            memory_dashboard.addstr(start_y + 4, start_x + 12, health.content.value, attr)

        # Health bar
        bar = mem_pressure[7]
        if bar.changed:
            attr = bar_style_map[bar.content.style]
            memory_dashboard.hline(start_y + 4, start_x + 20, " ", bar.content.bar_width, attr)
            memory_dashboard.hline(start_y + 4, start_x + 20 + bar.content.bar_width, " ", 30 - bar.content.bar_width)

        # -------------------------
        # MEMORY INFO (bottom)
        # -------------------------
        if mem_info[0].changed:
            attr = style_map[mem_info[0].content.style]
            memory_dashboard.addstr(start_y + 6, start_x + 16, mem_info[0].content.value, attr)

        if mem_info[1].changed:
            attr = style_map[mem_info[1].content.style]
            memory_dashboard.addstr(start_y + 7, start_x + 16, mem_info[1].content.value, attr)

        if mem_info[2].changed:
            attr = style_map[mem_info[2].content.style]
            memory_dashboard.addstr(start_y + 8, start_x + 16, mem_info[2].content.value, attr)

        if mem_info[3].changed:
            attr = style_map[mem_info[3].content.style]
            memory_dashboard.addstr(start_y + 9, start_x + 16, mem_info[3].content.value, attr)

        memory_dashboard.noutrefresh()