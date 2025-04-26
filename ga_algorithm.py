import math
import random
import statistics

def generate_population(population_size, number_of_genes):
    return [
        [random.choice([0, 1]) for _ in range(number_of_genes)]
        for _ in range(population_size)
    ]
    
def shubert(x1, x2):
    sum1 = sum(i * math.cos((i + 1) * x1 + i) for i in range(1, 6))
    sum2 = sum(i * math.cos((i + 1) * x2 + i) for i in range(1, 6))
    return sum1 * sum2
            
def camel(x1, x2):
    term1 = (4 - 2.1 * x1**2 + x1**4 / 3) * x1**2
    term2 = x1 * x2
    term3 = (-4 + 4 * x2**2) * x2**2
    return term1 + term2 + term3

def fitness(population, data_config):
    scores = {}
    
    for c_index, chromossome in enumerate(population):
        tamanho_total = len(chromossome)
        ponto_medio = tamanho_total // 2

        # Conversão dos bits para float corrigida
        x1_key = int("".join([str(chromossome[index]) for index in range(ponto_medio)]), 2)
        x1 = data_config['x1']['base'] + x1_key * data_config['x1']['precision']

        x2_key = int("".join([str(chromossome[index]) for index in range(ponto_medio, tamanho_total)]), 2)
        x2 = data_config['x2']['base'] + x2_key * data_config['x2']['precision']

        if data_config.get('problem') == 'shubert':
            raw_value = shubert(x1, x2)
        elif data_config.get('problem') == 'camel':
            raw_value = camel(x1, x2)
        
        # Corrigir para valores negativos: translação
        scores[c_index] = 1 / (200 + raw_value)

    return scores

def build_rigged_roulette(scores):
    total_score = sum(scores.values())
    roulette = {}
    cumulative = 0
    for c_index, score in scores.items():
        probability = score / total_score
        roulette[c_index] = (cumulative, cumulative + probability)
        cumulative += probability
    return roulette

def tournament(scores, window):
    indices = list(scores.keys())
    competitors_list = [random.choice(indices) for _ in range(window)]
    competitors = {id: scores[id] for id in competitors_list}
    winner_id = max(competitors, key=competitors.get)
    return winner_id

def chromosome_crossover(population, scores, competition_code, probability_of_crossing):
    def merge_genes(parent_1, parent_2):
        cut_point_1 = random.randint(1, 19)
        cut_point_2 = cut_point_1 + 20

        x1_parent_1 = parent_1[:cut_point_1]
        x1_parent_2 = parent_2[cut_point_1:20]
        x2_parent_1 = parent_1[20:cut_point_2]
        x2_parent_2 = parent_2[cut_point_2:]

        child_1 = x1_parent_1 + x1_parent_2 + x2_parent_1 + x2_parent_2
        child_2 = x1_parent_2 + x1_parent_1 + x2_parent_2 + x2_parent_1
        return child_1, child_2

    rigged_roulette = build_rigged_roulette(scores)
    new_population = []
    while len(new_population) < len(population):
        if competition_code == 'roda':
            parent_1 = population[use_rigged_roulette(rigged_roulette)]
            parent_2 = population[use_rigged_roulette(rigged_roulette)]
        elif competition_code == 'torneio':
            parent_1 = population[tournament(scores, 5)]
            parent_2 = population[tournament(scores, 5)]

        if random.random() <= probability_of_crossing:
            child_1, child_2 = merge_genes(parent_1, parent_2)
            new_population.append(child_1)
            new_population.append(child_2)

    return new_population[:len(population)]

def use_rigged_roulette(rigged_roulette):
    indicator = random.random()
    for c_index, (start, end) in rigged_roulette.items():
        if start <= indicator < end:
            return c_index
    return random.choice(list(rigged_roulette.keys()))

def mutation_generator(population, mutation_probability):
    for chromosome in population:
        for i in range(len(chromosome)):
            if random.random() <= mutation_probability:
                chromosome[i] = 1 - chromosome[i]
    return population

def swap_elite(population, new_population, n_elite_chromossomes, scores, data_config):
    elite_indices = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:n_elite_chromossomes]
    elite_indices = [idx for idx, _ in elite_indices]
    elite_chromossomes = [population[idx] for idx in elite_indices]

    new_scores = fitness(new_population, data_config)
    worse_indices = sorted(new_scores.items(), key=lambda item: item[1])[:n_elite_chromossomes]
    worse_indices = [idx for idx, _ in worse_indices]

    for i in range(n_elite_chromossomes):
        new_population[worse_indices[i]] = elite_chromossomes[i]

    return new_population

def get_best_result(scores):
    best_idx = max(scores.items(), key=lambda item: item[1])[0]
    best_value = (1 / scores[best_idx]) - 200  # Corrigir a volta da translação
    return best_value

def get_mean_fitness(scores):
    mean_fitness = statistics.mean(scores.values())
    mean_fitness_tranformed = (1 / mean_fitness) - 200  # Corrigir a volta da translação
    return mean_fitness_tranformed

def get_metrics(best_results):
    return {
        'mean': statistics.mean(best_results),
        'median': statistics.median(best_results),
        'max': max(best_results),
        'min': min(best_results)
    }
    

def evolutionary(population_size, number_of_genes, mutation_probability, probability_of_crossing, n_generations, data_config, competition_code, n_elite_chromossomes):
    population = generate_population(population_size, number_of_genes)
    best_results = []
    mean_fitness = []

    for generation in range(n_generations):
        # Roda a função fitness
        scores = fitness(population, data_config)
        # Coleta o melhor da população
        best_results.append(get_best_result(scores=scores))
        # Coleta a fitness média
        mean_fitness.append(get_mean_fitness(scores))
        # Faz o cruzamento
        new_population = chromosome_crossover(population, scores, competition_code, probability_of_crossing)
        # Faz a mutação
        new_population = mutation_generator(new_population, mutation_probability)
        # Insere os cromossomos de elite
        population = swap_elite(population, new_population, n_elite_chromossomes, scores, data_config)
        

    final_scores = fitness(population, data_config)
    best_idx = max(final_scores.items(), key=lambda item: item[1])[0]
    best_value = (1 / final_scores[best_idx]) - 200  # Corrigir a volta da translação
    best_chromossome = population[best_idx]

    # Faz o tratamento dos dados para obter a média, mediana, min e max de best_results
    metrics = get_metrics(best_results)

    return best_chromossome, best_value, best_results, mean_fitness

if __name__ == "__main__":
    population_size = 100
    number_of_genes = 40

    mutation_probability = 0.05
    probability_of_crossing = 0.95
    n_elite_chromossomes = 10

    data_config = {
        'x1': {'base': -10, 'precision': 0.000019074},
        'x2': {'base': -10, 'precision': 0.000019074}
    }

    n_generations = 30

    best_chromossome, best_chromossome_value = evolutionary(
        population_size,
        number_of_genes,
        mutation_probability,
        probability_of_crossing,
        n_generations,
        data_config,
        competition_code='roda',  # ou 'torneio'
        n_elite_chromossomes=n_elite_chromossomes
    )

    print("Melhor cromossomo encontrado:", best_chromossome)
    print("Valor mínimo da função Shubert:", best_chromossome_value)
