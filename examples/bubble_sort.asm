# Programa para ordenar um array usando bubble sort
# Array de 5 elementos: [5, 2, 8, 1, 9]

main:
    # Configurar base do array na memória (endereço 0x1000)
    lui x10, 0x1000      # x10 = 0x1000 (base do array)
    
    # Inicializar array na memória
    addi x1, zero, 5
    sw x1, 0(x10)        # array[0] = 5
    
    addi x1, zero, 2
    sw x1, 4(x10)        # array[1] = 2
    
    addi x1, zero, 8
    sw x1, 8(x10)        # array[2] = 8
    
    addi x1, zero, 1
    sw x1, 12(x10)       # array[3] = 1
    
    addi x1, zero, 9
    sw x1, 16(x10)       # array[4] = 9
    
    # Bubble sort
    addi x11, zero, 5    # tamanho do array
    addi x12, zero, 0    # i = 0

outer_loop:
    bge x12, x11, fim    # if i >= tamanho, fim
    
    addi x13, zero, 0    # j = 0
    sub x14, x11, x12    # x14 = tamanho - i
    addi x14, x14, -1    # x14 = tamanho - i - 1

inner_loop:
    bge x13, x14, next_i # if j >= tamanho-i-1, próximo i
    
    # Calcular endereços
    slli x15, x13, 2     # x15 = j * 4
    add x15, x10, x15    # x15 = base + j*4
    lw x16, 0(x15)       # x16 = array[j]
    lw x17, 4(x15)       # x17 = array[j+1]
    
    # Comparar e trocar se necessário
    ble x16, x17, no_swap # if array[j] <= array[j+1], não troca
    
    # Trocar elementos
    sw x17, 0(x15)       # array[j] = x17
    sw x16, 4(x15)       # array[j+1] = x16

no_swap:
    addi x13, x13, 1     # j++
    beq zero, zero, inner_loop

next_i:
    addi x12, x12, 1     # i++
    beq zero, zero, outer_loop

fim:
    # Array ordenado está na memória a partir de 0x1000
    beq zero, zero, fim  # loop infinito
