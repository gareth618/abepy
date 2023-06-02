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
                tree1 = Tree.parse(formula)
                cost1 = tree1.cost()
                time1 = time.time()
                tree2 = heuristics.custom(tree1)
                time2 = time.time()
                cost2 = tree2.cost()

                improvement = (cost1 - cost2) / cost1 * 100
                runningtime = time2 - time1
                avg_improvement += improvement
                max_improvement = max(max_improvement, (improvement, tree2.formula))
                avg_runningtime += runningtime

                assert Tree.probably_equivalent(tree1, tree2, 10000)
                fd.write(max_improvement[1] + '\n')

            avg_improvement /= len(formulas)
            avg_runningtime /= len(formulas)

            print(name)
            print(f'  avg: {"{:.2f}".format(avg_improvement)}%')
            print(f'  max: {"{:.2f}".format(max_improvement[0])}%')
            print(f'  time: {"{:.2f}".format(avg_runningtime)}s')

run('inputs', heuristics.custom)
