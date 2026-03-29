import curses
from readings.nvidia import Nvidia
from ui.formatters import NvidiaFormatter
from ui.contentdiff import ContentDiff

class NvidiaDashboard:

    __slots__= (
        "nvidia_dashboard",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "formatter",
        "nvidia_service",
        "__diff_engine",
        "__dashboard_disabled"
    )

    def __init__(self, stdscr: curses.window) -> object:
        self.nvidia_dashboard = stdscr
        
        self.nvidia_service= Nvidia()
        self.formatter= NvidiaFormatter()

        self.__diff_engine= ContentDiff()

    def assign_style(self):
        from core.style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_style_map= bar_map

    def resize(self, stdscr: curses.window, dash_coordinates: object):
        self.nvidia_dashboard= stdscr    

        self.draw_static_interface(dash_coordinates)

    def update_data_pipeline(self, schedule: dict) -> list:
        nvidia_service= self.nvidia_service
        formated_data= self.formatter

        nvidia_service.get_nvidia_gpu_readings(schedule)
        formated_data.format(nvidia_service.gpus_readings, schedule)
        self.__diff_engine.check_differences(formated_data.formatted_nvidia_output)

    def draw_static_interface(self, dash_coordinates: object):

        if dash_coordinates.sys_disabled is True:
            self.__dashboard_disabled= True
            return
        else:
            self.__dashboard_disabled= False
        
        nvidia_dashboard= self.nvidia_dashboard
        gpu_name_list= self.nvidia_service.gpu_name_list

        #starting position
        start_y= dash_coordinates.start_y 
        start_x= dash_coordinates.start_x

        #build the borders
        # Draw corners first
        nvidia_dashboard.addch(start_y, start_x, curses.ACS_ULCORNER)
        nvidia_dashboard.addch(start_y, start_x+ 50, curses.ACS_URCORNER)
        nvidia_dashboard.addch(start_y+ 11, start_x, curses.ACS_LLCORNER)
        nvidia_dashboard.addch(start_y+ 11, start_x+ 50, curses.ACS_LRCORNER)

        # Draw horizontal edges (width-1)
        nvidia_dashboard.hline(start_y, start_x+1, curses.ACS_HLINE, 49)
        nvidia_dashboard.hline(start_y+ 11, start_x+1, curses.ACS_HLINE, 49)

        # Draw vertical edges (height-1)
        nvidia_dashboard.vline(start_y + 1, start_x, curses.ACS_VLINE, 10)
        nvidia_dashboard.vline(start_y + 1, start_x+ 50, curses.ACS_VLINE, 10)
        #add title
        nvidia_dashboard.addstr(start_y+ 0, start_x+ 15, "nVidia Dashboard", curses.A_BOLD)

        nvidia_dashboard.addstr(start_y+ 1, max(1, (49 - len(gpu_name_list[0]))//2) + start_x + 1, f"{gpu_name_list[0]}"[:49])
        nvidia_dashboard.hline(start_y+ 2, start_x + 1, "=", 49)
        nvidia_dashboard.addstr(start_y+ 3, start_x + 1, "Temperature:")
        nvidia_dashboard.addstr(start_y+ 5, start_x + 1, "Clock Speed:")
        nvidia_dashboard.addstr(start_y+ 6, start_x + 1, "  Fan Speed:")
        nvidia_dashboard.addstr(start_y+ 7, start_x + 1, "Memory Load:")
        nvidia_dashboard.addstr(start_y+ 8, start_x + 1, "   GPU Load:")

        nvidia_dashboard.noutrefresh()

    def render(self):
        if self.__dashboard_disabled:
            return
        
        nvidia_dashboard= self.nvidia_dashboard
        content_list= self.__diff_engine.is_content_diff

        #starting position
        start_y= self.start_y 
        start_x= self.start_x

        style_map= self.style_map
        bar_style_map= self.bar_style_map

        if content_list[0].changed:
            style= content_list[0].content.style
            attr= style_map[style]

            nvidia_dashboard.addstr(start_y+ 3, start_x + 14, content_list[0].content.value, attr)

        if content_list[1].changed:
            style= content_list[1].content.style
            attr= bar_style_map[style]
            bar_width= content_list[1].content.bar_width
            nvidia_dashboard.hline(start_y+ 4, start_x + 1, " ", bar_width, attr)
            nvidia_dashboard.hline(start_y+ 4, start_x + 1 + bar_width, " ", max(0, 49 - bar_width))

        if content_list[2].changed:
            style= content_list[2].content.style
            attr= style_map[style]

            nvidia_dashboard.addstr(start_y+ 5, start_x + 14, content_list[2].content.value, attr)

        if content_list[3].changed:
            style= content_list[3].content.style
            attr= style_map[style]

            nvidia_dashboard.addstr(start_y+ 6, start_x + 14, content_list[3].content.value, attr)

        if content_list[4].changed:
            style= content_list[4].content.style
            attr= style_map[style]

            nvidia_dashboard.addstr(start_y+ 7, start_x + 14, content_list[4].content.value, attr)

        if content_list[5].changed:
            style= content_list[5].content.style
            attr= style_map[style]

            nvidia_dashboard.addstr(start_y+ 8, start_x + 14, content_list[5].content.value, attr)

        if content_list[6].changed:
            style= content_list[6].content.style
            attr= bar_style_map[style]
            bar_width= content_list[6].content.bar_width
            nvidia_dashboard.hline(start_y+ 9, start_x + 1, " ", bar_width, attr)
            nvidia_dashboard.hline(start_y+ 9, start_x + 1 + bar_width, " ", max(0, 49 - bar_width))

        nvidia_dashboard.noutrefresh()