from .cfgparser import BrainFuckNode, BrainfuckParser
from .lexer import BFLexer
from typing import List, Literal


class SemanticIssue:
    type = Literal["error", "warning"]
    value = ""
    node: BrainFuckNode

    def __init__(self, type: Literal["error", "warning"], value: str, node: BrainFuckNode) -> None:
        self.node = node
        self.value = value
        self.type = type


class SemanticAnalysis:
    def __init__(self, ast):
        self.ast: BrainFuckNode = ast
        self.issues: List[SemanticIssue] = []

    def analyze(self):
        ast: BrainFuckNode = self.ast
        self.found_char_other_than_dec = False

        def traverse(node: BrainFuckNode):
            if node.value == "Loop":
                # check that loop is not empty
                found_close = False
                for child in node.children:
                    if child.value == "LoopEnd":
                        found_close = True

                # then we can add an error to our list of issues
                if not found_close:
                    self.issues.append(
                        SemanticIssue("error", "Missing loop close", node)
                    )

                # if the only node is a loopend it indicates an empty loop
                if len(node.children) == 1 and node.children[0].value == "LoopEnd":
                    self.issues.append(
                        SemanticIssue(
                            "warning", "[] either do nothing or run forever", node)
                    )

            elif node.value == "<":
                # a pointer decrement at the beginning of the program would move the tape to a negative index which is not possible
                if not self.found_char_other_than_dec:
                    self.issues.append(
                        SemanticIssue(
                            "error", "Ptr decrement in the beginning of the program", node)
                    )
            elif node.value != "Program":
                self.found_char_other_than_dec = True

            # traverse ast recursively
            for child in node.children:
                traverse(child)

        traverse(ast)


def test():
    code = "[[]++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>."
    lexer = BFLexer()
    code = lexer.lex(code)

    parser = BrainfuckParser(code)
    ast = parser.parse_program()

    analyzer = SemanticAnalysis(ast)
    analyzer.analyze()

    for issue in analyzer.issues:
        print(issue.type, issue.value, "At index {}".format(issue.node.char_index))


if __name__ == "__main__":
    test()
