#!/usr/bin/env python3
"""
Testes básicos para o simulador RISC-V
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processor import RISCVProcessor
from assembler import RISCVAssembler

def teste_soma():
    """Testa programa de soma simples"""
    print("=== Teste: Soma ===")
    
    codigo = """
    addi x1, zero, 10
    addi x2, zero, 20
    add x3, x1, x2
    """
    
    assembler = RISCVAssembler()
    processor = RISCVProcessor(debug=True)
    
    instrucoes = assembler.assemblar(codigo)
    processor.carregar_programa(instrucoes)
    
    # Executar 3 instruções
    for _ in range(3):
        palavra = processor.buscar_instrucao()
        instrucao = processor.decodificador.decodificar(palavra)
        processor.executar_instrucao(instrucao)
    
    # Verificar resultado
    resultado = processor.ler_registrador(3)
    print(f"Resultado da soma: {resultado} (esperado: 30)")
    assert resultado == 30, f"Erro: esperado 30, obtido {resultado}"
    print("✓ Teste passou!\n")

def teste_branches():
    """Testa instruções de branch"""
    print("=== Teste: Branches ===")
    
    codigo = """
    addi x1, zero, 5
    addi x2, zero, 5
    beq x1, x2, igual
    addi x3, zero, 1
    beq zero, zero, fim
igual:
    addi x3, zero, 2
fim:
    """
    
    assembler = RISCVAssembler()
    processor = RISCVProcessor(debug=True)
    
    instrucoes = assembler.assemblar(codigo)
    processor.carregar_programa(instrucoes)
    
    # Executar até branch tomar
    for _ in range(10):  # limite de segurança
        if processor.pc >= len(instrucoes) * 4:
            break
        
        palavra = processor.buscar_instrucao()
        instrucao = processor.decodificador.decodificar(palavra)
        processor.executar_instrucao(instrucao)
        
        # Parar se chegar no fim
        nome = instrucao.obter_nome_instrucao()
        if nome == "ADDI" and processor.pc == 20:  # Instrução final
            break
    
    # Verificar se o branch foi tomado (x3 deve ser 2)
    resultado = processor.ler_registrador(3)
    print(f"Resultado do branch: {resultado} (esperado: 2)")
    assert resultado == 2, f"Erro: esperado 2, obtido {resultado}"
    print("✓ Teste passou!\n")

def teste_loads_stores():
    """Testa instruções de load e store"""
    print("=== Teste: Load/Store ===")
    
    codigo = """
    addi x1, zero, 100
    addi x2, zero, 0x100
    sw x1, 0(x2)
    lw x3, 0(x2)
    """
    
    assembler = RISCVAssembler()
    processor = RISCVProcessor(debug=True)
    
    instrucoes = assembler.assemblar(codigo)
    processor.carregar_programa(instrucoes)
    
    # Executar 4 instruções
    for _ in range(4):
        palavra = processor.buscar_instrucao()
        instrucao = processor.decodificador.decodificar(palavra)
        processor.executar_instrucao(instrucao)
    
    # Verificar se o valor foi carregado corretamente
    resultado = processor.ler_registrador(3)
    print(f"Valor carregado: {resultado} (esperado: 100)")
    assert resultado == 100, f"Erro: esperado 100, obtido {resultado}"
    print("✓ Teste passou!\n")

def teste_assembler():
    """Testa o assembler com várias instruções"""
    print("=== Teste: Assembler ===")
    
    codigo = """
    # Teste de comentários
    addi x1, zero, 42    # comentário inline
    
    # Labels
    loop:
        addi x2, x2, 1
        bne x2, x1, loop
    
    # Instruções variadas
    lui x3, 0x12345
    auipc x4, 0x1000
    jal x5, fim
    
    fim:
        add x6, x1, x2
    """
    
    assembler = RISCVAssembler()
    
    try:
        instrucoes = assembler.assemblar(codigo)
        print(f"Assemblagem bem-sucedida: {len(instrucoes)} instruções geradas")
        
        for i, instr in enumerate(instrucoes):
            print(f"  {i*4:04x}: {instr:08x}")
        
        print("✓ Teste passou!\n")
    
    except Exception as e:
        print(f"Erro na assemblagem: {e}")
        raise

def main():
    """Executa todos os testes"""
    print("Iniciando testes do simulador RISC-V...\n")
    
    try:
        teste_soma()
        teste_branches()
        teste_loads_stores()
        teste_assembler()
        
        print("🎉 Todos os testes passaram!")
        
    except Exception as e:
        print(f"❌ Teste falhou: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
