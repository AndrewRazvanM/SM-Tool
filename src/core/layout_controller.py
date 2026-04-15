# ---------------------------------------------------------------------------
# Layout constants
# Change these values to adjust the overall TUI structure.
# Keeping them here (rather than scattered as magic numbers inside methods)
# means there is exactly one place to update them.
# ---------------------------------------------------------------------------
_HEADER_HEIGHT  = 4   # rows reserved for the top header bar
_TOP_DASH_HEIGHT = 11  # content rows in each top-row dashboard
_TOP_DASH_WIDTH  = 51  # column width of each top-row dashboard
_DASH_GAP        = 2   # blank rows inserted between dashboard sections
_MIN_WIN_X       = 16  # window must be at least this wide for anything to render

# Derived constant: the y-coordinate where the top row ends.
# Computed once at import time, so no per-call arithmetic.
_TOP_ROW_BOTTOM = _HEADER_HEIGHT + _TOP_DASH_HEIGHT   # = 15


class DashCoordinates:
    """
    Stores the position and size of one dashboard panel.
    """
    __slots__ = ("start_y", "start_x", "max_y", "max_x", "sys_disabled")

    def __init__(self, start_y: int, start_x: int,
                 max_y: int, max_x: int, is_disabled: bool):
        self.start_y     = start_y
        self.start_x     = start_x
        self.max_y       = max_y
        self.max_x       = max_x
        self.sys_disabled = is_disabled

    def update(self, start_y: int, start_x: int,
               max_y: int, max_x: int, is_disabled: bool):
        """Mutate in-place rather than allocating a new object."""
        self.start_y     = start_y
        self.start_x     = start_x
        self.max_y       = max_y
        self.max_x       = max_x
        self.sys_disabled = is_disabled


class LayoutController:
    """
    Computes where every dashboard and button should be placed given the
    current terminal size and per-dashboard user preferences.

    Responsibilities
    ----------------
    - calculate_layout : work out positions (no drawing).
    - apply_layout     : draw everything from scratch (startup).
    - on_resize        : recalculate then redraw after a KEY_RESIZE event.

    The layout is split into two sections:
      static_layout  — top-row dashboards, placed left to right.
      dynamic_layout — vertical dashboards (cpu_load, process) placed below.
    """
    __slots__ = (
        "usr_dash_disabled",
        "static_layout",
        "window_max_lines",
        "window_max_columns",
        "dynamic_layout",
        "too_small",
        "nr_dash_visible",
        "top_dash_stack",
    )

    def __init__(self, stdscr):
        self.window_max_lines, self.window_max_columns = stdscr.getmaxyx()
        self.nr_dash_visible = 0
        self.too_small       = False

        # Defines the left-to-right render order of the top-row dashboards.
        self.top_dash_stack = ["cpu", "mem", "net", "nvidia", "io_tot"]
        
        # Per-dashboard user toggle.  False = shown, True = hidden by the user.
        self.usr_dash_disabled = {
            "cpu": False, "cpu_load": False, "mem": False,
            "net": False, "nvidia": False, "process": False,
            "io_tot": False,
        }

        # Computed positions — start fully disabled; calculate_layout fills them in.
        self.static_layout = {
            key: DashCoordinates(0, 0, 0, 0, True)
            for key in self.top_dash_stack
        }
        self.dynamic_layout = {
            "cpu_load": DashCoordinates(0, 0, 0, 0, True),
            "process":  DashCoordinates(0, 0, 0, 0, True),
        }

    # ------------------------------------------------------------------
    # Private helpers — each does exactly one thing
    # ------------------------------------------------------------------

    def _reset_all(self, buttons: dict):
        """
        Set every layout entry and button to its disabled/zero state.

        Called at the start of calculate_layout so we can unconditionally
        re-enable only what fits, rather than having to track what was
        previously enabled and manually undo it.
        """
        for coords in self.static_layout.values():
            coords.update(0, 0, 0, 0, True)
        for coords in self.dynamic_layout.values():
            coords.update(0, 0, 0, 0, True)
        for btn in buttons.values():
            btn.update_position(0, 0, True)

    def _place_top_row(self, buttons: dict) -> int:
        """
        Place top-row dashboards left to right until we run out of columns.

        Returns the x position we stopped at.  A return value of 0 means
        no dashboards were placed (either all user-disabled or no room). It
        also track if at least 1 dashboards is enabled.
        """
        x = 0
        for key in self.top_dash_stack:
            if self.usr_dash_disabled[key]:
                continue
            if x >= self.window_max_columns - _TOP_DASH_WIDTH - 1:
                break   # no room for another dashboard

            self.static_layout[key].update(
                _HEADER_HEIGHT, x, _TOP_ROW_BOTTOM, _TOP_DASH_WIDTH, False
            )
            # Place the toggle button on the last row of this dashboard,
            # aligned to its right edge.
            btn = buttons[key]
            btn.update_position(
                _HEADER_HEIGHT + 11,
                x + _TOP_DASH_WIDTH - btn.width - 2,
                False,
            )
            x += _TOP_DASH_WIDTH
            self.nr_dash_visible += 1

        return x

    def _place_cpu_load(self, dashboards: dict, buttons: dict, start_y: int) -> int:
        """
        Place the cpu_load dashboard (unless the user has hidden it) and its
        toggle button.

        Returns the y position where the process dashboard should start.
        When cpu_load is hidden, process still starts at the same y that
        cpu_load would have occupied, leaving no wasted gap.
        """
        cpu_load_dash = dashboards["cpu_load"]
        coords = self.dynamic_layout["cpu_load"]

        if not self.usr_dash_disabled["cpu_load"]:
            coords.update(start_y, 0, self.window_max_lines, self.window_max_columns, False)
            self.nr_dash_visible += 1

            # cpu_load calculates its own height based on thread count + space,
            # so we must ask it before we can know where process starts.
            cpu_load_dash.calculate_layout(coords)
            process_start_y = cpu_load_dash.last_line_y + _DASH_GAP

            # The dashboard title occupies roughly the first 45 columns, so
            # move the button to the right if there is space, else pin left.
            btn_x = self.window_max_columns - buttons["cpu_load"].width - 1
            buttons["cpu_load"].update_position(
                start_y + 1, btn_x if btn_x > 45 else 0, False
            )
        else:
            # Hidden by the user: process starts where cpu_load would have.
            process_start_y = start_y

        return process_start_y

    def _place_process(self, buttons: dict, process_start_y: int):
        """Place the process dashboard if there is enough vertical space."""
        remaining = self.window_max_lines - process_start_y - 1
        if remaining > 1 and not self.usr_dash_disabled["process"]:
            self.dynamic_layout["process"].update(
                process_start_y, 0, remaining, self.window_max_columns, False
            )
            self.nr_dash_visible += 1
            btn_x = self.window_max_columns - buttons["process"].width - 1
            # Button sits on the row just above the dashboard (the gap row).
            buttons["process"].update_position(process_start_y, btn_x, False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_layout(self, dashboards: dict, buttons: dict, global_buttons: dict):
        """
        Compute where every dashboard and button should go.  No drawing happens
        here — call apply_layout or on_resize to push the result to the screen.

        Three layout tiers are checked in order:

          Tier 1 — window too small
              Nothing can render safely.

          Tier 2 — not tall enough for the top row
              Only cpu_load is shown (if there are enough rows for it).

          Tier 3 — full layout
              Top-row dashboards fill columns left to right.
              cpu_load and process stack vertically below them.
        """
        self.nr_dash_visible = 0
        self._reset_all(buttons)

        # Pre-calculate cpu_load with disabled coordinates.  The dashboard
        # object needs this to be in a valid state even before it is shown.
        dashboards["cpu_load"].calculate_layout(self.dynamic_layout["cpu_load"])

        # --- Tier 1: window too small for anything ---
        if self.window_max_lines < _HEADER_HEIGHT or self.window_max_columns < _MIN_WIN_X:
            self.too_small = True
            global_buttons["dash_toggle"].update_position(2, 0, False, self.nr_dash_visible)
            global_buttons["settings"].update_position(1, 0, False)
            return

        self.too_small = False

        # --- Tier 2: not tall enough for the top-row dashboards ---
        if self.window_max_lines < _TOP_ROW_BOTTOM + 1:
            # Show cpu_load only if there are enough rows (header + at least 3 content rows)
            if self.window_max_lines > _HEADER_HEIGHT + 2:
                self._place_cpu_load(dashboards, buttons, _HEADER_HEIGHT)
            dashboards["cpu_load"].calculate_layout(self.dynamic_layout["cpu_load"])
            global_buttons["dash_toggle"].update_position(2, 0, False, self.nr_dash_visible)
            global_buttons["settings"].update_position(1, 0, False)
            return

        # --- Tier 3: full layout ---
        top_row_x_end = self._place_top_row(buttons)

        # If the top row is empty (all user-disabled or too narrow), the
        # dynamic section starts directly below the header instead of the
        # top row, so we don't leave a blank region.
        dyn_start_y = _TOP_ROW_BOTTOM if top_row_x_end > 0 else _HEADER_HEIGHT

        # Only add the dynamic section if there is meaningful vertical space.
        # The threshold is always relative to _TOP_ROW_BOTTOM (not dyn_start_y)
        # to match the original: a very wide-but-short window where all top
        # dashboards are user-disabled still needs the same minimum height.
        if self.window_max_lines - (_TOP_ROW_BOTTOM + _DASH_GAP) > _HEADER_HEIGHT:
            cpu_load_start_y = dyn_start_y + _DASH_GAP
            process_start_y  = self._place_cpu_load(dashboards, buttons, cpu_load_start_y)
            self._place_process(buttons, process_start_y)

        global_buttons["dash_toggle"].update_position(2, 0, False, self.nr_dash_visible)
        global_buttons["settings"].update_position(0, 0, False)

    def apply_layout(self, dashboards: dict, buttons: dict, global_buttons: dict, stdscr):
        """
        Draw the static chrome (borders, labels) of every dashboard and all
        buttons.  Call this once on startup after calculate_layout.
        """
        for key, coords in self.static_layout.items():
            dashboards[key].draw_static_interface(coords)
        for key, coords in self.dynamic_layout.items():
            dashboards[key].draw_static_interface(coords)
        for btn in buttons.values():
            btn.draw(stdscr)
        for btn in global_buttons.values():
            btn.draw(stdscr)

    def on_resize(self, stdscr, dashboards: dict, buttons: dict, global_buttons: dict):
        """
        Handle a KEY_RESIZE event: recalculate positions then redraw everything.
        """
        self.window_max_lines, self.window_max_columns = stdscr.getmaxyx()
        self.calculate_layout(dashboards, buttons, global_buttons)

        for key, coords in self.static_layout.items():
            dashboards[key].resize(stdscr, coords)
        for key, coords in self.dynamic_layout.items():
            dashboards[key].resize(stdscr, coords)
        for btn in buttons.values():
            btn.draw(stdscr)
        for btn in global_buttons.values():
            btn.draw(stdscr)
