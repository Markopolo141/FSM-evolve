import unittest
from sim import *

class TestStringMethods(unittest.TestCase):

    def test_generate_switch_extrema(self):
        A = [[0,0,0],[0,1,0],[1,1,0],[1,0,1]]
        generate_switch_extrema(switch)
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
