from utils import get_vm_resource_usage, get_hypervisor_resource_usage

def bfd_server_consolidation(source_conns, all_vms):
    migration_plan = {}

    vm_list = [vm for vms in all_vms.values() for vm in vms]

    vm_list.sort(key=lambda vm: get_vm_resource_usage(vm), reverse=True)

    source_conns.sort(key=lambda conn: get_hypervisor_resource_usage(conn))

    hypervisor_resources = {
        conn: get_hypervisor_resource_usage(conn) for conn in source_conns
    }

    for vm in vm_list:
        vm_usage = get_vm_resource_usage(vm)
        for conn in source_conns:
            hypervisor_avail = hypervisor_resources[conn]

            if can_fit_vm_on_hypervisor(vm_usage, hypervisor_avail):
                migration_plan[vm] = conn
                hypervisor_resources[conn]['cpu'] -= vm_usage['cpu']
                hypervisor_resources[conn]['memory'] -= vm_usage['memory']
                break
        else:
            print(f"Warning: No hypervisor can fit VM {vm.name()}.")

        source_conns.sort(key=lambda conn: hypervisor_resources[conn])

    return migration_plan

def can_fit_vm_on_hypervisor(vm, hypervisor_conn):
    vm_usage = get_vm_resource_usage(vm)
    hypervisor_avail = get_hypervisor_resource_usage(hypervisor_conn)
    
    return hypervisor_avail['cpu'] >= vm_usage['cpu'] and hypervisor_avail['memory'] >= vm_usage['memory']