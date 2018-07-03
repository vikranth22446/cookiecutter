# -*- coding: utf-8 -*-

from jinja2 import nodes
from jinja2.ext import Extension


class LocalExtension(Extension):
    tags = {'local'}

    def __init__(self, environment):
        super(LocalExtension, self).__init__(environment)

    def _local(self, name):
        return 'Hello Local {name}!'.format(name=name)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        node = parser.parse_expression()
        call_method = self.call_method('_local', [node], lineno=lineno)
        return nodes.Output([call_method], lineno=lineno)
