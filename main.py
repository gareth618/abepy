import os
import time
import heuristics
from tree import Tree
from pathlib import Path

def run(dirname, heuristic, iterations=10):
    for entry in os.scandir(dirname):
        name, extension = os.path.splitext(entry.name)
        if not (extension == '.txt' and entry.is_file()): continue

        path = Path(dirname) / 'results' / heuristic.__name__
        path.mkdir(parents=True, exist_ok=True)
        path /= f'{name}.txt'

        with open(path, 'w') as fd:
            total_avg_improvement = 0
            total_max_improvement = 0
            total_avg_runningtime = 0

            formulas = [line for line in open(entry).read().split('\n') if line != '']
            for formula in formulas:
                avg_improvement = 0
                max_improvement = 0, ''
                avg_runningtime = 0

                for _ in range(iterations):
                    tree = Tree.parse(formula)
                    old_cost = tree.cost()
                    old_time = time.time()
                    heuristic(tree)
                    new_time = time.time()
                    new_cost = tree.cost()

                    improvement = (old_cost - new_cost) / old_cost * 100
                    runningtime = new_time - old_time
                    avg_improvement += improvement
                    max_improvement = max(max_improvement, (improvement, tree.formula))
                    avg_runningtime += runningtime

                avg_improvement /= iterations
                avg_runningtime /= iterations
                fd.write(max_improvement[1] + '\n')

                total_avg_improvement += avg_improvement
                total_max_improvement += max_improvement[0]
                total_avg_runningtime += avg_runningtime

            total_avg_improvement /= len(formulas)
            total_max_improvement /= len(formulas)
            total_avg_runningtime /= len(formulas)

            print(f'[{heuristic.__name__}]', name)
            print(f'avg_cost: {"{:.2f}".format(total_avg_improvement)}%')
            print(f'max_cost: {"{:.2f}".format(total_max_improvement)}%')
            print(f'avg_time: {"{:.2f}".format(total_avg_runningtime)}s')
            print()
    print()

def iterated_naive(tree): return heuristics.iterate(tree, heuristics.naive)
def iterated_hill_climbing(tree): return heuristics.iterate(tree, heuristics.hill_climbing)
def iterated_simulated_annealing(tree): return heuristics.iterate(tree, heuristics.simulated_annealing)
def iterated_custom_heuristic(tree): return heuristics.iterate(tree, heuristics.custom_heuristic)

algorithms = [
    heuristics.naive,
    heuristics.hill_climbing,
    heuristics.simulated_annealing,
    heuristics.custom_heuristic,
    iterated_naive,
    iterated_hill_climbing,
    iterated_simulated_annealing,
    iterated_custom_heuristic
]
for algorithm in algorithms:
    run('inputs/old', algorithm)
