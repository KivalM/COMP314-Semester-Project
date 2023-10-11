import webview
import compiler.lexer as lexer
import compiler.cfgparser as cfgparser


html = ""


# read from index.html
with open("index.html", "r+") as f:
    html = f.read()


class api:

    def __init__(self):
        self.tokens = []
        pass

    def intro(self):
        # get the intro id and hide it
        window.evaluate_js(
            "document.getElementById('intro').style.display = 'none';")
        window.evaluate_js(
            "document.getElementById('lexer').style.display = 'flex';")

    def lexer(self, source):
        lex = lexer.BFLexer()
        self.tokens = lex.lex(source)
        return self.tokens

    def to_parser(self):
        window.evaluate_js(
            "document.getElementById('lexer').style.display = 'none';")
        window.evaluate_js(
            "document.getElementById('parser').style.display = 'flex';")

        parser = cfgparser.BrainfuckParser(self.tokens).parse_program()
        cfgparser.visualize(parser)

        # open CFG.png and load it into the webview

    def to_semantic(self):
        window.evaluate_js(
            "document.getElementById('parser').style.display = 'none';")
        window.evaluate_js(
            "document.getElementById('semantic').style.display = 'flex';")

    def to_ir(self):
        window.evaluate_js(
            "document.getElementById('semantic').style.display = 'none';")
        window.evaluate_js(
            "document.getElementById('ir').style.display = 'flex';")

    def to_compiler(self):
        window.evaluate_js(
            "document.getElementById('ir').style.display = 'none';")
        window.evaluate_js(
            "document.getElementById('output').style.display = 'flex';")


if __name__ == '__main__':
    w = webview.create_window(
        'BrainF**k Compiler', html=html, width=1920, height=1080, js_api=api())

    global window
    window = w
    webview.start()
