import pynvml

class Nvidia:
    """
    When initialized, it check if nvmlInit() can initialize the nVidia drivers. Otherwhise, disabled any further checks.
    Also has function to get data from the driver: get_nvidia_gpu_readings; and to close the drivers: close_nvidia_drivers.
    """
    __slots__= (
        "gpu_check_disable",
        "gpu_handles",
        "gpu_name_list",
        "gpu_fan_disabled",
        "gpu_mem_disabled",
        "gpus_readings",
    )

    def __init__(self):
        self.gpu_check_disable= self.__init_nvml()
        self.gpu_handles= []
        self.gpu_name_list= []
        self.__nvidia_gpu_name()
        self.gpu_fan_disabled= False
        self.gpu_mem_disabled= False
        self.gpus_readings= {}

    def __nvidia_gpu_name(self):
        if self.gpu_check_disable is False:
            gpu_name_list= self.gpu_name_list
            gpu_handles= self.gpu_handles
            gpu_count= pynvml.nvmlDeviceGetCount()
            for gpu in range(gpu_count):
                gpu_handle= pynvml.nvmlDeviceGetHandleByIndex(gpu)
                gpu_name= pynvml.nvmlDeviceGetName(gpu_handle)
                gpu_handles.append(gpu_handle)
                gpu_name_list.append(gpu_name)

        else:
            self.gpu_name_list.append("N/A")

    def __init_nvml(self):
        """
        Checks if nVidia card on device and initializez pynvml
        """
     
        try:

            pynvml.nvmlInit()
            nvidia_gpu_check_disable= False

        except (pynvml.NVMLError_LibraryNotFound,
            pynvml.NVMLError_DriverNotLoaded,
            pynvml.NVMLError_NoPermission) as error:
            nvidia_gpu_check_disable= True

        return nvidia_gpu_check_disable

    def close_nvidia_drivers(self):
        if self.gpu_check_disable is False:

            try:
                pynvml.nvmlShutdown()
            
            except pynvml.NVML_ERROR_UNINITIALIZED:
                pass

    def get_nvidia_gpu_readings(self, schedule):
        if schedule["nvidia"] is False:
            return
        
        gpu_index= 0

        try:
            if self.gpu_check_disable is False:
                gpu_data= self.gpus_readings
                gpu_fan_disabled= self.gpu_fan_disabled
                gpu_mem_disabled= self.gpu_mem_disabled

                for gpu in self.gpu_handles:
                    gpu_temp= pynvml.nvmlDeviceGetTemperature(gpu, pynvml.NVML_TEMPERATURE_GPU)
                    gpu_stats= pynvml.nvmlDeviceGetUtilizationRates(gpu)
                            #not supported on all cards
                    if gpu_fan_disabled == False:
                        try:
                            gpu_fan= pynvml.nvmlDeviceGetFanSpeed(gpu)

                        except pynvml.NVMLError:
                            gpu_fan = "N/A"
                            self.gpu_fan_disabled= True
                    else:
                        gpu_fan = "N/A"

                    gpu_core= pynvml.nvmlDeviceGetClockInfo(gpu, pynvml.NVML_CLOCK_GRAPHICS)
                    #it's not supported on all graphic cards
                    if gpu_mem_disabled == False:
                        try:

                            gpu_core_mem= pynvml.nvmlDeviceGetClockInfo(gpu, pynvml.NVML_CLOCK_MEM)

                        except pynvml.NVMLError:
                            gpu_core_mem= "N/A"
                            self.gpu_mem_disabled= True
                    else:
                        gpu_core_mem= "N/A"

                    gpu_data[gpu_index] ={
                        "Temperature": gpu_temp,
                        "GPU Clock Speed": gpu_core,
                        "Fan Speed": gpu_fan,
                        "Memory Load": gpu_stats.memory,
                        "GPU Load": gpu_stats.gpu,
                        "GPU Mem Clock": gpu_core_mem
                    }
                    gpu_index+= 1
            
            else:
                self.gpus_readings[0]= {
                    "Temperature": "N/A",
                    "GPU Clock Speed": "N/A",
                    "Fan Speed": "N/A",
                    "Memory Load": "N/A",
                    "GPU Load": "N/A",
                    "GPU Mem Clock": "N/A"
                }

        except (pynvml.NVMLError_LibraryNotFound, OSError, pynvml.NVMLError, RuntimeError):
                self.gpus_readings[0]= {
                    "Temperature": "N/A",
                    "GPU Clock Speed": "N/A",
                    "Fan Speed": "N/A",
                    "Memory Load": "N/A",
                    "GPU Load": "N/A",
                    "GPU Mem Clock": "N/A"
                }
