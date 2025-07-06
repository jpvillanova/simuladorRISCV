#!/usr/bin/env python3
"""
Simulador RISC-V RV32I
Ponto de entrada principal do simulador
"""

import sys
import argparse
from processor import RISCVProcessor
from assembler import RISCVAssembler

def main():
    parser = argparse.ArgumentParser(description='Simulador RISC-V RV32I')
    parser.add_argument('arquivo', help='Arquivo assembly (.asm) ou binário (.bin)')
    parser.add_argument('-d', '--debug', action='store_true', help='Modo debug')
    parser.add_argument('-s', '--step', action='store_true', help='Execução passo a passo')
    parser.add_argument('-v', '--verbose', action='store_true', help='Saída detalhada')
    
    args = parser.parse_args()
    
    # Criar processador
    processor = RISCVProcessor(debug=args.debug)
    
    try:
        # Carregar programa
        if args.arquivo.endswith('.asm'):
            # Assemblar o código
            assembler = RISCVAssembler()
            with open(args.arquivo, 'r') as f:
                codigo_assembly = f.read()
            
            print(f"Assemblando {args.arquivo}...")
            instrucoes = assembler.assemblar(codigo_assembly)
            processor.carregar_programa(instrucoes)
        
        elif args.arquivo.endswith('.bin'):
            # Carregar binário diretamente
            with open(args.arquivo, 'rb') as f:
                dados = f.read()
            processor.carregar_binario(dados)
        
        else:
            print("Erro: Arquivo deve ter extensão .asm ou .bin")
            return 1
        
        # Executar programa
        print("Iniciando execução...")
        if args.step:
            processor.executar_passo_a_passo()
        else:
            processor.executar()
        
        # Mostrar resultados
        if args.verbose:
            processor.imprimir_estado()
        
        print("Execução concluída.")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{args.arquivo}' não encontrado.")
        return 1
    except Exception as e:
        print(f"Erro durante execução: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
