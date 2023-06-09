import re
import random
import unittest
import operations
import heuristics
from tree import Tree

class TestTree(unittest.TestCase):
    def test_string_to_formula(self):
        self.assertEqual(Tree.parse('a').formula, 'a')
        self.assertEqual(Tree.parse('ab').formula, '(a*b)')
        self.assertEqual(Tree.parse('a1a').formula, '(a*a1)')
        self.assertEqual(Tree.parse('a*b').formula, '(a*b)')
        self.assertEqual(Tree.parse('a+b').formula, '(a+b)')
        self.assertEqual(Tree.parse('a(b+c)').formula, '((b+c)*a)')
        self.assertEqual(Tree.parse('(a+b)c').formula, '((a+b)*c)')
        self.assertEqual(Tree.parse('(a+b)(c+d)').formula, '((a+b)*(c+d))')
        self.assertEqual(Tree.parse('(a+b)*(c+d)').formula, '((a+b)*(c+d))')
        self.assertEqual(Tree.parse('((a+b)c)d').formula, '((a+b)*c*d)')

    def test_formula_to_tree(self):
        tree = Tree.parse('a(b+c)')
        self.assertEqual(str(tree), '\n'.join([
            '* ((b+c)*a)',
            '| + (b+c)',
            '| | ? b',
            '| | ? c',
            '| ? a'
        ]))
        self.assertTrue(TestTree.validate_nodes(tree))

    def test_trim(self):
        self.assertEqual(Tree.parse('(((aaa)))').formula, 'a')
        self.assertEqual(Tree.parse('(((ab+ab)*(ab+ab))+((ab+ab)*(ab+ab)))').formula, '(a*b)')
        self.assertEqual(Tree.parse('(a+b)+(b+c)').formula, '(a+b+c)')
        self.assertEqual(Tree.parse('(a+b)*(a+b)+a+(b+b)+(((c)))').formula, '(a+b+c)')

    def test_cost(self):
        self.assertEqual(Tree.parse('a').cost(), 1)
        self.assertEqual(Tree.parse('a1').cost(), 1)
        self.assertEqual(Tree.parse('a12').cost(), 1)
        self.assertEqual(Tree.parse('abc').cost(), 3)
        self.assertEqual(Tree.parse('(ab+c)d+ad+c').cost(), 7)

    def test_clone(self):
        tree = Tree.parse('a(b+c)')
        copy = tree.clone()
        self.assertEqual(str(tree), str(copy))
        self.assertTrue(TestTree.validate_nodes(copy))

    def test_random(self):
        def test(tree):
            self.assertTrue(TestTree.validate_nodes(tree))
            self.assertTrue(TestTree.check_invariants(tree))
        TestTree.for_random_tree(test, 10)

    @staticmethod
    def validate_nodes(node, parent=None):
        if node.parent is not parent:
            return False
        if node.gate == '?' and (node.children or not re.match(r'[a-z]\d*$', node.formula)):
            return False
        if node.gate != '?' and (not node.children or node.formula != '(' + node.gate.join([child.formula for child in node.children]) + ')'):
            return False
        return all(TestTree.validate_nodes(child, node) for child in node.children)

    @staticmethod
    def check_invariants(node):
        if len(node.children) == 1:
            return False
        subformulas = set()
        for child in node.children:
            if child.gate == node.gate:
                return False
            subformulas |= {child.formula}
        return len(subformulas) == len(node.children)

    @staticmethod
    def for_random_tree(callback, repeat=10):
        for _ in range(repeat):
            variable_count = random.randint(1, 100)
            max_degree = random.randint(2, 25)
            callback(Tree.random(variable_count, max_degree))

    def test_find_factorizable_lists(self):
        tree = Tree.parse('((a+b)*(a+c)*((x*y)+(x*z)+(x*t)))+(a*b*c)+((a+b)*((x*y)+(x*z)+(x*t)))')
        lists = operations.find_factorizable_lists(tree)
        answer = sorted([(nodes[0].formula, len(nodes)) for nodes in lists])
        target = sorted([('a', 2), ('x', 3), ('x', 3), ('((t*x)+(x*y)+(x*z))', 2), ('(a+b)', 2)])
        self.assertListEqual(answer, target)

    def test_apply_factorization(self):
        tree = Tree.parse('(x*a*b*c)+(x*d*e)+(x*f)+g')
        operations.factorize(operations.find_factorizable_lists(tree)[0])
        tree.trim()
        self.assertEqual(tree.formula, '((((a*b*c)+(d*e)+f)*x)+g)')

    def test_find_absorbable_lists(self):
        tree = Tree.parse('a+(a*b*(b+c)*(b+d))')
        lists = operations.find_absorbable_lists(tree)
        answer = sorted([[node.formula for node in nodes] for nodes in lists])
        target = sorted([['((b+c)*(b+d)*a*b)'], ['(b+c)', '(b+d)']])
        self.assertListEqual(answer, target)

    def test_apply_absorption(self):
        tree = Tree.parse('(a*b*(b+c)*(b+d))+d+(d*e)')
        operations.absorb(operations.find_absorbable_lists(tree)[0])
        tree.trim()
        operations.absorb(operations.find_absorbable_lists(tree)[0])
        tree.trim()
        self.assertEqual(tree.formula, '((a*b)+d)')

    def test_find_distributable_nodes(self):
        tree = Tree.parse('a*(b+c+((d+e)*(f+g)))*h')
        nodes = operations.find_distributable_nodes(tree)
        answer = sorted([node.formula for node in nodes])
        target = sorted(['(((d+e)*(f+g))+b+c)', '((d+e)*(f+g))', '(d+e)', '(f+g)'])
        self.assertListEqual(answer, target)

    def test_apply_distribution(self):
        tree = Tree.parse('a*(b+c+(d*e))*f')
        nodes = operations.find_distributable_nodes(tree)
        node = next(node for node in nodes if node.formula == '((d*e)+b+c)')
        sibling = next(sibling for sibling in node.parent.children if sibling.formula == 'a')
        operations.distribute(sibling, node)
        tree.trim()
        self.assertEqual(tree.formula, '(((a*b)+(a*c)+(a*d*e))*f)')

    def test_decrease_cost(self):
        def test(tree):
            old_cost = tree.cost()
            operations.decrease_cost(tree)
            new_cost = tree.cost()
            self.assertTrue(TestTree.validate_nodes(tree))
            self.assertTrue(TestTree.check_invariants(tree))
            self.assertLessEqual(new_cost, old_cost)
        TestTree.for_random_tree(test)

    def test_increase_cost_v1(self):
        def test(tree):
            old_cost = tree.cost()
            nodes = operations.find_distributable_nodes(tree)
            if nodes:
                node = random.choice(nodes)
                sibling = random.choice(list(set(node.parent.children) - {node}))
                operations.distribute(sibling, node)
            new_cost = tree.cost()
            self.assertGreaterEqual(new_cost, old_cost)
            tree.trim()
            self.assertTrue(TestTree.validate_nodes(tree))
            self.assertTrue(TestTree.check_invariants(tree))
        TestTree.for_random_tree(test)

    def test_increase_cost_v2(self):
        def test(tree):
            operations.increase_cost(tree)
            self.assertTrue(TestTree.validate_nodes(tree))
            self.assertTrue(TestTree.check_invariants(tree))
        TestTree.for_random_tree(test)

    def test_heuristics(self):
        variable_count = random.randint(20, 30)
        max_degree = random.randint(5, 10)
        tree = Tree.random(variable_count, max_degree)
        algorithms = [
            heuristics.naive,
            heuristics.hill_climbing,
            heuristics.simulated_annealing,
            heuristics.custom_heuristic
        ]
        for algorithm in algorithms:
            copy = tree.clone()
            algorithm(copy)
            self.assertTrue(TestTree.validate_nodes(copy))
            self.assertTrue(TestTree.check_invariants(copy))
            self.assertTrue(Tree.probably_equivalent(copy, tree))
            copy = tree.clone()
            heuristics.iterate(copy, algorithm, 3)
            self.assertTrue(TestTree.validate_nodes(copy))
            self.assertTrue(TestTree.check_invariants(copy))
            self.assertTrue(Tree.probably_equivalent(copy, tree))
