Real-time system monitoring tool written in Python with a TUI (hop/thop style). This is meant to be a telemetry dashboard with process inspection, not a process manager.

It is a curses-based terminal dashboard that:
- Reads live kernel telemetry from /proc
  - CPU stats (/proc/stat)
  - Memory info (/proc/meminfo)
  - PSI pressure metrics (/proc/pressure/*)
  - Network throughput (/proc/net/dev)
- Reads Nvidia graphic card telemetry via NVML (pynvml)

  <img width="1920" height="1040" alt="image" src="https://github.com/user-attachments/assets/11979d60-fdbd-4c9d-8235-d6031283857c" />

This was mainly done as a learning project, with minimal external dependencies.
