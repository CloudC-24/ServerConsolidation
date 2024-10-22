import random

def mutate(chromosome):
    original = chromosome.copy()
    
    pos1, pos2 = random.sample(range(len(chromosome)), 2)
    
    chromosome[pos1], chromosome[pos2] = chromosome[pos2], chromosome[pos1]
    
    # logger.info(f"Mutation: {original} => {chromosome} (swapped positions {pos1} and {pos2})")
    
    return chromosome