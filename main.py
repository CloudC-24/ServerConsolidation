from utils.connect import connect_hypervisor
from utils.migration import migrate_vm
from algorithms.dfd import bfd_server_consolidation

if __name__ == "__main__":
    hypervisor_uris = [
        "qemu:///system",
        "qemu+ssh://sushant@192.168.56.38/system"
    ]

    source_conns = [connect_hypervisor(uri) for uri in hypervisor_uris]

    vm_list = source_conns[0].listAllDomains()

    migration_plan = bfd_server_consolidation(source_conns, vm_list)

    for vm, target_conn in migration_plan.items():
        print(f"Migrating {vm.name()} to {target_conn.getHostname()}")
        migrate_vm(source_conns[0], target_conn, vm.name())

    for conn in source_conns:
        conn.close()