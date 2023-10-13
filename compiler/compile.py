from llvmlite import ir, binding as llvm
import ctypes
import sys

# courtesy of the llvmlite docs


class JITCompiler:
    def __init__(self) -> None:
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # And an execution engine with an empty backing module
        backing_mod = llvm.parse_assembly("")
        self.engine = llvm.create_mcjit_compiler(backing_mod, target_machine)

    def run(self, ir_module):
        binding_module = llvm.parse_assembly(str(ir_module))
        binding_module.verify()

        with self.engine as engine:

            engine.add_module(binding_module)
            engine.finalize_object()
            engine.run_static_constructors()

            func_ptr = engine.get_function_address("main")

            # create a function pointer to the main function
            asm_main = ctypes.CFUNCTYPE(ctypes.c_int)(func_ptr)

            print("running main...")
            out = asm_main()
            print("output code:", out)
            return out


def test():
    from lexer import BFLexer
    from cfgparser import BrainfuckParser
    from code_generation import IRManager

    lexer = BFLexer()
    code = lexer.lex(
        "--<-<<+[+[<+>--->->->-<<<]>]<<--.<++++++.<<-..<<.<+.>>.>>.<<<.+++.>>.>>-.<<<+.")

    print(code)

    tree = BrainfuckParser(code).parse_program()

    man = IRManager(tree)
    ll = man.to_llvm_ir()

    compiler = JITCompiler()
    compiler.run(ll)


if __name__ == "__main__":
    test()
