import random
from tree import Tree

def find_factorizable_lists(tree):
    lists = sum([find_factorizable_lists(child) for child in tree.children], [])
    subformulas = dict()
    for child in tree.children:
        for grandchild in child.children:
            subformulas.setdefault(grandchild.formula, [])
            subformulas[grandchild.formula] += [grandchild]
    lists += [nodes for nodes in subformulas.values() if len(nodes) > 1]
    return lists

def factorize(node1, node2):
    parent1 = node1.parent
    parent2 = node2.parent
    grandparent = parent1.parent
    lower_operator = parent1.gate
    upper_operator = grandparent.gate
    children_parent1 = list(set(parent1.children) - {node1})
    children_parent2 = list(set(parent2.children) - {node2})
    children_grandparent = list(set(grandparent.children) - {parent1, parent2})
    parent1.reset(lower_operator, children_parent1)
    parent2.reset(lower_operator, children_parent2)
    lower_node = Tree(upper_operator, [parent1, parent2])
    upper_node = Tree(lower_operator, [node1, lower_node])
    grandparent.reset(upper_operator, [upper_node] + children_grandparent)

def find_absorbable_nodes(tree):
    nodes = sum([find_absorbable_nodes(child) for child in tree.children], [])
    subformulas = set([child.formula for child in tree.children])
    nodes += [child for child in tree.children if any(grandchild.formula in subformulas for grandchild in child.children)]
    return nodes

def absorb(node):
    parent = node.parent
    children_parent = list(set(parent.children) - {node})
    parent.reset(parent.gate, children_parent)

def increase_cost(tree):
    lists = find_factorizable_lists(tree)
    nodes = find_absorbable_nodes(tree)
    if not lists and not nodes:
        return False
    if lists and (not nodes or random.random() < .5):
        factorize(*random.sample(random.choice(lists), 2))
    else:
        absorb(random.choice(nodes))
    tree.trim()
    return True
