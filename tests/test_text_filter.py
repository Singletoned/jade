# -*- coding: utf-8 -*-

import jade


def _text_filter(text):
    return text.replace("o", "a")

def loader(filename, context):
    src = """
html
  head
    title | master_foo
  body
    block main
    block footer
"""
    data = jade.generate_data(src)
    elements = jade.generate_elements(data, context=context)
    return elements

def test_text_filter():
    src = """
extends anything

append main
  div | foo1
    | foo2
    p | foo3
    p
    | foo4

replace footer
  | foo_ter
  div
""".strip()

    expected = """
<html>
  <head>
    <title>master_faa</title>
  </head>
  <body>
    <div>
      faa1faa2
      <p>
        faa3
      </p>
      <p></p>
      faa4
    </div>
    <div>
      faa_ter
      <div></div>
    </div>
  </body>
</html>
""".strip()

    context = dict(
        loader=loader,
        _text_filter=_text_filter)
    data = jade.generate_data(src)
    result = jade.to_html(src, tidy=True, context=context)
    assert expected == result
