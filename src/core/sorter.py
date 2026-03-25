def sorter(raw_readings: object, schedule: dict) -> list:

    if schedule["processes"]:
        raw_readings.process_list = dict(sorted(raw_readings.process_list.items(), key=lambda item: item[1].cpu_load, reverse=True))