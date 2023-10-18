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


class DecrementPointerIssueDFA:
    def __init__(self):
        self.state = 0
        self.accept_states = [2]

        self.alphabet = [">", "<", "+", "-", ".", ",", "[", "]", "#"]

        # transitions to recognize a program where the first character is a <
        self.transitions = {
            # initial state,
            0: {
                ">": 1,
                "<": 2,
                "+": 1,
                "-": 1,
                ".": 1,
                ",": 1,
                "[": 0,
                "]": 0,
                "#": 0
            },
            # accept state
            1: {
                ">": 1,
                "<": 1,
                "+": 1,
                "-": 1,
                ".": 1,
                ",": 1,
                "[": 1,
                "]": 1,
                "#": 0
            },
            2: {
                ">": 2,
                "<": 2,
                "+": 2,
                "-": 2,
                ".": 2,
                ",": 2,
                "[": 2,
                "]": 2,
                "#": 2
            },
        }

    def step(self, token):
        if token not in self.alphabet:
            token = "#"

        self.state = self.transitions[self.state][token]
        return self.state in self.accept_states

    def reset(self):
        self.state = 0


class EmptyLoopIssueDFA:
    def __init__(self):
        self.state = 0
        self.accept_states = [2]

        self.alphabet = [">", "<", "+", "-", ".", ",", "[", "]", "#"]

        # transitions to recognize a program where there exists an empty loop
        self.transitions = {
            # initial state,
            0: {
                ">": 0,
                "<": 0,
                "+": 0,
                "-": 0,
                ".": 0,
                ",": 0,
                "[": 1,
                "]": 1,
                "#": 0
            },

            # loop open state
            1: {
                ">": 1,
                "<": 1,
                "+": 1,
                "-": 1,
                ".": 1,
                ",": 1,
                "[": 1,
                "]": 2,
                "#": 1
            },

            # accept state (loop close immediately after loop open)
            2: {
                ">": 2,
                "<": 2,
                "+": 2,
                "-": 2,
                ".": 2,
                ",": 2,
                "[": 2,
                "]": 2,
                "#": 2
            },
        }

    def step(self, token):
        if token not in self.alphabet:
            token = "#"

        self.state = self.transitions[self.state][token]
        return self.state in self.accept_states

    def reset(self):
        self.state = 0


class MissingBracketDFA:
    def __init__(self):
        self.state = 0
        self.accept_states = [0, 8]

        self.alphabet = [">", "<", "+", "-", ".", ",", "[", "]", "#"]

        # transitions to recognize a program where there is a valid bracket pairs up to 8 levels of nesting
        self.transitions = {
            # initial state, anything goes
            0: {
                ">": 0,
                "<": 0,
                "+": 0,
                "-": 0,
                ".": 0,
                ",": 0,
                "[": 1,
                "]": 0,
                "#": 0
            },
            # accept state
            1: {
                ">": 1,
                "<": 1,
                "+": 1,
                "-": 1,
                ".": 1,
                ",": 1,
                "[": 2,
                "]": 0,
                "#": 1
            },
            2: {
                ">": 2,
                "<": 2,
                "+": 2,
                "-": 2,
                ".": 2,
                ",": 2,
                "[": 3,
                "]": 1,
                "#": 2
            },
            # initial state, anything goes
            3: {
                ">": 3,
                "<": 3,
                "+": 3,
                "-": 3,
                ".": 3,
                ",": 3,
                "[": 4,
                "]": 2,
                "#": 3
            },
            # accept state
            4: {
                ">": 1,
                "<": 1,
                "+": 1,
                "-": 1,
                ".": 1,
                ",": 1,
                "[": 5,
                "]": 3,
                "#": 0
            },
            5: {
                ">": 5,
                "<": 5,
                "+": 5,
                "-": 5,
                ".": 5,
                ",": 5,
                "[": 6,
                "]": 4,
                "#": 5
            },
            6: {
                ">": 6,
                "<": 6,
                "+": 6,
                "-": 6,
                ".": 6,
                ",": 6,
                "[": 7,
                "]": 5,
                "#": 6
            },
            7: {
                ">": 7,
                "<": 7,
                "+": 7,
                "-": 7,
                ".": 7,
                ",": 7,
                "[": 8,
                "]": 6,
                "#": 7
            },
            8: {
                ">": 8,
                "<": 8,
                "+": 8,
                "-": 8,
                ".": 8,
                ",": 8,
                "[": 8,
                "]": 8,
                "#": 8
            },

        }

    def step(self, token):
        if token not in self.alphabet:
            token = "#"

        self.state = self.transitions[self.state][token]
        return self.state in self.accept_states

    def reset(self):
        self.state = 0


class SemanticAnalysis:
    def __init__(self, ast):
        self.ast: BrainFuckNode = ast
        self.issues: List[SemanticIssue] = []
        self.dec_dfa = DecrementPointerIssueDFA()
        self.empty_dfa = EmptyLoopIssueDFA()
        self.bracket_dfa = MissingBracketDFA()

    def analyze(self):
        ast: BrainFuckNode = self.ast
        self.found_char_other_than_dec = False

        def traverse(node: BrainFuckNode):
            if node.value == "Loop":
                self.bracket_dfa.step('[')
                self.empty_dfa.step('[')
            elif node.value == "LoopEnd":
                self.bracket_dfa.step(']')

                if self.empty_dfa.step(']'):
                    self.issues.append(
                        SemanticIssue(
                            "warning", "[] either do nothing or run forever", node)
                    )
                    self.empty_dfa.reset()

            elif node.value != "Program":
                if self.dec_dfa.step(node.value):
                    self.issues.append(
                        SemanticIssue(
                            "error", "Ptr decrement in the beginning of the program", node)
                    )
                self.empty_dfa.step(node.value)

            # traverse ast recursively
            for child in node.children:
                traverse(child)

        traverse(ast)

        if not self.bracket_dfa.state in self.bracket_dfa.accept_states:
            self.issues.append(
                SemanticIssue("error", "Missing loop close", ast)
            )


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
