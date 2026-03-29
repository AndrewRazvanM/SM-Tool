
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

    def calculate_layout(self, dashboards: dict):

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

        #for the static dashboards
        top_dashboards_max_y = 13 #all top dashboard have the same number of lines
        top_dash_min_width= 51

        dash_not_disabled = False
        dash_disabled= True

        #window too small
        if window_max_lines < dashboard_min_y or window_max_columns < dashboard_min_x:
            self.too_small = True

            for key in layout:
                layout[key].update(0, 0, 0, 0, dash_disabled)

            return
        #small window; only 2 dashboards are available
        if window_max_lines < top_dashboards_max_y:

            layout["cpu"].update(0, 0, 0, 0, dash_disabled)
            layout["mem"].update(0, 0, 0, 0, dash_disabled)
            layout["net"].update(0, 0, 0, 0, dash_disabled)
            layout["nvidia"].update(0, 0, 0, 0, dash_disabled)

            layout["cpu_load"].update(
                dashboard_min_y,
                0,
                window_max_lines,
                window_max_columns,
                dash_not_disabled
            )

            cpu_load_dash.calculate_layout(layout["cpu_load"])
            cpu_load_last = cpu_load_dash.last_line_y

            remaining_height = max(0, window_max_lines - (cpu_load_last + yspace_between_dashboards))
            layout["process"].update(
                cpu_load_last + yspace_between_dashboards,
                0,
                remaining_height,
                window_max_columns,
                dash_not_disabled
            )

            return

        #static top dashboards        
        layout["cpu"].update(
        dashboard_min_y,
        0,
        window_max_lines,
        top_dash_min_width,
        False
        )

        mem_x_pos= top_dash_min_width
        if window_max_columns > mem_x_pos + top_dash_min_width:
            layout["mem"].update(
            dashboard_min_y,
            top_dash_min_width,
            window_max_lines,
            top_dash_min_width,
            dash_not_disabled
            )
        else:
            layout["mem"].update(0, 0, 0, 0, dash_disabled)

        net_x_pos= (top_dash_min_width * 2)
        if window_max_columns > net_x_pos + top_dash_min_width:
            layout["net"].update(
            dashboard_min_y,
            net_x_pos,
            window_max_lines,
            top_dash_min_width,
            dash_not_disabled
            )
        else:
            layout["net"].update(0, 0, 0, 0, dash_disabled)
        
        nvidia_x_pos= (top_dash_min_width * 3)
        if window_max_columns > nvidia_x_pos + top_dash_min_width:
            layout["nvidia"].update(
            dashboard_min_y,
            nvidia_x_pos,
            window_max_lines,
            top_dash_min_width,
            dash_not_disabled
            )
        else:
            layout["nvidia"].update(0, 0, 0, 0, dash_disabled)

        #dynamic dashboards
        layout["cpu_load"].update(
            top_dashboards_max_y + yspace_between_dashboards,
            0,
            window_max_lines,
            window_max_columns,
            dash_not_disabled
        )

        cpu_load_dash.calculate_layout(layout["cpu_load"])
        cpu_load_last = cpu_load_dash.last_line_y
        
        remaining_height = max(0, window_max_lines - (cpu_load_last + yspace_between_dashboards + 1))
        layout["process"].update(
            cpu_load_last + yspace_between_dashboards,
            0,
            remaining_height,
            window_max_columns,
            dash_not_disabled
        )

    def apply_layout(self, dashboards: dict):
        layout= self.layout

        for key, dash in dashboards.items():
            coords = layout[key]
            dash.draw_static_interface(coords)

    def on_resize(self, stdscr, dashboards: dict):
        self.window_max_lines, self.window_max_columns = stdscr.getmaxyx()
        layout= self.layout
        self.calculate_layout(dashboards)

        for key, dash in dashboards.items():
            coords = layout[key]
            dash.resize(stdscr, coords)