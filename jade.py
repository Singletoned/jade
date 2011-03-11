# -*- coding: utf-8 -*-

import pegger as pg

def tag():
    return pg.OneOf("p", "div")

def parse(text):
    return pg.parse_string(text, tag)

def to_html(text):
    data = pg.parse_string(text, tag)
    tag_name = data[1]
    return """
<%(tag_name)s>
</%(tag_name)s>
""".strip() % dict(tag_name=tag_name)
