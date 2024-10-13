import libvirt

def connect_hypervisor(uri):
    try:
        conn = libvirt.open(uri)
        if conn is None:
            print(f"Failed to open connection to {uri}")
            return None
        print(f"Successfully connected to {uri}")
        return conn
    except libvirt.libvirtError as e:
        print(f"Connection to {uri} failed: {e}")
        return None