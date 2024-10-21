import libvirt
import sys
import os
from xml.etree import ElementTree
import time

# Connect to the hypervisor
conn = libvirt.open("qemu:///system")
if conn is None:
    print("Failed to open connection to qemu:///system", file=sys.stderr)
    sys.exit(1)

# Get list of all VMs (running and inactive)
domains = conn.listAllDomains()

# Check if any VMs exist
if len(domains) == 0:
    print("No virtual machines found")
    sys.exit(0)

# Function to get detailed information about a VM
def get_vm_details(domain):
    info = domain.info()
    # Domain state
    state = {
        libvirt.VIR_DOMAIN_NOSTATE: "no state",
        libvirt.VIR_DOMAIN_RUNNING: "running",
        libvirt.VIR_DOMAIN_BLOCKED: "blocked",
        libvirt.VIR_DOMAIN_PAUSED: "paused",
        libvirt.VIR_DOMAIN_SHUTDOWN: "shut down",
        libvirt.VIR_DOMAIN_SHUTOFF: "shut off",
        libvirt.VIR_DOMAIN_CRASHED: "crashed",
        libvirt.VIR_DOMAIN_PMSUSPENDED: "pmsuspended",
    }

    print(f"Name: {domain.name()}")
    print(f"ID: {domain.ID() if domain.ID() != -1 else 'N/A'}")
    print(f"UUID: {domain.UUIDString()}")
    print(f"State: {state[info[0]]}")
    print(f"Max Memory: {info[1] / 1024} MB")
    print(f"Used Memory: {info[2] / 1024} MB")
    print(f"vCPUs: {info[3]}")
    print(f"CPU Time: {info[4] / 1e9} seconds")

    # Get disk details
    tree = ElementTree.fromstring(domain.XMLDesc())
    for disk in tree.findall('./devices/disk/target'):
        dev = disk.get('dev')
        print(f"Disk Device: {dev}")
        block_info = domain.blockInfo(dev)
        print(f"Disk Capacity: {block_info[0] / (1024 ** 3):.2f} GB")
        print(f"Disk Allocation: {block_info[1] / (1024 ** 3):.2f} GB")
        print(f"Disk Physical Size: {block_info[2] / (1024 ** 3):.2f} GB")

    # Get network details
    for interface in tree.findall('./devices/interface/target'):
        dev = interface.get('dev')
        print(f"Network Interface: {dev}")
        iface_stats = domain.interfaceStats(dev)
        print(f"RX bytes: {iface_stats[0]}")
        print(f"TX bytes: {iface_stats[4]}")

    print("\n" + "-"*30 + "\n")

# Iterate over all VMs and print details
for domain in domains:
    get_vm_details(domain)

def get_cpu_usage(domain, interval=1):
    vcpus = domain.info()[3]

    cpu_time_1 = domain.info()[4]

    time.sleep(interval)

    cpu_time_2 = domain.info()[4]

    cpu_time_diff = cpu_time_2 - cpu_time_1

    cpu_usage = (cpu_time_diff / (interval * 1e9 * vcpus)) * 100
    return cpu_usage

# Function to print CPU usage details for all VMs
def print_cpu_usage(domains):
    for domain in domains:
        print(f"Name: {domain.name()}")
        cpu_usage = get_cpu_usage(domain)
        print(f"CPU Usage: {cpu_usage:.2f}%\n")

# Print CPU usage for all VMs
print_cpu_usage(domains)

def get_hypervisor_cpu_usage(interval=1):
    # Get initial CPU statistics from the hypervisor
    cpu_stats_1 = conn.getCPUStats(-1, 0)  # -1 means get the stats of the host (hypervisor)
    
    # Total CPU time is the sum of kernel time, user time, and possibly other stats
    total_time_1 = cpu_stats_1['kernel'] + cpu_stats_1['user']

    # Get the number of physical CPUs (cores) on the host
    cpu_count = conn.getInfo()[2]

    # Wait for the interval (e.g., 1 second)
    time.sleep(interval)

    # Get CPU statistics again after the interval
    cpu_stats_2 = conn.getCPUStats(-1, 0)

    # Calculate the total CPU time for the second measurement
    total_time_2 = cpu_stats_2['kernel'] + cpu_stats_2['user']

    # Calculate the CPU time difference (in nanoseconds)
    cpu_time_diff = total_time_2 - total_time_1

    # Convert to percentage over the interval
    cpu_usage = (cpu_time_diff / (interval * 1e9 * cpu_count)) * 100
    return cpu_usage

# Function to print CPU usage of the hypervisor
def print_hypervisor_cpu_usage():
    cpu_usage = get_hypervisor_cpu_usage()
    print(f"Hypervisor (Host) CPU Usage: {cpu_usage:.2f}%")

# Print the CPU usage of the hypervisor
print_hypervisor_cpu_usage()

# Close the connection to the hypervisor
conn.close()
