from time import monotonic

class Scheduler:
    __slots__= (
        "cpu",
        "memory",
        "network",
        "nvidia",
        "processes",
        "io",
        "intervals",
    )

    def __init__(self):
        self.cpu = 0
        self.memory = 0
        self.network = 0
        self.nvidia = 0
        self.processes = 0
        self.io = 0
        self.intervals = {
            "cpu": 1,
            "memory": 1,
            "network": 0.5,
            "nvidia": 1,
            "processes": 2,
            "io": 2,
        }
        
    def should_run(self):
        now = monotonic()
        run_cpu = (now - self.cpu) >= self.intervals["cpu"]
        run_mem = (now - self.memory) >= self.intervals["memory"]
        run_network  = (now - self.network) >= self.intervals["network"]
        run_nvidia= (now - self.nvidia) >= self.intervals["nvidia"]
        run_processes= (now - self.processes) >= self.intervals["processes"]
        run_io= (now - self.io) >= self.intervals["io"]

        # update timestamps only if we actually run them
        if run_cpu:
            self.cpu = now
        if run_mem:
            self.memory = now
        if run_network:
            self.network = now
        if run_nvidia:
            self.nvidia = now
        if run_processes:
            self.processes = now
        if run_io:
            self.io = now


        return {
            "cpu": run_cpu,
            "memory": run_mem,
            "network": run_network,
            "nvidia": run_nvidia,
            "processes": run_processes,
            "io": run_io,
        }