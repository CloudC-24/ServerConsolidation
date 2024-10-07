import libvirt

host_ips = [
    "qemu:///system",
    "qemu+ssh://yogi@192.168.239.103/system",
]      

def connect_to_hypervisor(ip):
    try:
        conn = libvirt.open(ip)
        
        if conn is None:
            print('Failed to open connection to qemu+ssh://user@192.168.239.185/system')
            return None
        
        print(f'Successfully connected to {ip} the QEMU hypervisor')
        return conn
    except libvirt.libvirtError as e:
        print(f'Failed to connect to the hypervisor: {e}')
        return None

for ip in host_ips:
    hypervisor_connection = connect_to_hypervisor(ip)
    print("Listing the running VM's in the associated hypervisor")
    if hypervisor_connection:
        for vm_id in hypervisor_connection.listDomainsID():
            vm = hypervisor_connection.lookupByID(vm_id)
            print(f'Running VM: {vm.name()}')
