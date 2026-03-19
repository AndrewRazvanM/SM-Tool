import curses

text_map= (
            curses.color_pair(1),
            curses.color_pair(2),
            curses.color_pair(3),
            curses.A_DIM,
            curses.color_pair(4),
            curses.color_pair(5),
        )
bar_map= (
            curses.color_pair(1) | curses.A_REVERSE,
            curses.color_pair(2) | curses.A_REVERSE,
            curses.color_pair(3) | curses.A_REVERSE,
            curses.A_DIM,
        )