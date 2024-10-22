from utils.get_vm_resource_usage import get_vm_resource_usage
from utils.get_hypervisor_resource_usage import get_hypervisor_resource_usage

def pabfd_server_consolidation(source_conns, all_vms):
    migration_plan = {}
    
    # Flatten the list of all VMs from multiple hypervisors
    vm_list = [vm for vms in all_vms.values() for vm in vms]
    
    # Sort VMs by CPU usage in descending order (largest VMs first)
    vm_list.sort(key=lambda vm: get_vm_resource_usage(vm)['cpu'], reverse=True)
    
    # Get resource availability for each hypervisor
    hypervisor_resources = {
        conn: get_hypervisor_resource_usage(conn) for conn in source_conns
    }
    
    print("Initial Hypervisor Resources:")
    print(hypervisor_resources)

    # Iterate over the VMs and try to fit them on the best hypervisor
    for vm in vm_list:
        vm_usage = get_vm_resource_usage(vm)
        print(f"Evaluating VM {vm.name()} with resource usage {vm_usage}")

        # Try to find a hypervisor that can fit this VM
        for conn in source_conns:
            hypervisor_avail = hypervisor_resources[conn]
            
            # Check if the current hypervisor has enough CPU and memory to host the VM
            if can_fit_vm_on_hypervisor(vm_usage, hypervisor_avail):
                # Assign the VM to this hypervisor in the migration plan
                migration_plan[vm] = conn
                
                # Update the available resources of the hypervisor
                hypervisor_resources[conn]['cpu'] -= vm_usage['cpu']
                hypervisor_resources[conn]['memory'] -= vm_usage['memory']
                
                print(f"Placing VM {vm.name()} on Hypervisor {conn.getHostname()}. Updated resources: {hypervisor_resources[conn]}")
                break
        else:
            # If no hypervisor could fit the VM, print a warning
            print(f"Warning: No hypervisor can fit VM {vm.name()}. Skipping migration.")
    
    return migration_plan

# Function to check if a VM can fit on a given hypervisor based on available CPU and memory
def can_fit_vm_on_hypervisor(vm_usage, hypervisor_avail):
    # Check both CPU and memory availability
    return hypervisor_avail['cpu'] >= vm_usage['cpu'] and hypervisor_avail['memory'] >= vm_usage['memory']