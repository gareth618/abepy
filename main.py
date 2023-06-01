import os
import random
import heuristics
from tree import Tree

def probably_equal(variable_count, tree1, tree2, repeat):
    for _ in range(repeat):
        assignment = dict()
        for i in range(variable_count):
            variable = chr(ord('a') + i) if i < 26 else 'x' + str(i - 25)
            assignment[variable] = random.random() < .5
        if tree1.evaluate(assignment) != tree2.evaluate(assignment):
            return False
    return True

for entry in os.scandir('inputs/old'):
    name, extension = os.path.splitext(entry.name)
    if extension == '.txt' and entry.is_file():
        formulas = [line for line in open(entry).read().split('\n') if line != '']
        avg_improvement = 0
        max_improvement = 0
        for formula in formulas:
            tree1 = Tree.parse(formula)
            cost1 = tree1.cost()
            tree2 = heuristics.custom(tree1)
            cost2 = tree2.cost()
            improvement = (cost1 - cost2) / cost1 * 100
            avg_improvement += improvement
            max_improvement = max(max_improvement, improvement)
            assert probably_equal(50, tree1, tree2, 10000)
        avg_improvement /= len(formulas)
        print(name)
        print(f'avg: {"{:.2f}".format(avg_improvement)}%')
        print(f'max: {"{:.2f}".format(max_improvement)}%')
