def get_vm_resource_usage(vm):
    print(vm)
    memory_stats = vm.memoryStats()
    memory_usage = memory_stats.get('rss', 0)  

    cpu_stats = vm.info()
    cpu_time = cpu_stats[4]  
    
    return {
        'cpu': cpu_time,  
        'memory': memory_usage  
    }
