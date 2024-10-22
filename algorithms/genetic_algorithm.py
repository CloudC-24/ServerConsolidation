import random
import logging
from utils.get_vm_resource_usage import get_vm_resource_usage
from utils.get_hypervisor_resource_usage import get_hypervisor_resource_usage
from utils.selection import selection
from utils.crossover import crossover
from utils.mutate import mutate
# Configure logging with shorter format
logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

def genetic_algorithm_server_consolidation(source_conns, all_vms, population_size=10, generations=10, mutation_rate=0.1, elite_size=2):
    logger.info(f"Start: {len(all_vms)} VM groups, {len(source_conns)} servers")
    logger.info(f"Config: pop={population_size}, gen={generations}, mut={mutation_rate}, elite={elite_size}")
    
    vm_list = [vm for vms in all_vms.values() for vm in vms]
    print(vm_list)
    logger.info(f"Total VMs: {len(vm_list)}")
    
    # Log initial server states
    logger.info("Initial server resources:")
    for conn in source_conns:
        resources = get_hypervisor_resource_usage(conn,0)
        logger.info(f"Server {conn}: {resources}")
    
    population = [list(range(len(vm_list))) for _ in range(population_size)]


    for chromosome in population:
        random.shuffle(chromosome)

    best_fitness = float('-inf')
    gens_no_improvement = 0

    for generation in range(generations):
        logger.info(f"Processing generation {generation}")
        fitness_scores = []
        for chromosome in population:
            try:
                score = fitness(chromosome, source_conns, vm_list)
                fitness_scores.append(score)
            except Exception as e:
                logger.error(f"Error calculating fitness: {e}")
                fitness_scores.append(float('-inf'))
        
        current_best_fitness = max(fitness_scores)
        
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            gens_no_improvement = 0
            logger.info(f"Gen {generation}: New best={best_fitness:.4f}")
        else:
            gens_no_improvement += 1
            
        if generation % 10 == 0:
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            logger.info(f"Gen {generation}: Avg={avg_fitness:.4f} Best={current_best_fitness:.4f}")
        
        # Break if no improvement for many generations
        if gens_no_improvement > 3:
            logger.info("Stopping early due to no improvement")
            break
            
        elite = sorted(zip(fitness_scores, population), key=lambda x: x[0], reverse=True)[:elite_size]
        elite_fitness, elite_chromosomes = zip(*elite)
        
        # Write Roullete wheel for this 
        selected = selection(population, fitness_scores)

        new_population = list(elite_chromosomes)
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])
        new_population = new_population[:population_size]
        
        mutations = 0
        for chromosome in new_population[elite_size:]:
            if random.random() < mutation_rate:
                chromosome = mutate(chromosome)
                mutations += 1
        
        population = new_population
    
    logger.info("Finding best solution...")
    best_chromosome = max(population, key=lambda x: fitness(x, source_conns, vm_list))
    
    # Create migration plan
    migration_plan = {}
    server_loads = {conn: {'cpu': 0, 'memory': 0} for conn in source_conns}
    
    logger.info("Creating migration plan...")
    for i, vm_index in enumerate(best_chromosome):
        vm = vm_list[vm_index]
        target_conn = ffd_allocate(vm, source_conns, server_loads)
        migration_plan[vm] = target_conn
        
        vm_usage = get_vm_resource_usage(vm,0)
        server_loads[target_conn]['cpu'] += vm_usage['cpu']
        server_loads[target_conn]['memory'] += vm_usage['memory']
    
    # Log final stats
    used_servers = sum(1 for conn in server_loads if any(v > 0 for v in server_loads[conn].values()))
    logger.info(f"\nFinal: Using {used_servers}/{len(source_conns)} servers")
    
    for conn, loads in server_loads.items():
        logger.info(f"Server {conn}: CPU={loads['cpu']:.1f}%, Mem={loads['memory']:.1f}%")
    
    return migration_plan

def ffd_allocate(vm, source_conns, server_loads):
    vm_usage = get_vm_resource_usage(vm,0)
    logger.info(f"Allocating VM with usage: CPU={vm_usage['cpu']}%, Memory={vm_usage['memory']}")
    
    for conn in sorted(source_conns, key=lambda c: (-server_loads[c]['cpu'], -server_loads[c]['memory'])):
        try:
            hypervisor_avail = get_hypervisor_resource_usage(conn,0)
            available_cpu = hypervisor_avail['cpu']
            available_memory = hypervisor_avail['memory']
            
            if available_cpu >= vm_usage['cpu'] and available_memory >= vm_usage['memory']:
                logger.info(f"Found suitable server {conn}")
                return conn
        except Exception as e:
            logger.error(f"Error checking server {conn}: {e}")
    
    # If no server has enough resources, return the least loaded server
    logger.warning("No server has ideal resources, selecting least loaded server")
    return min(source_conns, key=lambda c: server_loads[c]['cpu'] + server_loads[c]['memory'])

def fitness(chromosome, source_conns, vm_list):
    allocated_conns = []
    server_loads = {conn: {'cpu': 0, 'memory': 0} for conn in source_conns}
    
    for vm_index in chromosome:
        vm = vm_list[vm_index]
        conn = ffd_allocate(vm, source_conns, server_loads)
        allocated_conns.append(conn)
        
        vm_usage = get_vm_resource_usage(vm,0)
        server_loads[conn]['cpu'] += vm_usage['cpu']
        server_loads[conn]['memory'] += vm_usage['memory']
    
    unique_conns = len(set(allocated_conns))
    
    cpu_loads = [load['cpu'] for load in server_loads.values() if load['cpu'] > 0]
    memory_loads = [load['memory'] for load in server_loads.values() if load['memory'] > 0]
    cpu_balance = max(cpu_loads) - min(cpu_loads) if cpu_loads else 0
    memory_balance = max(memory_loads) - min(memory_loads) if memory_loads else 0
    balance_factor = cpu_balance + memory_balance
    
    return 1 / (unique_conns + balance_factor * 0.1)