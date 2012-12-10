# -*- coding: utf-8 -*-

import unittest

import jade


class test_attribute_list(unittest.TestCase):
    def test_simple(self):
        data = '''(href="foo")'''
        expected = ['attribute_list', ['attribute', "href", ['quoted_string', 'foo']]]
        result = jade.parse(data, jade.attribute_list)
        assert expected == result

    def test_multiple(self):
        data = '''(href="foo", title="Foo!")'''
        expected = [
            'attribute_list',
            ['attribute', "href", ['quoted_string', 'foo']],
            ['attribute', "title", ['quoted_string', "Foo!"]]]
        result = jade.parse(data, jade.attribute_list)
        assert expected == result

class test_element(unittest.TestCase):
    def test_attribute_list(self):
        data = '''a(href='/contact') contact'''
        expected = [
            'element',
            ['open_tag', 'a',
             ['attribute_list',
              ['attribute', 'href',
               ['quoted_string', "/contact"]]]]]
        result = jade.parse(data, jade.element)
        assert expected == result
