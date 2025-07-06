# Programa para calcular o fatorial de 5
# Resultado ficará em x3

main:
    addi x1, zero, 5     # n = 5
    addi x2, zero, 1     # contador = 1
    addi x3, zero, 1     # resultado = 1

loop:
    blt x1, x2, fim      # if n < contador, vai para fim
    
    # resultado = resultado * contador
    add x4, zero, zero   # x4 = 0 (acumulador para multiplicação)
    add x5, zero, x2     # x5 = contador (contador para multiplicação)
    
mult_loop:
    beq x5, zero, mult_fim  # if contador == 0, fim da multiplicação
    add x4, x4, x3          # x4 += resultado
    addi x5, x5, -1         # contador--
    beq zero, zero, mult_loop  # volta para mult_loop

mult_fim:
    add x3, zero, x4     # resultado = x4
    addi x2, x2, 1       # contador++
    beq zero, zero, loop # volta para loop

fim:
    # Resultado do fatorial está em x3
    beq zero, zero, fim  # loop infinito
