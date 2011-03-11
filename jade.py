# -*- coding: utf-8 -*-

import pegger as pg

def tag():
    return "p"

def parse(text):
    return pg.parse_string(text, tag)

def to_html(text):
    data = pg.parse_string(text, tag)
    return """
<p>
</p>
""".strip()
