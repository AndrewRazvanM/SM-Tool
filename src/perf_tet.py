# benchmark.py — drop in src/
import time
from core.file_handling import NeededFiles

# Test OLD
from readings.processes import ProcessMonitor as OldPM
# Test NEW  
from readings.process_monitor import ProcessMonitor as NewPM

files = NeededFiles()
schedule = {"processes": True}

def bench(cls, n=50):
    pm = cls(files)
    pl = {}
    pm.update(schedule, pl)  # warmup
    t = time.perf_counter()
    for _ in range(n):
        pm.update(schedule, pl)
    return (time.perf_counter() - t) / n * 1000

old_ms = bench(OldPM)
new_ms = bench(NewPM)
print(f"Old: {old_ms:.2f}ms  New: {new_ms:.2f}ms  Speedup: {old_ms/new_ms:.2f}x")