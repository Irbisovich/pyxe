# PyXE Main

import traceback
import time
import sys
import com
import emu

def int_handler():
    global emulator

    syscall_num = emulator.registers['ACCUMULATOR']

    if syscall_num == 1:
        print(f"\nProgram exited with code: {emulator.registers['BASE']}")
        emulator.running = False

    elif syscall_num == 4:
        fd = emulator.registers['BASE']
        buffer_addr = emulator.registers['COUNT']
        size = emulator.registers['DATA']

        if fd == 1:
            data = emulator.read_memory(buffer_addr, size)
            try:
                text = ''.join(chr(byte) for byte in data)
                print(text, end='', flush=True)
            except Exception as e:
                print(f"Decoding error: {e}")

    elif syscall_num == 3:
        fd = emulator.registers['BASE']
        buffer_addr = emulator.registers['COUNT']
        size = emulator.registers['DATA']

        if fd == 0:
            try:
                user_input = input()
                byte_data = user_input.encode('utf-8')

                if len(byte_data) > size:
                    byte_data = byte_data[:size]

                emulator.write_memory(buffer_addr, byte_data)
                emulator.registers['ACCUMULATOR'] = len(byte_data)

            except:
                emulator.registers['ACCUMULATOR'] = -1

compiler = com.main()
emulator = emu.main()

emulator.register_interrupt(0x80, int_handler)

try:
    filename = sys.argv[1]

    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    result = compiler.compile(source)
    data = emulator.read_memory(0x2000, len(result['data']))
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        print(f"0x{0x2000 + i:04X}: ", end='')
        for byte in chunk:
            print(f"{byte:02X} ", end='')
        print()
    print()

    emulator.load_program(result['code'], result['data'], result['labels'])
    emulator.run()

    if '-d' in sys.argv:
        for reg, value in emulator.registers.items():
            print(f"{reg}: 0x{value:08X} ({value})")

except IndexError:
    pass

except:
    print('Fatal error has happened.\n')
    
print('Program completed. Window will closed.')
time.sleep(3)
