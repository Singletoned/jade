# -*- coding: utf-8 -*-

import string
import itertools

import pegger as pg

alphabet = pg.Words(string.lowercase+string.uppercase)
alphanumerics = pg.Words(string.lowercase+string.uppercase+string.digits)
identifier_parts = pg.Words(string.lowercase+string.uppercase+string.digits+"-")

def element():
    return pg.AllOf(
        open_tag,
        pg.Optional(
            pg.OneOf(
                content,
                pg.AllOf(
                    pg.Ignore("\n"),
                    pg.Indented(
                        element)))))

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

def indent(data):
    for item in data:
        yield "  %s" % item

def make_attr(head, rest):
    rest = iter(rest)
    attr_name = head[4:]
    attr_value = rest.next()
    attr = '''%s="%s"''' % (attr_name, attr_value)
    return attr

def make_content(head, rest):
    rest = iter(rest)
    return rest.next()

def make_open_tag(head, rest):
    rest = iter(rest)
    items = " ".join([do_render(i) for i in rest])
    return '''<%s>''' % items

def make_close_tag(head, rest):
    tag_name = iter(rest).next()
    return '''</%s>''' % tag_name

def make_element(head, rest):
    rest = iter(rest)
    open_tag, close_tag = itertools.tee(rest.next())
    open_tag = make_open_tag(open_tag.next(), open_tag)
    yield open_tag
    for item in rest:
        result = do_render(item)
        if isinstance(result, basestring):
            yield "  " + result
        else:
            for sub_item in indent(result):
                yield sub_item
    close_tag = make_close_tag(close_tag.next(), close_tag)
    yield close_tag

tag_funcs = {
    'tag_id': make_attr,
    'tag_class': make_attr,
    'content': make_content,
    'open_tag': make_open_tag,
    'element': make_element,
    }

tag_dispatchers = dict(
    element=make_element,
    open_tag=make_open_tag,
    )

def generate_html(data):
    "Convert a tree to flattened html"
    data = iter(data)
    head = data.next()
    dispatcher = tag_dispatchers[head]
    for item in dispatcher(head, data):
        yield item

def do_render(data):
    if isinstance(data, basestring):
        return data
    else:
        rest = iter(data)
        head = rest.next()
        func = tag_funcs[head]
        return func(head, rest)

def to_html(text, pattern=element):
    data = pg.parse_string(text, pattern)
    content = generate_html(data)
    return "\n".join(content)
