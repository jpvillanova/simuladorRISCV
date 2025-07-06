# Programa simples para testar o pipeline
# Faz algumas operações básicas

main:
    addi x1, zero, 10    # x1 = 10
    addi x2, zero, 20    # x2 = 20
    add x3, x1, x2       # x3 = x1 + x2 (30)
    sub x4, x3, x1       # x4 = x3 - x1 (20)
    and x5, x3, x2       # x5 = x3 & x2
    or x6, x1, x2        # x6 = x1 | x2
    
    # Operações com memória
    addi x7, zero, 0x100 # endereço base
    sw x3, 0(x7)         # armazena x3 na memória
    lw x8, 0(x7)         # carrega de volta em x8
    
    # Loop simples
    addi x9, zero, 3     # contador = 3
loop:
    addi x9, x9, -1      # contador--
    bne x9, zero, loop   # se contador != 0, loop
    
fim:
    beq zero, zero, fim  # loop infinito
