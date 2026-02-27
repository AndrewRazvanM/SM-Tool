import time
from functionalityv2 import NeededFiles, get_cpu_load, current_processes

def benchmark_get_processes(iterations=50):
    file_path = NeededFiles()

    # initial CPU snapshot (required for delta calc)
    cpu_raw, cpu_load, _ = get_cpu_load(False, file_path)
    time.sleep(1)
    cpu_raw, cpu_load, total_delta = get_cpu_load(False, file_path, cpu_raw)
    stat_data = None
    number_of_threads = len(cpu_raw) - 1
    status_index = 0
    data_lenght=1000

    # ---- Warmup ----
    for _ in range(5):
        stat_data, status_data, process_cpu_load, status_index =current_processes(
            stat_data,
            total_delta,
            number_of_threads,
            data_lenght,
            status_index
        )
        # stat_data, status_data, process_cpu_load, status_index= current_processes(stat_data,
        #     total_delta,
        #     number_of_threads,
        #     data_lenght,
        #     status_index,
        # )
    # ---- Timed runs ----
    start = time.perf_counter()

    for _ in range(iterations):
        stat_data, status_data, process_cpu_load, status_index = current_processes(
            stat_data,
            total_delta,
            number_of_threads,
            data_lenght,
            status_index
        )
        # stat_data, status_data, process_cpu_load, status_index= current_processes(stat_data,
        #     total_delta,
        #     number_of_threads,
        #     data_lenght,
        #     status_index,
        # )

    end = time.perf_counter()

    total_time = end - start
    avg_time = total_time / iterations

    print(f"Total time: {total_time:.6f} seconds")
    print(f"Average per call: {avg_time:.6f} seconds")
    print(f"Calls per second: {1/avg_time:.2f}")

if __name__ == "__main__":
    benchmark_get_processes(30)
