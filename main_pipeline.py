#!/usr/bin/env python3
"""
Simulador RISC-V com Pipeline
Programa principal
"""

import sys
import os
from processor_pipeline import RISCVPipelineProcessor
from assembler import RISCVAssembler

def imprimir_uso():
    """Imprime instruções de uso"""
    print("Simulador RISC-V com Pipeline de 5 estágios")
    print("Uso: python main.py <arquivo> [opções]")
    print()
    print("Argumentos:")
    print("  arquivo          Arquivo .asm ou .bin para executar")
    print()
    print("Opções:")
    print("  -d, --debug      Modo debug (imprime também no terminal)")
    print("  -o, --output     Nome do arquivo de saída (padrão: saida.out)")
    print("  -h, --help       Mostra esta ajuda")
    print()
    print("Exemplos:")
    print("  python main.py examples/soma.asm")
    print("  python main.py programa.bin -d")
    print("  python main.py examples/fatorial.asm -o resultado.out")
    print()
    print("O simulador gera um arquivo de saída com:")
    print("  - Estado do pipeline a cada ciclo")
    print("  - Valor dos 32 registradores")
    print("  - Conteúdo da memória (posições preenchidas)")

def main():
    """Função principal"""
    # Verificar argumentos
    if len(sys.argv) < 2:
        imprimir_uso()
        return 1
    
    # Parse dos argumentos
    arquivo = None
    debug = False
    arquivo_saida = "saida.out"
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['-h', '--help']:
            imprimir_uso()
            return 0
        elif arg in ['-d', '--debug']:
            debug = True
        elif arg in ['-o', '--output']:
            if i + 1 < len(sys.argv):
                arquivo_saida = sys.argv[i + 1]
                i += 1
            else:
                print("Erro: opção -o requer um argumento")
                return 1
        elif not arquivo:
            arquivo = arg
        else:
            print(f"Argumento desconhecido: {arg}")
            return 1
        
        i += 1
    
    if not arquivo:
        print("Erro: nenhum arquivo especificado")
        imprimir_uso()
        return 1
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo):
        print(f"Erro: arquivo '{arquivo}' não encontrado")
        return 1
    
    # Criar processador
    processor = RISCVPipelineProcessor(debug=debug)
    
    try:
        # Carregar programa
        if arquivo.endswith('.asm'):
            if not processor.carregar_arquivo_asm(arquivo):
                return 1
        elif arquivo.endswith('.bin'):
            if not processor.carregar_arquivo_bin(arquivo):
                return 1
        else:
            print("Erro: arquivo deve ter extensão .asm ou .bin")
            return 1
        
        print(f"Executando programa: {arquivo}")
        print(f"Arquivo de saída: {arquivo_saida}")
        print("Iniciando simulação com pipeline...")
        
        # Configurar arquivo de saída
        processor.abrir_arquivo_saida(arquivo_saida)
        
        # Executar com pipeline
        processor.executar_com_pipeline()
        
        print("Simulação concluída!")
        print(f"Resultados salvos em: {arquivo_saida}")
        
        return 0
    
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário")
        return 1
    except Exception as e:
        print(f"Erro durante execução: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
