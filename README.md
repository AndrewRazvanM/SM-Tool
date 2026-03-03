Real-time system monitoring tool written in Python with a TUI (hop style). This is meant to be a telemetry dashboard with process inspection. Does not yet have the capability to kill or search processes.

It is a curses-based terminal dashboard that:
- Reads live kernel telemetry from /proc
  - CPU stats (/proc/stat)
  - Memory info (/proc/meminfo)
  - PSI pressure metrics (/proc/pressure/*)
  - Network throughput (/proc/net/dev)
- Reads Nvidia graphic card telemetry via NVML (pynvml)

![ReadMeScreenshot](assets/ReadMeScreenshot.png)
