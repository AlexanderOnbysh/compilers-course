from .tree import *
from .utils import *
from ..lexer.keywords import *

BIN_OP = (ADD_OP, SUB_OP, MUL_OP, DIV_OP, POWER_OP, MOD_OP, AND_OP, OR_OP, GE_OP, GT_OP, LE_OP, LT_OP, EQ_OP, NE_OP)


class SyntaxError(Exception): ...


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token  # set current token to the first token taken from the input

    def error(self, message):
        raise SyntaxError(message)

    def eat(self, token_type):
        """ Compare the current token type with the passed token
        type and if they match then "eat" the current token
        and assign the next token to the self.current_token,
        otherwise raise an exception. """

        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token
        else:
            self.error(
                'Expected token <{}> but found <{}> at line {}.'.format(
                    token_type, self.current_token.type, self.lexer.line
                )
            )

    def program(self):
        root = Program(
            declarations=self.declarations(),
            line=self.lexer.line
        )
        return root

    def declarations(self):
        declarations = []

        while self.current_token.type in (DEF_FUC, ID):
            if self.current_token.type == ID:
                declarations.extend(self.declaration())
            elif self.current_token.type == DEF_FUC:
                declarations.append(self.function_declaration())
        return declarations

    def declaration(self):
        variable = self.variable()
        self.eat(COLON)
        type_node = self.type_spec()
        if self.current_token == ASSIGN:
            self.eat(ASSIGN)
        expression = self.expression()

        return VarDecl(
            var_node=variable,
            type_node=type_node,
            line=self.lexer.line,
            value=expression,
        )

    def function_declaration(self):
        self.eat(DEF_FUC)
        func_name = self.current_token.value
        self.eat(LPAREN)
        params = self.arg_list()
        self.eat(RPAREN)
        self.eat(RETURN_FUNC)
        type_node = self.type_spec()
        return FunctionDecl(
            type_node=type_node,
            func_name=func_name,
            params=params,
            body=self.block(),
            line=self.lexer.line
        )

    def block(self):
        result = []

        self.eat(BEGIN)
        while self.current_token.type != END:
            # declaration
            if self.current_token.type in (ID, DEF_FUC):
                result.extend(self.declarations())
            # statements
            elif self.current_token.type in (IF, FOR, WHILE, RETURN):
                result.extend(self.statement())
            else:
                result.append(self.expression())
        self.eat(END)
        return FunctionBody(
            children=result,
            line=self.lexer.line
        )

    def arg_list(self):
        nodes = []
        if self.current_token.type != RPAREN:
            identifier = self.variable()
            type_spec = self.type_spec()
            nodes = [Param(
                type_node=type_spec,
                var_node=identifier,
                line=self.lexer.line
            )]
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                identifier = self.variable()
                type_spec = self.type_spec()
                nodes.append(Param(
                    type_node=type_spec,
                    var_node=identifier,
                    line=self.lexer.line
                ))
        return nodes

    def init_declarator(self):
        """
        init_declarator             : variable (ASSIGN assignment_expression)?
        """
        var = self.variable()
        result = list()
        result.append(var)
        if self.current_token.type == ASSIGN:
            token = self.current_token
            self.eat(ASSIGN)
            result.append(Assign(
                left=var,
                op=token,
                right=self.assignment_expression(),
                line=self.lexer.line
            ))
        return result

    def statement(self):
        if self.current_token.type == FOR:
            return self.for_statement()
        elif self.current_token.type == IF:
            return self.if_statement()
        elif self.current_token.type == WHILE:
            return self.while_statement()
        elif self.current_token == RETURN:
            self.eat(RETURN)
            expression = self.expression()
            return ReturnStmt(expression, self.lexer.line)
        elif self.current_token == BREAK:
            self.eat(BREAK)
            return BreakStmt(self.lexer.line)
        elif self.current_token == CONTINUE:
            self.eat(CONTINUE)
            return ContinueStmt(self.lexer.line)
        else:
            self.error(f'Expected "if", "for", "while" or "return" statement '
                       f'but found <{self.current_token}> at line {self.lexer.line}.')

    def for_statement(self):
        self.eat(FOR)
        if self.current_token == ID:
            setup = self.declaration()
        else:
            setup = self.expression()
        self.eat(SEMICOLON)
        condition = self.expression()
        self.eat(SEMICOLON)
        increment = self.expression()
        block = self.block()

        return ForStmt(
            setup=setup,
            condition=condition,
            increment=increment,
            body=block,
            line=self.lexer.line,
        )

    def if_statement(self):
        self.eat(IF)
        condition = self.expression()
        self.eat(COLON)
        true_block = self.block()
        false_block = None
        if self.current_token == ELSE:
            false_block = self.block()
        return IfStmt(
            condition=condition,
            tbody=true_block,
            fbody=false_block,
            line=self.lexer.line
        )

    def while_statement(self):
        self.eat(WHILE)
        condition = self.expression()
        self.eat(COLON)
        block = self.block()

        return WhileStmt(
            condition=condition,
            body=block,
            line=self.lexer.line
        )

    def expression(self):
        if self.current_token == NOT_OP:
            operator = self.current_token
            self.eat(NOT_OP)
            return UnOp(operator, self.expression(), self.lexer.line)
        elif self.current_token == SUB_OP:
            operator = self.current_token
            self.eat(SUB_OP)
            return UnOp(operator, self.expression(), self.lexer.line)
        elif self.current_token == LPAREN:
            self.eat(LPAREN)
            node = self.expression()
            self.eat(RPAREN)
            return node
        elif self.current_token.type == self.check_assignment_expression():
            identifier = self.current_token
            self.eat(ID)
            operator = self.current_token
            self.eat(ASSIGN)
            expression = self.expression()
            return Assign(identifier, operator, expression, self.lexer.line)
        elif self.current_token in (ID, FLOAT, INT, CHAR, BOOL, STRING):
            atom = self.atom_expression()
            if self.current_token == EOL:
                return atom
            if self.current_token in BIN_OP:
                operator = self.current_token
                second_atom = self.expression()
                return BinOp(atom, operator, second_atom, self.lexer.line)

    @restorable
    def check_assignment_expression(self):
        if self.current_token.type == ID:
            self.eat(ID)
            if self.current_token == ASSIGN:
                return True
        return False

    def assignment(self):
        name = self.current_token
        self.eat(ID)
        operator = self.current_token
        self.eat(ASSIGN)
        value = self.expression()
        return Assign(name, operator, value, self.lexer.line)

    @restorable
    def check_function_call(self):
        if self.current_token == ID:
            self.eat(ID)
            self.eat(LPAREN)
            if self.current_token == RPAREN:
                return True
            args = []
            while self.current_token != RPAREN:
                args.append(self.expression())
                self.eat(COMMA)
            return True
        return False

    def function_call(self):
        if self.current_token == ID:
            name = self.current_token
            line = self.lexer.line
            self.eat(ID)
            self.eat(LPAREN)
            if self.current_token == RPAREN:
                return True
            args = []
            while self.current_token != RPAREN:
                args.append(self.expression())
                self.eat(COMMA)
            return FunctionCall(name, args, line)

    def atom_expression(self):
        if self.check_function_call():
            return self.function_call()
        elif self.current_token == ID:
            return self.variable()
        return self.constant()

    def constant(self):
        token = self.current_token
        if token in (INT, FLOAT, CHAR, STRING, BOOL):
            self.eat(token.type)
            return Num(
                token=token,
                line=self.lexer.line
            )
        raise Exception()

    def type_spec(self):
        token = self.current_token
        if token.type in (CHAR, INT, FLOAT, BOOL, VOID):
            self.eat(token.type)
            return Type(
                token=token,
                line=self.lexer.line
            )

    def variable(self):
        node = Var(
            token=self.current_token,
            line=self.lexer.line
        )
        self.eat(ID)
        return node

    def empty(self):
        return NoOp(
            line=self.lexer.line
        )

    def string(self):
        token = self.current_token
        self.eat(STRING)
        return String(
            token=token,
            line=self.lexer.line
        )

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error("Expected token <EOF> but found <{}>".format(self.current_token.type))

        return node
