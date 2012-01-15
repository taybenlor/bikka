from template import *
import unittest

class TestIfNode(unittest.TestCase):
    def test_true(self):
        p = Parser("hello {% if True %}world!{% end if %}")
        tree = p.parse()
        self.assertEqual(tree.eval({}), "hello world!")

    def test_false(self):
        p = Parser("hello {% if False %}world!{% end if %}")
        tree = p.parse()
        self.assertEqual(tree.eval({}), "hello ")

    def test_context(self):
        p = Parser("hello {% if x == 2 %}two!{% end if %} {% if x%2 == 1 %}odd!{% end if %}")
        tree = p.parse()
        self.assertEqual(tree.eval({'x':2}), "hello two! ")
        self.assertEqual(tree.eval({'x':3}), "hello  odd!")

    def test_nested(self):
        p = Parser("foo{% if s == 'bar' %}bar{% if t == 'baz' %}baz{% end if %}{% end if %}")
        tree = p.parse()
        self.assertEqual(tree.eval({'s':'bar', 't':'baz'}), "foobarbaz")
        self.assertEqual(tree.eval({'s':'baz', 't':'baz'}), "foo")
        self.assertEqual(tree.eval({'s':'bar', 't':'bar'}), "foobar")

    @unittest.expectedFailure
    def test_failure(self):
        p = Parser("foo{% if True %}bar{% end for %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_failure2(self):
        p = Parser("foo{% if True %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_bad_syntax(self):
        p = Parser("foo{% if %}bar{% end if %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_bad_syntax2(self):
        p = Parser("foo{% if True %}bar{% end %}")
        tree = p.parse()

    def test_else(self):
        p = Parser("foo{% if x == True %}bar{% else %}baz{% end if %}")
        tree = p.parse()
        self.assertEqual(tree.eval({'x':True}), "foobar")
        self.assertEqual(tree.eval({'x':False}), "foobaz")

    def test_else_nest(self):
        p = Parser("foo{% if x == True %}{% if y == True %}a{% else %}b{% end if %}{% else %}{% if y == True %}c{% else %}d{% end if %}{% end if %}")
        tree = p.parse()
        self.assertEqual(tree.eval({'x':True,'y':True}), "fooa")
        self.assertEqual(tree.eval({'x':True,'y':False}), "foob")
        self.assertEqual(tree.eval({'x':False,'y':True}), "fooc")
        self.assertEqual(tree.eval({'x':False,'y':False}), "food")

    @unittest.expectedFailure
    def test_else_missing_end(self):
        p = Parser("foo{% if True %}bar{% else %}baz")
        tree = p.parse()

    @unittest.expectedFailure
    def test_else_wrong_end(self):
        p = Parser("foo{% if True %}bar{% else %}baz{% end for %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_else_no_if(self):
        p = Parser("foo{% else %}bar{% end if %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_for_else(self):
        p = Parser("foo{% for i in xrange(10) %}{{ i }}{% else %}{{ i+1 }}{% end for %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_multiple_else(self):
        p = Parser("foo{% if True %}a{% else %}b{% else %}c{% end if %}")
        tree = p.parse()


class TestForNode(unittest.TestCase):
    def test_xrange(self):
        p = Parser("hello{% for i in xrange(n) %}world{% end for %}")
        tree = p.parse()
        self.assertEqual(tree.eval({'n': 0}), "hello")
        self.assertEqual(tree.eval({'n': 3}), "helloworldworldworld")

    def test_iter(self):
        p = Parser("hello{% for name in names %}{{ name }}{% end for %}")
        tree = p.parse()
        self.assertEqual(tree.eval({'names':['one', 'two', 'three']}), "helloonetwothree")
        self.assertEqual(tree.eval({'names':[]}), "hello")

    def test_nested(self):
        p = Parser("hello{% for name1 in names1 %}{{ name1 }}{% for name2 in names2 %}{{ name2 }}{% end for %}{% end for %}")
        tree = p.parse()
        self.assertEqual(tree.eval({'names1':['bob','jane','fred'], 'names2':['one','two','three']}), "hellobobonetwothreejaneonetwothreefredonetwothree")
        self.assertEqual(tree.eval({'names1':['bob','jane','fred'], 'names2':[]}), "hellobobjanefred")
        self.assertEqual(tree.eval({'names1':[], 'names2':['one','two','three']}), "hello")

    @unittest.expectedFailure
    def test_failure(self):
        p = Parser("foo{% for i in xrange(3) %}bar{% end if %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_failure2(self):
        p = Parser("foo{% for i in xrange(3) %}bar")
        tree = p.parse()

    @unittest.expectedFailure
    def test_bad_syntax(self):
        p = Parser("hello{% for name in %}world{% end for %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_bad_syntax2(self):
        p = Parser("hello{% for in names %}world{% end for %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_bad_syntax3(self):
        p = Parser("hello{% for in %}world{% end for %}")
        tree = p.parse()

    @unittest.expectedFailure
    def test_condition(self):
        p = Parser("foo{% for x == True %}{{ x }}{% end for %}")
        tree = p.parse()

if __name__ == "__main__":
	unittest.main()
