import re
from typing import List, Dict

INSTRUCTION_SET = {
    'LOAD': 0x01,
    'ADD': 0x02,
    'SUB': 0x03,
    'JMP': 0x04,
    'JNZ': 0x05,
    'HALT': 0x06,
}

REGISTER_MAP = {
    'R0': 0x0,
    'R1': 0x1,
    'R2': 0x2,
    'R3': 0x3,
}

class AssemblyError(Exception):
    pass

class Assembler:
    def __init__(self):
        self.labels: Dict[str, int] = {}
        self.instructions: List[int] = []
        self.pending_jumps: List[tuple] = []

    def assemble(self, source: str) -> List[int]:
        lines = source.splitlines()
        address = 0
        for line_no, line in enumerate(lines, 1):
            line = line.split(';', 1)[0].strip()
            if not line:
                continue
            if line.endswith(':'):
                label = line[:-1].strip().upper()
                if label in self.labels:
                    raise AssemblyError(
                        f"Duplicate label {label} at line {line_no}")
                self.labels[label] = address
                continue
            tokens = re.split(r'[\s,]+', line.upper())
            op = tokens[0]
            if op not in INSTRUCTION_SET:
                raise AssemblyError(
                    f"Unknown instruction {op} at line {line_no}")
            self.instructions.append(INSTRUCTION_SET[op])
            address += 1
            if op == 'HALT':
                continue
            elif op in ('LOAD', 'ADD', 'SUB', 'JNZ'):
                if len(tokens) != 3:
                    raise AssemblyError(
                        f"Invalid operands at line {line_no}")
                reg = self._reg_value(tokens[1], line_no)
                self.instructions.append(reg)
                address += 1
                if op == 'LOAD':
                    value = int(tokens[2], 0)
                    self.instructions.append(value & 0xFF)
                    address += 1
                elif op in ('ADD', 'SUB'):
                    reg2 = self._reg_value(tokens[2], line_no)
                    self.instructions.append(reg2)
                    address += 1
                elif op == 'JNZ':
                    self.pending_jumps.append(
                        (len(self.instructions), tokens[2], line_no))
                    self.instructions.append(0)
                    address += 1
            elif op == 'JMP':
                if len(tokens) != 2:
                    raise AssemblyError(
                        f"Invalid operands at line {line_no}")
                self.pending_jumps.append(
                    (len(self.instructions), tokens[1], line_no))
                self.instructions.append(0)
                address += 1
        for idx, label, line_no in self.pending_jumps:
            if label not in self.labels:
                raise AssemblyError(
                    f"Undefined label {label} referenced at line {line_no}")
            target = self.labels[label]
            self.instructions[idx] = target & 0xFF
        return self.instructions

    def _reg_value(self, token: str, line_no: int) -> int:
        token = token.upper()
        if token not in REGISTER_MAP:
            raise AssemblyError(
                f"Unknown register {token} at line {line_no}")
        return REGISTER_MAP[token]
