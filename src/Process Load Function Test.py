import os
from types import SimpleNamespace
from unittest.mock import patch, mock_open

# Minimal classes for your code
class ProcessStat:
    def __init__(self, name, stats_list):
        self.name = name
        self.utime = int(stats_list[13]) if len(stats_list) > 13 else 10
        self.stime = int(stats_list[14]) if len(stats_list) > 14 else 5
        self.process_time = self.utime + self.stime
        self.starttime = int(stats_list[21]) if len(stats_list) > 21 else 1000
        self.name = name

class ProcessStatus:
    pass

# --- Fixed fully mocked test with non-zero CPU load ---
def test_current_processes_fixed_full():
    # Mock previous stat data
    prev_stat_data = {
        101: ProcessStat("proc1", [0]*22),  # process_time = 15
        102: ProcessStat("proc2", [0]*22),  # process_time = 15
    }
    
    total_cpu_load_delta = 1000
    number_of_cpu_threads = 4
    
    # Fake /proc entries
    fake_dirs = [SimpleNamespace(name="101"), SimpleNamespace(name="102")]

    # Fake current stat file content (simulate CPU usage)
    fake_stat_content_101 = "1 (proc1) " + " ".join(["0"]*13 + ["15", "10"] + ["0"]*7)  # process_time = 25
    fake_stat_content_102 = "1 (proc2) " + " ".join(["0"]*13 + ["20", "5"] + ["0"]*7)   # process_time = 25

    # Fake status file content
    fake_status_content = "Uid: 1000\nGid: 1000\nState: R\nThreads: 1\nFDSize: 256\n"

    # Custom open: returns stat or status content per PID
    def mocked_open(file, *args, **kwargs):
        if file.endswith("/101/stat"):
            return mock_open(read_data=fake_stat_content_101).return_value
        elif file.endswith("/102/stat"):
            return mock_open(read_data=fake_stat_content_102).return_value
        elif file.endswith("/101/status") or file.endswith("/102/status"):
            return mock_open(read_data=fake_status_content).return_value
        else:
            raise FileNotFoundError

    with patch("os.scandir", return_value=fake_dirs), \
         patch("builtins.open", new=mocked_open):

        from functionalityv2 import current_processes  # your actual function

        stat_data, status_data, process_cpu_load, status_index = current_processes(
            prev_stat_data=prev_stat_data,
            total_cpu_load_delta=total_cpu_load_delta,
            number_of_cpu_threads=number_of_cpu_threads,
            data_length=10,
            status_index=3  # force status reading
        )

        print("STAT DATA KEYS:", list(stat_data.keys()))
        print("STATUS DATA KEYS:", list(status_data.keys()))
        print("PROCESS CPU LOAD:")
        for pid, load in process_cpu_load.items():
            print(f"PID {pid}: {load:.2f}%")
        print("STATUS INDEX:", status_index)

# Run the test
test_current_processes_fixed_full()