import curses

text_map= (
            curses.color_pair(1), #green text, black background
            curses.color_pair(2), #yellow text
            curses.color_pair(3), #red text
            curses.A_DIM,
            curses.color_pair(4), #white text
            curses.color_pair(5), #blue text
        )
bar_map= (
            curses.color_pair(1) | curses.A_REVERSE,
            curses.color_pair(2) | curses.A_REVERSE,
            curses.color_pair(3) | curses.A_REVERSE,
            curses.A_DIM,
            curses.color_pair(6) , #white text, green background
        )

button_map= (
    curses.color_pair(5), #blue text, for the label
    curses.color_pair(1), #green text , for the toggle
    curses.color_pair(2), #yellow text, for the toggle
    curses.color_pair(3), #red text, for the toggle
)