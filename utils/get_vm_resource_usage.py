import time
def get_vm_resource_usage(vm,interval=1):
    memory_stats = vm.memoryStats()
    memory_usage = memory_stats.get('rss', 0)  

    cpu_stats = vm.info()
    cpu_time = cpu_stats[4]  
    
    vcpus = vm.info()[3]

    # Get the initial CPU time (in nanoseconds)
    cpu_time_1 = vm.info()[4]

    # Wait for the interval (e.g., 1 second)
    time.sleep(interval)

    # Get the CPU time after the interval
    cpu_time_2 = vm.info()[4]

    # Calculate CPU time difference (in nanoseconds)
    cpu_time_diff = cpu_time_2 - cpu_time_1

    # Convert the CPU time to percentage
    cpu_usage = (cpu_time_diff / (1 * 1e9 * vcpus)) * 100
    
    return {
        'cpu': cpu_usage, # percentage
        'memory': memory_usage * 1024 # kiB --> converted to Bytes
    }
