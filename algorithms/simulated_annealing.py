import random
import math
from utils.get_hypervisor_resource_usage import get_hypervisor_resource_usage
from utils.get_vm_resource_usage import get_vm_resource_usage
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def sa_server_consolidation(source_conns, all_vms, initial_temp=100, cooling_rate=0.95, 
                          min_temp=1, max_iterations=40):
    """
    Combined server consolidation function using simulated annealing.
    Returns a migration plan for all VMs, including those staying on their current servers.
    """
    logger.info("Starting server consolidation process")
    
    try:
        # Create initial solution and track original locations
        current_solution = {conn: list(vms) for conn, vms in all_vms.items()}
        initial_locations = {}
        for conn, vms in all_vms.items():
            for vm in vms:
                initial_locations[vm] = conn
        
        logger.info(f"Created initial solution with {len(all_vms)} hypervisors")
        
        current_energy = sum(1 for vms in current_solution.values() if vms)
        best_solution = current_solution.copy()
        best_energy = current_energy
        temperature = initial_temp
        iteration = 0

        # Simulated annealing process
        while temperature > min_temp and iteration < max_iterations:
            # Generate neighbor solution
            new_solution = {conn: vms[:] for conn, vms in current_solution.items()}
            active_conns = [conn for conn, vms in new_solution.items() if vms]
            
            if active_conns:
                source_conn = random.choice(active_conns)
                if new_solution[source_conn]:
                    vm = random.choice(new_solution[source_conn])
                    new_solution[source_conn].remove(vm)
                    
                    possible_targets = [
                        conn for conn in source_conns 
                        if conn != source_conn and can_host(conn, vm, new_solution)
                    ]
                    
                    if possible_targets:
                        target_conn = random.choice(possible_targets)
                        new_solution[target_conn].append(vm)
                        logger.info(
                            f"Generated neighbor: Moving VM {vm.name()} from "
                            f"{source_conn.getHostname()} to {target_conn.getHostname()}"
                        )
                    else:
                        new_solution[source_conn].append(vm)
                        logger.debug(
                            f"No suitable target found for VM {vm.name()}, "
                            f"returning to source {source_conn.getHostname()}"
                        )
            
            # Evaluate new solution
            neighbor_energy = sum(1 for vms in new_solution.values() if vms)
            delta_energy = neighbor_energy - current_energy
            
            # Accept or reject new solution
            if (delta_energy < 0 or 
                random.random() < math.exp(-delta_energy / temperature)):
                current_solution = new_solution
                current_energy = neighbor_energy
                
                if current_energy < best_energy:
                    best_solution = current_solution.copy()
                    best_energy = current_energy
                    logger.info(
                        f"New best solution found - Iteration: {iteration}, "
                        f"Temperature: {temperature:.2f}, Energy: {best_energy}"
                    )
            
            temperature *= cooling_rate
            iteration += 1
            
            logger.debug(
                f"Iteration {iteration}: Temperature={temperature:.2f}, "
                f"Current Energy={current_energy}, Best Energy={best_energy}"
            )

        # Create comprehensive migration plan for all VMs
        migration_plan = {}
        
        # First, add all VMs to the migration plan with their current/initial locations
        for vm, initial_conn in initial_locations.items():
            migration_plan[vm] = initial_conn
        
        # Then update with new locations from the best solution
        for target_conn, vms in best_solution.items():
            for vm in vms:
                migration_plan[vm] = target_conn
        
        logger.info(f"Consolidation completed - Migration plan created for {len(migration_plan)} VMs")
        
        # Log all VM placements
        for vm, target_conn in migration_plan.items():
            if initial_locations[vm] != target_conn:
                logger.info(
                    f"VM {vm.name()} will migrate from "
                    f"{initial_locations[vm].getHostname()} to "
                    f"{target_conn.getHostname()}"
                )
            else:
                logger.info(
                    f"VM {vm.name()} will stay on "
                    f"{target_conn.getHostname()}"
                )
        
        return migration_plan
    
    except Exception as e:
        logger.error(f"Error during server consolidation: {str(e)}")
        raise

def can_host(conn, vm, solution):
    """Helper function to check if a hypervisor can host a VM"""
    try:
        host_resources = get_hypervisor_resource_usage(conn, 0)
        host_cpu = host_resources['cpu']
        host_memory = host_resources['memory']
        
        vm_resources = get_vm_resource_usage(vm, 0)
        vm_cpu = vm_resources['cpu']
        vm_memory = vm_resources['memory']
        
        current_cpu_usage = sum(get_vm_resource_usage(v, 0)['cpu'] for v in solution[conn])
        current_memory_usage = sum(get_vm_resource_usage(v, 0)['memory'] for v in solution[conn])
        
        can_host = (host_cpu >= current_cpu_usage + vm_cpu and
                   host_memory >= current_memory_usage + vm_memory)
        
        logger.debug(
            f"Host check - Hypervisor: {conn.getHostname()} "
            f"VM: {vm.name()} "
            f"Result: {can_host} "
            f"(CPU: {current_cpu_usage + vm_cpu:.1f}/{host_cpu:.1f}%, "
            f"Mem: {(current_memory_usage + vm_memory)/1024/1024:.1f}/{host_memory/1024/1024:.1f}MB)"
        )
        return can_host
    except Exception as e:
        logger.error(f"Error checking host capabilities: {str(e)}")
        return False