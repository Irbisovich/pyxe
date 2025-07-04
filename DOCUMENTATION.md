# PyXE Documentation

## Introduction
PyXE is a custom assembly-like programming language and virtual machine designed just for fun. It features a simplified instruction set, custom registers, and built-in I/O capabilities.

Key Features:
- 8 dedicated registers
- 16 custom instructions with aliases
- Built-in string handling and I/O
- 1MB memory space

## Registers
PyXE provides 8 specialized registers:

| Register Name     | Code | Purpose                          |
|-------------------|------|----------------------------------|
| ACCUMULATOR       | 0x01 | Primary operations and results   |
| BASE              | 0x02 | Secondary operations and data    |
| COUNT             | 0x03 | Loop counters and sizes          |
| DATA              | 0x04 | General purpose data storage     |
| SOURCE            | 0x05 | Source address for operations    |
| DEST              | 0x06 | Destination address for operations |
| BASEPOINTER       | 0x07 | Inventory/bitmask storage        |
| STACKPOINTER      | 0x08 | Manages the call stack           |

## Instruction Set

### Core Instructions
Each instruction has a 1-byte opcode:

| Mnemonic | Opcode | Description                          | Operands                  |
|----------|--------|--------------------------------------|---------------------------|
| MOV      | 0x10   | Move data between locations          | dest, src                 |
| ADD      | 0x20   | Add values                           | dest, src                 |
| SUB      | 0x30   | Subtract values                      | dest, src                 |
| INC      | 0x40   | Increment value                      | register                  |
| DEC      | 0x50   | Decrement value                      | register                  |
| CMP      | 0x60   | Compare values                       | op1, op2                  |
| JMP      | 0x70   | Unconditional jump                   | address                   |
| JE       | 0x80   | Jump if equal                        | address                   |
| JNE      | 0x90   | Jump if not equal                    | address                   |
| CALL     | 0xA0   | Call subroutine                      | address                   |
| RET      | 0xB0   | Return from subroutine               | none                      |
| PUSH     | 0xC0   | Push value onto stack                | register                  |
| POP      | 0xD0   | Pop value from stack                 | register                  |
| INT      | 0xE0   | Software interrupt                   | vector                    |
| HLT      | 0xF0   | Halt execution                       | none                      |
| AND      | 0x22   | Bitwise AND                          | dest, src                 |
| OR       | 0x33   | Bitwise OR                           | dest, src                 |
| XOR      | 0x44   | Bitwise XOR                          | dest, src                 |
| NOP      | 0x00   | No operation                         | none                      |
| INPUT    | 0x55   | Read input to register               | register                  |
| PRINT    | 0x66   | Print value or string                | value/address             |

### Custom Commands
PyXE provides user-friendly aliases for instructions:

| Custom Command | Maps To | Example Usage                |
|----------------|---------|------------------------------|
| drag           | MOV     | drag ACCUMULATOR, 42         |
| add            | ADD     | add ACCUMULATOR, 10          |
| subtract       | SUB     | subtract ACCUMULATOR, 5      |
| increase       | INC     | increase ACCUMULATOR         |
| decrease       | DEC     | decrease COUNT               |
| compare        | CMP     | compare ACCUMULATOR, 100     |
| go             | JMP     | go game_loop                 |
| go-true        | JE      | go-true valid_exit           |
| go-false       | JNE     | go-false no_item             |
| call           | CALL    | call show_room               |
| return         | RET     | return                       |
| place          | PUSH    | place ACCUMULATOR            |
| extract        | POP     | extract BASEPOINTER          |
| interrupt      | INT     | interrupt 0x80               |
| stop           | HLT     | stop                         |
| logic-and      | AND     | logic-and BASEPOINTER, 1     |
| logic-or       | OR      | logic-or BASEPOINTER, 2      |
| exclude-or     | XOR     | exclude-or BASEPOINTER, 4    |
| pass           | NOP     | pass                         |
| input          | INPUT   | input ACCUMULATOR            |
| print          | PRINT   | print "Hello World"          |
| defbyte        | DB      | defbyte my_var: 10           |
| defword        | DW      | defword room_items: 0x2000   |
| defdouble      | DD      | defdouble player_score: 0    |

## Data Directives
Define data in memory with these directives:

```assembly
; Define byte values (1 byte each)
defbyte my_char: 'A'
defbyte values: 1, 2, 3, 4
defbyte message: "Hello", 0

; Define word values (2 bytes each, little-endian)
defword pointers: key_name, torch_name
defword room_exits: 2, 0, 0, 0

; Define double-word values (4 bytes each)
defdouble player_health: 100
defdouble player_score: 0
defdouble game_state: 0xCAFEBABE
```

## System Calls
Use `interrupt 0x80` for I/O operations:

```assembly
drag ACCUMULATOR, 4  ; sys_write
drag BASE, 1         ; stdout
drag COUNT, message  ; buffer address
drag DATA, 12        ; buffer size
interrupt 0x80

drag ACCUMULATOR, 3  ; sys_read
drag BASE, 0         ; stdin
drag COUNT, buffer   ; buffer address
drag DATA, 32        ; buffer size
interrupt 0x80

drag ACCUMULATOR, 1  ; sys_exit
drag BASE, 0         ; exit code
interrupt 0x80
```

## Memory Organization
PyXE uses a fixed memory layout:

| Address Range  | Size    | Purpose                |
|----------------|---------|------------------------|
| 0x0000-0x0FFF | 4KB     | Reserved               |
| 0x1000-0x1FFF | 4KB     | Code section           |
| 0x2000-0xFFFF | 56KB    | Data section           |
| 0x10000+      | 960KB   | Stack (grows downward) |

## Examples

### Hello World
```assembly
start:
    print "Hello, PyXE World!\n"
    stop

; Alternatively using sys_write:
start:
    drag ACCUMULATOR, 4
    drag BASE, 1
    drag COUNT, message
    drag DATA, 14
    interrupt 0x80
    stop

message:
    defbyte "Hello World!\n", 0
```

### Input and Output
```assembly
start:
    print "Enter your name: "
    drag ACCUMULATOR, 3
    drag BASE, 0
    drag COUNT, buffer
    drag DATA, 32
    interrupt 0x80
    
    print "Hello, "
    print buffer
    stop

buffer:
    defbyte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

## Building and Running
1. Save your code with `.pyxe` extension (e.g., `game.pyxe`)
2. Run with PyXE:
```bash
main.pyxe
```
or run it from your file manager.

3. Compilation process:
   - Removes comments and empty lines
   - Processes in 4 passes:
     1. Collect labels and calculate addresses
     2. Resolve data addresses
     3. Compile instructions
     4. Compile data
