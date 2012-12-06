# -*- coding: utf-8 -*-

import unittest

import jade


class test_attribute_list(unittest.TestCase):
    def test_simple(self):
        data = '''(href="foo")'''
        expected = ['attribute_list', ['attribute', '''href="foo"''']]
        result = jade.parse(data, jade.attribute_list)
        assert expected == result
