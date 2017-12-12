import logging

from text_processing import NGramUtils
from text_processing.RulesLexer import RulesLexer
import ply.yacc as yacc


class RulesParser:
    tokens = RulesLexer.tokens

    def __init__(self):
        self.lexer = RulesLexer()
        self.parser = yacc.yacc(module=self)
        self.logger = logging.getLogger('RulesParser')
        self.text = None

    def set_text(self, text):
        self.text = text

    def _is_present(self, phrase):
        return NGramUtils.is_phrase_present(phrase, self.text)

    def p_rule(self, p):
        """rule : unbound_variable EQUALS expr"""
        p[0] = (p[1], p[3])

    def p_expr(self, p):
        """expr : not_expr
                    | and_expr
                    | or_expr
                    | bound_variable"""
        p[0] = p[1]

    def p_and_expr(self, p):
        """and_expr : AND LPAR comma_arg_list PPAR"""
        p[0] = all(p[3])

    def p_or_expr(self, p):
        """or_expr : OR LPAR comma_arg_list PPAR"""
        p[0] = any(p[3])

    def p_comma_arg_list(self, p):
        """comma_arg_list : single_arg
                     | arg_list"""
        p[0] = p[1]

    def p_single_arg(self, p):
        """single_arg : expr"""
        p[0] = [p[1]]

    def p_arg_list(self, p):
        """arg_list : comma_arg_list COMMA expr"""
        p[0] = p[1] + [p[3]]

    def p_not_expr(self, p):
        """not_expr : NOT LPAR expr PPAR"""
        p[0] = not p[3]

    def p_bound_variable(self, p):
        """bound_variable : VARIABLE"""
        p[0] = self._is_present(p[1])

    def p_unbound_variable(self, p):
        """unbound_variable : UNDERSCORE VARIABLE"""
        p[0] = p[1] + p[2]

    def p_error(self, p):
        self.logger.error('Parser error: %s' % str(p))

    def parse(self, rule):
        return self.parser.parse(rule)
