from utils.connect import connect_hypervisor
from utils.migration import migrate_vm
from algorithms.bfd import bfd_server_consolidation

if __name__ == "__main__":
    hypervisor_uris = [
        "qemu:///system",
        "qemu+ssh://sushant@192.168.139.38/system"
    ]
     
    source_conns = [connect_hypervisor(uri) for uri in hypervisor_uris]

    all_vms = {}

    for conn in source_conns:
        vm_list = conn.listAllDomains()
        print(vm_list)
        all_vms[conn] = vm_list

    # migrate_vm(source_conn=source_conns[0],dest_conn=source_conns[1],vm_name="parth@linux2022")
    
    migration_plan = bfd_server_consolidation(source_conns, all_vms)


    for vm, target_conn in migration_plan.items():
        print(f"Migrating {vm.name()} to {target_conn.getHostname()}")
        # migrate_vm(source_conns[0], target_conn, vm.name())

    for conn in source_conns:
        conn.close()