import random
import math
import libvirt

def get_vm_resources(vm):
    try:
        stats = vm.getCPUStats(True)
        cpu_usage = stats[0]['cpu_time'] / 1000000000  # Convert to seconds
        memory_stats = vm.memoryStats()
        memory_usage = memory_stats.get('actual', 0) / 1024  # Convert to MB
        return cpu_usage, memory_usage
    except libvirt.libvirtError as e:
        print(f"Error getting resources for VM {vm.name()}: {e}")
        return 0, 0

def get_host_resources(conn):
    try:
        node_info = conn.getInfo()
        cpu_capacity = node_info[2] * node_info[3]  # cores * speed (MHz)
        memory_capacity = node_info[1]  # in MB
        return cpu_capacity, memory_capacity
    except libvirt.libvirtError as e:
        print(f"Error getting resources for host {conn.getHostname()}: {e}")
        return 0, 0

def initial_solution(all_vms):
    return {conn: list(vms) for conn, vms in all_vms.items()}

def objective_function(solution):
    return sum(1 for vms in solution.values() if vms)

def can_host(conn, vm, solution):
    host_cpu, host_memory = get_host_resources(conn)
    vm_cpu, vm_memory = get_vm_resources(vm)
    
    current_cpu_usage = sum(get_vm_resources(v)[0] for v in solution[conn])
    current_memory_usage = sum(get_vm_resources(v)[1] for v in solution[conn])
    
    return (host_cpu >= current_cpu_usage + vm_cpu and
            host_memory >= current_memory_usage + vm_memory)

def generate_neighbor(solution, all_conns):
    new_solution = {conn: vms[:] for conn, vms in solution.items()}
    source_conn = random.choice([conn for conn, vms in new_solution.items() if vms])
    vm = random.choice(new_solution[source_conn])
    new_solution[source_conn].remove(vm)
    
    possible_targets = [conn for conn in all_conns if conn != source_conn and can_host(conn, vm, new_solution)]
    if possible_targets:
        target_conn = random.choice(possible_targets)
        new_solution[target_conn].append(vm)
    else:
        new_solution[source_conn].append(vm)
    
    return new_solution

def simulated_annealing(all_vms, all_conns, initial_temp=100, cooling_rate=0.95, min_temp=0.1, max_iterations=1000):
    current_solution = initial_solution(all_vms)
    current_energy = objective_function(current_solution)
    best_solution = current_solution
    best_energy = current_energy
    temperature = initial_temp
    iteration = 0

    while temperature > min_temp and iteration < max_iterations:
        neighbor = generate_neighbor(current_solution, all_conns)
        neighbor_energy = objective_function(neighbor)
        
        if neighbor_energy < current_energy or random.random() < math.exp((current_energy - neighbor_energy) / temperature):
            current_solution = neighbor
            current_energy = neighbor_energy
            
            if current_energy < best_energy:
                best_solution = current_solution
                best_energy = current_energy
        
        temperature *= cooling_rate
        iteration += 1

    return best_solution, best_energy

def sa_server_consolidation(source_conns, all_vms):
    best_solution, best_energy = simulated_annealing(all_vms, source_conns)
    
    migration_plan = {}
    for target_conn, vms in best_solution.items():
        for vm in vms:
            if vm not in all_vms[target_conn]:
                migration_plan[vm] = target_conn
    
    return migration_plan