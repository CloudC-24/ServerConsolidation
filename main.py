from utils.connect import connect_hypervisor
from utils.migration import migrate_vm
from algorithms.bfd import bfd_server_consolidation

if __name__ == "__main__":
    hypervisor_uris = [
        "qemu:///system",
        "qemu+ssh://yogi@[2402:e280:217b:338:1ef6:4461:a182:d39e]/system"
    ]
     
    source_conns = [connect_hypervisor(uri) for uri in hypervisor_uris]

    all_vms = {}

    for conn in source_conns:
        vm_list = conn.listAllDomains()
        all_vms[conn] = vm_list

    migration_plan = bfd_server_consolidation(source_conns, all_vms)

    for vm, target_conn in migration_plan.items():
        print(f"Migrating {vm.name()} to {target_conn.getHostname()}")
        migrate_vm(source_conns[0], target_conn, vm.name())

    for conn in source_conns:
        conn.close()