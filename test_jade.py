# -*- coding: utf-8 -*-

import jade


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
        expected = ['tag', data]
        result = jade.parse(data)
        assert expected == result

        expected = """
<%(data)s>
</%(data)s>
        """.strip() % dict(data=data)
        result = jade.to_html(data)
        assert expected == result

    for tag in ["p", "div"]:
        yield do_test, tag

def test_tag_with_id():
    def do_test(data):
        tag, tag_id = data.split("#")
        expected = [
            'tag',
            tag,
            ['tag_id', tag_id]]
        result = jade.parse(data)
        assert expected == result

        expected = """
<%(tag)s id="%(tag_id)s">
</%(tag)s>
        """.strip() % dict(tag=tag, tag_id=tag_id)
        result = jade.to_html(data)
        assert expected == result

    for data in ["div#foo", "p#foo", "div#bar", "p#bar"]:
        yield do_test, data

def test_tag_with_class():
    def do_test(data):
        tag, tag_class = data.split(".")
        expected = [
            'tag',
            tag,
            ['tag_class', tag_class]]
        result = jade.parse(data)
        assert expected == result

        expected = """
<%(tag)s class="%(tag_class)s">
</%(tag)s>
        """.strip() % dict(tag=tag, tag_class=tag_class)
        result = jade.to_html(data)
        assert expected == result

    for data in ["div.foo", "p.foo", "div.bar", "p.bar"]:
        yield do_test, data
