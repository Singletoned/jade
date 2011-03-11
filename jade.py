# -*- coding: utf-8 -*-

import pegger as pg

def tag():
    return "p"

def parse(text):
    return pg.parse_string(text, tag)
