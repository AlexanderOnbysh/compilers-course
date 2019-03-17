""" SCI - Simple C Interpreter """
from .keywords import *
from .token import Token

RESERVED_KEYWORDS = {
    'def': Token(DEF_FUC, 'def'),
    'begin': Token(BEGIN, 'begin'),
    'end': Token(END, 'end'),

    'char': Token(CHAR, 'char'),
    'int': Token(INT, 'int'),
    'float': Token(FLOAT, 'float'),
    'void': Token(VOID, 'void'),
    'bool': Token(BOOL, 'bool'),
    'True': Token(TRUE, 'True'),
    'False': Token(FALSE, 'False'),

    'if': Token(IF, 'if'),
    'elif': Token(ELIF, 'elif'),
    'else': Token(ELSE, 'else'),
    'for': Token(FOR, 'for'),
    'while': Token(WHILE, 'while'),
    'do': Token(DO, 'do'),
    'return': Token(RETURN, 'return'),
    'break': Token(BREAK, 'break'),
    'continue': Token(CONTINUE, 'continue'),
}


class LexicalError(Exception): ...


class Lexer:
    def __init__(self, text):
        self.text = text.replace('\\n', '\n')
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.line = 1

    def error(self, message):
        raise LexicalError(message)

    def make_step(self):
        """ Advance the `pos` pointer and set the `current_char` variable. """
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def ahead(self, n):
        """ Check next n-th char but don't change state. """
        peek_pos = self.pos + n
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        """ Skip all whitespaces between tokens from input """
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
            self.make_step()

    def skip_comment(self):
        """ Skip single line comment """
        while self.current_char is not None:
            if self.current_char == '\n':
                self.line += 1
                self.make_step()
                return
            self.make_step()

    def number(self):
        """Return a (multidigit) integer or float consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.make_step()

        if self.current_char == '.':
            result += self.current_char
            self.make_step()

            while (self.current_char is not None and self.current_char.isdigit()):
                result += self.current_char
                self.make_step()

            return Token(FLOAT_CONST, float(result))
        return Token(INTEGER_CONST, int(result))

    def string(self):
        """ Return string written in code without double quotes"""
        result = ''
        self.make_step()
        while self.current_char is not '"':
            if self.current_char is None:
                self.error(
                    message='Unfinished string with \'"\' at line {}'.format(self.line)
                )
            result += self.current_char
            self.make_step()
        self.make_step()
        return Token(STRING, result)

    def char(self):
        """ Handle chars between single quotes """
        self.make_step()
        char = self.current_char
        self.make_step()
        if self.current_char != '\'':
            self.error("Unclosed char constant at line {}".format(self.line))
        self.make_step()
        return Token(CHAR_CONST, ord(char))

    def _id(self):
        """ Handle identifiers and reserved keywords """
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.make_step()

        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    @property
    def get_next_token(self):
        """ Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time. """

        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.skip_comment()
                continue

            if self.current_char == '-' and \
                self.ahead(1) == '>':
                self.make_step()
                self.make_step()
                return Token(RETURN_FUNC, '->')

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '"':
                return self.string()

            if self.current_char == '\'':
                return self.char()

            if self.current_char == '<' and self.ahead(1) == '=':
                self.make_step()
                self.make_step()
                return Token(LE_OP, '<=')

            if self.current_char == '>' and self.ahead(1) == '=':
                self.make_step()
                self.make_step()
                return Token(GE_OP, '>=')

            if self.current_char == '=' and self.ahead(1) == '=':
                self.make_step()
                self.make_step()
                return Token(EQ_OP, '==')

            if self.current_char == '!' and self.ahead(1) == '=':
                self.make_step()
                self.make_step()
                return Token(NE_OP, '!=')

            if self.current_char == '<':
                self.make_step()
                return Token(LT_OP, '<')

            if self.current_char == '>':
                self.make_step()
                return Token(GT_OP, '>')

            if self.current_char == '=':
                self.make_step()
                return Token(ASSIGN, '=')

            if self.current_char == '+':
                self.make_step()
                return Token(ADD_OP, '+')

            if self.current_char == '-':
                self.make_step()
                return Token(SUB_OP, '-')

            if self.current_char == '*' and \
                    self.ahead(1) == '*':
                self.make_step()
                self.make_step()
                return Token(POWER_OP, '**')

            if self.current_char == '*':
                self.make_step()
                return Token(MUL_OP, '*')

            if self.current_char == '/':
                self.make_step()
                return Token(DIV_OP, '/')

            if self.current_char == '%':
                self.make_step()
                return Token(MOD_OP, '%')

            if self.current_char == '(':
                self.make_step()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.make_step()
                return Token(RPAREN, ')')

            if self.current_char == ';':
                self.make_step()
                return Token(SEMICOLON, ';')

            if self.current_char == ':':
                self.make_step()
                return Token(COLON, ':')

            if self.current_char == ',':
                self.make_step()
                return Token(COMMA, ',')

            if self.current_char == '.':
                self.make_step()
                return Token(DOT, '.')

            self.error(
                message="Invalid char {} at line {}".format(self.current_char, self.line)
            )

        return Token(EOF, None)

    def __next__(self):
        token = self.get_next_token
        if token.type == EOF:
            raise StopIteration
        return token

    def __iter__(self):
        return self
