from typing import Union

from dataclasses import dataclass


@dataclass
class Token:
    """ This class represents Token
    Output from Lexical analysis is list of tokens"""
    type: str
    value: Union[int, str, float, bool]

    def __eq__(self, other: str):
        return self.type == other
