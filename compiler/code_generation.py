# referenced https://github.com/PurpleMyst/bf_compiler
# but changed to support our ast structure


from llvmlite import ir, binding as llvm
from .cfgparser import BrainfuckParser, BrainFuckNode
from .lexer import BFLexer


INDEX_BIT_SIZE = 16


class IRManager:
    def __init__(self, ast) -> None:
        self.ast = ast
        pass

    def to_llvm_ir(self):
        ast = self.ast

        byte = ir.IntType(8)
        int32 = ir.IntType(32)
        size_t = ir.IntType(64)

        void = ir.VoidType()

        module = ir.Module(name=__file__)
        main_type = ir.FunctionType(int32, ())
        main_func = ir.Function(module, main_type, name="main")
        entry = main_func.append_basic_block(name="entry")

        builder = ir.IRBuilder(entry)

        putchar_type = ir.FunctionType(int32, (int32,))
        putchar = ir.Function(module, putchar_type, name="putchar")

        getchar_type = ir.FunctionType(int32, ())
        getchar = ir.Function(module, getchar_type, name="getchar")

        bzero_type = ir.FunctionType(void, (byte.as_pointer(), size_t))
        bzero = ir.Function(module, bzero_type, name="bzero")

        index_type = ir.IntType(INDEX_BIT_SIZE)
        index = builder.alloca(index_type)
        builder.store(ir.Constant(index_type, 0), index)

        tape_type = byte
        tape = builder.alloca(tape_type, size=2 ** INDEX_BIT_SIZE)
        builder.call(bzero, (tape, size_t(2 ** INDEX_BIT_SIZE)))

        zero8 = byte(0)
        one8 = byte(1)

        eof = int32(-1)

        def get_tape_location():
            index_value = builder.load(index)
            index_value = builder.zext(index_value, int32)
            location = builder.gep(tape, (index_value,), inbounds=True)
            return location

        def compile_instruction(instruction: BrainFuckNode):
            if instruction.value == "Loop":
                # append a llvm loop block
                preloop = builder.append_basic_block(name="preloop")
                # branch into the block
                builder.branch(preloop)
                # go to the start position of the loop
                builder.position_at_start(preloop)

                location = get_tape_location()
                tape_value = builder.load(location)

                is_zero = builder.icmp_unsigned("==", tape_value, zero8)
                # add a body block so we can dump the looop contents and recurse
                body = builder.append_basic_block(name="body")
                builder.position_at_start(body)
                for child in instruction.children:
                    if child.value != "LoopEnd":
                        # compile any valid nodes
                        compile_instruction(child)

                # branch back out, to the upper level after processing child nodes
                builder.branch(preloop)

                # go out of the loop
                postloop = builder.append_basic_block(name="postloop")

                builder.position_at_end(preloop)
                builder.cbranch(is_zero, postloop, body)

                builder.position_at_start(postloop)
            elif instruction.value == "+" or instruction.value == "-":
                location = get_tape_location()
                value = builder.load(location)
                # add or subtract 1 from the value
                if instruction.value == "+":
                    new_value = builder.add(value, one8)
                else:
                    new_value = builder.sub(value, one8)

                builder.store(new_value, location)
            elif instruction.value == ">" or instruction.value == "<":
                index_value = builder.load(index)
                # add or subtract 1 from the index i.e move pointer left or right
                if instruction.value == ">":
                    index_value = builder.add(index_value, index_type(1))
                else:
                    index_value = builder.sub(index_value, index_type(1))

                builder.store(index_value, index)

            elif instruction.value == ".":
                # print the value at the current tape location
                location = get_tape_location()
                tape_value = builder.load(location)
                tape_value = builder.zext(tape_value, int32)

                builder.call(putchar, (tape_value,))
            elif instruction.value == ",":
                #  read a character from stdin and store it at the current tape location
                location = get_tape_location()

                char = builder.call(getchar, ())
                is_eof = builder.icmp_unsigned("==", char, eof)

                with builder.if_else(is_eof) as (then, otherwise):
                    with then:
                        builder.store(zero8, location)

                    with otherwise:
                        char = builder.trunc(char, tape_type)
                        builder.store(char, location)

        # compile the ast recursively
        for instruction in ast.children:
            compile_instruction(instruction)

        # add a return statement
        builder.ret(int32(0))

        # print the llvm ir
        return module


def test():
    code = "+-[]"
    lexer = BFLexer()
    code = lexer.lex(code)

    parser = BrainfuckParser(code)
    ast = parser.parse_program()

    converter = IRManager(ast)
    result = converter.to_llvm_ir()

    print(result)


if __name__ == "__main__":
    test()
