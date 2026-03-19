import curses

class NvidiaDashboard:

    __slots__= (
        "nvidia_dashboard",
        "window_max_columns",
        "window_max_lines",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "__nvidia_content_list",
        "__dashboard_disabled",
        "gpu_name_list",
    )

    def __init__(self, stdscr: curses.window, content_diff_engine: object, gpu_name_list: list) -> object:
        self.nvidia_dashboard = stdscr
        
        self.start_y= 3
        self.start_x= 50 + 48 + 50 + 2 #other dashboard column width
        self.gpu_name_list= gpu_name_list

        #max text width
        window_max_lines, window_max_columns= stdscr.getmaxyx()

        self.window_max_columns= window_max_columns - 1  - self.start_x#leaves space for edge
        #if there's noe enough vertical space, disable it. +3 leaves space for the tytle
        if window_max_lines > 13 + self.start_y and window_max_columns > 50 + self.start_x:
            self.__dashboard_disabled= False
        else:
            self.__dashboard_disabled= True

        self.__nvidia_content_list= content_diff_engine()

    def assing_style(self):
        from .style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_style_map= bar_map

    def resize(self, stdscr: curses.window):
        self.nvidia_dashboard= stdscr
        window_max_lines, window_max_columns= stdscr.getmaxyx()

        if window_max_lines > 13 + self.start_y and window_max_columns > 50 + self.start_x:
            self.__dashboard_disabled= False
            self.__nvidia_content_list.force_write= True
        else:
            self.__dashboard_disabled= True
            

        self.draw_static_interface()

    def check_content_diff(self, nvidia_content_list: list) -> list:
        self.__nvidia_content_list.check_differences(nvidia_content_list)

    def draw_static_interface(self):

        if self.__dashboard_disabled:
            return
        
        nvidia_dashboard= self.nvidia_dashboard

        #starting position
        start_y= self.start_y 
        start_x= self.start_x

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

        nvidia_dashboard.addstr(start_y+ 1, max(1, (49 - len(self.gpu_name_list[0]))//2) + start_x + 1, f"{self.gpu_name_list[0]}"[:49])
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
        content_list= self.__nvidia_content_list.is_content_diff

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