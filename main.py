import os
import random
import optimizer
from tree import Tree

def heuristic(tree):
    best_tree = None
    best_cost = 1e9
    k_max = 160
    can_factorize = True
    for k in range(k_max):
        if not can_factorize or random.randrange(5 * k_max) < k_max - k:
            optimizer.increase_cost(tree)
            can_factorize = True
        elif not optimizer.decrease_cost(tree):
            can_factorize = False
            continue
        cost = tree.cost()
        if cost < best_cost:
            best_cost = cost
            best_tree = tree.clone()
    while optimizer.decrease_cost(tree):
        pass
    return best_tree

for entry in os.scandir('inputs'):
    name, extension = os.path.splitext(entry.name)
    if extension == '.txt' and entry.is_file():
        formulas = open(entry).read().split('\n')
        avg_improvement = 0
        max_improvement = 0
        for formula in formulas:
            tree = Tree.parse(formula)
            cost1 = tree.cost()
            tree = heuristic(tree)
            cost2 = tree.cost()
            improvement = (cost1 - cost2) / cost1 * 100
            avg_improvement += improvement
            max_improvement = max(max_improvement, improvement)
        avg_improvement /= len(formulas)
        print(name)
        print(f'avg: {"{:.2f}".format(avg_improvement)}%')
        print(f'max: {"{:.2f}".format(max_improvement)}%')
