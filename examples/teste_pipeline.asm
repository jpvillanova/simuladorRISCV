# Programa simples para testar pipeline
# Soma de dois números

addi x1, zero, 10
addi x2, zero, 20
add x3, x1, x2
addi x4, x3, 5
sw x4, 0x100(zero)
lw x5, 0x100(zero)
