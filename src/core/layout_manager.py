

class DashCoordinates:
    __slots__ = (
        "start_y",
        "start_x",
        "max_y",
        "max_x",
        "sys_disabled"
    )

    def __init__ (self, start_y: int, start_x: int, max_y:int, max_x:int, is_disabled: bool):
        self.start_y = start_y
        self.start_x = start_x
        self.max_y = max_y
        self.max_x = max_x
        self.sys_disabled= is_disabled

    def update(self, start_y: int, start_x: int, max_y:int, max_x:int, is_disabled: bool):
        self.start_y = start_y
        self.start_x = start_x
        self.max_y = max_y
        self.max_x = max_x
        self.sys_disabled= is_disabled

class LayoutController:
    __slots__ = (
        "usr_dash_disabled",
        "top_dashboard_stack",
        "window_max_lines",
        "window_max_columns",
        "layout",
        "too_small"
    )

    def __init__ (self, stdscr):
        self.window_max_lines, self.window_max_columns = stdscr.getmaxyx()
        self.usr_dash_disabled= {
            "cpu": False,
            "cpu_load": False,
            "mem": False,
            "net": False,
            "nvidia": False,
            "process": False,
        }

        #initialize the layout. Dashboards are disabled
        self.layout = {
        key: DashCoordinates(0, 0, 0, 0, True)
        for key in self.usr_dash_disabled
        }
        
        self.too_small= False

    def initial_layout(self, dashboards: dict):

        #local references
        cpu_dash = dashboards["cpu"]
        cpu_load_dash = dashboards["cpu_load"]
        process_dash = dashboards["process"]
        net_dash = dashboards["net"]
        mem_dash = dashboards["mem"]
        nvidia_dash = dashboards["nvidia"]

        layout = self.layout

        window_max_lines = self. window_max_lines
        window_max_columns= self.window_max_columns

        #general limits
        dashboard_min_y = 3 #leaves space for the header
        dashboard_min_x = 16
        yspace_between_dashboards = 2
        xspace_between_dashboards = 1

        #for the static dashboards
        top_dashboards_max_y = 13 #all top dashboard have the same number of lines
        top_dash_min_width= 51

        dash_not_disabled = False
        dash_disabled= True


        if window_max_lines < dashboard_min_y or window_max_columns < dashboard_min_x:

            self.too_small= True
            
            #disable all dash
            cpu_dash.draw_static_interface(layout["cpu"])
            cpu_load_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))
            mem_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))
            net_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))
            nvidia_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))
            process_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))

            return

        elif window_max_lines < top_dashboards_max_y + dashboard_min_y:
            #disabled dash
            cpu_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))
            mem_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))
            net_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))
            nvidia_dash.draw_static_interface(DashCoordinates(0, 0, 0, 0, dash_disabled))

            #enabled dash
            cpu_load_dash.draw_static_interface(DashCoordinates(dashboard_min_y, 0, window_max_lines, window_max_columns, dash_not_disabled))
            process_dash.draw_static_interface(DashCoordinates(cpu_load_dash.last_line_y + yspace_between_dashboards, 0, window_max_lines, window_max_columns, dash_not_disabled))
            return
        
        else:
            #enabled dash
            cpu_dash.draw_static_interface(DashCoordinates(dashboard_min_y, 0, window_max_lines, top_dash_min_width, dash_not_disabled))
            cpu_load_dash.draw_static_interface(DashCoordinates(cpu_dash.last_line_y + yspace_between_dashboards, 0, window_max_lines, window_max_columns, dash_not_disabled))
            process_dash.draw_static_interface(DashCoordinates(cpu_load_dash.last_line_y + yspace_between_dashboards, 0, window_max_lines, window_max_columns, dash_not_disabled))

            #enabled if dash fits
            


