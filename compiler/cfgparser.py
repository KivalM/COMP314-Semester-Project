# an implementation of a recursive desscent parser for brainfuck
# https://en.wikipedia.org/wiki/Recursive_descent_parser
# https://www.geeksforgeeks.org/recursive-descent-parser/
# https://tuckyou.in/2016/05/27/brainfuq-a-brainfuck-interpreter/

from typing import Literal
from graphviz import Digraph
from .lexer import BFLexer

# program -> (loop | operation)*
# loop -> loop_start program loop_end
# operation -> (increment | decrement | move_right | move_left | input | output)
# loop_start -> [
# loop_end -> ]
# increment -> +
# decrement -> -
# move_right -> >
# move_left -> <
# input -> ,
# output -> .
# comment -> #


# a node in our AST
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
            # perform recursive parsing depending on the type of instruction
            if char in (">", "<", "+", "-", ".", ","):
                nodes.append(self.parse_command())
            elif char == "[":
                nodes.append(self.parse_loop())
            elif char == ']':
                nodes.append(BrainFuckNode("LoopEnd", self.ptr))
                return BrainFuckNode("Program", self.ptr, nodes)
            else:
                assert AssertionError

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


# function to draw the ast as a digraph to a png using graphviz
def visualize_tree(node: BrainFuckNode, dot=None):
    if dot is None:
        dot = Digraph(format="png")
    dot.node(str(id(node)), label=node.value)

    for child in node.children:
        dot.edge(str(id(node)), str(id(child)))
        visualize_tree(child, dot)
    return dot


def visualize(tree):
    dot = visualize_tree(tree)
    dot.render('CFG', view=False)


def test():
    # Example usage:
    code = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>."
    lexer = BFLexer()
    code = lexer.lex(code)

    parser = BrainfuckParser(code)
    ast = parser.parse_program()

    visualize(ast)

    # Function to print the AST

    def print_tree(node, level=0):
        print("  " * level + node.value)
        for child in node.children:
            print_tree(child, level + 1)

    # Print AST
    print_tree(ast)


if __name__ == "__main__":
    test()
