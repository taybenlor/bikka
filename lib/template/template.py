import cgi
import re, os

EXPRESSION_OPEN = '{{'
EXPRESSION_CLOSE = '}}'
FIZZLY_OPEN = '{%'
FIZZLY_CLOSE = '%}'

END_MARKER = None

class TemplateError(Exception):
    pass

class Parser(object):
    def __init__(self, string):
        self.upto = 0
        #tag_delimiters = re.compile('([{{|{%|}}|%}])')
        tag_delimiters = re.compile('(%s|%s|%s|%s)' % (EXPRESSION_OPEN, EXPRESSION_CLOSE, FIZZLY_OPEN, FIZZLY_CLOSE))
        self.tokens = tag_delimiters.split(string)

    def next(self):
        self.upto += 1

    def peek(self):
        if self.end():
            return None
        else:
            return self.tokens[self.upto]

    def end(self):
        return self.upto >= len(self.tokens)

    def parse(self, parent=None):
        root = MultiNode()
        while not self.end():
            peek_value = self.peek()
            if peek_value == FIZZLY_OPEN:
                self.next()
                node = self.parse_fizzly(parent=parent)
                if node == END_MARKER:
                	return root
                root.add_child(node)
            elif peek_value == EXPRESSION_OPEN:
                self.next()
                root.add_child(self.parse_expression())
            elif peek_value == FIZZLY_CLOSE or peek_value == EXPRESSION_CLOSE:
                raise TemplateError("Templating: you're doing it wrong")
            else:
                root.add_child(self.parse_text())

        if parent != None:
            raise TemplateError("Missing close tag: expected %s" % parent.name())

        return root

    def parse_fizzly(self, parent=None):
        peek_value = self.peek().strip()
        self.next()

        if self.peek() != FIZZLY_CLOSE:
            raise TemplateError('No matching %s found' % FIZZLY_CLOSE)
        self.next()

        safe_expr_match = re.match(r'^safe\s+(.+)$', peek_value)
        include_match = re.match(r'^include\s+(.+)$', peek_value)
        if_match = re.match(r'^if\s+(.+)$', peek_value)
        else_match = re.match(r'^else$', peek_value)
        end_match = re.match(r'^end\s+(.+)$', peek_value)
        for_match = re.match(r'^for\s+(.+)\s+in\s+(.+)$', peek_value)
        # put more matches here

        if include_match:
            filename = include_match.group(1)
            return IncludeNode(filename)
        elif safe_expr_match:
            return SafeExprNode(safe_expr_match.group(1))
        elif if_match:
            node = IfNode(if_match.group(1))
            node.set_if_body(self.parse(parent=node))
            return node
        elif else_match:
            if parent is not None and parent.name() == 'if' and not parent.is_parsing_else():
            	parent.set_is_parsing_else(True)
                parent.set_else_body(self.parse(parent=parent))
                return END_MARKER
            else:
            	raise TemplateError('Else with no if encountered')
        elif for_match:
            #return ForNode(for_match.group(1), for_match.group(2), self.parse(node_name='for'))
            node = ForNode(for_match.group(1), for_match.group(2))
            node.set_body(self.parse(parent=node))
            return node
        elif end_match:
            #if node_name == end_match.group(1):
            if parent is not None and parent.name() == end_match.group(1):
            	return END_MARKER
            else:
                raise TemplateError('Not a valid end tag: got %s, expected %s' % (end_match.group(1), node_name))
        else:
            raise TemplateError('Not a valid fizzly: %s' % peek_value)

    def parse_expression(self):
        peek_value = self.peek().strip()
        self.next()
        if self.peek() != EXPRESSION_CLOSE:
            raise TemplateError('No matching %s found' % EXPRESSION_CLOSE)
        self.next()

        return ExprNode(peek_value)

    def parse_text(self):
        peek_value = self.peek()
        if peek_value != None:
            ret_node = TextNode(peek_value)
            self.next()
            return ret_node

class Node(object):
    def __init__(self, string):
        self.string = string
        self.upto = 0

    def eval(self, context):
        raise NotImplementedError

class MultiNode(Node):
    def __init__(self):
        super(MultiNode, self).__init__(None)
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def eval(self, context):
        rendered = ''
        for child in self.children:
            rendered += child.eval(context)
        return rendered

class IfNode(Node):
    def __init__(self, string):
        super(IfNode, self).__init__(string)
        self._if_body = None
        self._else_body = None
        self._is_parsing_else = False

    def name(self):
        return 'if'

    def is_parsing_else(self):
        return self._is_parsing_else

    def set_is_parsing_else(self, is_parsing_else):
        self._is_parsing_else = is_parsing_else

    def set_if_body(self, if_body):
        self._if_body = if_body

    def set_else_body(self, else_body):
        self._else_body = else_body

    def eval(self, context):
        if eval(self.string, {}, context):
        	return self._if_body.eval(context)
        elif self._else_body:
        	return self._else_body.eval(context)
        else:
        	return ''

class ForNode(Node):
    def __init__(self, varname, iterable):
        super(ForNode, self).__init__('')
        self.varname = varname
        self.iterable = iterable
        self._body = None

    def name(self):
        return 'for'

    def set_body(self, body):
        self._body = body

    def eval(self, context):
        rendered = ""
        for elem in eval(self.iterable, {}, context):
        	context[self.varname] = elem
        	rendered += self._body.eval(context)
        return rendered

class IncludeNode(Node):
    def eval(self, context):
        try:
            f = open(self.string, 'rU')
        except IOError:
            raise TemplateError('File not found')
        else:
            contents = f.read().strip()
            f.close()

            next_parser = Parser(contents)
            rendered = next_parser.parse().eval(dict(context))

            return rendered

class TextNode(Node):
    def eval(self, context):
        return self.string

class ExprNode(Node):
    def eval(self, context):
        return cgi.escape(str(eval(self.string, {}, context)))

class SafeExprNode(Node):
    def eval(self, context):
        return str(eval(self.string, {}, context))

def render(html_string, context):
    """
    Given a html_string, and a context dictionary, renders the html_string based on the dictionary.
    """

    return Parser(html_string).parse().eval(context)

def render_file(filename, context):
    """
    Given a file, renders the contents of the file based on the dictionary
    """

    f = open(filename)
    html_string = f.read()
    f.close()
    return render(html_string, context)
