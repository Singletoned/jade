# -*- coding: utf-8 -*-

import string

import pegger as pg

alphabet = pg.Words(string.lowercase+string.uppercase)
alphanumerics = pg.Words(string.lowercase+string.uppercase+string.digits)

def tag():
    return pg.AllOf(
        alphabet,
        pg.Optional(
            tag_id),
        pg.Optional(
            tag_class))

def tag_id():
    return pg.AllOf(
        pg.Ignore("#"),
        pg.Words())

def tag_class():
    return pg.AllOf(
        pg.Ignore("."),
        pg.Words())

def parse(text):
    return pg.parse_string(text, tag)

def to_html(text):
    data = pg.parse_string(text, tag)
    tag_name = data[1]
    open_tag_items = [tag_name]
    if len(data) > 2:
        item = data[2]
        if item[0] == "tag_id":
            open_tag_items.append('''id="%s"''' % data[2][1])
        else:
            open_tag_items.append('''class="%s"''' % data[2][1])
    open_tag = " ".join(open_tag_items)
    return """
<%(open_tag)s>
</%(tag_name)s>
""".strip() % dict(open_tag=open_tag, tag_name=tag_name)
