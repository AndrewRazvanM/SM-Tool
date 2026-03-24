def sorter(formatted_readings: list, schedule: dict) -> list:
    if schedule["processes"]:
        formatted_readings.sort(key=lambda row: row[14], reverse=True)