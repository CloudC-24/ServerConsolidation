from utils.get_vm_resource_usage import get_vm_resource_usage
from utils.get_hypervisor_resource_usage import get_hypervisor_resource_usage

def bfd_server_consolidation(source_conns, all_vms):
    migration_plan = {}
    
    vm_list = [(vm, conn) for conn, vms in all_vms.items() for vm in vms]
    
    vm_list.sort(key=lambda x: get_vm_resource_usage(x[0])['cpu'], reverse=True)

    hypervisor_resources = {
        conn: get_hypervisor_resource_usage(conn) for conn in source_conns
    }
    
    source_conns.sort(key=lambda conn: hypervisor_resources[conn]['cpu'], reverse=True)
    
    target_conn = source_conns[0]
    
    for vm, current_conn in vm_list:
        vm_usage = get_vm_resource_usage(vm)
        
        if can_fit_vm_on_hypervisor(vm_usage, hypervisor_resources[target_conn]):
            if current_conn != target_conn:
                migration_plan[vm] = target_conn
                hypervisor_resources[target_conn]['cpu'] -= vm_usage['cpu']
                hypervisor_resources[target_conn]['memory'] -= vm_usage['memory']
                
                hypervisor_resources[current_conn]['cpu'] += vm_usage['cpu']
                hypervisor_resources[current_conn]['memory'] += vm_usage['memory']
            else:
                print(f"VM {vm.name()} is already on the target hypervisor.")
        else:
            print(f"Warning: Cannot fit VM {vm.name()} on the target hypervisor.")
            if current_conn != target_conn:
                print(f"VM {vm.name()} will remain on its current hypervisor.")
    
    return migration_plan

def can_fit_vm_on_hypervisor(vm_usage, hypervisor_avail):
    return (
        hypervisor_avail['cpu'] >= vm_usage['cpu'] and
        hypervisor_avail['memory'] >= vm_usage['memory']
    )