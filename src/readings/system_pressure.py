
def system_pressure(cpu_disable,memory_disable,file_paths):
    data_memory={
        "some": {},
        "full": {}
    }
    data_cpu={}
    if cpu_disable is False:
        try:
            for line in file_paths.get_file("cpu_pressure"):
                    if "full" in line:
                        break
                    line= line.strip()
                    for i, token in enumerate(line.split()):
                        if token == "some":
                            continue
                        key, value= token.split("=", 1)
                        value= round(float(value.strip()), 1)
                        data_cpu[key]= value
                            
        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            data_cpu["avg10"]= "N/A"
            data_cpu["avg60"]= "N/A"
            data_cpu["avg300"]= "N/A"
            data_cpu["total"]= "N/A"
    else:
            data_cpu["avg10"]= "N/A"
            data_cpu["avg60"]= "N/A"
            data_cpu["avg300"]= "N/A"
            data_cpu["total"]= "N/A"

    if memory_disable is False:
        try:
            for line in file_paths.get_file("mem_pressure"):
                    split= line.strip().split(" ")
                    if "some" in line:
                        for _, token in enumerate(split):
                            if token == "some":
                                    continue
                            key, value= token.split("=", 1)
                            value= value.strip()
                            data_memory["some"][key]= float(value)
                    if "full" in line:
                        for _, token in enumerate(split):
                            if token == "full":
                                    continue
                            key, value= token.split("=", 1)
                            value= value.strip()
                            data_memory["full"][key]= float(value)

        except (RuntimeError, UnboundLocalError, FileNotFoundError):
            data_memory["some"]["avg10"]= "N/A"
            data_memory["some"]["avg60"]= "N/A"
            data_memory["some"]["avg300"]= "N/A"
            data_memory["some"]["total"]= "N/A"
            data_memory["full"]["avg10"]= "N/A"
            data_memory["full"]["avg60"]= "N/A"
            data_memory["full"]["avg300"]= "N/A"
            data_memory["full"]["total"]= "N/A"
    else:
            data_memory["some"]["avg10"]= "N/A"
            data_memory["some"]["avg60"]= "N/A"
            data_memory["some"]["avg300"]= "N/A"
            data_memory["some"]["total"]= "N/A"
            data_memory["full"]["avg10"]= "N/A"
            data_memory["full"]["avg60"]= "N/A"
            data_memory["full"]["avg300"]= "N/A"
            data_memory["full"]["total"]= "N/A"

    return data_cpu, data_memory
      