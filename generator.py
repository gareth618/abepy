import random
from tree import Tree

metadata = [
    ('small', 20, 25, 2, 5, 20, 40, 50),
    ('medium', 20, 20, 2, 3, 60, 90, 50),
    ('large', 25, 35, 2, 3, 160, 200, 10)
]

for name, min_variable_count, max_variable_count, min_max_degree, max_max_degree, min_cost, max_cost, formula_count in metadata:
    formulas = []
    while True:
        tree = Tree.random(random.randint(min_variable_count, max_variable_count), random.randint(min_max_degree, max_max_degree))
        if min_cost <= tree.cost() <= max_cost:
            formulas += [tree.formula]
            if len(formulas) == formula_count:
                break
    with open(f'inputs/{name}.txt', 'w') as fd:
        for formula in formulas:
            fd.write(formula + '\n')
