# -*- coding: utf-8 -*-

import string
import itertools

import wiseguy.html_tags

import pegger as pg


alphabet = pg.Words(string.lowercase+string.uppercase)
alphanumerics = pg.Words(string.lowercase+string.uppercase+string.digits)
identifier_parts = pg.Words(string.lowercase+string.uppercase+string.digits+"-_")

def document():
    return pg.AllOf(
        element,
        pg.Optional(
            pg.Many(
                pg.AllOf(
                    pg.Ignore("\n"),
                    element))))

def element():
    return pg.AllOf(
        open_tag,
        pg.Optional(
            pg.AllOf(
                pg.Ignore(": ",),
                element)),
        pg.Optional(
            pg.Many(
                pg.AllOf(
                    pg.Ignore("\n"),
                    pg.Indented(
                        element)))))

def open_tag():
    return pg.AllOf(
        alphanumerics,
        pg.Optional(
            pg.Many(
                pg.OneOf(
                    tag_id,
                    tag_class,
                    attribute_list))),
        pg.Optional(
            pg.OneOf(
                content,
                code)))

def code():
    return pg.AllOf(
        pg.Ignore("= "),
        pg.Join(
            pg.Many(
                pg.Not(
                    "\n"))))

def tag_id():
    return pg.AllOf(
        pg.Ignore("#"),
        identifier_parts)

def tag_class():
    return pg.AllOf(
        pg.Ignore("."),
        identifier_parts)

def quoted_string():
    return pg.OneOf(
        pg.AllOf(
            pg.Ignore("'"),
            pg.Optional(
                pg.Join(
                    pg.Many(
                        pg.Not("'")))),
            pg.Ignore("'")),
        pg.AllOf(
            pg.Ignore('"'),
            pg.Optional(
                pg.Join(
                    pg.Many(
                        pg.Not('"')))),
            pg.Ignore('"')))

def attribute_value_code():
    return pg.Join(
        pg.Many(
            pg.Not(
                pg.OneOf(
                    ")",
                    ","))))

def attribute():
    return pg.OneOf(
        pg.AllOf(
            identifier_parts,
            pg.Ignore("="),
            pg.OneOf(
                quoted_string,
                attribute_value_code)),
        alphanumerics)

def attribute_list():
    return pg.AllOf(
        pg.Ignore("("),
        attribute,
        pg.Optional(
            pg.Many(
                pg.AllOf(
                    pg.Ignore(","),
                    pg.Ignore(pg.Optional(" ")),
                    attribute))),
        pg.Ignore(")"))

def content():
    return pg.AllOf(
        pg.Ignore(" | "),
        pg.Words())

def parse(text, pattern=element):
    return pg.parse_string(text, pattern)

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

def add_attributes(el, attributes):
    attributes = list(attributes)
    for item in attributes:
        if len(item) == 2:
            _, key = item
            value_pair = [None, key]
        else:
            (_, key, value_pair) = item
        if value_pair[0] == "attribute_value_code":
            value = eval(value_pair[1])
        else:
            value = value_pair[1]
        if value is None:
            value = ""
        elif value is False:
            continue
        else:
            value = str(value)
        if key == "class":
            el.add_class(None, value)
        else:
            el.attrib[key] = value

def make_element(head, rest):
    rest = list(rest)
    rest = iter(rest)
    open_tag = iter(rest.next())
    _ = open_tag.next()
    tag_name = open_tag.next()
    el = getattr(wiseguy.html_tags, tag_name.upper())()
    open_tag = list(open_tag)
    for item in open_tag:
        if item[0] == 'attribute_list':
            add_attributes(el, item[1:])
        elif item[0] == 'tag_class':
            el.add_class(None, item[1])
        elif item[0] == 'tag_id':
            el.attrib['id'] = item[1]
        elif item[0] == 'content':
            el.text = item[1]
        elif item[0] == 'code':
            val = eval(item[1])
            if val is None:
                val = ""
            el.text = str(val)
    for item in rest:
        if item[0] == 'element':
            sub_el = make_element(item[0], item[1:])
            el.extend(sub_el)
    yield el

def make_document(head, rest):
    rest = list(rest)
    for el in rest:
        for item in do_render(el):
            yield item

tag_funcs = {
    'tag_id': make_attr,
    'tag_class': make_attr,
    'content': make_content,
    'open_tag': make_open_tag,
    'element': make_element,
    'document': make_document,
    }

tag_dispatchers = dict(
    document=make_document,
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

def generate_elements(text, pattern=document):
    data = pg.parse_string(text, pattern)
    elements = generate_html(data)
    return elements

def generate_strings(text, pattern, tidy=False):
    elements = generate_elements(text, pattern)
    if tidy:
        for el in elements:
            yield wiseguy.html_tidy.tidy_html(el)
    else:
        for el in elements:
            yield el.to_string()

def to_html(text, pattern=document, tidy=False):
    return "".join(generate_strings(text, pattern, tidy=tidy))
