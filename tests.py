import random
import unittest
import optimizer
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
        if node.gate == '?' and node.children:
            return False
        if node.parent != parent:
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
    def for_random_tree(callback, repeat):
        for _ in range(repeat):
            variable_count = random.randint(1, 100)
            max_degree = random.randint(2, 25)
            callback(Tree.random(variable_count, max_degree))

    def test_find_factorizable_lists(self):
        tree = Tree.parse('((a+b)*(a+c)*((x*y)+(x*z)+(x*t)))+(a*b*c)+((a+b)*((x*y)+(x*z)+(x*t)))')
        lists = optimizer.find_factorizable_lists(tree)
        answer = sorted([(nodes[0].formula, len(nodes)) for nodes in lists])
        target = sorted([('a', 2), ('x', 3), ('x', 3), ('((t*x)+(x*y)+(x*z))', 2), ('(a+b)', 2)])
        self.assertListEqual(answer, target)

    def test_apply_factorization(self):
        tree = Tree.parse('(x*a*b*c)+(x*d*e)+(x*f)+g')
        optimizer.factorize(optimizer.find_factorizable_lists(tree)[0])
        tree.trim()
        self.assertEqual(tree.formula, '((((a*b*c)+(d*e)+f)*x)+g)')

    def test_find_absorbable_lists(self):
        tree = Tree.parse('a+(a*b*(b+c)*(b+d))')
        lists = optimizer.find_absorbable_lists(tree)
        answer = sorted([[node.formula for node in nodes] for nodes in lists])
        target = sorted([['((b+c)*(b+d)*a*b)'], ['(b+c)', '(b+d)']])
        self.assertListEqual(answer, target)

    def test_apply_absorption(self):
        tree = Tree.parse('(a*b*(b+c)*(b+d))+d+(d*e)')
        optimizer.absorb(optimizer.find_absorbable_lists(tree)[0])
        tree.trim()
        optimizer.absorb(optimizer.find_absorbable_lists(tree)[0])
        tree.trim()
        self.assertEqual(tree.formula, '((a*b)+d)')

    def test_decrease_cost(self):
        def test(tree):
            cost1 = tree.cost()
            optimizer.decrease_cost(tree)
            cost2 = tree.cost()
            self.assertTrue(TestTree.validate_nodes(tree))
            self.assertTrue(TestTree.check_invariants(tree))
            self.assertLessEqual(cost2, cost1)
        TestTree.for_random_tree(test, 10)
