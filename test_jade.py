# -*- coding: utf-8 -*-

import jade

def test_simple_tag():
    data = "p"
    expected = ['tag', "p"]
    result = jade.parse(data)
    assert expected == result

    expected = """
<p>
</p>
    """.strip()
    result = jade.to_html(data)
    assert expected == result
