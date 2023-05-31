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
        for _ in range(10):
            leaf_count = random.randint(1, 100)
            max_degree = random.randint(2, 25)
            tree = Tree.random(leaf_count, max_degree)
            self.assertTrue(TestTree.validate_nodes(tree))
            self.assertEqual(len(TestTree.collect_leaves(tree)), leaf_count)

    @staticmethod
    def validate_nodes(node, parent=None):
        if node.gate == '?' and node.children:
            return False
        if node.parent != parent:
            return False
        for child in node.children:
            if not TestTree.validate_nodes(child, node):
                return False
        return True

    @staticmethod
    def collect_leaves(node):
        if node.children:
            leaves = set()
            for child in node.children:
                leaves |= TestTree.collect_leaves(child)
            return leaves
        return {node.formula}

    @staticmethod
    def compute_max_degree(node):
        return max([len(node.children)] + [TestTree.compute_max_degree(child) for child in node.children])

    def test_find_factorizable_lists(self):
        tree = Tree.parse('((a+b)*(a+c)*((x*y)+(x*z)+(x*t)))+(a*b*c)+((a+b)*((x*y)+(x*z)+(x*t)))')
        lists = optimizer.find_factorizable_lists(tree)
        answer = sorted([(nodes[0].formula, len(nodes)) for nodes in lists])
        target = sorted([('x', 3), ('x', 3), ('((t*x)+(x*y)+(x*z))', 2), ('(a+b)', 2)])
        self.assertListEqual(answer, target)

    def test_apply_random_factorization(self):
        tree = Tree.parse('xab+xc+d')
        optimizer.apply_random_factorization(tree)
        self.assertEqual(tree.formula, '((((a*b)+c)*x)+d)')
