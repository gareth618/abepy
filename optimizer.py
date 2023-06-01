import random
from tree import Tree

def find_factorizable_lists(tree):
    subformulas = dict()
    for child in tree.children:
        for grandchild in child.children:
            subformulas.setdefault(grandchild.formula, [])
            subformulas[grandchild.formula] += [grandchild]
    lists = [nodes for nodes in subformulas.values() if len(nodes) > 1]
    return lists + sum([find_factorizable_lists(child) for child in tree.children], [])

def factorize(nodes):
    parents = [node.parent for node in nodes]
    grandparent = parents[0].parent
    lower_operator = parents[0].gate
    upper_operator = grandparent.gate
    for node, parent in zip(nodes, parents):
        children_parent = list(set(parent.children) - {node})
        parent.reset(lower_operator, children_parent)
    lower_node = Tree(upper_operator, parents)
    upper_node = Tree(lower_operator, [nodes[0], lower_node])
    children_grandparent = list(set(grandparent.children) - set(parents))
    grandparent.reset(upper_operator, [upper_node] + children_grandparent)

def find_absorbable_lists(tree):
    subformulas = { child.formula: [] for child in tree.children }
    for child in tree.children:
        for grandchild in child.children:
            if grandchild.formula in subformulas:
                subformulas[grandchild.formula] += [child]
    lists = [nodes for nodes in subformulas.values() if nodes]
    return lists + sum([find_absorbable_lists(child) for child in tree.children], [])

def absorb(nodes):
    parent = nodes[0].parent
    children_parent = list(set(parent.children) - set(nodes))
    parent.reset(parent.gate, children_parent)

def decrease_cost(tree):
    lists1 = find_factorizable_lists(tree)
    lists2 = find_absorbable_lists(tree)
    if not lists1 and not lists2:
        return False
    if lists1 and (not lists2 or random.random() < .5):
        factorize(random.choice(lists1))
    else:
        absorb(random.choice(lists2))
    tree.trim()
    return True
