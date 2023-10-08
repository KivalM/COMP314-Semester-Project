import webview
import compiler.lexer as lexer

html = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Start page</title>
</head>

<body>
    <h1>BrainF**k Compiler</h1>
    <div>
        <p>BrainF**k is an esoteric programming language created in 1993 by Urban Müller, and notable for its extreme
            minimalism.</p>
        <p>It consists of only eight simple commands and an instruction pointer. While it is fully Turing-complete, it
            is not intended for practical use, but to challenge and amuse programmers.</p>
    </div>

    <div id="editor">
        <textarea id="code" rows="10" cols="50">++</textarea>
        <div id="output"></div>

    </div>
    <button id="compile" onclick="lex()">
        Next
    </button>

    <div>

        <script>
            function lex() {
                var source = document.getElementById('code').value;
                pywebview.api.compile(source).then(function(tokens) {
                    document.getElementById('output').innerHTML = tokens;
                });
            }
        </script>

        <style>
            body {
                font-family: sans-serif;
            }

            h1 {
                text-align: center;
            }

            div {
                margin: 20px;
            }

            textarea {
                width: 50%;
            }

            #editor {
                display: flex;
            }

            #code {
                width: 50%;
                border: 1px solid #ccc;
                padding: 10px;
            }

            #output {
                width: 50%;
                border: 1px solid #ccc;
                padding: 10px;
            }

            button {
                font-size: 1.2em;
                padding: 10px;
                margin: 10px;
            }
        </style>

</body>

</html>
"""


class api:
    def __init__(self):
        pass

    def compile(self, source):
        lex = lexer.BFLexer()
        tokens = lex.lex(source)
        print(tokens)
        return tokens


def startpage():
    webview.create_window('BrainF**k Compiler',
                          html=html, width=800, height=600, js_api=api())


if __name__ == '__main__':
    startpage()
    webview.start()
