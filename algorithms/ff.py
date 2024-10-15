from utils import get_vm_resource_usage, get_hypervisor_resource_usage

def ff_server_consolidation(source_conns, vm_list):
    migration_plan = {}
    for vm in vm_list:
        for conn in source_conns:
            if can_fit_vm_on_hypervisor(vm, conn):
                migration_plan[vm] = conn
                update_hypervisor_resources(conn, vm)
                break  # Move to next VM once we find a suitable hypervisor
    return migration_plan

def can_fit_vm_on_hypervisor(vm, hypervisor_conn):
    vm_usage = get_vm_resource_usage(vm)
    hypervisor_avail = get_hypervisor_resource_usage(hypervisor_conn)
    
    return (hypervisor_avail['cpu'] >= vm_usage['cpu'] and 
            hypervisor_avail['memory'] >= vm_usage['memory'])

def update_hypervisor_resources(hypervisor_conn, vm):
    vm_usage = get_vm_resource_usage(vm)
    hypervisor_avail = get_hypervisor_resource_usage(hypervisor_conn)
    
    # Update the available resources
    hypervisor_avail['cpu'] -= vm_usage['cpu']
    hypervisor_avail['memory'] -= vm_usage['memory']