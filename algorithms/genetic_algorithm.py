import random
from utils import get_vm_resource_usage, get_hypervisor_resource_usage

def genetic_algorithm_server_consolidation(source_conns, all_vms, population_size=50, generations=100, mutation_rate=0.1, elite_size=2):
    vm_list = [vm for vms in all_vms.values() for vm in vms]
    
    population = [list(range(len(vm_list))) for _ in range(population_size)]
    for chromosome in population:
        random.shuffle(chromosome)
    
    for generation in range(generations):
        fitness_scores = [fitness(chromosome, source_conns, vm_list) for chromosome in population]
        
        elite = sorted(zip(fitness_scores, population), key=lambda x: x[0], reverse=True)[:elite_size]
        elite_fitness, elite_chromosomes = zip(*elite)
        
        selected = selection(population, fitness_scores)
        
        new_population = list(elite_chromosomes) 
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])
        new_population = new_population[:population_size] 
        
        for chromosome in new_population[elite_size:]: 
            if random.random() < mutation_rate:
                mutate(chromosome)
        
        population = new_population
    
    best_chromosome = max(population, key=lambda x: fitness(x, source_conns, vm_list))
    
    migration_plan = {}
    for i, vm_index in enumerate(best_chromosome):
        vm = vm_list[vm_index]
        target_conn = ffd_allocate(vm, source_conns)
        migration_plan[vm] = target_conn
    
    return migration_plan

def fitness(chromosome, source_conns, vm_list):

    allocated_conns = []
    server_loads = {conn: {'cpu': 0, 'memory': 0} for conn in source_conns}
    
    for vm_index in chromosome:
        vm = vm_list[vm_index]
        conn = ffd_allocate(vm, source_conns, server_loads)
        allocated_conns.append(conn)

        vm_usage = get_vm_resource_usage(vm)
        server_loads[conn]['cpu'] += vm_usage['cpu']
        server_loads[conn]['memory'] += vm_usage['memory']

    unique_conns = len(set(allocated_conns))
    
    cpu_loads = [load['cpu'] for load in server_loads.values() if load['cpu'] > 0]
    memory_loads = [load['memory'] for load in server_loads.values() if load['memory'] > 0]
    cpu_balance = max(cpu_loads) - min(cpu_loads) if cpu_loads else 0
    memory_balance = max(memory_loads) - min(memory_loads) if memory_loads else 0
    balance_factor = cpu_balance + memory_balance
    
    return 1 / (unique_conns + balance_factor * 0.1) 

def ffd_allocate(vm, source_conns, server_loads):
    vm_usage = get_vm_resource_usage(vm)
    for conn in sorted(source_conns, key=lambda c: (-server_loads[c]['cpu'], -server_loads[c]['memory'])):
        hypervisor_avail = get_hypervisor_resource_usage(conn)
        if hypervisor_avail['cpu'] >= vm_usage['cpu'] and hypervisor_avail['memory'] >= vm_usage['memory']:
            return conn
    return min(source_conns, key=lambda c: server_loads[c]['cpu'] + server_loads[c]['memory'])

def selection(population, fitness_scores):
    tournament_size = 3
    selected = []
    for _ in range(len(population)):
        tournament = random.sample(list(enumerate(fitness_scores)), tournament_size)
        winner = max(tournament, key=lambda x: x[1])[0]
        selected.append(population[winner])
    return selected

def crossover(parent1, parent2):
    crossover_point1 = random.randint(0, len(parent1) - 2)
    crossover_point2 = random.randint(crossover_point1 + 1, len(parent1) - 1)
    
    child1 = parent1[crossover_point1:crossover_point2]
    child2 = parent2[crossover_point1:crossover_point2]
    
    def fill_child(child, parent):
        for gene in parent:
            if gene not in child:
                child.append(gene)
        return child
    
    child1 = fill_child(child1, parent2 + parent1)
    child2 = fill_child(child2, parent1 + parent2)
    
    return child1, child2

def mutate(chromosome):
    i, j = random.sample(range(len(chromosome)), 2)
    chromosome[i], chromosome[j] = chromosome[j], chromosome[i]