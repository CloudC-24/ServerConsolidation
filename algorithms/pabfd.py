# algorithms/pabfd.py

def power_aware_best_fit_decreasing(source_conns, all_vms):
    """
    Power-Aware Best Fit Decreasing (PABFD) algorithm for server consolidation.
    Tries to minimize power usage while consolidating VMs on fewer active hypervisors.

    Parameters:
        source_conns (list): List of connections to hypervisors.
        all_vms (dict): Dictionary where key is the hypervisor connection, and value is a list of VMs on that hypervisor.

    Returns:
        migration_plan (dict): Dictionary where key is the VM, and value is the target connection (hypervisor) for migration.
    """
    # Step 1: Gather resource information (e.g., memory or CPU usage) for each hypervisor
    hypervisor_resources = {}
    active_hypervisors = set()
    
    for conn in source_conns:
        total_memory = conn.getInfo()[1]  # Get total memory of hypervisor (in MB)
        used_memory = sum([vm.info()[2] for vm in all_vms[conn]])  # Sum of memory used by VMs on this hypervisor
        
        hypervisor_resources[conn] = {'total_memory': total_memory, 'used_memory': used_memory}
        if used_memory > 0:
            active_hypervisors.add(conn)  # Mark as active if there are any VMs on the hypervisor

    # Step 2: Create a list of VMs sorted by decreasing resource demand (e.g., memory usage)
    vm_list = []
    for conn, vms in all_vms.items():
        for vm in vms:
            vm_memory = vm.info()[2]  # Memory used by the VM (in MB)
            vm_list.append((vm, vm_memory, conn))

    vm_list.sort(key=lambda x: x[1], reverse=True)  # Sort by memory usage in decreasing order

    # Step 3: Power-Aware Best Fit Decreasing (PABFD) consolidation
    migration_plan = {}

    for vm, vm_memory, src_conn in vm_list:
        best_fit_conn = None
        min_waste = float('inf')

        # Try to place the VM in the best fit hypervisor to minimize waste
        for conn, resources in hypervisor_resources.items():
            available_memory = resources['total_memory'] - resources['used_memory']
            
            if available_memory >= vm_memory:
                waste = available_memory - vm_memory
                # Power-aware: prioritize active hypervisors
                if conn in active_hypervisors:
                    # If the hypervisor is active and has enough resources, prefer it
                    if waste < min_waste:
                        min_waste = waste
                        best_fit_conn = conn
                else:
                    # If no active hypervisor can accommodate, consider inactive ones
                    if best_fit_conn is None or waste < min_waste:
                        min_waste = waste
                        best_fit_conn = conn

        # If a suitable hypervisor is found, add the VM to the migration plan
        if best_fit_conn and best_fit_conn != src_conn:
            migration_plan[vm] = best_fit_conn
            # Update the used memory of the target hypervisor
            hypervisor_resources[best_fit_conn]['used_memory'] += vm_memory
            # Update the source hypervisor used memory
            hypervisor_resources[src_conn]['used_memory'] -= vm_memory

            # Mark the target hypervisor as active
            active_hypervisors.add(best_fit_conn)

    return migration_plan
