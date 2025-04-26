import math
import random


def generate_population(population_size, number_of_genes):
    return [
        [random.choice([0, 1]) for gene in range(number_of_genes)]
        for gene in range(population_size)
    ]

def fitness(population, data_config):
    scores = {}
    
    for c_index, chromossome in enumerate(population):
        tamanho_total = len(chromossome)

        ponto_medio = tamanho_total // 2  # Calcula o índice do meio (divisão inteira)

        # Obtém a primeira metade dos dados e converte para float
        x1_key = int("".join([str(chromossome[index]) for index in range(ponto_medio)]), 2)
        x1 = data_config.get('x1').get('base') + x1_key*data_config.get('x1').get('precision')

        # Obtém a segunda metade dos dados e converte para float
        x2_key = int("".join([str(chromossome[index]) for index in range(ponto_medio, tamanho_total)]), 2)
        x2 = data_config.get('x1').get('base') + x2_key*data_config.get('x2').get('precision')
        
        # Calcula a função fitness
        def shubert(x1, x2):
            """
            Calcula o valor da função de Shubert para as entradas x1 e x2.

            Args:
                x1: O primeiro parâmetro de entrada (um número real).
                x2: O segundo parâmetro de entrada (um número real).

            Returns:
                O valor da função de Shubert para (x1, x2) (um número real).
            """
            sum1 = 0
            for i in range(1, 6):  # i varia de 1 a 5
                sum1 += i * math.cos((i + 1) * x1 + i)

            sum2 = 0
            for i in range(1, 6):  # i varia de 1 a 5
                sum2 += i * math.cos((i + 1) * x2 + i)

            return sum1 * sum2
        
        scores[c_index] = 1/(1+shubert(x1,x2))
    
    return scores # Pontuação transladada e 

def build_rigged_roulette(scores):
    total_score = sum([score for c_index, score in scores.items()])
    roulette = {}
    for c_index, score in scores.items():
        if c_index == 0:
            roulette[c_index] = [0, score/total_score]
        else:
            roulette[c_index] = [roulette[c_index-1][1], roulette[c_index-1][1] + score/total_score]
    return roulette

def tournament(scores, window):
    indices = scores.keys()
    competitors_list = [random.choice(indices) for i in range(window)]
    competitors = {id: value for id, value in scores.items() if id in competitors_list}
    winner_id = next((competitor for competitor, score in competitors.items() if score == max(competitors.values())), None)
    return winner_id

def chromosome_crossover(population: list, scores: dict, competition_code: str, probability_of_crossing: float):
    def merge_genes(parent_1, parent_2):
        # Decidindo os pontos de corte
        cut_point_1 = random.choice(list(range(1,20))) # ponto de corte
        cut_point_2 = cut_point_1 + 20
        # Fazendo a separação de genes e juntando os genes
        # Pai 1
        x1_parent_1_gameta = [parent_1[:cut_point_1], parent_1[cut_point_1:20]]
        x2_parent_1_gameta = [parent_1[20:cut_point_2], parent_1[cut_point_2:]]
        # Pai 2
        x1_parent_2_gameta = [parent_2[:cut_point_1], parent_2[cut_point_1:20]]
        x2_parent_2_gameta = [parent_2[20:cut_point_2], parent_2[cut_point_2:]]
        # Montando genes dos filhos
        child_1 = []
        child_1.extend(x1_parent_1_gameta[0])
        child_1.extend(x1_parent_1_gameta[1])
        child_1.extend(x2_parent_1_gameta[0])
        child_1.extend(x2_parent_2_gameta[1])
        child_2 = []
        child_2.extend(x1_parent_1_gameta[1])
        child_2.extend(x1_parent_1_gameta[0])
        child_2.extend(x2_parent_1_gameta[1])
        child_2.extend(x2_parent_2_gameta[0])
        
        return child_1, child_2
    
    rigged_roulette = build_rigged_roulette(scores)
    new_population = []
    while len(new_population) != len(population):
        if competition_code == 'roda':
            parent_1 = population[use_rigged_roulette(rigged_roulette)]
            parent_2 = population[use_rigged_roulette(rigged_roulette)]
        if competition_code == 'torneio':
            parent_1 = population[use_rigged_roulette(rigged_roulette)]
            parent_2 = population[use_rigged_roulette(rigged_roulette)]
        # Verificando se haverá cruzamento
        if random.random() <= probability_of_crossing:
            # Fazer o cruzamento
            child_1, child_2 = merge_genes(parent_1, parent_2)
            new_population.append(child_1)
            new_population.append(child_2)
    return new_population

def use_rigged_roulette(rigged_roulette):
    indicator = random.random()
    return next((c_index for c_index, probability in rigged_roulette.items() if probability[0] < indicator and indicator < probability[1]), None)
    

def mutation_generator(population: list, mutation_probability: float):
    for chomossome in population:
        for gene in chomossome:
            if random.random() <= mutation_probability:
                if gene == 0:
                    gene = 1
                else:
                    gene = 0
    return population
                    
def swap_elite(population, new_population, n_elite_chromossomes, scores, data_config):
    # Separa os n_elite_chromossomes melhores da primeira população
    elite_indices = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:n_elite_chromossomes]
    elite_indices = [item[0] for item in elite_indices]
    elite_chromossomes = [population[chromossome_idx] for chromossome_idx in elite_indices]
    
    # Calcula os valores de score novamente
    new_scores = fitness(new_population, data_config)
    worse_indices = sorted(new_scores.items(), key=lambda item: item[1], reverse=False)[:n_elite_chromossomes]
    worse_indices = [item[0] for item in worse_indices]
    
    # Troca os n_elite_chromossomes piores pelos melhores da última população
    for idx_to_swap in range(n_elite_chromossomes):
        new_population[worse_indices[idx_to_swap]] = elite_chromossomes[idx_to_swap]
        
    return new_population


def evolutionary(population_size, number_of_genes, mutation_probability, probability_of_crossing, n_generations, data_config, competition_code, n_elite_chromossomes):
    # Selecionar a primeria população
    population = generate_population(population_size, number_of_genes)
    
    for generation in range(n_generations):
        # Avaliar a população na função fitness
        scores = fitness(population, data_config)
        
        # Selecionar usando roleta viciada ou torneio Fazer o cruzamento
        new_population = chromosome_crossover(population, scores, competition_code, probability_of_crossing)
        
        # Fazer a mutação
        new_population = mutation_generator(population=new_population, mutation_probability=mutation_probability)
        
        # Elitismo
        population = swap_elite(population, new_population, n_elite_chromossomes, scores, data_config)
        
    final_scores = fitness(population=population, data_config=data_config)
    best_chromossome_idx = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)[0]
    best_chromossome_value = (1/best_chromossome_idx[1]) - 1
    best_chromossome = population[best_chromossome_idx[0]]
    
    return best_chromossome, best_chromossome_value
        

if __name__ == "__main__":
    # Configuração inicial
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

    best_chromossome, best_chromossome_value = evolutionary(population_size, number_of_genes, mutation_probability, probability_of_crossing, n_generations, data_config, competition_code='roda', n_elite_chromossomes=n_elite_chromossomes)
    print (best_chromossome)
    print (best_chromossome_value)
    a = 1
