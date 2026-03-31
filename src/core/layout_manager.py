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
        "static_layout",
        "window_max_lines",
        "window_max_columns",
        "dynamic_layout",
        "too_small",
        "header_height",
        "nr_top_dash_visible",
        "top_dash_stack"
    )

    def __init__ (self, stdscr):
        self.window_max_lines, self.window_max_columns = stdscr.getmaxyx()

        self.nr_top_dash_visible = 0
        self.top_dash_stack = [
            "cpu",
            "mem",
            "net",
            "nvidia"
        ]

        self.usr_dash_disabled= {
            "cpu": False,
            "cpu_load": False,
            "mem": False,
            "net": False,
            "nvidia": False,
            "process": False,
        }

        #initialize the layout. Dashboards are disabled
        self.static_layout = {
            "cpu": DashCoordinates(0, 0, 0, 0, True),
            "mem": DashCoordinates(0, 0, 0, 0, True),
            "net": DashCoordinates(0, 0, 0, 0, True),
            "nvidia": DashCoordinates(0, 0, 0, 0, True)
        }
        self.dynamic_layout = {
        "cpu_load": DashCoordinates(0, 0, 0, 0, True),
        "process": DashCoordinates(0, 0, 0, 0, True)
        }
        
        self.too_small = False
        self.header_height = 4

    def place_global_btn(self, global_buttons: dict):

        global_buttons["dash_toggle"].update_button(0, 0, False, self.nr_top_dash_visible)

    def calculate_layout(self, dashboards: dict, buttons: dict, global_buttons: dict):
        self.nr_top_dash_visible = 0

        #local references
        usr_dash_disabled = self.usr_dash_disabled
        cpu_dash = dashboards["cpu"]
        cpu_load_dash = dashboards["cpu_load"]
        process_dash = dashboards["process"]
        net_dash = dashboards["net"]
        mem_dash = dashboards["mem"]
        nvidia_dash = dashboards["nvidia"]

        static_layout = self.static_layout
        dynamic_layout = self.dynamic_layout
        top_dash_stack = self.top_dash_stack

        window_max_lines = self. window_max_lines
        window_max_columns = self.window_max_columns

        #general limits
        dashboard_min_y = self.header_height #leaves space for the header
        dashboard_min_x = 16
        yspace_between_dashboards = 2

        #for the static dashboards
        top_dashboards_max_y = 11 + dashboard_min_y #all top dashboard have the same number of lines
        top_dash_width= 51

        #for dynamic dash
        dyn_dash_y_pos = self.header_height

        dash_not_disabled = False
        dash_disabled= True

        #Disable static dashboards. Will re-enable if screen is is large enough
        #Helps simplify the logic below and prevents me from re-writing this for the 2 if statements below
        for dash in top_dash_stack:
                static_layout[dash].update(0, 0, 0, 0, dash_disabled)

        #disables dinamic dash - same reasons as above
        for dash in dynamic_layout:
            dynamic_layout[dash].update(0, 0, 0, 0, dash_disabled)

        #pre-calculation the layout as disabled. Simplifies the if statements below
        cpu_load_dash.calculate_layout(dynamic_layout["cpu_load"])

        #disabled button - same reason as above
        for btn in buttons:
            buttons[btn].update_position(0, 0, dash_disabled)

        #window too small; disable all dashboards
        if window_max_lines < dashboard_min_y or window_max_columns < dashboard_min_x:
            self.too_small = True
            self.place_global_btn(global_buttons)
            return
        #small window; only cpu load dashboards can rander
        ##doesn't write over the header. Need at least 7 lines to write without errors
        if window_max_lines < top_dashboards_max_y + 1:
            if window_max_lines > dashboard_min_y + 2:
                dynamic_layout["cpu_load"].update(
                    dyn_dash_y_pos,
                    0,
                    window_max_lines, 
                    window_max_columns,
                    dash_not_disabled
                    )

            cpu_load_dash.calculate_layout(dynamic_layout["cpu_load"])
            self.place_global_btn(global_buttons)

            return
        
        #static dashboards
        x_pos = 0
        for dash in top_dash_stack:
            usr_disabled = usr_dash_disabled[dash]
            if x_pos < (window_max_columns - top_dash_width - 1) and usr_disabled is False:
                
                static_layout[dash].update(
                dashboard_min_y,
                x_pos,
                top_dashboards_max_y, #is static; doesn't need to know the nr line available 
                top_dash_width,
                usr_disabled,
                )
                #button is on the last line of the dashboard. Top dashboard are 10 lines and 51 columns
                buttons[dash].update_position(dashboard_min_y + 10, x_pos + 51 - buttons[dash].width - 2, usr_disabled)
                x_pos += top_dash_width #will move x_pos if should_render is True
                self.nr_top_dash_visible += 1

        self.place_global_btn(global_buttons)

        if x_pos > 0:
            dyn_dash_y_pos = top_dashboards_max_y
        else:
            dyn_dash_y_pos = dashboard_min_y
        #dynamic dashboards
        #cpu load 
        remaining_height = window_max_lines - (top_dashboards_max_y + yspace_between_dashboards)
        
        #need space for header + total load + 1 extra row
        if remaining_height > dashboard_min_y: 
            cpu_start_y_pos = dyn_dash_y_pos + yspace_between_dashboards
            if usr_dash_disabled["cpu_load"] is False:
                dynamic_layout["cpu_load"].update(
                    cpu_start_y_pos,
                    0,
                    window_max_lines,
                    window_max_columns,
                    dash_not_disabled
                )
                cpu_load_dash.calculate_layout(dynamic_layout["cpu_load"])
                process_start_y = cpu_load_dash.last_line_y + yspace_between_dashboards
                #goes around the dash title
                button_x_pos = window_max_columns - buttons["cpu_load"].width - 1
                if button_x_pos > 45: 
                    buttons["cpu_load"].update_position(cpu_start_y_pos, button_x_pos, dash_not_disabled)
                else:
                    buttons["cpu_load"].update_position(cpu_start_y_pos, 0, dash_not_disabled)
            else:
                process_start_y = cpu_start_y_pos

            #processes
            remaining_height = window_max_lines - process_start_y - 1 #need space for the header and 1 process to show
            if remaining_height > 1:
                if usr_dash_disabled["process"] is False:
                    dynamic_layout["process"].update(
                        process_start_y,
                        0,
                        remaining_height,
                        window_max_columns,
                        dash_not_disabled
                    )
                    button_x_pos = window_max_columns - buttons["process"].width - 1
                    buttons["process"].update_position(process_start_y - 1, button_x_pos, dash_not_disabled)

    def apply_layout(self, dashboards: dict, buttons: dict, global_buttons: dict, stdscr):
        static_layout = self.static_layout
        dynamic_layout = self.dynamic_layout

        for key in static_layout:
            coords = static_layout[key]
            dashboards[key].draw_static_interface(coords)

        for key in dynamic_layout:
            coords = dynamic_layout[key]
            dashboards[key].draw_static_interface(coords)

        for btn in buttons:
            buttons[btn].draw(stdscr)

        for btn in global_buttons:
            global_buttons[btn].draw(stdscr)

    def on_resize(self, stdscr, dashboards: dict, buttons: dict, global_buttons: dict):
        self.window_max_lines, self.window_max_columns = stdscr.getmaxyx()
        
        self.calculate_layout(dashboards, buttons, global_buttons)

        static_layout = self.static_layout
        dynamic_layout = self.dynamic_layout

        for key in static_layout:
            coords = static_layout[key]
            dashboards[key].resize(stdscr, coords)

        for key in dynamic_layout:
            coords = dynamic_layout[key]
            dashboards[key].resize(stdscr, coords)

        for btn in buttons:
            buttons[btn].draw(stdscr)

        for btn in global_buttons:
            global_buttons[btn].draw(stdscr)