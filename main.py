import webview
import compiler.lexer as lexer
import compiler.cfgparser as cfgparser
import base64
import compiler.semantic_analysis as semantic
import compiler.code_generation as cg
import compiler.compile as compile

html = ""

# read from index.html
with open("index.html", "r+") as f:
    html = f.read()


class api:
    def __init__(self):
        self.tokens = []
        self.ast = None
        self.ir = None
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

        self.ast = cfgparser.BrainfuckParser(self.tokens).parse_program()
        cfgparser.visualize(self.ast)

        # open CFG.png and load it into the webview
        with open("CFG.png", "rb") as f:
            data = f.read()
            data = base64.b64encode(data).decode()
            window.evaluate_js(
                "document.getElementById('cfgimg').style.backgroundImage = 'url(data:image/png;base64,{base64})';".format(
                    base64=data)
            )

    def to_semantic(self):
        window.evaluate_js(
            "document.getElementById('parser').style.display = 'none';")
        window.evaluate_js(
            "document.getElementById('semantic').style.display = 'flex';")

        analysis = semantic.SemanticAnalysis(self.ast)
        analysis.analyze()

        issues = analysis.issues
        print(issues)

        text = ""
        for issue in issues:
            text += "[{}] {} at index {}\\n".format(
                issue.type, issue.value, issue.node.char_index-1)

        if text == "":
            text = "No issues found!"

        window.evaluate_js(
            "document.getElementById('semantic-output').innerHTML = '{}';".format(text))

    def to_ir(self):
        window.evaluate_js(
            "document.getElementById('semantic').style.display = 'none';")
        window.evaluate_js(
            "document.getElementById('ir').style.display = 'flex';")

        converter = cg.IRManager(self.ast)
        ir = converter.to_llvm_ir()
        self.ir = ir

        # escape string for js
        ir = str(ir).replace("\n", "\\n")

        window.evaluate_js(
            "document.getElementById('ir-output').innerHTML = '{}';".format(ir))

    def to_compiler(self):
        window.evaluate_js(
            "document.getElementById('ir').style.display = 'none';")
        window.evaluate_js(
            "document.getElementById('output').style.display = 'flex';")

        self.status = compile.JITCompiler().run(self.ir)

    def finish(self):
        window.destroy()
        import sys
        print("BF Program Output:")
        print()
        sys.exit(self.status)


if __name__ == '__main__':

    w = webview.create_window(
        'BrainF**k Compiler', html=html, width=1920, height=1080, js_api=api())

    global window
    window = w
    webview.start()
