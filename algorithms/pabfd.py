from utils.get_vm_resource_usage import get_vm_resource_usage
from utils.get_hypervisor_resource_usage import get_hypervisor_resource_usage

def pabfd_server_consolidation(source_conns, all_vms):
    migration_plan = {}
    vm_list = [vm for vms in all_vms.values() for vm in vms]
    vm_list.sort(key=lambda vm: get_vm_resource_usage(vm)['cpu'], reverse=True)
    
    hypervisor_resources = {
        conn: get_hypervisor_resource_usage(conn) for conn in source_conns
    }
    
    print(hypervisor_resources)

    for vm in vm_list:
        vm_usage = get_vm_resource_usage(vm)
        print(vm.name(), vm_usage)
        for conn in source_conns:
            hypervisor_avail = hypervisor_resources[conn]
            if can_fit_vm_on_hypervisor(vm_usage, hypervisor_avail):
                migration_plan[vm] = conn
                hypervisor_resources[conn]['cpu'] -= vm_usage['cpu']
                hypervisor_resources[conn]['memory'] -= vm_usage['memory']
                break
        else:
            print(f"Warning: No hypervisor can fit VM {vm.name()}.")
    
    return migration_plan

def can_fit_vm_on_hypervisor(vm_usage, hypervisor_avail):
    return hypervisor_avail['cpu'] >= vm_usage['cpu'] and hypervisor_avail['memory'] >= vm_usage['memory']