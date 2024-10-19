import time

def get_hypervisor_resource_usage(hypervisor_conn):

    node_info = hypervisor_conn.getInfo()
    print(node_info)
    total_memory = node_info[1]  
    total_cpus = node_info[3]  

    # Get initial CPU statistics from the hypervisor
    cpu_stats_1 = hypervisor_conn.getCPUStats(-1, 0)  # -1 means get the stats of the host (hypervisor)
    
    # Total CPU time is the sum of kernel time, user time, and possibly other stats
    total_time_1 = cpu_stats_1['kernel'] + cpu_stats_1['user']

    # Get the number of physical CPUs (cores) on the host
    cpu_count = hypervisor_conn.getInfo()[2]

    # Wait for the interval (e.g., 1 second)
    time.sleep(1)

    # Get CPU statistics again after the interval
    cpu_stats_2 = hypervisor_conn.getCPUStats(-1, 0)

    # Calculate the total CPU time for the second measurement
    total_time_2 = cpu_stats_2['kernel'] + cpu_stats_2['user']

    # Calculate the CPU time difference (in nanoseconds)
    cpu_time_diff = total_time_2 - total_time_1

    # Convert to percentage over the interval
    cpu_usage = (cpu_time_diff / (1 * 1e9 * cpu_count)) * 100

    free_memory = hypervisor_conn.getFreeMemory()
    
    return {
        'cpu': 100-cpu_usage, # percentage  
        'memory': free_memory # bytes
    }
