import curses

#Button constans
_TOT_NR_DASHBOARDS = 7 #used by the EnableDashButton. It's the total number of dashboards

class Button:
    __slots__=(
        "y",
        "x",
        "disabled",
        "width",
        "label",
        "button_style_map"
    )
    def __init__(self, label: str, button_style_map:tuple) -> object:
        self.label = label
        self.width = len(label) + 1  # padding
        self.button_style_map = button_style_map
        self.disabled = True

    def update_position(self, y: int, x:int, disabled: bool):
        self.y = y
        self.x = x
        self.disabled = disabled

    def draw(self, win):
        if self.disabled is False:
            attr = self.button_style_map[0]

            # Draw label centered
            win.addstr(self.y, self.x + 1, self.label, attr)
    
    def is_clicked(self, mouse_y, mouse_x):
        if self.disabled is False:
            return self.y <= mouse_y <= self.y + 1 and self.x <= mouse_x <= self.x + self.width - 1
        else:
            return False
    
class EnableDashButton:
    __slots__=(
        "y",
        "x",
        "disabled",
        "width",
        "label",
        "button_style_map",
        "toggle_val",
        "attr_toggle"
    )
    def __init__(self, label: str, button_style_map:tuple) -> object:
        self.label = label
        self.button_style_map = button_style_map
        self.disabled = True
        self.width = len(label) + 7  # padding

    def update_position(self, y: int, x:int, disabled: bool, toggle: int):
        self.y = y
        self.x = x
        self.disabled = disabled
        self.toggle_val = toggle

        if toggle == 0:
            self.attr_toggle = self.button_style_map[3]  #red
        elif toggle < _TOT_NR_DASHBOARDS: 
            self.attr_toggle = self.button_style_map[2] #yellow
        else:
            self.attr_toggle = self.button_style_map[1]  #green

        self.width = len(self.label) + 7  # in draw() 6 extra characters are added + 1 for the nr. of dashboards

    def draw(self, win: curses.window):
        if self.disabled is False:
            y = self.y 
            x = self.x

            attr_label = self.button_style_map[0] #blue

            # Draw label centered
            win.addstr(y, x , f"| {self.label} ", attr_label)
            win.addstr(f"{self.toggle_val} ", self.attr_toggle)
            win.addch("|", attr_label)
            #Visually shows how many dashboards are showing vs the maximum number
            win.hline(y + 1, x + 5, ".", self.toggle_val, self.attr_toggle)
            win.hline(y + 1, x + 5 + self.toggle_val, ".", _TOT_NR_DASHBOARDS - self.toggle_val, self.button_style_map[3])


    def is_clicked(self, mouse_y, mouse_x):
        return self.y <= mouse_y <= self.y + 1 and self.x <= mouse_x <= self.x + self.width - 1