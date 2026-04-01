import curses

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
            win.addstr(self.y + 1, self.x + 1, self.label, attr)
    
    def is_clicked(self, mouse_y, mouse_x):
        if self.disabled is False:
            return self.y <= mouse_y <= self.y + 1 and self.x <= mouse_x <= self.x + self.width - 1
        else:
            return False
    
class GlobalButton:
    __slots__=(
        "y",
        "x",
        "disabled",
        "width",
        "label",
        "button_style_map",
        "toggle_val",
        "toggle_str"
    )
    def __init__(self, label: str, button_style_map:tuple) -> object:
        self.label = label
        self.button_style_map = button_style_map
        self.disabled = True
        self.toggle_str = "None"
        self.width = len(label) + len(self.toggle_str) + 1  # padding

    def update_button(self, y: int, x:int, disabled: bool, toggle: int):
        self.y = y
        self.x = x
        self.disabled = disabled
        self.toggle_val = toggle

        if toggle == 0:
            self.toggle_str = "None" 
        elif toggle < 6:  #got 6 dsahboards in total
            self.toggle_str = "Some"
        else:
            self.toggle_str = "All " #padding manually

        self.width = len(self.label) + len(self.toggle_str) + 6  # padding. when rendering, extra characters are added

    def draw(self, win: curses.window):
        if self.disabled is False:
            y = self.y 
            x = self.x
            toggle = self.toggle_str
            attr_label = self.button_style_map[0] #blue
            if toggle == "None":
                attr_toggle = self.button_style_map[3]  #red
            elif toggle == "All":
                attr_toggle = self.button_style_map[1]  #green
            else:
                attr_toggle = self.button_style_map[2] #yellow

            # Draw label centered
            win.addstr(y + 1, x + 1, f"| {self.label} ", attr_label)
            win.addstr(f"{toggle} ", attr_toggle)
            win.addch("|", attr_label)
            win.hline(y + 2, x + 5, ".", self.toggle_val, attr_toggle)


    def is_clicked(self, mouse_y, mouse_x):
        return self.y <= mouse_y <= self.y + 1 and self.x <= mouse_x <= self.x + self.width - 1
