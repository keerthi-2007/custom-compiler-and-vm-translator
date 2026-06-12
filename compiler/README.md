src/
* ├── JackTokenizer.py
* ├── CompilationEngine.py
* ├── SymbolTable.py
* ├── VMWriter.py
* ├── JackCompiler.py
* └── README.md

jack/
├── Conv.jack
└── Main.jack

VMfiles/
├── Conv.vm
└── Main.vm


The compiler pipeline is:

```text
Jack Source
   ↓
Tokenizer
   ↓
Tokens XML
   ↓
Parser / Compilation Engine
   ↓
Parse Tree XML
   ↓
VM Code
```

---

# How to Run

## Step 1 — Compile a Jack File

Example:

```bash
python3 JackCompiler.py Conv.jack
```

or

```bash
python3 JackCompiler.py Main.jack
```

This generates:

- `ConvT.xml` / `MainT.xml`
- `Conv.xml` / `Main.xml`
- `Conv.vm` / `Main.vm`

---

## Step 2 — Compile an Entire Folder

All `.jack` files are inside a folder:

```bash
python3 JackCompiler.py jack/
```

---

# VM Translation

Place:

```text
Conv.vm
Main.vm
```

inside a folder named `VMfiles/`.

Then run the  VM Translator:

```bash
python3 main.py VMfiles
```

This generates:

```text
VMfiles.asm
```

---

# Running on the nand2tetris VM Emulator

1. Open `VMEmulator`
2. Click `File → Load Program`
3. Select the `VMfiles/` folder
4. Set speed to `No Animation`
5. Click `Run`

Expected output:

```text
Conv output (5x5, Sobel, stride=1):
8 8 8
8 8 8
8 8 8
```
```
8 8 8 8 8 8 8
8 8 8 8 8 8 8
8 8 8 8 8 8 8
8 8 8 8 8 8 8
8 8 8 8 8 8 8
```

---

# 2D Convolution Details

The implementation uses:

- Filter size: `3 × 3`
- Padding: `0`
- Stride: `1`
- Flattened arrays for matrix storage

The Sobel horizontal edge detector kernel used is:

```text
-1  0  1
-2  0  2
-1  0  1
```


# Files Generated

| File | Description |
|------|-------------|
| ConvT.xml | Token stream XML |
| Conv.xml | Parse tree XML |
| Conv.vm | Generated VM code |
| Main.vm | Driver program VM code |

---

# End-to-End Flow

```text
Conv.jack / Main.jack
        ↓
JackTokenizer.py
        ↓
Tokens XML
        ↓
CompilationEngine.py
        ↓
VM Code
        ↓
Assignment 2 VM Translator
        ↓
Hack Assembly
        ↓
VM Emulator Execution
```
