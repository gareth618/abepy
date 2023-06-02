import random
from tree import Tree

def find_factorizable_lists(tree):
    """ Finds every subformula of the form `(x*φ1)+(x*φ2)+...+(x*φn)` or `(x+φ1)*(x+φ2)*...*(x+φn)`,
    creates a list containing the `x` nodes, and adds it to the returned lists.
    """

    subformulas = dict()
    for child in tree.children:
        for grandchild in child.children:
            subformulas.setdefault(grandchild.formula, [])
            subformulas[grandchild.formula] += [grandchild]
    lists = [nodes for nodes in subformulas.values() if len(nodes) > 1]
    return lists + sum([find_factorizable_lists(child) for child in tree.children], [])

def factorize(nodes):
    """ Receives the `x` nodes in a subformula like `(x*φ1)+(x*φ2)+...+(x*φn)` or `(x+φ1)*(x+φ2)*...*(x+φn)`
    and replaces that subformula by `(x*(φ1+φ2+...+φn))` or `(x+(φ1*φ2*...*φn))`.
    """

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
    """ Finds every subformula of the form `x+(x*φ1)+(x*φ2)+...+(x*φn)` or `x*(x+φ1)*(x+φ2)*...*(x+φn)`,
    creates a list containing the `(x*φi)` or `(x+φi)` nodes, and adds it to the returned lists.
    """

    subformulas = {child.formula: [] for child in tree.children}
    for child in tree.children:
        for grandchild in child.children:
            if grandchild.formula in subformulas:
                subformulas[grandchild.formula] += [child]
    lists = [nodes for nodes in subformulas.values() if nodes]
    return lists + sum([find_absorbable_lists(child) for child in tree.children], [])

def absorb(nodes):
    """ Receives the `(x*φi)` or `(x+φi)` nodes in a subformula like `x+(x*φ1)+(x*φ2)+...+(x*φn)` or `x*(x+φ1)*(x+φ2)*...*(x+φn)`
    and replaces that subformula by `x`.
    """

    parent = nodes[0].parent
    children_parent = list(set(parent.children) - set(nodes))
    parent.reset(parent.gate, children_parent)

def find_distributable_nodes(tree):
    """ Returns a list of all the nodes in `tree` having both a parent and children. """
    nodes = [child for child in tree.children if child.children]
    return nodes + sum([find_distributable_nodes(child) for child in tree.children], [])

def distribute(node1, node2):
    """ For a subformula of the form `x+(y1*y2*...*yn)` or `x*(y1+y2+...+yn)`,
    it receives the `x` and `(y1*y2*...*yn)` or `(y1+y2+...+yn)` nodes as `node1` and `node2` respectively,
    and replaces that subformula by `((x+y1)*(x+y2)*...*(x+yn))` or `((x*y1)+(x*y2)+...+(x*yn))`.
    """

    parent = node1.parent
    for child in node2.children:
        if child.children:
            children_child = [node1.clone()] + child.children
            child.reset(parent.gate, children_child)
        else:
            child.reset(parent.gate, [node1.clone(), child.clone()])
    children_parent = list(set(parent.children) - {node1})
    parent.reset(parent.gate, children_parent)

def decrease_cost(tree):
    """ Randomly applies a factorization or absorption operation on `tree` and then trims it.
    The function returns a boolean indicating whether any operation could be applied or not.
    It guarantees that the new cost of the tree will not be greater than the initial one.
    """

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

def increase_cost(tree):
    """ Randomly applies a distribution operation on `tree` and then trims it.
    The function returns a boolean indicating whether any operation could be applied or not.
    It does not guarantee that the new cost of the tree will not be lower than the initial one, because of the final trimming.
    """

    nodes = find_distributable_nodes(tree)
    if not nodes:
        return False
    node = random.choice(nodes)
    sibling = random.choice(list(set(node.parent.children) - {node}))
    distribute(sibling, node)
    tree.trim()
    return True
