def sorter(process_list: dict, schedule: dict) -> list:

    if schedule["processes"] is False:
            return
        
    sorted_items = sorted(
    process_list.items(),
    key=lambda item: item[1].cpu_load,
    reverse=True
    )

    process_list.clear()
    process_list.update(sorted_items)