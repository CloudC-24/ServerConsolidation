# Algorithms: Memory Allocation

## First Fit Decreasing Memory (FFDM)

1. The First Fit Decreasing algorithm is used for bin packing problems, which in our case is server consolidation. The goal is to efficiently distribute virtual machines (VMs) across physical servers (hypervisors) to minimize the number of active servers while ensuring each server has enough resources to run its assigned VMs.
2. Key Characteristics of FFD:
    - The algorithm sorts VMs in descending order of resource usage.
    - It then places each VM on the first hypervisor that can accommodate it.
    - The order of hypervisors remains constant throughout the process.
3. Advantages of FFD:
    - simple to implement and understand.
    - Generally produces good results for bin packing problems.
    - Efficient in terms of time complexity (O(n log n) for sorting, then O(n*m) for placement, where n is the number of VMs and m is the number of hypervisors).
4. Disadvantages of FFD:
    - May not always produce the optimal solution.
    - Can lead to fragmentation of resources, especially if VMs are not sorted optimally.

## Ant Colony System Algorithm (ACS)

* The main reason of selecting the ACS algorithm for our research is that our main
problem i.e the Virtual Machine Placement problem is a NP-hard problem as well
as a Combinatorial Optimization Problem (COP) which means that this problem
has a finite set of solutions but in order to choose the best solution we need an EC
Algorithm. An EC algorithm is an evolutionary computation algorithm that helps
to improve the resource utilization and reduce energy consumption of our VMP
problem. Out of all EC algorithms, the Ant Colony System algorithm addresses the
problem more eﬃciently with strong logical inference.
