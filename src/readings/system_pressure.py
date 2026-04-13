class MemPressure:
    """
    Check for memory pressure. Can be disabled individually.
      Requires as an argument the object that stores the open files.
    """
    __slots__ =(
          "memory_some",
          "memory_full",
          "file_paths"
     )

    def __init__(self, file_paths: object):
        self.file_paths= file_paths
        self.memory_some= ["N/A"] * 3 #pre-allocating list size. Excluding total from file
        self.memory_full= ["N/A"] * 3 #pre-allocating list size

    def read_mem(self, memory_check_disable: bool, schedule: dict):
        if schedule["memory"] is False:
            return

        file_paths= self.file_paths

        if memory_check_disable is False:
            try:
                for line in file_paths.get_file("mem_pressure"):
                    if line.startswith("some"):
                        
                        parts_mem = line.split()

                        some_avg10= self.memory_some[0] = float(parts_mem[1][6:])
                        some_avg60= self.memory_some[1] = float(parts_mem[2][6:])
                        some_avg300= self.memory_some[2] = float(parts_mem[3][7:])

                    if line.startswith("full"):
                        parts_mem_full = line.split()

                        full_avg10= self.memory_full[0] = float(parts_mem_full[1][6:])
                        full_avg60= self.memory_full[1] = float(parts_mem_full[2][6:])
                        full_avg300= self.memory_full[2] = float(parts_mem_full[3][7:])


            except FileNotFoundError:
                memory_check_disable= True

        return memory_check_disable
    
class CPUPressure:
    """
    Check for cpu pressure. Can be disabled individually.
      Requires as an argument the object that stores the open files.
    """
    __slots__ =(
          "cpu_avg10",
          "cpu_avg60",
          "cpu_avg300",
          "file_paths"
     )

    def __init__(self, file_paths: object):
        self.file_paths= file_paths
        self.cpu_avg10= "N/A"
        self.cpu_avg60= "N/A"
        self.cpu_avg300= "N/A"
    
    def read_cpu(self, cpu_check_disable: bool, schedule: dict):
        if schedule["cpu"] is False:
            return
        
        file_paths= self.file_paths

        if cpu_check_disable is False:
            try:
                for line in file_paths.get_file("cpu_pressure"):
                    if line.startswith("full"):
                        break
                    
                    parts = line.split()

                    self.cpu_avg10 = float(parts[1][6:])
                    self.cpu_avg60 = float(parts[2][6:])
                    self.cpu_avg300 = float(parts[3][7:])

            except FileNotFoundError:
                 cpu_check_disable= True
        
        return cpu_check_disable
    
class IOPressure:
    """
    Check for io pressure. Can be disabled individually.
      Requires as an argument the object that stores the open files.
    """
    __slots__ =(
          "io_some",
          "io_full",
          "file_paths"
     )

    def __init__(self, file_paths: object):
        self.file_paths= file_paths
        self.io_some= ["N/A"] * 4
        self.io_full= ["N/A"] * 4


    def read_io(self, schedule: dict):

        if schedule["io"] is False:
            return
        
        file_paths= self.file_paths

        try:
            for line in file_paths.get_file("io_pressure"):
                if line.startswith("some"):
                    parts_io = line.split()

                    self.io_some[0] = float(parts_io[1][6:])
                    self.io_some[1] = float(parts_io[2][6:])
                    self.io_some[2] = float(parts_io[3][7:])
                    self.io_some[3] = float(parts_io[4][6:])

                if line.startswith("full"):
                    parts_io_full = line.split()

                    self.io_full[0] = float(parts_io_full[1][6:])
                    self.io_full[1] = float(parts_io_full[2][6:])
                    self.io_full[2] = float(parts_io_full[3][7:])
                    self.io_full[3] = float(parts_io_full[4][6:])

        except FileNotFoundError:
            return