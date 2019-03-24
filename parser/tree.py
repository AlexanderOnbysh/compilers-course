from typing import Union, List

from dataclasses import dataclass

from lexer.lexer_token import Token


@dataclass
class Node:
    line: int


@dataclass
class NoOp(Node): ...


@dataclass
class Num(Node):
    token: Token
    value: Union[int, float, str, bool]


@dataclass
class String(Node):
    token: Token


@dataclass
class Type(Node):
    token: Token


@dataclass
class Var(Node):
    token: Token


@dataclass
class BinOp(Node):
    left: Node
    op: Token
    right: Node


@dataclass
class UnOp(Node):
    token: Token
    expr: Node
    prefix: Token


@dataclass
class Assign(Node):
    left: Token
    token: Token


@dataclass
class Expression(Node):
    children: Node


@dataclass
class FunctionCall(Node):
    name: Token
    args: List[Node]


@dataclass
class IfStmt(Node):
    condition: Node
    tbody: Node
    fbody: Node


@dataclass
class WhileStmt(Node):
    condition: Node
    body: Node


@dataclass
class ReturnStmt(Node):
    expression: Node


@dataclass
class BreakStmt(Node): ...


@dataclass
class ContinueStmt(Node): ...


@dataclass
class ForStmt(Node):
    setup: Node
    condition: Node
    increment: Node
    body: Node


@dataclass
class CompoundStmt(Node):
    children: Node


@dataclass
class VarDecl(Node):
    var_node: Node
    type_node: Node
    value: Union[int, str, bool, float] = None


@dataclass
class Param(Node):
    type_node: Node
    var_node: Node


@dataclass
class FunctionDecl(Node):
    type_node: Node
    func_name: Token
    params: List[Node]
    body: Node


@dataclass
class FunctionBody(Node):
    children: Node


@dataclass
class Program(Node):
    declarations: Node
