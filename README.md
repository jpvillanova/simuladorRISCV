# Simulador RISC-V em Python

Um simulador básico da arquitetura RISC-V RV32I implementado em Python.

## Características

- Suporte para instruções RV32I básicas
- Memória de instruções e dados
- Registradores de 32 bits
- Interface de linha de comando
- Depurador integrado

## Instruções Suportadas

### Tipo R (Register-Register)
- ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND

### Tipo I (Immediate)
- ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI
- LB, LH, LW, LBU, LHU

### Tipo S (Store)
- SB, SH, SW

### Tipo B (Branch)
- BEQ, BNE, BLT, BGE, BLTU, BGEU

### Tipo U (Upper Immediate)
- LUI, AUIPC

### Tipo J (Jump)
- JAL, JALR

## Como usar

```bash
python main.py programa.asm
```

## Estrutura do Projeto

- `main.py` - Ponto de entrada do simulador
- `processor.py` - Classe principal do processador RISC-V
- `memory.py` - Implementação da memória
- `decoder.py` - Decodificador de instruções
- `assembler.py` - Assembler simples para código RISC-V
- `examples/` - Programas de exemplo
