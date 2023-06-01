import random
import operations

def custom(tree):
    best_tree = None
    best_cost = 1e9
    k_max = 160
    can_factorize = True
    for k in range(k_max):
        if not can_factorize or random.randrange(5 * k_max) < k_max - k:
            operations.increase_cost(tree)
            can_factorize = True
        elif not operations.decrease_cost(tree):
            can_factorize = False
            continue
        cost = tree.cost()
        if cost < best_cost:
            best_cost = cost
            best_tree = tree.clone()
    while operations.decrease_cost(tree):
        pass
    return best_tree
