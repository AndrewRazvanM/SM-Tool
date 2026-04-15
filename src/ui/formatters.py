"""
formatters.py
-------------
Converts raw readings into TextStyle objects consumed by the UI dashboards.

Every formatter follows this contract:
  - __init__   : pre-allocate self.formatted_* with placeholder TextStyle objects
  - format/format_* : update those objects in-place; return nothing
  - Never allocate new lists during format() — only mutate existing slots

TextStyle fields:
  value     : string drawn to the terminal
  style     : index into text_map / bar_map (0=green, 1=yellow, 2=red, 3=dim, 4=white, 5=blue)
  bar_width : pixel-width of progress bar (0 when not a bar entry)

Helper functions:
  time_formatter  : seconds → "HH:MM:SS"
  classify        : maps a numeric value to a style index via threshold tuple
  scale_formatter : scales a raw number to a human-readable magnitude string
"""

from core.formatter_thresholds import (
    CPU_AVG10_THRESHOLDS,
    CPU_AVG60_THRESHOLDS,
    CPU_AVG300_THRESHOLDS,
    MEM_IO_SOME_AVG10_60_THRESHOLDS,
    MEM_IO_SOME_AVG300_THRESHOLDS,
    MEM_IO_FULL_AVG10_60_THRESHOLDS,
    MEM_IO_FULL_AVG300_THRESHOLDS,
    IO_PRESSURE_THRESHOLDS,
    PRESSURE_HEALTH_THRESHOLDS,
    CPU_TEMP_THRESHOLDS,
    GPU_TEMP_THRESHOLDS,
    GPU_LOAD_THRESHOLDS,
    BINARY_UNITS_SCALES,
    DECIMAL_UNITS_SCALES,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def time_formatter(seconds: float) -> str:
    """Convert a float number of seconds to a "HH:MM:SS " string."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02}:{m:02}:{s:02} "


def classify(value, thresholds: tuple) -> int:
    """
    Map *value* to a style index using *thresholds*.

    Each entry in thresholds is (upper_limit, style_index).
    Returns the style_index of the first entry whose upper_limit > value.
    Returns 3 (dim/muted) when value is "N/A".
    """
    if value == "N/A":
        return 3
    for limit, style in thresholds:
        if value < limit:
            return style


def scale_formatter(value, scale: tuple) -> str:
    """
    Format *value* to a human-readable magnitude string using *scale*.

    scale is a tuple of (factor, suffix) pairs ordered largest-first.
    The factor and value must share the same unit (e.g. both bytes).
    """
    for factor, suffix in scale:
        if value >= factor:
            if factor == 1:
                return f"{value:.0f} {suffix}"
            return f"{value / factor:.1f} {suffix}"


# ---------------------------------------------------------------------------
# Base data object
# ---------------------------------------------------------------------------

class TextStyle:
    """One drawable cell: a string value, a colour style, and an optional bar width."""
    __slots__ = ("value", "style", "bar_width")

    def __init__(self, text: str, style: int, bar_width: int = 0):
        self.value = text
        self.style = style
        self.bar_width = bar_width


# ---------------------------------------------------------------------------
# CPU pressure formatter
# ---------------------------------------------------------------------------

class CPUPressureFormatter:
    """
    Formats CPU PSI (pressure-stall information) readings.

    Output slots (5 total):
      [0] avg10  text + style
      [1] avg60  text + style
      [2] avg300 text + style
      [3] health score text + style
      [4] health bar  (bar_width + style only, value unused)
    """
    __slots__ = ("formatted_output",)

    # Max characters for each pressure value string
    _VALUE_WIDTH = 5
    # Bar spans 23 columns; health score 0-100 maps linearly
    _BAR_MAX = 23

    def __init__(self):
        self.formatted_output = [TextStyle("N/A", 3) for _ in range(5)]

    def format(self, readings: object, schedule: dict):
        """Update formatted_output from a CPUPressure readings object."""
        if not schedule["cpu"]:
            return

        out = self.formatted_output
        w = self._VALUE_WIDTH

        avg10  = readings.cpu_avg10
        avg60  = readings.cpu_avg60
        avg300 = readings.cpu_avg300

        # --- Classify each average ---
        out[0].value = f"{avg10:<{w}}"
        out[0].style = classify(avg10, CPU_AVG10_THRESHOLDS)

        out[1].value = f"{avg60:<{w}}"
        out[1].style = classify(avg60, CPU_AVG60_THRESHOLDS)

        out[2].value = f"{avg300:<{w}}"
        out[2].style = classify(avg300, CPU_AVG300_THRESHOLDS)

        # --- Compute and classify health score ---
        if avg10 == "N/A":
            health        = "N/A"
            bar_width     = 0
            health_style  = 3
        else:
            # Higher penalty = worse health; penalise longer windows more
            penalty = avg10 * 2.0 + avg60 * 6.0 + avg300 * 50.0
            health  = max(0.0, 100.0 - penalty)

            bar_width    = max(1, min(self._BAR_MAX, int(health // 4.3)))
            health_style = classify(health, PRESSURE_HEALTH_THRESHOLDS)

        out[3].value = f"{health:<{w}.1f}" if health != "N/A" else "N/A"
        out[3].style = health_style

        out[4].bar_width = bar_width
        out[4].style     = health_style


# ---------------------------------------------------------------------------
# Memory pressure formatter
# ---------------------------------------------------------------------------

class MemoryPressureFormatter:
    """
    Formats memory PSI readings.

    Output slots (8 total):
      [0] some avg10  text + style
      [1] some avg60  text + style
      [2] some avg300 text + style
      [3] full avg10  text + style
      [4] full avg60  text + style
      [5] full avg300 text + style
      [6] health score text + style
      [7] health bar  (bar_width + style only)
    """
    __slots__ = ("formatted_output",)

    _VALUE_WIDTH = 5
    _BAR_MAX     = 30   # columns available for the health bar

    def __init__(self):
        self.formatted_output = [TextStyle("N/A", 3) for _ in range(8)]

    def format_mem(self, readings: object, schedule: dict):
        """Update formatted_output from a MemPressure readings object."""
        if not schedule["memory"]:
            return

        out = self.formatted_output
        w   = self._VALUE_WIDTH

        s10, s60, s300 = readings.memory_some
        f10, f60, f300 = readings.memory_full

        # --- Classify "some" averages ---
        out[0].value, out[0].style = f"{s10:<{w}}", classify(s10,  MEM_IO_SOME_AVG10_60_THRESHOLDS)
        out[1].value, out[1].style = f"{s60:<{w}}", classify(s60,  MEM_IO_SOME_AVG10_60_THRESHOLDS)
        out[2].value, out[2].style = f"{s300:<{w}}", classify(s300, MEM_IO_SOME_AVG300_THRESHOLDS)

        # --- Classify "full" averages ---
        out[3].value, out[3].style = f"{f10:<{w}}", classify(f10,  MEM_IO_FULL_AVG10_60_THRESHOLDS)
        out[4].value, out[4].style = f"{f60:<{w}}", classify(f60,  MEM_IO_FULL_AVG10_60_THRESHOLDS)
        out[5].value, out[5].style = f"{f300:<{w}}", classify(f300, MEM_IO_FULL_AVG300_THRESHOLDS)

        # --- Health score ---
        if s10 == "N/A":
            health       = "N/A"
            bar_width    = 0
            health_style = 3
        else:
            # "full" events penalised much more heavily than "some"
            penalty = (
                s10  * 1.0  + s60  * 2.0  + s300 * 3.0 +
                f10  * 20.0 + f60  * 40.0 + f300 * 60.0
            )
            health       = max(0.0, 100.0 - penalty)
            bar_width    = min(self._BAR_MAX, int(health / 3.2))
            health_style = 0 if health > 80 else 1 if health > 60 else 2

        out[6].value = f"{health:.1f}" if health != "N/A" else "N/A"
        out[6].style = health_style

        out[7].bar_width = bar_width
        out[7].style     = health_style


# ---------------------------------------------------------------------------
# Memory info formatter
# ---------------------------------------------------------------------------

class MemoryFormatter:
    """
    Formats raw /proc/meminfo values (in kB) to human-readable strings.

    Output slots (4 total):
      [0] MemTotal    text + style
      [1] MemAvailable text + style
      [2] SwapTotal   text + style
      [3] SwapFree    text + style
    """
    __slots__ = ("formatted_output",)

    # Thresholds for memory size classification (in kB)
    # Below 1 MB = critical, below 1 GB = warning, else good
    _KB_WARNING  = 1_000       # 1 MB boundary
    _KB_GOOD     = 1_000_000  # 1 GB boundary

    # Max display characters for each value
    _VALUE_WIDTH = 6

    def __init__(self):
        self.formatted_output = [TextStyle("N/A", 3) for _ in range(4)]

    def _fmt_kb(self, kb: int) -> tuple[str, int]:
        """Convert a kB integer to a (display_string, style) pair."""
        if kb < self._KB_WARNING:
            return f"{kb} kB",        2   # critical — very small
        if kb < self._KB_GOOD:
            return f"{kb // 1000} MB", 1   # warning
        return f"{kb // 1_000_000} GB", 0  # good

    def format(self, readings: object, schedule: dict):
        """Update formatted_output from a MemoryInfo readings object."""
        if not schedule["memory"]:
            return

        out = self.formatted_output
        w   = self._VALUE_WIDTH

        fields = [
            readings.MemTotal,
            readings.MemAvailable,
            readings.SwapTotal,
            readings.SwapFree,
        ]

        for idx, kb_value in enumerate(fields):
            text, style       = self._fmt_kb(kb_value)
            out[idx].value    = text[:w]
            out[idx].style    = style


# ---------------------------------------------------------------------------
# CPU temperature formatter
# ---------------------------------------------------------------------------

class CPUTempFormatter:
    """
    Formats CPU sensor temperature readings.

    Output slots (6 total):
      [0] die temp text ("Package id 0") + style
      [1] die temp bar (bar_width + style)
      [2] average temp text + style
      [3] average temp bar (bar_width + style)
      [4] core count text + style
      [5] thread count text + style
    """
    __slots__ = ("formatted_cpu_readings",)

    # Bar column widths for die and average
    _DIE_BAR_MAX = 24
    _AVG_BAR_MAX = 23

    def __init__(self):
        self.formatted_cpu_readings = [
            TextStyle("N/A", 3),
            TextStyle(" ",   3, 1),
            TextStyle("N/A", 3),
            TextStyle(" ",   3, 1),
            TextStyle("N/A", 3),
            TextStyle("N/A", 3),
        ]

    def format_info(self, readings: object, schedule: dict):
        """Update formatted_cpu_readings from a CPUInfoTemp readings object."""
        if not schedule.get("cpu", True):
            return

        cpu_temp = readings.cpu_temp
        if cpu_temp is None:
            return

        out = self.formatted_cpu_readings

        # Total entries minus the two computed keys (Package id 0, Average)
        core_count = len(cpu_temp)

        # --- Die temperature ("Package id 0") ---
        if "Package id 0" in cpu_temp:
            core_count -= 1
            die_val   = cpu_temp["Package id 0"].temp
            die_text  = f"{die_val:>3} °C"
            die_style = classify(die_val, CPU_TEMP_THRESHOLDS)
            die_bar   = min(self._DIE_BAR_MAX, die_val // 4)
        else:
            die_text  = "N/A   "
            die_style = 3
            die_bar   = 0

        out[0].value    = die_text
        out[0].style    = die_style
        out[1].bar_width = die_bar
        out[1].style    = die_style

        # --- Average temperature ---
        if "Average" in cpu_temp:
            core_count -= 1
            avg_val   = cpu_temp["Average"]
            avg_text  = f"{avg_val:>3} °C"
            avg_style = classify(avg_val, CPU_TEMP_THRESHOLDS)
            avg_bar   = min(self._AVG_BAR_MAX, avg_val // 4)
        else:
            avg_text  = "N/A   "
            avg_style = 3
            avg_bar   = 0

        out[2].value    = avg_text
        out[2].style    = avg_style
        out[3].bar_width = avg_bar
        out[3].style    = avg_style

        # --- Core / thread counts (style 0 = always green) ---
        out[4].value = f" {core_count:<4}"
        out[4].style = 0
        out[5].value = f" {core_count * 2:<4}"
        out[5].style = 0


# ---------------------------------------------------------------------------
# CPU load formatter
# ---------------------------------------------------------------------------

class CPULoadFormatter:
    """
    Formats per-core CPU usage percentages as bar+text entries.

    Output slots: one TextStyle per CPU entry (Total + per-core).
      value     : "CPU_label: XX.X %______" truncated to bar width
      bar_width : filled portion of the bar
      style     : always 0 (green); bar colour conveys no severity here
    """
    __slots__ = ("formatted_cpu_load",)

    def __init__(self):
        self.formatted_cpu_load = []

    def format_load(self, readings: object, bar_width_max: int, schedule: dict):
        """
        Update formatted_cpu_load from a CPUInfoLoad readings object.

        bar_width_max : total column width available for each bar row
        """
        if not schedule.get("cpu", True):
            return

        cpu_load = readings.cpu_load
        out      = self.formatted_cpu_load

        # Grow list to match cpu count; never shrink (avoids alloc churn)
        if not out:
            out.extend(TextStyle("N/A", 3) for _ in cpu_load)

        symbol = f"{"%":<{bar_width_max}}"

        for idx, cpu_label in enumerate(cpu_load):
            val = cpu_load[cpu_label]

            # Build display text: "Label: value %" padded to bar width
            raw_text  = f"{cpu_label}: {val} {symbol}"
            out[idx].value     = raw_text[:bar_width_max - 2]   # -2 for bracket chars
            out[idx].style     = 0

            if val in (None, "N/A"):
                out[idx].bar_width = 0
            else:
                out[idx].bar_width = int((val / 100) * bar_width_max)

        self.formatted_cpu_load = out


# ---------------------------------------------------------------------------
# Network formatter
# ---------------------------------------------------------------------------

class NetworkFormatter:
    """
    Formats network throughput readings.

    Output slots (10 total):
      [0] total download text + style
      [1] total download drop text + style
      [2] total upload text + style
      [3] total upload drop text + style
      [4..9] per-physical-interface combined strings (up to 6 interfaces)
    """
    __slots__ = ("formatted_network_output",)

    # Display widths
    _TOTAL_UPLOAD_WIDTH   = 8
    _TOTAL_DOWNLOAD_WIDTH = 10
    _PER_IF_WIDTH         = 14

    def __init__(self):
        # 4 totals + 6 interface slots
        self.formatted_network_output = [TextStyle(" ", 0) for _ in range(10)]

    @staticmethod
    def _bits_to_str(bytes_per_sec: float) -> str:
        """Convert bytes/s to a right-aligned bits/s string."""
        bits = bytes_per_sec * 8
        return scale_formatter(bits, DECIMAL_UNITS_SCALES) or f"0 b"

    def format(self, throughput: dict, schedule: dict):
        """Update formatted_network_output from NetworkTraffic.throughput dict."""
        if not schedule["network"]:
            return

        out = self.formatted_network_output
        out_len = len(out)
        w_dl = self._TOTAL_DOWNLOAD_WIDTH
        w_ul = self._TOTAL_UPLOAD_WIDTH
        _width = self._PER_IF_WIDTH

        # Running totals across all physical interfaces
        total_rx_bytes  = 0.0
        total_rx_drop   = 0.0
        total_tx_bytes  = 0.0
        total_tx_drop   = 0.0

        # Interface slots start at index 4
        if_idx = 4

        for iface, data in throughput.items():
            if data.Type != "Physical":
                continue
            if if_idx >= out_len:
                break   # no more display slots

            rx = data.Received_bytes
            tx = data.Transmitted_bytes

            rx_str = self._bits_to_str(rx)
            tx_str = self._bits_to_str(tx)

            out[if_idx].value = f"{iface:>{w_ul}.{w_ul}}: {rx_str:<{_width}.{_width}} | {tx_str:<{_width}.{_width}}"[:49]
            if_idx += 1

            total_rx_bytes += rx
            total_rx_drop  += data.Received_drop
            total_tx_bytes += tx
            total_tx_drop  += data.Transmitted_drop


        out[0].value = f"{self._bits_to_str(total_rx_bytes):<{w_dl}}"
        out[1].value = f"{self._bits_to_str(total_rx_drop):<{w_dl}}"
        out[2].value = f"{self._bits_to_str(total_tx_bytes):<{w_ul}}"
        out[3].value = f"{self._bits_to_str(total_tx_drop):<{w_ul}}"


# ---------------------------------------------------------------------------
# Nvidia formatter
# ---------------------------------------------------------------------------

class NvidiaFormatter:
    """
    Formats NVML GPU readings for a single GPU.

    Output slots (7 total):
      [0] temperature text + style
      [1] temperature bar (bar_width + style)
      [2] GPU clock speed text + style
      [3] fan speed text + style
      [4] memory load text + style
      [5] GPU load text + style
      [6] GPU load bar (bar_width + style)
    """
    __slots__ = ("formatted_nvidia_output",)

    _TEXT_MAX = 20      # max characters for each value field
    _TEMP_BAR_MAX = 49  # columns for temperature bar  (100 °C reference)
    _LOAD_BAR_MAX = 49  # columns for GPU load bar     (100 % reference)

    def __init__(self):
        self.formatted_nvidia_output = [TextStyle(" ", 3) for _ in range(7)]

    @staticmethod
    def _fmt_or_na(value, suffix: str, text_max: int) -> tuple[str, int]:
        """Return (formatted_string, style) or N/A placeholder when value is 'N/A'."""
        if value == "N/A":
            return f"{'N/A':<{text_max}}", 3
        return f"{value} {suffix:<{text_max}}", 0

    def format(self, gpu_readings: dict, schedule: dict):
        """Update formatted_nvidia_output from Nvidia.gpus_readings dict."""
        if not schedule["nvidia"]:
            return

        out = self.formatted_nvidia_output
        w   = self._TEXT_MAX

        # Currently only GPU index 0 is rendered
        data = gpu_readings.get(0, {})

        # --- Temperature ---
        temp = data.get("Temperature", "N/A")
        if temp == "N/A":
            temp_text    = f"{'N/A':<{w}}"
            temp_bar     = 3
            temp_style   = 3
        else:
            temp_text  = f"{temp} {'°C':<{w}}"
            temp_bar   = min(self._TEMP_BAR_MAX, int((temp / 100) * self._TEMP_BAR_MAX))
            temp_style = classify(temp, GPU_TEMP_THRESHOLDS)

        out[0].value    = temp_text
        out[0].style    = temp_style
        out[1].bar_width = temp_bar
        out[1].style    = temp_style

        # --- Clock speed ---
        clock       = data.get("GPU Clock Speed", "N/A")
        clock_text, clock_style = self._fmt_or_na(clock, "Mhz", w)
        out[2].value = clock_text
        out[2].style = clock_style

        # --- Fan speed ---
        fan       = data.get("Fan Speed", "N/A")
        fan_text, fan_style = self._fmt_or_na(fan, "RPM", w)
        out[3].value = fan_text
        out[3].style = fan_style

        # --- Memory load ---
        mem_load       = data.get("Memory Load", "N/A")
        mem_text, mem_style = self._fmt_or_na(mem_load, "%", w)
        if mem_load != "N/A":
            mem_style = classify(mem_load, GPU_LOAD_THRESHOLDS)
        out[4].value = mem_text
        out[4].style = mem_style

        # --- GPU load ---
        gpu_load = data.get("GPU Load", "N/A")
        if gpu_load == "N/A":
            load_text  = f"{'N/A':<{w}}"
            load_bar   = 0
            load_style = 3
        else:
            load_text  = f"{gpu_load} {'%':<{w}}"
            load_bar   = min(self._LOAD_BAR_MAX, int((gpu_load / 100) * self._LOAD_BAR_MAX))
            load_style = classify(gpu_load, GPU_LOAD_THRESHOLDS)

        out[5].value    = load_text
        out[5].style    = load_style
        out[6].bar_width = load_bar
        out[6].style    = load_style


# ---------------------------------------------------------------------------
# Process formatter
# ---------------------------------------------------------------------------

class ProcessFormatter:
    """
    Formats process entries for the scrollable process table.

    Each row is a list of 13 TextStyle objects:
      [0]  PID
      [1]  PPID
      [2]  Username
      [3]  Priority
      [4]  State
      [5]  Uptime
      [6]  Thread count
      [7]  CPU %
      [8]  Virtual memory
      [9]  RSS memory
      [10] Process name
      [11] Command line
      [12] Start time (used by ContentDiff for PID-recycle detection, never drawn)
    """
    __slots__ = ("formatted_processes_output",)

    def __init__(self):
        self.formatted_processes_output = []

    @staticmethod
    def _mib_to_str(mib: int) -> str:
        """Convert MiB integer to a GB or MB display string."""
        if mib > 1024:
            return f"{(mib // 1024) * 1.048576:<1.0f} {'GB':<6}"
        return f"{mib * 1.048576:<1.0f} {'MB':<6}"

    def format(self, processes: dict, process_monitor: object, schedule: dict):
        """
        Update formatted_processes_output from the live process dict.

        processes       : {pid: ProcessInfo, ...} already sorted by sorter()
        process_monitor : ProcessMonitor instance (provides user_list, current_user)
        """
        if not schedule["processes"]:
            return

        out          = self.formatted_processes_output
        usernames    = process_monitor.user_list
        current_users = set(process_monitor.current_user)

        # Trim stale rows when process count drops
        if len(out) > len(processes):
            del out[len(processes):]

        for idx, (pid, proc) in enumerate(processes.items()):
            # Grow list on demand
            if idx >= len(out):
                out.append([TextStyle("N/A", 3) for _ in range(13)])

            row      = out[idx]
            username = usernames.get(proc.uid, str(proc.uid))

            # Determine username colour: current user=green, root=blue, other=dim
            if username in current_users:
                user_style = 0
            elif username == "root":
                user_style = 5
            else:
                user_style = 3

            cpu = proc.cpu_load

            row[0].value,  row[0].style  = f"{pid:<10}",                    0
            row[1].value,  row[1].style  = f"{proc.ppid:<10}",              5
            row[2].value,  row[2].style  = f"{username:<14.14}",            user_style
            row[3].value,  row[3].style  = f"{proc.priority:<5}",           3
            row[4].value,  row[4].style  = f"{proc.state:<7}",              0
            row[5].value,  row[5].style  = time_formatter(proc.process_up_time), 0
            row[6].value,  row[6].style  = f"{proc.num_threads:<9}",        0
            row[7].value,  row[7].style  = f"{cpu:<6.6}",                   0 if cpu < 50.0 else 1 if cpu < 80.0 else 2
            row[8].value,  row[8].style  = self._mib_to_str(proc.vsize),    0
            row[9].value,  row[9].style  = self._mib_to_str(proc.rss),      0
            row[10].value, row[10].style = f"{proc.name:<19.19}",           4
            row[11].value, row[11].style = f"{proc.command:<150}",          4
            row[12].value                = proc.starttime   # sentinel only


# ---------------------------------------------------------------------------
# IO totals formatter
# ---------------------------------------------------------------------------

# Layout constants shared between format() and the dashboard renderer
FIELDS_PER_DEVICE     = 6   # name, read, write, read_latency, write_latency, utilisation
_FIRST_COL_WIDTH      = 9   # characters for name / throughput fields
_LAST_COL_WIDTH       = 6   # characters for latency / utilisation fields
_MILLISECOND_SUFFIX   = f"{'ms':<{_LAST_COL_WIDTH}}"


class IOTotalFormatter:
    """
    Formats block-device I/O statistics (one row per device).

    Each device produces FIELDS_PER_DEVICE consecutive TextStyle slots:
      base+0  device name
      base+1  read throughput
      base+2  write throughput
      base+3  read latency
      base+4  write latency
      base+5  utilisation %
    """
    __slots__ = ("formatted_io_output",)

    def __init__(self):
        self.formatted_io_output = []

    def format(self, readings: object, schedule: dict):
        """Update formatted_io_output from a ReadTotalIO readings object."""
        if not schedule["io"]:
            return

        devices = readings.devices_total_io
        out     = self.formatted_io_output

        # Resize list to exactly fit current device count (6 slots each)
        required = len(devices) * FIELDS_PER_DEVICE
        current  = len(out)
        if current < required:
            out.extend(TextStyle(" ", 3) for _ in range(required - current))
        elif current > required:
            del out[required:]

        for idx, (name, dev) in enumerate(devices.items()):
            base = idx * FIELDS_PER_DEVICE
            fw   = _FIRST_COL_WIDTH
            lw   = _LAST_COL_WIDTH

            # --- Throughput ---
            read  = dev.read_throughput
            write = dev.write_throughput

            if read == "N/A" or read == 0:
                read_text,  read_style  = f"{read:<{fw}}", 3
            else:
                read_text,  read_style  = scale_formatter(read,  BINARY_UNITS_SCALES), 0

            if write == "N/A" or write == 0:
                write_text, write_style = f"{write:<{fw}}", 3
            else:
                write_text, write_style = scale_formatter(write, BINARY_UNITS_SCALES), 0

            out[base + 0].value, out[base + 0].style = f"{name:<{fw}.{fw}}", 0
            out[base + 1].value, out[base + 1].style = f"{read_text:<{fw}.{fw}}", read_style
            out[base + 2].value, out[base + 2].style = f"{write_text:<{fw}.{fw}}", write_style

            # --- Latency ---
            r_lat = dev.read_latency
            w_lat = dev.write_latency

            if r_lat == "N/A" or r_lat == 0:
                out[base + 3].value, out[base + 3].style = f"{r_lat:<{lw}}", 3
            else:
                out[base + 3].value, out[base + 3].style = f"{r_lat:.1f}" + _MILLISECOND_SUFFIX, 0

            if w_lat == "N/A" or w_lat == 0:
                out[base + 4].value, out[base + 4].style = f"{w_lat:<{lw}}", 3
            else:
                out[base + 4].value, out[base + 4].style = f"{w_lat:.1f}" + _MILLISECOND_SUFFIX, 0

            # --- Utilisation % ---
            util = dev.time_busy
            if util == "N/A" or util == 0:
                # -1 width: avoid overwriting the dashboard border
                out[base + 5].value, out[base + 5].style = f"{util:<{lw - 1}}", 3
            else:
                out[base + 5].value, out[base + 5].style = f"{util:<{lw - 1}.1f}", 0


# ---------------------------------------------------------------------------
# IO pressure formatter
# ---------------------------------------------------------------------------

class IOPressureFormatter:
    """
    Formats IO PSI (pressure-stall information) readings.

    Output slots (8 total):
      [0] some avg10  text + style
      [1] some avg60  text + style
      [2] some avg300 text + style
      [3] full avg10  text + style
      [4] full avg60  text + style
      [5] full avg300 text + style
      [6] health score text + style
      [7] health bar  (bar_width + style only)
    """
    __slots__ = ("formatted_io_output",)

    _VALUE_WIDTH  = 5
    _BAR_MAX      = 30
    # IO pressure penalises more aggressively than memory pressure
    _HEALTH_SCALE = 1.5

    def __init__(self):
        self.formatted_io_output = [TextStyle("N/A", 3) for _ in range(8)]

    def format(self, readings: object, schedule: dict):
        """Update formatted_io_output from an IOPressure readings object."""
        if not schedule["io"]:
            return

        out = self.formatted_io_output
        w   = self._VALUE_WIDTH

        # IOPressure stores 4 values: avg10, avg60, avg300, total (we skip total)
        s10, s60, s300, _ = readings.io_some
        f10, f60, f300, _ = readings.io_full

        # --- Classify "some" averages ---
        out[0].value, out[0].style = f"{s10:<{w}.{w}}", classify(s10,  IO_PRESSURE_THRESHOLDS)
        out[1].value, out[1].style = f"{s60:<{w}.{w}}", classify(s60,  IO_PRESSURE_THRESHOLDS)
        out[2].value, out[2].style = f"{s300:<{w}.{w}}", classify(s300, IO_PRESSURE_THRESHOLDS)

        # --- Classify "full" averages ---
        out[3].value, out[3].style = f"{f10:<{w}.{w}}", classify(f10,  IO_PRESSURE_THRESHOLDS)
        out[4].value, out[4].style = f"{f60:<{w}.{w}}", classify(f60,  IO_PRESSURE_THRESHOLDS)
        out[5].value, out[5].style = f"{f300:<{w}.{w}}", classify(f300, IO_PRESSURE_THRESHOLDS)

        # --- Health score ---
        if s10 == "N/A":
            health       = "N/A"
            bar_width    = 0
            health_style = 3
        else:
            penalty = (
                s10  * 2.0  + s60  * 5.0  + s300  * 10.0 +
                f10  * 10.0 + f60  * 20.0 + f300  * 50.0
            )
            health       = max(0.0, 100.0 - penalty * self._HEALTH_SCALE)
            bar_width    = min(self._BAR_MAX, int(health / 3.2))
            health_style = classify(health, PRESSURE_HEALTH_THRESHOLDS)

        out[6].value = f"{health:<{w}.1f}" if health != "N/A" else "N/A  "
        out[6].style = health_style

        out[7].bar_width = bar_width
        out[7].style     = health_style