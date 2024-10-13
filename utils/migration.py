import libvirt

def migrate_vm(source_conn, dest_conn, vm_name):
    try:
        dom = source_conn.lookupByName(vm_name)
        if dom is None:
            raise SystemExit(f"Domain {vm_name} not found on the source hypervisor.")
        
        print(f"Starting migration for VM: {vm_name}")
        
        flags = libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_UNSAFE | libvirt.VIR_MIGRATE_NON_SHARED_DISK 
        newDOM = dom.migrate(dest_conn, flags=flags, dname=None, uri=None, bandwidth=100)
        
        if newDOM is None:
            raise SystemExit("Migration failed: Could not migrate to the destination hypervisor.")
        else:
            print(f"New domain created after migration: {newDOM}")
        
        print(f"Domain {vm_name} was migrated successfully.")
    
    except libvirt.libvirtError as e:
        print(f"Libvirt error during migration of {vm_name}: {e.get_error_message()}")
        print(f"Migration failed for VM {vm_name} from {source_conn.getURI()} to {dest_conn.getURI()}.")
    
    except Exception as e:
        print(f"An unexpected error occurred during migration: {str(e)}")