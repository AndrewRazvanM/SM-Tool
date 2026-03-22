import curses

class NetworkDashboard:
        __slots__= (
        "network_dashboard",
        "start_y",
        "start_x",
        "style_map",
        "bar_style_map",
        "__network_object_diff",
        "__dashboard_disabled",
        )

        def __init__(self, stdscr: curses.window, content_diff_engine: object) -> object:
            self.network_dashboard= stdscr

            self.start_y= 3
            self.start_x= 50 + 48 + 1 #the other dashboard positions
 
            window_max_lines, window_max_columns= stdscr.getmaxyx()

            if window_max_lines > 13 + self.start_y and window_max_columns > 51 + self.start_x:
                self.__dashboard_disabled= False
            else:
                self.__dashboard_disabled= True

            self.__network_object_diff= content_diff_engine()

        def resize(self, stdscr: curses.window):
            self.network_dashboard= stdscr
            window_max_lines, window_max_columns= stdscr.getmaxyx()

            if window_max_lines >= 13 + self.start_y and window_max_columns >= 51 + self.start_x:
                self.__dashboard_disabled= False
                self.draw_static_interface()
                self.__network_object_diff.force_write= True

            else:
                self.__dashboard_disabled= True

        def assing_style(self):
            from .style_maps import text_map, bar_map

            self.style_map= text_map
            self.bar_style_map= bar_map

        def check_content_diff(self, formatted_network_readings: list) -> list:
            self.__network_object_diff.check_differences(formatted_network_readings)

        def draw_static_interface(self):
            if self.__dashboard_disabled:
                return
            
            network_dashboard= self.network_dashboard

            #starting position
            start_y= self.start_y 
            start_x= self.start_x

            #build the borders
            # Draw corners first
            network_dashboard.addch(start_y, start_x, curses.ACS_ULCORNER)
            network_dashboard.addch(start_y, start_x+ 50, curses.ACS_URCORNER)
            network_dashboard.addch(start_y+ 11, start_x, curses.ACS_LLCORNER)
            network_dashboard.addch(start_y+ 11, start_x+ 50, curses.ACS_LRCORNER)

            # Draw horizontal edges (width-1)
            network_dashboard.hline(start_y, start_x+1, curses.ACS_HLINE, 49)
            network_dashboard.hline(start_y+ 11, start_x+1, curses.ACS_HLINE, 49)

            # Draw vertical edges (height-1)
            network_dashboard.vline(start_y+1, start_x, curses.ACS_VLINE, 10)
            network_dashboard.vline(start_y+1, start_x+ 50, curses.ACS_VLINE, 10)
            #add title
            network_dashboard.addstr(start_y+ 0, start_x+ 15, "Network Dashboard", curses.A_BOLD)

            network_dashboard.addstr(0 + start_y, 15 + start_x, "Network Dashboard", curses.A_BOLD)
            network_dashboard.addstr(1 + start_y, 1 + start_x, "  Upload:")
            network_dashboard.addstr(2 + start_y, 1 + start_x, "Up dropp:")
            network_dashboard.addstr(1 + start_y, 28 + start_x, "Download:")
            network_dashboard.addstr(2 + start_y, 28 + start_x, "Dw dropp:")
            network_dashboard.vline(1 + start_y, 26 + start_x, "|", 2)
            network_dashboard.hline(3 + start_y, 1 + start_x, "-", 49)
            network_dashboard.addstr(3 + start_y, 10 + start_x, "Total")
            network_dashboard.addch(curses.ACS_UARROW)
            network_dashboard.addstr(" - Individual")
            network_dashboard.addch(curses.ACS_DARROW)
            network_dashboard.addstr(4 + start_y, 1 + start_x, "Interfaces:")

            network_dashboard.noutrefresh()

        def render(self):

            if self.__dashboard_disabled:
                return
        
            network_dashboard= self.network_dashboard

            content_list= self.__network_object_diff.is_content_diff

            start_y= self.start_y 
            start_x= self.start_x

            style_map= self.style_map

            interface_index= 0

            for list_index in range(4, len(content_list)):
                if content_list[list_index].changed:
                    style= content_list[list_index].content.style
                    attr= style_map[style]
                    network_dashboard.addstr(5 + start_y + interface_index, 1+ start_x, content_list[list_index].content.value, attr)
                    interface_index+= 1

            if content_list[0].changed:
                style= content_list[0].content.style
                attr= style_map[style]
                network_dashboard.addstr(1 + start_y, 10 + start_x, content_list[0].content.value, attr)

            if content_list[1].changed:
                style= content_list[1].content.style
                attr= style_map[style]
                network_dashboard.addstr(2 + start_y, 10 + start_x, content_list[1].content.value, attr)

            if content_list[2].changed:
                style= content_list[2].content.style
                attr= style_map[style]
                network_dashboard.addstr(1 + start_y, 37 + start_x, content_list[2].content.value, attr)

            if content_list[3].changed:
                style= content_list[3].content.style
                attr= style_map[style]
                network_dashboard.addstr(2 + start_y, 37 + start_x, content_list[3].content.value, attr)

            network_dashboard.noutrefresh()

            

            