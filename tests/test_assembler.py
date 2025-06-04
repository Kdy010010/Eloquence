import unittest
from eas import Assembler, AssemblyError

class TestAssembler(unittest.TestCase):
    def test_simple_program(self):
        src = """
start:
    load r0, 1
    load r1, 2
    add r0, r1
    halt
"""
        asm = Assembler()
        code = asm.assemble(src)
        # expected opcodes: LOAD R0 1, LOAD R1 2, ADD R0 R1, HALT
        expected = [0x01, 0x0, 0x01, 0x01, 0x1, 0x02, 0x02, 0x0, 0x1, 0x06]
        self.assertEqual(code, expected)

    def test_jump(self):
        src = """
    jmp end
    load r0, 1
end:
    halt
"""
        asm = Assembler()
        code = asm.assemble(src)
        # jmp should resolve to address 5 (halt opcode position)
        expected = [0x04, 0x05, 0x01, 0x0, 0x01, 0x06]
        self.assertEqual(code, expected)

    def test_unknown_instruction(self):
        asm = Assembler()
        with self.assertRaises(AssemblyError):
            asm.assemble('foo r0, r1')

if __name__ == '__main__':
    unittest.main()
