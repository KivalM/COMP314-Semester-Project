class BFLexDFA:
    def __init__(self):
        self.state = 0
        self.accept_states = [1]

        self.alphabet = [">", "<", "+", "-", ".", ",", "[", "]", "#"]
        
        # transitions to only recognize single tokens
        self.transitions = {
            # initial state, 
            0: {
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
            1: {
                ">": 2,
                "<": 2,
                "+": 2,
                "-": 2,
                ".": 2,
                ",": 2,
                "[": 2,
                "]": 2,
                "#": 0
            },
            # error state
            2:{
                ">": 2,
                "<": 2,
                "+": 2,
                "-": 2,
                ".": 2,
                ",": 2,
                "[": 2,
                "]": 2,
                "#": 2
            }
        }
    
    def step(self, token):
        if token not in self.alphabet:
            token = "#"

        self.state = self.transitions[self.state][token]
        return self.state in self.accept_states

    def reset(self):
        self.state = 0


class BFLexer:
    def __init__(self):
        self.dfa = BFLexDFA()
    
    def lex(self, program):
        # is a bit convoluted and unnecessary, but it properly demonstrates the DFA
        tokens = []

        token_buffer = ""

        pointer1 = 0
        pointer2 = 0

        while pointer1 < len(program):
            token_buffer = ""
            pointer2 = pointer1

            while pointer2 < len(program) and self.dfa.step(program[pointer2]):
                
                token_buffer += program[pointer2]
                pointer2 += 1
            
            if token_buffer != "":
                tokens.append(token_buffer)
                pointer1 = pointer2
                self.dfa.reset()
            else:
                pointer1 += 1
            

        return tokens


# tests
def test_lexer():
    lexer = BFLexer()
    tokens = lexer.lex(">+<")
    assert tokens == [">", "+", "<"]

    tokens = lexer.lex(">>+<")
    assert tokens == [">", ">", "+", "<"]

    tokens = lexer.lex(">>+<A")
    assert tokens == [">", ">", "+", "<"]

    tokens = lexer.lex(">>+<A[]")
    assert tokens == [">", ">", "+", "<", "[", "]"]

if __name__ == "__main__":
    test_lexer()