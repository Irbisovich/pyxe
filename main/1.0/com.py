# PyXE Compiler

import struct

class main:
    INSTRUCTION_OPCODES = {
        'MOV': 0x10, 'ADD': 0x20, 'SUB': 0x30, 'INC': 0x40, 'DEC': 0x50,
        'CMP': 0x60, 'JMP': 0x70, 'JE': 0x80, 'JNE': 0x90, 'CALL': 0xA0,
        'RET': 0xB0, 'PUSH': 0xC0, 'POP': 0xD0, 'INT': 0xE0, 'HLT': 0xF0,
        'AND': 0x22, 'OR': 0x33, 'XOR': 0x44, 'NOP': 0x00, 'INPUT': 0x55,
        'PRINT': 0x66
    }

    REGISTER_CODES = {
        'ACCUMULATOR': 0x01,
        'BASE': 0x02,
        'COUNT': 0x03,
        'DATA': 0x04,
        'SOURCE': 0x05,
        'DEST': 0x06,
        'BASEPOINTER': 0x07,
        'STACKPOINTER': 0x08
    }

    CUSTOM_COMMANDS = {
        'drag': 'MOV',
        'add': 'ADD',
        'subtract': 'SUB',
        'increase': 'INC',
        'decrease': 'DEC',
        'compare': 'CMP',
        'go': 'JMP',
        'go-true': 'JE',
        'go-false': 'JNE',
        'call': 'CALL',
        'return': 'RET',
        'place': 'PUSH',
        'extract': 'POP',
        'interrupt': 'INT',
        'stop': 'HLT',
        'logic-and': 'AND',
        'logic-or': 'OR',
        'exclude-or': 'XOR',
        'pass': 'NOP',
        'input': 'INPUT',
        'print': 'PRINT',
        'defbyte': 'DB',
        'defword': 'DW',
        'defdouble': 'DD'
    }

    def __init__(self):
        self.code_section = bytearray()
        self.data_section = bytearray()
        self.labels = {}
        self.data_address = 0x2000
        self.code_address = 0x1000
        self.current_address = 0x1000

    def compile(self, source):
        lines = source.splitlines()
        cleaned_lines = []

        for line in lines:
            if ';' in line:
                line = line.split(';', 1)[0]
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        lines = cleaned_lines

        current_code_addr = self.code_address
        current_data_addr = self.data_address

        for i, line in enumerate(lines):
            if ':' in line:
                parts = line.split(':', 1)
                label = parts[0].strip()
                line_rest = parts[1].strip()
                if i + 1 < len(lines) and lines[i + 1].strip().upper().startswith('DB'):
                    self.labels[label] = current_data_addr
                else:
                    self.labels[label] = current_code_addr
                if not line_rest:
                    continue
                else:
                    line = line_rest

            if ' equ ' in line:
                parts = line.split(' equ ', 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    value_str = parts[1].strip()
                    try:
                        value = int(value_str, 0)
                    except:
                        value = 0
                    self.labels[label] = value

            elif line.upper().startswith('DB'):
                data_str = line[2:].strip()
                values = [v.strip() for v in data_str.split(',') if v.strip()]
                current_data_addr += len(values)

            else:
                parts = line.split()
                if parts:
                    original_mnemonic = parts[0]
                    if original_mnemonic in self.CUSTOM_COMMANDS:
                        mnemonic = self.CUSTOM_COMMANDS[original_mnemonic]
                    else:
                        mnemonic = original_mnemonic.upper()

                    if mnemonic in ['HLT', 'NOP', 'RET']:
                        current_code_addr += 1
                    elif mnemonic in ['INC', 'DEC', 'PUSH', 'POP', 'INPUT']:
                        current_code_addr += 2
                    elif mnemonic in ['INT', 'PRINT']:
                        current_code_addr += 2
                    elif mnemonic in ['JMP', 'JE', 'JNE', 'CALL']:
                        current_code_addr += 5
                    else:
                        current_code_addr += 11

        current_data_addr = self.data_address
        for i, line in enumerate(lines):
            if line.upper().startswith('DB'):
                if i > 0 and ':' in lines[i - 1]:
                    label = lines[i - 1].split(':', 1)[0].strip()
                    self.labels[label] = current_data_addr
                data_str = line[2:].strip()
                values = [v.strip() for v in data_str.split(',') if v.strip()]
                current_data_addr += len(values)

        for line in lines:
            if ':' in line or line.upper().startswith('DB') or ' equ ' in line:
                continue
            self.compile_instruction(line)
          
        for line in lines:
            if line.upper().startswith('DB'):
                self.compile_data(line)

        return {
            'code': bytes(self.code_section),
            'data': bytes(self.data_section),
            'labels': self.labels
        }

    def compile_instruction(self, line):
        parts = line.split()
        if not parts:
            return

        original_mnemonic = parts[0]

        if original_mnemonic in self.CUSTOM_COMMANDS:
            mnemonic = self.CUSTOM_COMMANDS[original_mnemonic]
        else:
            mnemonic = original_mnemonic.upper()

        if mnemonic not in self.INSTRUCTION_OPCODES:
            print(f"Syntax error: '{parts[0]}'")
            return

        opcode = self.INSTRUCTION_OPCODES[mnemonic]
        self.code_section.append(opcode)

        if mnemonic == 'PRINT':
            if len(parts) > 1:
                operand_str = ' '.join(parts[1:])
                if (operand_str.startswith('"') and operand_str.endswith('"')) or \
                        (operand_str.startswith("'") and operand_str.endswith("'")):
                    str_content = operand_str[1:-1]
                    str_addr = self.data_address + len(self.data_section)
                    self.data_section.extend(str_content.encode('utf-8'))
                    self.data_section.append(0)

                    self.code_section.append(0x02)
                    self.code_section.extend(struct.pack('<I', str_addr))
                else:
                    self.encode_operand(operand_str)
            else:
                self.code_section.append(0x02)
                self.code_section.extend(struct.pack('<I', 0))
            return

        if mnemonic in ['MOV', 'ADD', 'SUB', 'CMP', 'AND', 'OR', 'XOR']:
            for operand_str in parts[1:3]:
                operand = operand_str.strip().rstrip(',')
                self.encode_operand(operand)

        elif mnemonic in ['INC', 'DEC', 'PUSH', 'POP']:
            if len(parts) > 1:
                operand = parts[1].strip().rstrip(',')
                reg_code = self.REGISTER_CODES.get(operand.upper(), 0)
                self.code_section.append(reg_code)

        elif mnemonic in ['JMP', 'JE', 'JNE', 'CALL']:
            if len(parts) > 1:
                operand = parts[1].strip().rstrip(',')
                address = self.labels.get(operand, 0)
                self.code_section.extend(struct.pack('<I', address))

        elif mnemonic == 'INT':
            if len(parts) > 1:
                try:
                    vector = int(parts[1].strip().rstrip(','), 0)
                    self.code_section.append(vector & 0xFF)
                except:
                    self.code_section.append(0)

        elif mnemonic == 'INPUT':
            if len(parts) > 1:
                operand = parts[1].strip().rstrip(',')
                reg_code = self.REGISTER_CODES.get(operand.upper(), 0)
                self.code_section.append(reg_code)

    def encode_operand(self, operand):
        if operand.upper() in self.REGISTER_CODES:
            self.code_section.append(0x01)
            self.code_section.append(self.REGISTER_CODES[operand.upper()])
            self.code_section.extend(bytes(3))
            return

        try:
            value = int(operand, 0)
            self.code_section.append(0x02)
            self.code_section.extend(struct.pack('<I', value))
            return
        except:
            pass

        if operand in self.labels:
            value = self.labels[operand]
            self.code_section.append(0x02)
            self.code_section.extend(struct.pack('<I', value))
            return

        if operand.startswith('[') and operand.endswith(']'):
            addr_str = operand[1:-1].strip()
            try:
                address = int(addr_str, 0)
                self.code_section.append(0x03)
                self.code_section.extend(struct.pack('<I', address))
                return
            except:
                if addr_str in self.labels:
                    address = self.labels[addr_str]
                    self.code_section.append(0x03)
                    self.code_section.extend(struct.pack('<I', address))
                    return

        self.code_section.append(0x00)
        self.code_section.extend(bytes(4))

    def compile_data(self, line):
        data_str = line[2:].strip()
        values = []
        current = ''
        in_quotes = False
        quote_char = None
        escape = False

        for char in data_str:
            if escape:
                if char == 'n':
                    current += '\n'
                elif char == 't':
                    current += '\t'
                elif char == '0':
                    current += '\x00'
                else:
                    current += char
                escape = False
            elif char == '\\':
                escape = True
            elif in_quotes:
                if char == quote_char:
                    values.append(quote_char + current + quote_char)
                    current = ''
                    in_quotes = False
                else:
                    current += char
            else:
                if char in ('"', "'"):
                    in_quotes = True
                    quote_char = char
                elif char == ',':
                    if current.strip():
                        values.append(current.strip())
                    current = ''
                else:
                    current += char

        if current.strip():
            values.append(current.strip())

        for val in values:
            if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
                content = val[1:-1]
                for char in content:
                    self.data_section.append(ord(char))
            elif val.startswith('0x'):
                try:
                    self.data_section.append(int(val, 16))
                except:
                    self.data_section.append(0)
            elif val.isdigit():
                try:
                    self.data_section.append(int(val))
                except:
                    self.data_section.append(0)
            elif val == '\\n':
                self.data_section.append(10)
            elif val == '\\t':
                self.data_section.append(9)
            elif val == '\\0':
                self.data_section.append(0)
            elif val == '0':
                self.data_section.append(0)
            else:
                try:
                    self.data_section.append(ord(val))
                except:
                    self.data_section.append(0)
