Real-time system monitoring tool written in Python with a TUI (curses-based like htop). Intended to have a simple layout and provide all the system monitoring needs a user has. 

Currently implemented:
- Reads live kernel telemetry from /proc
  - CPU stats (/proc/stat):
     - Temperature
     - CPU usage % (per-core and overall)
     - Fan Speed (if exposed by the motherboard)
  - Memory info (/proc/meminfo)
  - PSI pressure metrics (/proc/pressure/*)
     - For both CPU and Memory
  - Network interfaces and throughput (/proc/net/dev)
  - Current processes (/proc/pid/stat and /proc/pid/status):
     - Process information
     - Process CPU usage % (htop style calculation)
- Reads Nvidia graphic card telemetry via NVML (nvidia-ml-py)

![SM-Tool](assets/ReadMeScreenshot.png)

To be implemented:
- I/O monitoring
- AMD graphic card monitoring
- Process management (search, kill/stop)
- config file + options

Current dependencies:
- nvidia-ml-py

To build the app, you need to run the one of the commands below in the terminal:
- pip install -e ./SM-Tool
   - this needs to be ran from the folder where the app was donloaded

Tool was tested on a machine with ~30.000 (dummy) processes and still remained responsive.
