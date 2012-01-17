import re

class Node(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self):
        pass

class AndNode(Node):
    pass

class OrNode(Node):
    pass

class NotNode(Node):
    pass

class TextNode(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value

class SearchQueryException(Exception):
    pass

class Parser(object):
    def __init__(self, tokens):
        self._tokens = [x for x in re.split(r'([() ])', tokens) if x.strip() != '']
        self._length = len(tokens)
        self._upto = 0

    def parse(self):
        # (1) read the left expression
        # (2) read the operator
        # (3) read the right expression

        if self.peek() == '(':
            self.next()
            node = self.parse()
            if self.peek() == ')':
                self.next()
                return node
            else:
            	print self.peek()
                raise SearchQueryException('Missing a closing bracket')

        left_value = self.peek()
        if left_value == '(':
            left_node = self.parse()
        else:
            left_node = TextNode(self.peek())
        self.next()

        operator_value = self.peek()
        self.next()

        right_value = self.peek()
        if right_value == '(':
            right_node = self.parse()
        else:
            right_node = TextNode(self.peek())
        self.next()

        if operator_value == 'and':
            operator_node = AndNode(left_node, right_node)

        elif operator_value == 'or':
            operator_node = OrNode(left_node, right_node)

        elif operator_value == 'not':
            operator_node = NotNode(left_node, right_node)

        return operator_node

    def is_end(self):
        return self._upto == self._length

    def peek(self):
        return None if self.is_end() else self._tokens[self._upto]

    def next(self):
        if not self.is_end():
            self._upto += 1
