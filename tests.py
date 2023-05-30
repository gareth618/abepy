import unittest
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
        self.assertTrue(TestTree.valid_nodes(tree))

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
        self.assertTrue(TestTree.valid_nodes(copy))

    @staticmethod
    def valid_nodes(node, parent=None):
        if node.gate == '?' and node.children:
            return False
        if node.parent != parent:
            return False
        for child in node.children:
            if not TestTree.valid_nodes(child, node):
                return False
        return True
