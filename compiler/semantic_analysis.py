from cfgparser import BrainFuckNode, BrainfuckParser
from lexer import BFLexer
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
        return self.check_missing_brackets() and self.check_ptr_decrements_at_start() and self.check_empty_loops()

    def check_missing_brackets(self) -> bool:
        ast: BrainFuckNode = self.ast

        def check_if_has_loop_end(ast: BrainFuckNode) -> bool:
            children: List[BrainFuckNode] = ast.getChildren()
            missing_brace = False
            for node in children:

                if node.getValue() == "Loop":
                    if not check_if_has_loop_end(node):
                        self.issues.append(
                            SemanticIssue("error", "Missing loop close", node)
                        )
                        missing_brace = True

            return not missing_brace

        return check_if_has_loop_end(ast)

    def check_ptr_decrements_at_start(self) -> bool:
        def check_if_dec_at_start(node: BrainFuckNode) -> bool:
            child: BrainFuckNode = node.children[0]
            if child.value == "Loop":
                return check_if_dec_at_start(child)
            elif child.value == "<":
                self.issues.append(
                    SemanticIssue(
                        "error", "Ptr decrement in the beginning of the program", node)
                )
                return True
            else:
                return False

        return not check_if_dec_at_start(self.ast)

    def check_empty_loops(self):

        def find_empty_loops(ast: BrainFuckNode) -> bool:
            children: List[BrainFuckNode] = ast.getChildren()
            empty_loops = False
            for node in children:
                if node.getValue() == "Loop":
                    node_children: List[BrainFuckNode] = ast.getChildren()
                    if len(node_children) > 0 and node_children[0].value == "LoopEnd":
                        empty_loops = True
                        self.issues.append(
                            SemanticIssue(
                                "error", "[] either do nothing or run forever", node)
                        )
                    else:
                        if find_empty_loops(node):
                            empty_loops = True

            return empty_loops

        return not find_empty_loops(self.ast)


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
