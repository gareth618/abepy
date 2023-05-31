import random

class Tree:
    """ Used for representing Abstract Syntax Trees for Boolean formulas.
    It stores the following data about the current node:
    1. `parent` which is `None` for the root
    2. `gate` the type of node, namely `'*'` for `AND`, `'+'` for `OR`, and `'?'` for `INPUT`
    3. `children` the list of children, lexicographically ordered by their corresponding subformulas
    4. `formula` the formula corresponding to the entire subtree; it respects the order of `children`
    """

    def __init__(self, gate, arg):
        """ Constructs a new tree by initializing its parent to `None` and calling `reset(gate, arg)`. """
        self.parent = None
        self.reset(gate, arg)

    def __str__(self):
        """ Converts the tree to a string such that each line contains the formula of a single node.
        The formula is preceded by one `|` sign for each level of indentation.
        """
        str_self = self.gate + ' ' + self.formula
        if not self.children:
            return str_self
        str_children = '\n'.join([str(child) for child in self.children])
        return '\n'.join([str_self] + ['| ' + line for line in str_children.split('\n')])

    def reset(self, gate, arg):
        """ Resets the contents of the node, except for the parent.
        If `gate == '?'`, then `arg` is the literal corresponding to the input.
        Otherwise, `arg` is the new list of children for the node.
        When updating children, the formula is updated too, as well as the parents of the children.
        """
        self.gate = gate
        if gate == '?':
            literal = arg
            self.children = []
            self.formula = literal
        else:
            children = arg
            children.sort(key=lambda child: child.formula)
            self.children = children
            self.formula = '(' + gate.join([child.formula for child in children]) + ')'
            for child in children:
                child.parent = self

    def trim(self):
        """ Simplifies the tree by getting rid of the following three structural flaws:
        1. nodes with only one child `((a*b)) -> (a*b)`
        2. nodes with the same gate as their parent `(a+(b+c)) -> (a+b+c)`
        3. duplicate children `(a+a+b) -> (a+b)`
        """

        subformulas = set()
        new_children = []

        def update_children(child):
            nonlocal subformulas, new_children
            if child.formula not in subformulas:
                subformulas |= {child.formula}
                new_children += [child]

        for child in self.children:
            child.trim()
            if child.gate == self.gate:
                for grandchild in child.children:
                    update_children(grandchild)
            else:
                update_children(child)

        self.reset(self.gate, self.formula if self.gate == '?' else new_children)
        if len(self.children) == 1:
            child = self.children[0]
            self.reset(child.gate, child.formula if child.gate == '?' else child.children)

    def cost(self):
        """ Returns the number of literals in the formula. """
        return sum([1 for char in self.formula if char.isalpha()])

    def clone(self):
        """ Returns a deep-copy of the tree by creating new nodes. """
        if self.gate == '?':
            return Tree(self.gate, self.formula)
        return Tree(self.gate, [child.clone() for child in self.children])

    @staticmethod
    def parse(string):
        """ Builds and returns the corresponding tree of the given formula.
        Note that the rules for `string` are relaxed.
        Thus, the first step of `parse` is normalizing the formula by making changes like the ones below.
        With that being said, the given formula still needs to be a valid one from a logical point of view.
        1. `a+b` becomes `(a+b)`
        2. `ab` becomes `(a*b)`
        3. `a(b+c)` becomes `(a*(b+c))`
        """

        formula = '('
        for char in string:
            last = formula[-1]
            lhs = last == ')' or last.isalnum()
            rhs = char == '(' or char.isalpha()
            if lhs and rhs:
                formula += '*'
            formula += char
        formula += ')'

        operators = []
        operands = []
        for char in formula:
            if char.isalpha():
                operands += [Tree('?', char)]
            elif char.isnumeric():
                operands[-1].formula += char
            else:
                operators += [char]
                if char == ')':
                    sub_operators = []
                    sub_operands = []
                    while True:
                        operator = operators.pop()
                        if operator == '(':
                            terms = []
                            factors = [sub_operands.pop()]
                            while sub_operands:
                                if sub_operators.pop() == '*':
                                    factors += [sub_operands.pop()]
                                else:
                                    terms += [Tree('*', factors)]
                                    factors = [sub_operands.pop()]
                            terms += [Tree('*', factors)]
                            operands += [Tree('+', terms)]
                            break
                        operand = operands.pop()
                        if operator != ')':
                            sub_operators += [operator]
                        sub_operands += [operand]

        tree = operands[-1]
        tree.trim()
        return tree

    @staticmethod
    def random(leaf_count, max_degree):
        """ Generates and returns a random AST having `leaf_count` leaves (variables in the corresponding formula)
        such that no node in it has more than `max_degree` children (before trimming).
        The construction goes bottom-top, starting with the leaves, and it builds one level at a time.
        If the previous level has `n` nodes, then the current level (the one above it) will have `(n + 1) // 2` nodes.
        This way, it is guaranteed that each node on the previous level will have a parent.
        After assigning the parents for the previous level, it fills the remaining edges with clones of random existing nodes.
        """

        levels = [[Tree('?', chr(ord('a') + i) if i < 26 else 'x' + str(i - 25)) for i in range(leaf_count)]]
        nodes = [*levels[0]]

        while len(levels[-1]) > 1:
            level_size = (len(levels[-1]) + 1) // 2
            level_children = [[] for _ in range(level_size)]
            for node in levels[-1]:
                index = random.choice([index for index in range(level_size) if len(level_children[index]) < max_degree])
                level_children[index] += [node]

            levels += [[]]
            for index in range(level_size):
                available_children = list(set(nodes) - set(level_children[index]))
                available_max_degree = min(max_degree - len(level_children[index]), len(available_children))
                new_children_count = 0 if available_max_degree == 0 else random.randint(1, available_max_degree)
                level_children[index] += random.sample(available_children, new_children_count)
                children = [child if child.parent is None else child.clone() for child in level_children[index]]
                levels[-1] += [Tree(random.choice('*+'), children)]
            nodes += levels[-1]

        tree = nodes[-1]
        tree.trim()
        return tree
