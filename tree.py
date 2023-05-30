class Tree:
    def __init__(self, gate, arg):
        self.parent = None
        self.reset(gate, arg)

    def __str__(self):
        str_self = self.gate + ' ' + self.formula
        if not self.children:
            return str_self
        str_children = '\n'.join([str(child) for child in self.children])
        return '\n'.join([str_self] + ['| ' + line for line in str_children.split('\n')])

    def reset(self, gate, arg):
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
        subformulas = set()
        new_children = []

        def update_children(child):
            nonlocal subformulas, new_children
            if child.formula not in subformulas:
                subformulas.add(child.formula)
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
        return sum([1 for char in self.formula if char.isalpha()])

    def clone(self):
        if self.gate == '?':
            return Tree(self.gate, self.formula)
        return Tree(self.gate, [child.clone() for child in self.children])

    @staticmethod
    def parse(string):
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
    def random(leaf_count, max_degree): pass
