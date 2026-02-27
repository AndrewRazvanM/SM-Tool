Real-time system monitoring tool written in Python with a TUI (hop/thop style). This is meant to be a telemetry dashboard with process inspection, not a process manager.

It is a curses-based terminal dashboard that:
- Reads live kernel telemetry from /proc
  - CPU stats (/proc/stat)
  - Memory info (/proc/meminfo)
  - PSI pressure metrics (/proc/pressure/*)
  - Network throughput (/proc/net/dev)
- Reads Nvidia graphic card telemetry via NVML (pynvml)

<img width="1811" height="781" alt="image" src="https://github.com/user-attachments/assets/2e8440d5-b171-4815-884b-bf1e81331fa4" />

This was mainly done as a learning project, with minimal external dependencies.
