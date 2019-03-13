from lexer.lexer import Lexer
import os

examples = 'examples'
files = os.listdir(examples)

for file in files:
    filepath = os.path.join(examples, file)
    with open(filepath) as f:
        text = f.read()

    print(f'\n', filepath)
    print('-' * 20, '\n')
    lexer = Lexer(text)
    for x in lexer:
        print(x)


