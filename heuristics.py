import math
import random
import operations

def naive(tree):
    """ Just applies factorizations and absorptions on `tree` as long as possible. """
    while operations.decrease_cost(tree):
        pass

def hill_climbing(tree, neighbors=5):
    """ Performs Hill Climbing on `tree`.
    The neighbors of the current state are obtained by randomly applying `neighbors` factorizations and absorptions on `tree`.
    """
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
        tree.assign(best_tree)

def simulated_annealing(tree, t_min=10, t_max=200, cooling_rate=.15, increase_prob=.3, steps=15):
    """ Performs Simulated Annealing on `tree`. """
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
                tree.assign(copy)
        t = (1 - cooling_rate) * t
    while operations.decrease_cost(tree):
        pass

def custom_heuristic(tree, steps=200):
    """ Performs our Custom Heuristic algorithm on `tree`. """
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
    """ Performs `iterations` runs of `heuristic` on `tree` and assigns to it the best result. """
    best_cost = 1e9
    best_tree = None
    for _ in range(iterations):
        copy = tree.clone()
        heuristic(copy)
        cost = copy.cost()
        if cost < best_cost:
            best_cost = cost
            best_tree = copy
    tree.assign(best_tree)
