import math
import random
import operations

def naive(tree):
    while operations.decrease_cost(tree):
        pass

def hill_climbing(tree, neighbors=5):
    while True:
        best_cost = 1e9
        best_tree = None
        for _ in range(neighbors):
            copy = tree.clone()
            if not operations.decrease_cost(copy): return
            cost = copy.cost()
            if cost < best_cost:
                best_cost = cost
                best_tree = copy
        tree.reset(best_tree.gate, best_tree.children)

def simulated_annealing(tree, t_min=10, t_max=200, cooling_rate=.15, increase_prob=.3, steps=15):
    t = t_max
    while t > t_min:
        for _ in range(steps):
            copy = tree.clone()
            old_cost = copy.cost()
            if random.random() < increase_prob:
                operations.increase_cost(copy)
            else:
                operations.decrease_cost(copy)
            new_cost = copy.cost()
            delta = new_cost - old_cost
            if delta < 0 or random.random() < math.exp(-delta / t):
                tree.reset(copy.gate, copy.children)
        t = (1 - cooling_rate) * t
    while operations.decrease_cost(tree):
        pass

def custom_heuristic(tree, steps=200):
    can_factorize = True
    for step in range(steps):
        if not can_factorize or random.randrange(5 * steps) < steps - step:
            operations.increase_cost(tree)
            can_factorize = True
        elif not operations.decrease_cost(tree):
            can_factorize = False
    while operations.decrease_cost(tree):
        pass

def iterate(tree, heuristic, iterations=10):
    best_cost = 1e9
    best_tree = None
    for _ in range(iterations):
        copy = tree.clone()
        heuristic(copy)
        cost = copy.cost()
        if cost < best_cost:
            best_cost = cost
            best_tree = copy
    tree.reset(best_tree.gate, best_tree.children)
