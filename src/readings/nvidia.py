import pynvml

def check_if_nvidia():
    """
    Checks if nVidia card on device and initializez pynvml"""
     
    try:

        pynvml.nvmlInit()
        nvidia_gpu_check_disable= False

    except (pynvml.NVMLError_LibraryNotFound,
        pynvml.NVMLError_DriverNotLoaded,
        pynvml.NVMLError_NoPermission) as error:
        nvidia_gpu_check_disable= True

    return nvidia_gpu_check_disable

def close_nvidia_drivers():
    try:
        pynvml.nvmlShutdown()
    
    except pynvml.NVML_ERROR_UNINITIALIZED:
        pass

def nvidia_gpu_name(gpu_check_disable):
    gpu_handles= None
    if gpu_check_disable is False:
            data= []
            gpu_handles= []
            gpu_count= pynvml.nvmlDeviceGetCount()
            for gpu in range(gpu_count):
                gpu_handles.append(pynvml.nvmlDeviceGetHandleByIndex(gpu))
                gpu_name= pynvml.nvmlDeviceGetName(gpu_handles[gpu])
                data.append(gpu_name)
    else:
        data= ["Disabled on this system"]
    
    return data, gpu_handles

def nvidia_gpu_readings(gpu_check_disable, gpu_handles, gpu_fan_disabled= False,gpu_mem_disabled= False):

    try:
        if gpu_check_disable is False:
            data= []
            for gpu in gpu_handles:
                gpu_temp= pynvml.nvmlDeviceGetTemperature(gpu, pynvml.NVML_TEMPERATURE_GPU)
                gpu_stats= pynvml.nvmlDeviceGetUtilizationRates(gpu)
                        #not supported on all cards
                if gpu_fan_disabled == False:
                    try:
                        gpu_fan= pynvml.nvmlDeviceGetFanSpeed(gpu)

                    except pynvml.NVMLError:
                        gpu_fan = "N/A"
                        gpu_fan_disabled= True
                else:
                    gpu_fan = "N/A"

                gpu_core= pynvml.nvmlDeviceGetClockInfo(gpu, pynvml.NVML_CLOCK_GRAPHICS)
                #it's not supported on all graphic cards
                if gpu_mem_disabled == False:
                    try:

                        gpu_core_mem= pynvml.nvmlDeviceGetClockInfo(gpu, pynvml.NVML_CLOCK_MEM)

                    except pynvml.NVMLError:
                        gpu_core_mem= "N/A"
                        gpu_mem_disabled= True
                else:
                    gpu_core_mem= "N/A"

                data.append({
                    "Temperature": gpu_temp,
                    "GPU Clock Speed": gpu_core,
                    "Fan Speed": gpu_fan,
                    "Memory Load": gpu_stats.memory,
                    "GPU Load": gpu_stats.gpu,
                    "GPU Mem Clock": gpu_core_mem
                })
        
        else:
            data= [{
                "Temperature": "N/A",
                "GPU Clock Speed": "N/A",
                "Fan Speed": "N/A",
                "Memory Load": "N/A",
                "GPU Load":"N/A",
            }]

    except (pynvml.NVMLError_LibraryNotFound, OSError, pynvml.NVMLError, RuntimeError):
                data= [{
            "Temperature": 0,
            "GPU Clock Speed": 0,
            "Fan Speed": 0,
            "Memory Load": 0,
            "GPU Load":0,
            }]
    return data, gpu_fan_disabled, gpu_mem_disabled
