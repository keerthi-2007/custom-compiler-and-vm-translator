# Hack Computing Stack
A complete computing stack built for the Hack Architecture, covering multiple layers of computer systems including hardware design, virtual machine translation, and compiler construction. This project was developed as part of the Introduction to Computer Systems coursework at IIT Madras and follows the Nand2Tetris philosophy of building a computer system from the ground up.

# Overview
The project spans three major components:
- Hardware Design
- Virtual Machine Translation
- Compiler Construction
Together, these components form an end-to-end toolchain capable of translating high-level Jack programs into executable code for the Hack computer.

Jack Source 
    ↓ 
Tokenizer
    ↓ 
Parser 
    ↓ 
VM Code 
    ↓ 
VM Translator 
    ↓ 
Hack Assembly 
    ↓ 
Hack Machine Code

# Hardware Design
The hardware portion focuses on memory architecture and processor extensions using Hack HDL
Implemented components include:
- 1-bit and 16-bit Registers
- RAM hierarchy and memory modules
- Addressing and memory management circuits
- Hardware Multiplier
- ALU extensions for multiplication support
This stage provided hands-on experience with sequential logic, memory organization, and hardware-level arithmetic operations

# Virtual Machine Translator
A VM Translator was implemented in Python to convert Hack Virtual Machine instructions into Hack Assembly language.
Supported functionality:
- Stack arithmetic operations
- Memory access commands
- Program flow instructions
- Labels and branching
- Function calls and returns
The translator forms the bridge between the high-level VM abstraction and the underlying Hack Assembly language.

# Compiler Construction
A compiler frontend for the Jack programming language was implemented in Python.
Components:
- # Tokenizer
  Performs lexical analysis by converting Jack source code into a stream of tokens while handling comments, symbols, identifiers, keywords, and constants.
- # Parser
  Uses recursive-descent parsing to validate program structure according to the Jack grammar and generate the corresponding parse tree.
- # Symbol Table
  Maintains identifier information across class-level and subroutine-level scopes during compilation.
- # VM Code Generator
  Generates valid VM instructions from parsed Jack programs, enabling execution through the VM Translator.

# Demonstration Program
To validate the complete compilation pipeline, a 2D Convolution application was implemented in Jack.
The program:
- Accepts a flattened input matrix
- Applies a 3×3 convolution filter
- Supports configurable stride values
- Generates an output matrix through repeated multiply-accumulate operations
This served as an end-to-end test case for the compiler and VM translator.

# Repository Structure
* hardware
* │ 
* ├── Memory Components 
* ├── RAM Modules 
* ├── Multiplier 
* └── ALU
* vm-translator 
* │ 
* ├── main.py 
* ├── parser.py 
* └── code_writer.py 
* compiler
* │ 
* ├── JackTokenizer.py 
* ├── CompilationEngine.py 
* ├── SymbolTable.py 
* ├── VMWriter.py 
* └── JackCompiler.py
screenshots/

# Key Learnings
- Design and implementation of sequential memory systems
- Hardware arithmetic and processor extensions
- Stack-based virtual machine architecture
- Lexical analysis and parsing techniques
- Symbol table management
- VM code generation
- End-to-end compiler construction

# Author
Vallem Keerthi Reddy
B.Tech in Artificial Intelligence and Data Analytics
Indian Institute of Technology Madras

