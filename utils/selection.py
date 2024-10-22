import random

def roulette_wheel_selection(population, fitness_scores):
    total_fitness = sum(fitness_scores)
    relative_fitness = [f / total_fitness for f in fitness_scores]
    cumulative_probability = [sum(relative_fitness[:i+1]) for i in range(len(relative_fitness))]

    rand = random.random()
    for i, cp in enumerate(cumulative_probability):
        if rand <= cp:
            return population[i]
        
def selection(population, fitness_scores):
    first_selection = roulette_wheel_selection(population, fitness_scores)
    second_selection = roulette_wheel_selection(population,fitness_scores)
    return [first_selection,second_selection]