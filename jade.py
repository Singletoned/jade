# -*- coding: utf-8 -*-

import string

import pegger as pg

alphabet = pg.Words(string.lowercase+string.uppercase)
alphanumerics = pg.Words(string.lowercase+string.uppercase+string.digits)
identifier_parts = pg.Words(string.lowercase+string.uppercase+string.digits+"-")

def element():
    return pg.AllOf(
        open_tag,
        pg.Optional(
            content))

def open_tag():
    return pg.AllOf(
        alphabet,
        pg.Optional(
            tag_id),
        pg.Optional(
            tag_class))

def tag_id():
    return pg.AllOf(
        pg.Ignore("#"),
        identifier_parts)

def tag_class():
    return pg.AllOf(
        pg.Ignore("."),
        identifier_parts)

def content():
    return pg.AllOf(
        pg.Ignore(" | "),
        pg.Words())

def parse(text):
    return pg.parse_string(text, element)

def make_attr(head, rest):
    attr_name = head[4:]
    attr_value = rest[0]
    attr = '''%s="%s"''' % (attr_name, attr_value)
    return attr

def make_content(head, rest):
    return rest[0]

def make_open_tag(head, rest):
    tag_name = rest[0]
    items = " ".join([do_render(i) for i in rest])
    return '''<%s>''' % items

def make_element(head, rest):
    element_lines = [do_render(item) for item in rest]
    element_lines.append("</%s>" % rest[0][1])
    return "".join(element_lines)

tag_funcs = {
    'tag_id': make_attr,
    'tag_class': make_attr,
    'content': make_content,
    'open_tag': make_open_tag,
    'element': make_element,
    }

def do_render(data):
    if isinstance(data, basestring):
        return data
    else:
        head, rest = data[0], data[1:]
        func = tag_funcs[head]
        return func(head, rest)

def to_html(text):
    data = pg.parse_string(text, element)
    return do_render(data)
