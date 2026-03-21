import curses

class MemoryDashboard:
    "Memory Dashboard monitor. It's 9 lines and 51 columns."
    __slots__= (
        "memory_dashboard",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "__mem_info_content_diff",
        "__mem_pressure_content_diff",
        "__dashboard_disabled"
    )

    def __init__(self, stdscr: curses.window, content_diff_engine: object) -> object:
        self.memory_dashboard = stdscr

        #starting position
        self.start_y= 3
        self.start_x= 51
        self.__mem_info_content_diff= content_diff_engine()
        self.__mem_pressure_content_diff= content_diff_engine()

        window_max_lines, window_max_columns= stdscr.getmaxyx()
        if window_max_lines >= 10 + self.start_y and window_max_columns >= 51 + self.start_x:
            self.__dashboard_disabled= False
        else:
            self.__dashboard_disabled= True

    def assing_styles(self):
        from .style_maps import text_map, bar_map

        self.style_map= text_map
        self.bar_style_map= bar_map

    def resize(self, stdscr):
        self.memory_dashboard= stdscr
        window_max_lines, window_max_columns= stdscr.getmaxyx()

        if window_max_lines >= 10 + self.start_y and window_max_columns >= 51 + self.start_x:
            self.__dashboard_disabled= False
            self.draw_static_interface()
            self.__mem_info_content_diff.force_write= True
            self.__mem_pressure_content_diff.force_write= True

        else:
            self.__dashboard_disabled= True

    def draw_static_interface(self):
        if self.__dashboard_disabled:
            return
        
        memory_dashboard= self.memory_dashboard

        #starting position
        start_y= self.start_y 
        start_x= self.start_x

        #build the borders
        # Draw corners first
        memory_dashboard.addch(start_y, start_x, curses.ACS_ULCORNER)
        memory_dashboard.addch(start_y, start_x+ 47, curses.ACS_URCORNER)
        memory_dashboard.addch(start_y+ 11, start_x, curses.ACS_LLCORNER)
        memory_dashboard.addch(start_y+ 11, start_x+ 47, curses.ACS_LRCORNER)

        # Draw horizontal edges (width-1)
        memory_dashboard.hline(start_y, start_x+1, curses.ACS_HLINE, 46)
        memory_dashboard.hline(start_y+ 11, start_x+1, curses.ACS_HLINE, 46)

        # Draw vertical edges (height-1)
        memory_dashboard.vline(start_y + 1, start_x, curses.ACS_VLINE, 10)
        memory_dashboard.vline(start_y + 1, start_x+ 47, curses.ACS_VLINE, 10)
        #add title
        memory_dashboard.addstr(start_y+ 0, start_x+ 15, "Memory Dashboard", curses.A_BOLD)

        memory_dashboard.addstr(start_y+ 1, start_x+ 2, "Some  |  Avg 10:")
        memory_dashboard.addstr(start_y+ 2, start_x+ 8, "|  Avg 60:")
        memory_dashboard.addstr(start_y+ 3, start_x+ 8, "| Avg 300:")
        memory_dashboard.hline(start_y+ 4, start_x+ 1, "-", 46)
        
        memory_dashboard.addstr(start_y+ 5, start_x+ 2, "Full  |  Avg 10:")
        memory_dashboard.addstr(start_y+ 6, start_x+ 8, "|  Avg 60:")
        memory_dashboard.addstr(start_y+ 7, start_x+ 8, "| Avg 300:")
        memory_dashboard.hline(start_y+ 8, start_x+ 1, "-", 46)

        memory_dashboard.addstr(start_y+ 9, start_x+ 7, "PSI Health:")
        memory_dashboard.vline(start_y+ 1, start_x+ 26, "|", 10)

        memory_dashboard.addstr(start_y+ 1, start_x+ 28, "Total Memory:")
        memory_dashboard.addstr(start_y+ 2, start_x+ 28, " Free Memory:")
        memory_dashboard.addstr(start_y+ 5, start_x+ 28, "  Total SWAP:")
        memory_dashboard.addstr(start_y+ 6, start_x+ 28, "   Free SWAP:")
        memory_dashboard.noutrefresh()

    def check_content_diff(self, mem_info_content_list: list, mem_pressure_content_list: list):
        self.__mem_info_content_diff.check_differences(mem_info_content_list)
        self.__mem_pressure_content_diff.check_differences(mem_pressure_content_list)

    def render(self):
        if self.__dashboard_disabled:
            return
        
        memory_dashboard= self.memory_dashboard
        start_y= self.start_y
        start_x= self.start_x
        style_map= self.style_map
        bar_style_map= self.bar_style_map

        mem_info= self.__mem_info_content_diff.is_content_diff
        mem_pressure= self.__mem_pressure_content_diff.is_content_diff

        if mem_info[0].changed:
            style= mem_info[0].content.style
            attr= style_map[style]
            memory_dashboard.addstr(1 + start_y, 42 + start_x, mem_info[0].content.value, attr)

        if mem_info[1].changed:
            style= mem_info[1].content.style
            attr= style_map[style]
            memory_dashboard.addstr(2 + start_y, 42 + start_x, mem_info[1].content.value, attr)

        if mem_info[2].changed:
            style= mem_info[2].content.style
            attr= style_map[style]
            memory_dashboard.addstr(5 + start_y, 42 + start_x, mem_info[2].content.value, attr)

        if mem_info[3].changed:
            style= mem_info[3].content.style
            attr= style_map[style]
            memory_dashboard.addstr(6 + start_y, 42 + start_x, mem_info[3].content.value, attr)
            
        if mem_pressure[0].changed:
            style= mem_pressure[0].content.style
            attr= style_map[style]
            memory_dashboard.addstr(1 + start_y, 19 + start_x, mem_pressure[0].content.value, attr)
           
        if mem_pressure[1].changed:
            style= mem_pressure[1].content.style
            attr= style_map[style]
            memory_dashboard.addstr(2 + start_y, 19 + start_x, mem_pressure[1].content.value, attr)
           
        if mem_pressure[2].changed:
            style= mem_pressure[2].content.style
            attr= style_map[style]
            memory_dashboard.addstr(3 + start_y, 19 + start_x, mem_pressure[2].content.value, attr)
            
        if mem_pressure[3].changed:
            style= mem_pressure[3].content.style
            attr= style_map[style]
            memory_dashboard.addstr(5 + start_y, 19 + start_x, mem_pressure[3].content.value, attr)
           
        if mem_pressure[4].changed:
            style= mem_pressure[4].content.style
            attr= style_map[style]
            memory_dashboard.addstr(6 + start_y, 19 + start_x, mem_pressure[4].content.value, attr)
            
        if mem_pressure[5].changed:
            style= mem_pressure[5].content.style
            attr= style_map[style]
            memory_dashboard.addstr(7 + start_y, 19 + start_x, mem_pressure[5].content.value, attr)
        
        #PSI health
        if mem_pressure[6].changed:
            style= mem_pressure[6].content.style
            attr= style_map[style]
            memory_dashboard.addstr(9 + start_y, 19 + start_x, mem_pressure[6].content.value, attr)
        
        #Health bar
        if mem_pressure[7].changed:
            style= mem_pressure[7].content.style
            attr= bar_style_map[style]
            width= min(24, mem_pressure[7].content.bar_width)
            memory_dashboard.hline(10 + start_y, 1 + start_x, " ", width, attr)
            memory_dashboard.hline(10 + start_y, 1 + start_x + width, " ", 23 - width) 

        memory_dashboard.noutrefresh()
