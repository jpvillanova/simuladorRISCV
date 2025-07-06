# Programa simples: soma de dois números
# Este programa soma 10 + 20 e armazena o resultado em x3

main:
    addi x1, zero, 10    # x1 = 10
    addi x2, zero, 20    # x2 = 20
    add x3, x1, x2       # x3 = x1 + x2 (resultado: 30)
    
    # Loop infinito para manter o programa rodando
loop:
    beq x0, x0, loop     # Salta sempre para loop
