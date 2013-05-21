# -*- coding: utf-8 -*-

import string
import itertools

import lxml

import wiseguy.html

import pegger as pg


alphabet = pg.Words(string.lowercase+string.uppercase)
alphanumerics = pg.Words(string.lowercase+string.uppercase+string.digits)
identifier_parts = pg.Words(string.lowercase+string.uppercase+string.digits+"-_")
filename_parts = pg.Words(string.lowercase+string.uppercase+string.digits+"-_.")
whitespace = pg.Words(" \t")

newline_or_eof = pg.OneOf("\n", pg.EOF())
newlines_or_eof = pg.OneOf(pg.Many("\n"), pg.EOF())

def document():
    return pg.AllOf(
        pg.Optional(
            pg.Ignore(
                newlines_or_eof)),
        pg.Optional(
            doctype),
        pg.OneOf(
            extends,
            pg.Many(
                pg.AllOf(
                    pg.OneOf(
                        element,
                        code_block,
                        comment),
                    pg.Optional(
                        pg.Ignore(
                            pg.Many(
                                "\n")))))))

def doctype():
    return pg.AllOf(
        "!!!",
        pg.Ignore(newline_or_eof))

def sub_element():
    return pg.AllOf(
        pg.Ignore(": "),
        open_tag,
        pg.Optional(
            sub_element))

def nested_elements():
    return pg.AllOf(
        pg.Indented(
            pg.Many(
                pg.OneOf(
                    block,
                    code_block,
                    element,
                    comment,
                    text))),
        pg.Ignore(newlines_or_eof))

def element():
    return pg.AllOf(
        open_tag,
        pg.Optional(
            sub_element),
        pg.Ignore(
            newlines_or_eof),
        pg.Optional(
            nested_elements))

def comment():
    return pg.AllOf(
        pg.Optional(
            pg.Ignore(
                pg.Many(
                    " "))),
        pg.Ignore(
            "// "),
        pg.Join(
            pg.Many(
                pg.Not(
                    newline_or_eof))),
        pg.Ignore(newline_or_eof))

def code_block():
    return pg.AllOf(
        pg.Ignore("!="),
        pg.Join(
            pg.Many(
                pg.Not(newline_or_eof))),
        pg.Ignore(newline_or_eof))

def custom_tag(tag_name):
    def _inner():
        return pg.AllOf(
            pg.Ignore(tag_name),
            pg.Ignore(" "),
            identifier_parts,
            pg.Ignore(newline_or_eof),
            pg.Optional(
                nested_elements))
    _inner.__name__ = tag_name
    return _inner

block = custom_tag('block')
replace = custom_tag('replace')
append = custom_tag('append')

def extends():
    return pg.AllOf(
        pg.Ignore("extends"),
        pg.Ignore(" "),
        filename_parts,
        pg.Ignore(newlines_or_eof),
        pg.Optional(
            pg.Many(
                pg.OneOf(
                    replace,
                    append))))

def text():
    return pg.AllOf(
        pg.Ignore("| "),
        pg.Join(
            pg.Many(
                pg.Not(newline_or_eof))),
        pg.Ignore(newline_or_eof))

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
                    newline_or_eof))))

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
        pg.Ignore(
            pg.OneOf(
                " | ",
                " ")),
        pg.Join(
            pg.Many(
                pg.Not(newline_or_eof))))


class UnknownItemError(Exception):
    pass

html_builder = wiseguy.html.HtmlBuilder()

def El(tag_name):
    return getattr(html_builder, tag_name)()

def make_attr(head, rest, context=None):
    rest = iter(rest)
    attr_name = head[4:]
    attr_value = rest.next()
    attr = '''%s="%s"''' % (attr_name, attr_value)
    return attr

def make_content(head, rest, context=None):
    rest = iter(rest)
    return rest.next()

def make_open_tag(head, rest, context=None):
    rest = iter(rest)
    items = " ".join([do_render(i) for i in rest])
    return '''<%s>''' % items

def make_close_tag(head, rest, context=None):
    tag_name = iter(rest).next()
    return '''</%s>''' % tag_name

def add_attributes(el, attributes, context=None):
    attributes = list(attributes)
    for item in attributes:
        if len(item) == 2:
            _, key = item
            value_pair = [None, key]
        else:
            (_, key, value_pair) = item
        if value_pair[0] == "attribute_value_code":
            value = eval(value_pair[1], context)
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

def make_comment(head, rest, context=None):
    rest = iter(rest)
    yield lxml.html.HtmlComment(rest.next())

def make_block(head, rest, context=None):
    rest = iter(rest)
    el = html_builder.block({'data-id': rest.next()})
    add_subelements(el, rest, context)
    yield el

def make_extends(head, rest, context=None):
    rest = iter(rest)
    document = context['loader'](rest.next())
    document = list(document)
    for block in rest:
        block_type = block[0]
        block_name = block[1]
        block_rest = block[2][1:]
        if block_type == 'replace':
            if len(block_rest) > 1:
                block_el = El('div')
                add_subelements(block_el, block_rest, context)
            else:
                block_rest = block_rest[0]
                if block_rest[0] == 'text':
                    block_el = block_rest[1]
                else:
                    block_el = make_element(block_rest[0], block_rest[1:], context).next()
            for el in document:
                el.replace("block[data-id='%s']"%block_name, block_el)
        elif block_type == 'append':
            for item in block_rest:
                block_el = make_element(item[0], item[1:], context).next()
                for el in document:
                    el.add("block[data-id='%s']"%block_name, block_el)
        else:
            assert False
    for el in document:
        yield el

class DocType(object):
    def __init__(self, string):
        self.string = "<!DOCTYPE html>"

    def to_string(self):
        return self.string

def make_doctype(head, rest, context=None):
    rest = iter(rest)
    yield DocType(rest.next())

def make_element(head, rest, context=None):
    rest = iter(rest)
    open_tag = iter(rest.next())
    _ = open_tag.next()
    tag_name = open_tag.next()
    el = El(tag_name)
    open_tag = list(open_tag)
    for item in open_tag:
        if item[0] == 'attribute_list':
            add_attributes(el, item[1:], context)
        elif item[0] == 'tag_class':
            el.add_class(None, item[1])
        elif item[0] == 'tag_id':
            el.attrib['id'] = item[1]
        elif item[0] == 'content':
            el.text = item[1]
        elif item[0] == 'code':
            val = eval(item[1], context)
            if val is None:
                val = ""
            el.text = str(val)
    rest = list(rest)
    add_subelements(el, rest, context)
    yield el

def add_subelements(el, rest, context=None):
    for item in rest:
        if item[0] == 'text':
            if el.getchildren():
                last_child = el.getchildren()[-1]
                last_child.tail = (last_child.tail or '') + item[1]
            else:
                el.text = (el.text or '') + item[1]
        elif item[0] == 'nested_elements':
            add_subelements(el, item[1:], context=context)
        else:
            for sub_item in do_render(item, context):
                el.add(None, sub_item)

def make_document(head, rest, context=None):
    rest = list(rest)
    for el in rest:
        for item in do_render(el, context):
            yield item

def make_code_block(head, rest, context=None):
    for item in rest:
        yield eval(item, context)

tag_funcs = {
    'tag_id': make_attr,
    'tag_class': make_attr,
    'content': make_content,
    'open_tag': make_open_tag,
    'element': make_element,
    'sub_element': make_element,
    'document': make_document,
    'comment': make_comment,
    'doctype': make_doctype,
    'block': make_block,
    'extends': make_extends,
    'code_block': make_code_block,
    }

tag_dispatchers = dict(
    document=make_document,
    element=make_element,
    open_tag=make_open_tag,
    )

def do_render(data, context=None):
    if isinstance(data, basestring):
        return data
    else:
        rest = iter(data)
        head = rest.next()
        func = tag_funcs[head]
        return func(head, rest, context)

def generate_data(text, pattern=document):
    data = pg.parse_string(text, pattern)
    return data

def generate_elements(data, context=None):
    data = iter(data)
    head = data.next()
    dispatcher = tag_dispatchers[head]
    for item in dispatcher(head, data, context=context):
        yield item

def generate_strings(elements, tidy=False):
    if tidy:
        for el in elements:
            if isinstance(el, DocType):
                yield el.to_string()
            else:
                yield wiseguy.html_tidy.tidy_html(el, with_doctype=False)
    else:
        for el in elements:
            yield el.to_string()

def remove_blocks(elements):
    for el in elements:
        if not isinstance(el, (lxml.html.HtmlComment, DocType)):
            el.extract("block")
        yield el

def to_elements(text, pattern=document, tidy=False, context=None):
    text = text.decode('utf-8')
    data = generate_data(text, pattern=document)
    elements = generate_elements(data, context)
    elements = remove_blocks(elements)
    for element in elements:
        yield element

def to_html(text, pattern=document, tidy=False, context=None):
    elements = to_elements(text, pattern, tidy, context)
    strings = generate_strings(elements, tidy=tidy)
    if tidy:
        joiner = "\n"
    else:
        joiner = ""
    return joiner.join(strings)
