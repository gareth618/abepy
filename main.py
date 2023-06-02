import os
import time
import heuristics
from tree import Tree
from pathlib import Path

def run(dirname, heuristic):
    for entry in os.scandir(dirname):
        name, extension = os.path.splitext(entry.name)
        if not (extension == '.txt' and entry.is_file()): continue

        path = Path(dirname) / 'results' / heuristic.__name__
        path.mkdir(parents=True, exist_ok=True)
        path /= f'{name}.txt'

        with open(path, 'w') as fd:
            avg_improvement = 0
            max_improvement = 0, ''
            avg_runningtime = 0

            formulas = [line for line in open(entry).read().split('\n') if line != '']
            for formula in formulas:
                tree = Tree.parse(formula)
                old_tree = tree.clone()
                old_cost = tree.cost()
                old_time = time.time()
                heuristic(tree)
                new_time = time.time()
                new_tree = tree.clone()
                new_cost = tree.cost()

                improvement = (old_cost - new_cost) / old_cost * 100
                runningtime = new_time - old_time
                avg_improvement += improvement
                max_improvement = max(max_improvement, (improvement, new_tree.formula))
                avg_runningtime += runningtime

                assert Tree.probably_equivalent(old_tree, new_tree, 1000)
                fd.write(max_improvement[1] + '\n')

            avg_improvement /= len(formulas)
            avg_runningtime /= len(formulas)

            print(f'[{heuristic.__name__}]', name)
            print(f'avg_cost: {"{:.2f}".format(avg_improvement)}%')
            print(f'max_cost: {"{:.2f}".format(max_improvement[0])}%')
            print(f'avg_time: {"{:.2f}".format(avg_runningtime)}s')
    print()

run('inputs', heuristics.hill_climbing)
run('inputs', heuristics.simulated_annealing)
run('inputs', heuristics.custom_heuristic)
