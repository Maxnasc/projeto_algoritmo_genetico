import pandas as pd
import matplotlib.pyplot as plt
import itertools

from ga_algorithm import evolutionary

if __name__ == "__main__":
    number_of_genes = 40
    n_elite_chromossomes = 10

    population_sizes = [100]  # fixo
    n_generations_list = [30]  # fixo

    mutation_probabilitys = [0.05, 0.10, 0.20]
    probability_of_crossings = [0.95, 0.9, 0.8]
    problems = ["shubert", "camel"]
    selection_methods = ["roda", "torneio"]

    data_config_problems = {
        "shubert": {
            "x1": {"base": -10, "precision": 0.000019074},
            "x2": {"base": -10, "precision": 0.000019074},
        },
        "camel": {
            "x1": {"base": -3, "precision": 0.000005722},
            "x2": {"base": -2, "precision": 0.000003815},
        },
    }

    results = []

    all_combinations = itertools.product(
        population_sizes,
        n_generations_list,
        mutation_probabilitys,
        probability_of_crossings,
        problems,
        selection_methods,
    )

    for (
        population_size,
        n_generations,
        mutation_probability,
        probability_of_crossing,
        problem,
        selection_method,
    ) in all_combinations:
        
        print(f"Rodando: pop={population_size}, gen={n_generations}, mut={mutation_probability}, cross={probability_of_crossing}, prob={problem}, sel={selection_method}")

        best_chromossome, best_chromossome_value, all_best_values, all_mean_fitness = evolutionary(
            population_size,
            number_of_genes,
            mutation_probability,
            probability_of_crossing,
            n_generations,
            {
                "problem": problem,
                "x1": data_config_problems[problem]["x1"],
                "x2": data_config_problems[problem]["x2"],
            },
            competition_code=selection_method,
            n_elite_chromossomes=n_elite_chromossomes,
        )

        results.append({
            "pop_size": population_size,
            "n_generations": n_generations,
            "mutation_prob": mutation_probability,
            "crossover_prob": probability_of_crossing,
            "problem": problem,
            "selection_method": selection_method,
            "fitness_values": all_best_values,
            "mean": sum(all_best_values) / len(all_best_values),
            "median": sorted(all_best_values)[len(all_best_values)//2],
            "min": min(all_best_values),
            "max": max(all_best_values),
        })

    # Criar DataFrame
    df = pd.DataFrame(results)

    # Separar Shubert e Camel
    df_shubert = df[df["problem"] == "shubert"]
    df_camel = df[df["problem"] == "camel"]

    # Plotar boxplot para Shubert
    fig, ax = plt.subplots(figsize=(20, 10))
    labels = []
    data = []

    for idx, row in df_shubert.iterrows():
        label = f"{row['selection_method']}|mut={row['mutation_prob']}|cross={row['crossover_prob']}"
        labels.append(label)
        data.append(row["fitness_values"])

    ax.boxplot(data, showfliers=False)
    ax.set_xticklabels(labels, rotation=90)
    ax.set_title("Shubert - Comparação de Configurações")
    ax.set_ylabel("Fitness Final")
    plt.tight_layout()

    # Plotar boxplot para Camel
    fig, ax = plt.subplots(figsize=(20, 10))
    labels = []
    data = []

    for idx, row in df_camel.iterrows():
        label = f"{row['selection_method']}|mut={row['mutation_prob']}|cross={row['crossover_prob']}"
        labels.append(label)
        data.append(row["fitness_values"])

    ax.boxplot(data, showfliers=False)
    ax.set_xticklabels(labels, rotation=90)
    ax.set_title("Camel - Comparação de Configurações")
    ax.set_ylabel("Fitness Final")
    plt.tight_layout()
    
    # Plot da evolução com os melhores parâmetros
    # Shubert
    best_shubert = df_shubert.loc[df_shubert['min'].idxmin()]
    valores_fitness = best_shubert['fitness_values']
    # Plotar
    plt.figure(figsize=(10,6))
    plt.plot(range(1, len(valores_fitness)+1), valores_fitness, marker='o', label="Fitness por execução")
    plt.axhline(y=-186.7309, color='r', linestyle='--', label="Valor esperado (-183.7309)")

    plt.title("Evolução do Fitness - Melhor Configuração Shubert")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # camel
    best_camel = df_camel.loc[df_camel['min'].idxmin()]
    valores_fitness = best_camel['fitness_values']
    # Plotar
    plt.figure(figsize=(10,6))
    plt.plot(range(1, len(valores_fitness)+1), valores_fitness, marker='o', label="Fitness por execução")
    plt.axhline(y=-1.0316, color='r', linestyle='--', label="Valor esperado (-183.7309)")

    plt.title("Evolução do Fitness - Melhor Configuração camel")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    
    # Mostrar gráficos
    plt.show()
