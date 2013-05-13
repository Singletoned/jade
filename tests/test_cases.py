# -*- coding: utf-8 -*-

import path

import jade

cases = path.path(__file__).dirname().child("cases")


def loader(filename):
    f = cases / filename
    src = f.text()
    data = jade.generate_data(src)
    elements = jade.generate_elements(data)
    return elements

context = dict(loader=loader)

def test_cases():
    def do_test(filename):
        jade_file = cases.child(filename+".jade")
        jade_src = jade_file.text()
        html_file = cases.child(filename+".html")
        html_src = html_file.text().strip()
        result = jade.to_html(jade_src, tidy=True, context=context)
        assert html_src == result

    filenames = cases.glob("*.jade")
    filenames = [f.name for f in filenames]
    filenames = map(lambda x:x.replace('.jade',''),filenames)
    for filename in filenames:
        yield do_test, filename
