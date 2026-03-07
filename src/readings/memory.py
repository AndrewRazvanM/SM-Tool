def memory_readings(memory_disable, path):
    data={}
    if memory_disable is False:
        try:
            for line in path.get_file("meminfo"):
                    if (("MemTotal" not in line) and ("MemAvailable" not in line) and ("SwapTotal" not in line) and ("SwapFree" not in line)):
                        continue #skips lines that are not relevant
                    key, value= line.split(":", 1)
                    value= int(value.strip().split()[0])
                    data[key]= int(value)
                
        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            data= {
            "MemTotal": "N/A",
            "MemAvailable": "N/A",
            "SwapTotal": "N/A",
            "SwapFree": "N/A"
        }
    
    else:
        data= {
            "MemTotal": "N/A",
            "MemAvailable": "N/A",
            "SwapTotal": "N/A",
            "SwapFree": "N/A"
        }

    return data
