from utils import get_vm_resource_usage, get_hypervisor_resource_usage

def bfd_server_consolidation(source_conns, vm_list):
  
    vm_list.sort(key=lambda vm: get_vm_resource_usage(vm), reverse=True)

    source_conns.sort(key=lambda conn: get_hypervisor_resource_usage(conn))

    migration_plan = {}

    for vm in vm_list:
        for conn in source_conns:
            if can_fit_vm_on_hypervisor(vm, conn): 
                migration_plan[vm] = conn
                break  

    return migration_plan

def can_fit_vm_on_hypervisor(vm, hypervisor_conn):
    vm_usage = get_vm_resource_usage(vm)
    hypervisor_avail = get_hypervisor_resource_usage(hypervisor_conn)
    
    return hypervisor_avail['cpu'] >= vm_usage['cpu'] and hypervisor_avail['memory'] >= vm_usage['memory']