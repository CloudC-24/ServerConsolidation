import random
def crossover(parent1, parent2):
    length = len(parent1)
    
    start = random.randint(0, length - 2)
    end = random.randint(start + 1, length - 1)
    
    child1 = [None] * length
    child2 = [None] * length
    
    child1[start:end] = parent1[start:end]
    child2[start:end] = parent2[start:end]
    
    remaining_positions1 = list(range(0, start)) + list(range(end, length))
    remaining_values1 = [x for x in parent2 if x not in parent1[start:end]]
    for pos, val in zip(remaining_positions1, remaining_values1):
        child1[pos] = val
        
    remaining_positions2 = list(range(0, start)) + list(range(end, length))
    remaining_values2 = [x for x in parent1 if x not in parent2[start:end]]
    for pos, val in zip(remaining_positions2, remaining_values2):
        child2[pos] = val
    
    return child1, child2