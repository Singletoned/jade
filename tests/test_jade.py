# -*- coding: utf-8 -*-

import jade


def listify(data):
    if isinstance(data, basestring):
        return data
    else:
        return [listify(item) for item in data]


def test_make_attr():
    def do_test(head, rest, expected):
        result = jade.make_attr(head, rest)
        assert expected == result

    items = [
        ('tag_id', ["foo"], '''id="foo"'''),
        ('tag_class', ["foo"], '''class="foo"'''),
        ('tag_id', ["bar"], '''id="bar"'''),
        ('tag_class', ["bar"], '''class="bar"''')]

    for head, rest, expected in items:
        yield do_test, head, rest, expected

def test_make_content():
    def do_test(rest, expected):
        result = jade.make_content("", rest)
        assert expected == result

    items = [
        (["hello"], "hello")
        ]

    for rest, expected in items:
        yield do_test, rest, expected

def test_make_open_tag():
    def do_test(head, rest, expected):
        result = jade.make_open_tag(head, rest)
        assert expected == result

    items = [
        ('open_tag', ["p"], '''<p>'''),
        ('open_tag', ["p", ['tag_id', "foo"]], '''<p id="foo">'''),
        ]

    for head, rest, expected in items:
        yield do_test, head, rest, expected

def test_make_close_tag():
    def do_test(head, rest, expected):
        result = jade.make_close_tag(head, rest)
        assert expected == result

    items = [
        ('open_tag', ["p"], '''</p>'''),
        ('open_tag', ["p", ['tag_id', "foo"]], '''</p>'''),
        ]

    for head, rest, expected in items:
        yield do_test, head, rest, expected

def test_make_element():
    def do_test(head, rest, expected):
        result = jade.make_element(head, rest)
        result = [el.to_string() for el in result]
        assert expected == result

    items = [
        ('element', [['open_tag', "p"]], ['''<p></p>\n'''])
        ]

    for head, rest, expected in items:
        yield do_test, head, rest, expected

def test_do_render():
    def do_test(data, expected):
        result = jade.do_render(data)
        assert expected == result

    items = [
        ("foo", "foo"),
        (['tag_id', "foo"], '''id="foo"'''),
        (['tag_class', "foo"], '''class="foo"'''),
        (['tag_id', "bar"], '''id="bar"'''),
        (['tag_class', "bar"], '''class="bar"'''),]

    for data, expected in items:
        yield do_test, data, expected

def test_simple_tag():
    def do_test(data):
        expected = ['element', ['open_tag', data]]
        result = jade.generate_data(data, pattern=jade.element)
        assert expected == result

        expected = "<%(data)s></%(data)s>\n" % dict(data=data)
        result = jade.to_html(data)
        assert expected == result

    for tag in ["p", "div"]:
        yield do_test, tag

def test_tag_with_id():
    def do_test(data):
        tag, tag_id = data.split("#")
        expected = [
            'element',
            ['open_tag',
             tag,
             ['tag_id', tag_id]]]
        result = jade.generate_data(data, pattern=jade.element)
        assert expected == result

        expected = """<%(tag)s id="%(tag_id)s"></%(tag)s>\n""" % dict(tag=tag, tag_id=tag_id)
        result = jade.to_html(data)
        assert expected == result

    for data in ["div#foo", "p#foo", "div#bar", "p#bar", "div#foo-bar", "p#foo-bar"]:
        yield do_test, data

def test_tag_with_class():
    def do_test(data):
        tag, tag_class = data.split(".")
        expected = [
            'element',
            ['open_tag',
             tag,
             ['tag_class', tag_class]]]
        result = jade.generate_data(data, pattern=jade.element)
        assert expected == result

        expected = """<%(tag)s class="%(tag_class)s"></%(tag)s>\n""" % dict(tag=tag, tag_class=tag_class)
        result = jade.to_html(data)
        assert expected == result

    for data in ["div.foo", "p.foo", "div.bar", "p.bar", "div.foo-bar", "p.foo-bar"]:
        yield do_test, data

def test_tag_with_id_and_class():
    def do_test(data):
        tag, bits = data.split("#")
        tag_id, tag_class = bits.split(".")
        expected = [
            'element',
            ['open_tag',
             tag,
             ['tag_id', tag_id],
             ['tag_class', tag_class]]]
        result = jade.generate_data(data, pattern=jade.element)
        assert expected == result

        expected = """<%(tag)s id="%(tag_id)s" class="%(tag_class)s"></%(tag)s>\n""" % dict(tag=tag, tag_id=tag_id, tag_class=tag_class)
        result = jade.to_html(data)
        assert expected == result

    for data in ["div#foo.bar", "p#foo.bar", "div#foo-1.bar-1", "p#foo-1.bar-1"]:
        yield do_test, data

def test_content():
    def do_test(data):
        tag, content = [item.strip() for item in data.split("|")]
        expected = [
            'element',
            ['open_tag',
             tag,
             ['content',
              content]]]
        result = jade.generate_data(data, pattern=jade.element)
        assert expected == result

        expected = """<%(tag)s>%(content)s</%(tag)s>\n""" % dict(tag=tag, content=content)
        result = jade.to_html(data)
        assert expected == result

    items = [
        "p | hello",
        "div | hello",
        "p | foo",
        "div | bar"]

    for item in items:
        yield do_test, item

def test_nested():
    data = """
div#foo.bar
  p | A paragraph
    """.strip()
    expected = [
        'element',
        ['open_tag',
         "div",
         ['tag_id', "foo"],
         ['tag_class', "bar"]],
        ['element',
         ['open_tag',
          "p",
          ['content',
           "A paragraph"]]]]
    result = jade.generate_data(data, pattern=jade.element)
    assert expected == result

    expected = '''<div id="foo" class="bar"><p>A paragraph</p></div>\n'''
    result = jade.to_html(data)
    assert expected == result

def test_doctype():
    data = """
!!!
html
  body
    div
    """
    expected = [
        'document',
        ['doctype',
         "!!!"],
        ['element',
         ['open_tag',
          'html'],
         ['element',
          ['open_tag',
           'body'],
           ['element',
            ['open_tag',
            'div']]]]]
    result = jade.generate_data(data)
    assert expected == result

    expected = '''
<!DOCTYPE html>
<html>
  <body>
    <div></div>
  </body>
</html>'''.strip()
    result = jade.to_html(data, tidy=True)
    assert expected == result
