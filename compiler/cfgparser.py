# an implementation of a recursive desscent parser for brainfuck
# https://en.wikipedia.org/wiki/Recursive_descent_parser
# https://www.geeksforgeeks.org/recursive-descent-parser/
from typing import Literal
from lexer import BFLexer


class BrainFuckNode:
    def __init__(self, value, char_index, children=None, ):
        self.value: Literal["Loop", "Program", "LoopEnd",
                            "<", ">", ".", ",", "+", "-"] = value
        self.children = children or []
        self.parent = None
        self.char_index = char_index

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def __str__(self):
        return self.value

    def getValue(self):
        return self.value

    def getChildren(self):
        return self.children


class BrainfuckParser:
    def __init__(self, code):
        self.code = code
        self.ptr = 0

    def parse_program(self):
        nodes = []
        while self.ptr < len(self.code):
            char = self.code[self.ptr]

            if char in (">", "<", "+", "-", ".", ","):
                nodes.append(self.parse_command())
            elif char == "[":
                nodes.append(self.parse_loop())
            elif char == ']':
                nodes.append(BrainFuckNode("LoopEnd", self.ptr))
                return BrainFuckNode("Program", self.ptr, nodes)
            else:
                AssertionError

        return BrainFuckNode("Program", self.ptr, nodes)

    def parse_command(self):
        char = self.code[self.ptr]
        self.ptr += 1
        return BrainFuckNode(char, self.ptr)

    def parse_loop(self):
        self.ptr += 1  # Skip the opening '['
        loop_nodes = self.parse_program()
        self.ptr += 1  # Skip the closing ']'
        return BrainFuckNode("Loop", self.ptr, loop_nodes.children)


def test():
    # Example usage:
    code = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>."
    lexer = BFLexer()
    code = lexer.lex(code)

    parser = BrainfuckParser(code)
    ast = parser.parse_program()

    # Function to print the AST

    def print_tree(node, level=0):
        print("  " * level + node.value)
        for child in node.children:
            print_tree(child, level + 1)

    # Print AST
    print_tree(ast)


if __name__ == "__main__":
    test()
