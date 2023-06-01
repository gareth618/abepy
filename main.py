import os
import heuristics
from tree import Tree

for entry in os.scandir('inputs'):
    name, extension = os.path.splitext(entry.name)
    if extension == '.txt' and entry.is_file():
        formulas = [line for line in open(entry).read().split('\n') if line != '']
        avg_improvement = 0
        max_improvement = 0
        for formula in formulas:
            tree = Tree.parse(formula)
            cost1 = tree.cost()
            tree = heuristics.custom(tree)
            cost2 = tree.cost()
            improvement = (cost1 - cost2) / cost1 * 100
            avg_improvement += improvement
            max_improvement = max(max_improvement, improvement)
        avg_improvement /= len(formulas)
        print(name)
        print(f'avg: {"{:.2f}".format(avg_improvement)}%')
        print(f'max: {"{:.2f}".format(max_improvement)}%')
