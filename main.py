

from utils.connect import connect_hypervisor
from utils.migration import migrate_vm
from ServerConsolidation.algorithms.ff import ff_server_consolidation
from ServerConsolidation.algorithms.simulated_annealing import sa_server_consolidation
from ServerConsolidation.algorithms.genetic_algorithm import genetic_algorithm_server_consolidation
from ServerConsolidation.algorithms.bfd import bfd_server_consolidation



def choose_algorithm():
    print("Choose a consolidation algorithm:")
    print("1. First fit")
    print("2. Simulated Annealing (SA)")
    print("3. enetic_algorithm_server_consolidation")
    print("4. bfd_server_consolidation")
    
 
    
    while True:
        choice = input("Enter the number of your choice: ")
        if choice == "1":
            return ff_server_consolidation
        elif choice == "2":
            return sa_server_consolidation
        elif choice == "3":
            return genetic_algorithm_server_consolidation
        elif choice == "4":
            return bfd_server_consolidation

        
    
        else:
            print("Invalid choice. Please try again.")

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

    # Choose the consolidation algorithm
    consolidation_algorithm = choose_algorithm()

    # Use the chosen algorithm for VM consolidation
    migration_plan = consolidation_algorithm(source_conns, all_vms)

    # Execute the migration plan
    for vm, target_conn in migration_plan.items():
        print(f"Migrating {vm.name()} to {target_conn.getHostname()}")
        migrate_vm(vm.connect(), target_conn, vm.name())

    # Close connections
    for conn in source_conns:
        conn.close()