# -*- coding: utf-8 -*-

import pegger as pg

def tag():
    return pg.AllOf(
        pg.Words(),
        pg.Optional(
            tag_id))

def tag_id():
    return pg.AllOf(
        pg.Ignore("#"),
        pg.Words())

def parse(text):
    return pg.parse_string(text, tag)

def to_html(text):
    data = pg.parse_string(text, tag)
    tag_name = data[1]
    open_tag_items = [tag_name]
    if len(data) > 2:
        open_tag_items.append('''id="%s"''' % data[2][1])
    open_tag = " ".join(open_tag_items)
    return """
<%(open_tag)s>
</%(tag_name)s>
""".strip() % dict(open_tag=open_tag, tag_name=tag_name)
