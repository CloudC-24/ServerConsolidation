def get_hypervisor_resource_usage(hypervisor_conn):

    node_info = hypervisor_conn.getInfo()
    total_memory = node_info[1]  
    total_cpus = node_info[2]  

    free_memory = hypervisor_conn.getFreeMemory() / 1024 / 1024
    
    return {
        'cpu': total_cpus,  
        'memory': free_memory 
    }
