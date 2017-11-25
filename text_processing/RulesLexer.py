import logging

from ply import lex


class RulesLexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.logger = logging.Logger('RulesLexer')

    tokens = ('VARIABLE', 'EQUALS', 'NOT', 'AND', 'OR', 'LPAR', 'PPAR', 'COMMA', 'UNDERSCORE')

    t_EQUALS = r'='
    t_LPAR = r'\('
    t_PPAR = r'\)'
    t_COMMA = r','
    t_UNDERSCORE = r'_'

    t_ignore = ' \t\n'

    reserved = {
        'not': 'NOT',
        'and': 'AND',
        'or': 'OR'
    }

    def t_VARIABLE(self, t):
        """([a-ząęóśżźćńł]+)|("[a-ząęóśżźćńł ]+")"""
        t.type = self.reserved.get(t.value, 'VARIABLE')
        return t

    def t_error(self, t):
        self.logger.error('Parser error. Illegal character: %s' % t.value[0])
