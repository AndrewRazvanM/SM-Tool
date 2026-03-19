
class MemoryInfo:
    """
    Collects RAM and Swap info.
    """
    __slots__=(
          "MemTotal",
          "MemAvailable",
          "SwapTotal",
          "SwapFree",
          "__file_path",
          "disable_memory_checks"
    )

    def __init__(self, file_path: object, disable_memory_checks= False):
        self.MemTotal= "N/A"
        self.MemAvailable= "N/A"
        self.SwapTotal= "N/A"
        self.SwapFree= "N/A"
        self.__file_path= file_path
        self.disable_memory_checks= disable_memory_checks
    
    def update(self, schedule):
        if self.disable_memory_checks:
            return
        
        if schedule["memory"] is False:
            return

        __file_path= self.__file_path
        values_read= 0
        try:
            for line in __file_path.get_file("meminfo"):
                if line.startswith("MemTotal"):
                    _, value= line.split(":", 1)
                    value= int(value.split()[0])
                    self.MemTotal= value
                    values_read+= 1

                elif line.startswith("MemAvailable"):
                    _, value= line.split(":", 1)
                    value= int(value.split()[0])
                    self.MemAvailable= value
                    values_read+= 1

                elif line.startswith("SwapTotal"):
                    _, value= line.split(":", 1)
                    value= int(value.split()[0])
                    self.SwapTotal= value
                    values_read+= 1

                elif line.startswith("SwapFree"):
                    _, value= line.split(":", 1)
                    value= int(value.split()[0])
                    self.SwapFree= value
                    values_read+= 1

                if values_read == 4:
                    return
                
        except FileNotFoundError:
            return