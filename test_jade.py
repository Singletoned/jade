# -*- coding: utf-8 -*-

import jade

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
    data = "div#foo"
    expected = ['tag',
                "div",
                ['tag_id', "foo"]]
    result = jade.parse(data)
    assert expected == result

    expected = """
<div id="foo">
</div>
    """.strip()
    result = jade.to_html(data)
    assert expected == result
