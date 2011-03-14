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
        alphanumerics)

def tag_class():
    return pg.AllOf(
        pg.Ignore("."),
        alphanumerics)

def parse(text):
    return pg.parse_string(text, tag)

def do_render(item):
    if isinstance(item, basestring):
        return item
    else:
        return '''%s="%s"''' % (item[0][4:], item[1])

def to_html(text):
    data = pg.parse_string(text, tag)
    tag_name = data[1]
    open_tag_items = [do_render(item) for item in data[1:]]
    open_tag = " ".join(open_tag_items)
    return """
<%(open_tag)s>
</%(tag_name)s>
""".strip() % dict(open_tag=open_tag, tag_name=tag_name)
