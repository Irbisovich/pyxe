# PyXE x86 Assembly Emulator

import struct
import sys

class main:
    REGISTERS = {
        0x01: 'ACCUMULATOR',
        0x02: 'BASE',
        0x03: 'COUNT',
        0x04: 'DATA',
        0x05: 'SOURCE',
        0x06: 'DEST',
        0x07: 'BASEPOINTER',
        0x08: 'STACKPOINTER'
    }

    def __init__(self, mem_size=1024 * 1024):
        self.registers = {name: 0 for name in self.REGISTERS.values()}
        self.eip = 0x1000
        self.eflags = 0
        self.memory = bytearray(mem_size)
        self.running = False
        self.interrupts = {}
        self.registers['STACKPOINTER'] = mem_size - 4
        self.code_end = 0x1000

        self.instruction_handlers = {
            0x00: self.handle_nop,
            0x10: self.handle_mov,
            0x20: self.handle_add,
            0x22: self.handle_and,
            0x30: self.handle_sub,
            0x33: self.handle_or,
            0x40: self.handle_inc,
            0x44: self.handle_xor,
            0x50: self.handle_dec,
            0x55: self.handle_input,
            0x60: self.handle_cmp,
            0x66: self.handle_print,
            0x70: self.handle_jmp,
            0x80: self.handle_je,
            0x90: self.handle_jne,
            0xA0: self.handle_call,
            0xB0: self.handle_ret,
            0xC0: self.handle_push,
            0xD0: self.handle_pop,
            0xE0: self.handle_int,
            0xF0: self.handle_hlt
        }

    def load_program(self, code, data, labels):
        code_start = 0x1000
        for i, byte in enumerate(code):
            self.memory[code_start + i] = byte
        self.code_end = code_start + len(code)

        data_start = 0x2000
        for i, byte in enumerate(data):
            self.memory[data_start + i] = byte

        self.eip = code_start

    def register_interrupt(self, vector, handler):
        self.interrupts[vector] = handler

    def read_memory(self, address, size):
        if address < 0 or address + size > len(self.memory):
            print(f"Memory warning: Invalid memory access at 0x{address:08X}, size={size}")
            return bytes([0] * size)
        return bytes(self.memory[address:address + size])

    def write_memory(self, address, data):
        if address < 0 or address + len(data) > len(self.memory):
            print(f"Memory warning: Invalid memory write at 0x{address:08X}, size={len(data)}")
            return
        for i, byte in enumerate(data):
            self.memory[address + i] = byte

    def run(self):
        self.running = True
        while self.running:
            if self.eip >= self.code_end:
                print(f"Execution reached end of code at 0x{self.eip:08X}")
                self.running = False
                break

            opcode = self.memory[self.eip]
            self.eip += 1

            if opcode in self.instruction_handlers:
                self.instruction_handlers[opcode]()
            else:
                print(f"Syntax error: 0x{opcode:02X} at 0x{self.eip - 1:08X}")
                self.running = False

    def read_operand_type(self):
        op_type = self.memory[self.eip]
        self.eip += 1

        if op_type == 0x01:
            reg_code = self.memory[self.eip]
            self.eip += 1
            self.eip += 3
            return ('REG', reg_code)

        elif op_type == 0x02:
            data = self.memory[self.eip:self.eip + 4]
            self.eip += 4
            value = struct.unpack('<I', bytes(data))[0]
            return ('IMM', value)

        elif op_type == 0x03:
            data = self.memory[self.eip:self.eip + 4]
            self.eip += 4
            address = struct.unpack('<I', bytes(data))[0]
            return ('MEM', address)

        else:
            self.eip += 4
            return ('UNK', 0)

    def get_reg_name(self, reg_code):
        return self.REGISTERS.get(reg_code, 'ACCUMULATOR')

    def get_value(self, operand):
        if operand[0] == 'REG':
            return self.registers[self.get_reg_name(operand[1])]
        elif operand[0] == 'IMM':
            return operand[1]
        elif operand[0] == 'MEM':
            start_addr = operand[1]
            end_addr = start_addr + 4
            data = self.memory[start_addr:end_addr]
            return struct.unpack('<I', bytes(data))[0]
        return 0

    def set_value(self, operand, value):
        if operand[0] == 'REG':
            self.registers[self.get_reg_name(operand[1])] = value
        elif operand[0] == 'MEM':
            start_addr = operand[1]
            end_addr = start_addr + 4
            packed_value = struct.pack('<I', value)
            self.memory[start_addr:end_addr] = packed_value

    def handle_nop(self):
        pass

    def handle_mov(self):
        dest = self.read_operand_type()
        src = self.read_operand_type()
        self.set_value(dest, self.get_value(src))

    def handle_add(self):
        dest = self.read_operand_type()
        src = self.read_operand_type()
        self.set_value(dest, self.get_value(dest) + self.get_value(src))

    def handle_sub(self):
        dest = self.read_operand_type()
        src = self.read_operand_type()
        self.set_value(dest, self.get_value(dest) - self.get_value(src))

    def handle_inc(self):
        reg_code = self.memory[self.eip]
        self.eip += 1
        reg_name = self.get_reg_name(reg_code)
        self.registers[reg_name] += 1

    def handle_dec(self):
        reg_code = self.memory[self.eip]
        self.eip += 1
        reg_name = self.get_reg_name(reg_code)
        self.registers[reg_name] -= 1

    def handle_and(self):
        dest = self.read_operand_type()
        src = self.read_operand_type()
        self.set_value(dest, self.get_value(dest) & self.get_value(src))

    def handle_or(self):
        dest = self.read_operand_type()
        src = self.read_operand_type()
        self.set_value(dest, self.get_value(dest) | self.get_value(src))

    def handle_xor(self):
        dest = self.read_operand_type()
        src = self.read_operand_type()
        self.set_value(dest, self.get_value(dest) ^ self.get_value(src))

    def handle_cmp(self):
        op1 = self.read_operand_type()
        op2 = self.read_operand_type()
        val1 = self.get_value(op1)
        val2 = self.get_value(op2)
        result = val1 - val2
        self.eflags = 0
        if result == 0:
            self.eflags |= 0x40
        if result < 0:
            self.eflags |= 0x80

    def handle_jmp(self):
        address = struct.unpack('<I', bytes(self.memory[self.eip:self.eip + 4]))[0]
        self.eip = address

    def handle_je(self):
        address = struct.unpack('<I', bytes(self.memory[self.eip:self.eip + 4]))[0]
        self.eip += 4
        if self.eflags & 0x40:
            self.eip = address

    def handle_jne(self):
        address = struct.unpack('<I', bytes(self.memory[self.eip:self.eip + 4]))[0]
        self.eip += 4
        if not (self.eflags & 0x40):
            self.eip = address

    def handle_call(self):
        address = struct.unpack('<I', bytes(self.memory[self.eip:self.eip + 4]))[0]
        self.eip += 4
        self.registers['STACKPOINTER'] -= 4
        return_addr = self.eip
        addr = self.registers['STACKPOINTER']
        self.memory[addr:addr + 4] = struct.pack('<I', return_addr)
        self.eip = address

    def handle_ret(self):
        addr = self.registers['STACKPOINTER']
        return_addr = struct.unpack('<I', bytes(self.memory[addr:addr + 4]))[0]
        self.registers['STACKPOINTER'] += 4
        self.eip = return_addr

    def handle_push(self):
        reg_code = self.memory[self.eip]
        self.eip += 1
        reg_name = self.get_reg_name(reg_code)
        value = self.registers[reg_name]
        self.registers['STACKPOINTER'] -= 4
        addr = self.registers['STACKPOINTER']
        self.memory[addr:addr + 4] = struct.pack('<I', value)

    def handle_pop(self):
        reg_code = self.memory[self.eip]
        self.eip += 1
        reg_name = self.get_reg_name(reg_code)
        addr = self.registers['STACKPOINTER']
        value = struct.unpack('<I', bytes(self.memory[addr:addr + 4]))[0]
        self.registers['STACKPOINTER'] += 4
        self.registers[reg_name] = value

    def handle_int(self):
        vector = self.memory[self.eip]
        self.eip += 1
        if vector in self.interrupts:
            self.interrupts[vector]()
        else:
            print(f"Unhandled interrupt: 0x{vector:02X}")

    def handle_hlt(self):
        self.running = False

    def handle_input(self):
        reg_code = self.memory[self.eip]
        self.eip += 1
        reg_name = self.get_reg_name(reg_code)

        try:
            user_input = input()
            value = int(user_input)
            self.registers[reg_name] = value
        except ValueError:
            print(f"Type error: Invalid input, expected integer")
            self.registers[reg_name] = 0

    def handle_print(self):
        op = self.read_operand_type()
        value = self.get_value(op)

        if op[0] == 'IMM':
            if value == 0:
                print("", end='', flush=True)
            else:
                s = bytearray()
                addr = value
                while True:
                    if addr >= len(self.memory):
                        break
                    ch = self.memory[addr]
                    addr += 1
                    if ch == 0:
                        break
                    s.append(ch)
                try:
                    decoded = bytes(s).decode('utf-8', errors='ignore').replace('\\n', '\n')
                    print(decoded, end='', flush=True)
                except:
                    print(f"Decode error: cannot decode string at 0x{value:08X}")
        else:
            print(str(value) + " ", end='', flush=True)
