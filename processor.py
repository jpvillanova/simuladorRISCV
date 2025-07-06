"""
Processador RISC-V RV32I
Classe principal que implementa o processador
"""

from memory import Memoria
from decoder import DecodificadorRISCV

class RISCVProcessor:
    def __init__(self, debug=False):
        # Registradores (x0 sempre zero)
        self.registradores = [0] * 32
        
        # Program Counter
        self.pc = 0
        
        # Memória
        self.memoria = Memoria()
        
        # Decodificador
        self.decodificador = DecodificadorRISCV()
        
        # Estado de execução
        self.executando = False
        self.debug = debug
        self.ciclos = 0
        
    def reset(self):
        """Reinicia o processador"""
        self.registradores = [0] * 32
        self.pc = 0
        self.memoria.limpar()
        self.executando = False
        self.ciclos = 0
    
    def carregar_programa(self, instrucoes):
        """Carrega um programa (lista de instruções de 32 bits) na memória"""
        endereco = 0
        for instrucao in instrucoes:
            self.memoria.escrever_word(endereco, instrucao)
            endereco += 4
    
    def carregar_binario(self, dados):
        """Carrega dados binários na memória"""
        self.memoria.carregar_dados(0, dados)
    
    def ler_registrador(self, num_reg):
        """Lê um registrador (x0 sempre retorna 0)"""
        if num_reg == 0:
            return 0
        return self.registradores[num_reg] & 0xFFFFFFFF
    
    def escrever_registrador(self, num_reg, valor):
        """Escreve em um registrador (x0 sempre permanece 0)"""
        if num_reg != 0:
            self.registradores[num_reg] = valor & 0xFFFFFFFF
    
    def buscar_instrucao(self):
        """Busca a próxima instrução da memória"""
        return self.memoria.ler_word(self.pc)
    
    def executar_instrucao(self, instrucao):
        """Executa uma instrução decodificada"""
        nome = instrucao.obter_nome_instrucao()
        
        if self.debug:
            print(f"PC: {self.pc:08x}, Instrução: {nome}")
        
        # Tipo R
        if nome == "ADD":
            resultado = (self.ler_registrador(instrucao.rs1) + 
                        self.ler_registrador(instrucao.rs2)) & 0xFFFFFFFF
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SUB":
            resultado = (self.ler_registrador(instrucao.rs1) - 
                        self.ler_registrador(instrucao.rs2)) & 0xFFFFFFFF
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "AND":
            resultado = self.ler_registrador(instrucao.rs1) & self.ler_registrador(instrucao.rs2)
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "OR":
            resultado = self.ler_registrador(instrucao.rs1) | self.ler_registrador(instrucao.rs2)
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "XOR":
            resultado = self.ler_registrador(instrucao.rs1) ^ self.ler_registrador(instrucao.rs2)
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SLL":
            shift = self.ler_registrador(instrucao.rs2) & 0x1F
            resultado = (self.ler_registrador(instrucao.rs1) << shift) & 0xFFFFFFFF
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SRL":
            shift = self.ler_registrador(instrucao.rs2) & 0x1F
            resultado = self.ler_registrador(instrucao.rs1) >> shift
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SRA":
            shift = self.ler_registrador(instrucao.rs2) & 0x1F
            valor = self.ler_registrador(instrucao.rs1)
            if valor & 0x80000000:  # Negativo
                resultado = (valor >> shift) | (0xFFFFFFFF << (32 - shift))
            else:
                resultado = valor >> shift
            self.escrever_registrador(instrucao.rd, resultado & 0xFFFFFFFF)
        
        elif nome == "SLT":
            rs1_val = self._sinal_extendido_32(self.ler_registrador(instrucao.rs1))
            rs2_val = self._sinal_extendido_32(self.ler_registrador(instrucao.rs2))
            resultado = 1 if rs1_val < rs2_val else 0
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SLTU":
            resultado = 1 if self.ler_registrador(instrucao.rs1) < self.ler_registrador(instrucao.rs2) else 0
            self.escrever_registrador(instrucao.rd, resultado)
        
        # Tipo I
        elif nome == "ADDI":
            resultado = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SLTI":
            rs1_val = self._sinal_extendido_32(self.ler_registrador(instrucao.rs1))
            resultado = 1 if rs1_val < instrucao.imm else 0
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SLTIU":
            resultado = 1 if self.ler_registrador(instrucao.rs1) < (instrucao.imm & 0xFFFFFFFF) else 0
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "XORI":
            resultado = self.ler_registrador(instrucao.rs1) ^ (instrucao.imm & 0xFFFFFFFF)
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "ORI":
            resultado = self.ler_registrador(instrucao.rs1) | (instrucao.imm & 0xFFFFFFFF)
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "ANDI":
            resultado = self.ler_registrador(instrucao.rs1) & (instrucao.imm & 0xFFFFFFFF)
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SLLI":
            shift = instrucao.imm & 0x1F
            resultado = (self.ler_registrador(instrucao.rs1) << shift) & 0xFFFFFFFF
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SRLI":
            shift = instrucao.imm & 0x1F
            resultado = self.ler_registrador(instrucao.rs1) >> shift
            self.escrever_registrador(instrucao.rd, resultado)
        
        elif nome == "SRAI":
            shift = instrucao.imm & 0x1F
            valor = self.ler_registrador(instrucao.rs1)
            if valor & 0x80000000:  # Negativo
                resultado = (valor >> shift) | (0xFFFFFFFF << (32 - shift))
            else:
                resultado = valor >> shift
            self.escrever_registrador(instrucao.rd, resultado & 0xFFFFFFFF)
        
        # Loads
        elif nome == "LW":
            endereco = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            valor = self.memoria.ler_word(endereco)
            self.escrever_registrador(instrucao.rd, valor)
        
        elif nome == "LH":
            endereco = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            valor = self.memoria.ler_halfword(endereco)
            if valor & 0x8000:  # Estender sinal
                valor |= 0xFFFF0000
            self.escrever_registrador(instrucao.rd, valor)
        
        elif nome == "LHU":
            endereco = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            valor = self.memoria.ler_halfword(endereco)
            self.escrever_registrador(instrucao.rd, valor)
        
        elif nome == "LB":
            endereco = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            valor = self.memoria.ler_byte(endereco)
            if valor & 0x80:  # Estender sinal
                valor |= 0xFFFFFF00
            self.escrever_registrador(instrucao.rd, valor)
        
        elif nome == "LBU":
            endereco = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            valor = self.memoria.ler_byte(endereco)
            self.escrever_registrador(instrucao.rd, valor)
        
        # Stores
        elif nome == "SW":
            endereco = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            valor = self.ler_registrador(instrucao.rs2)
            self.memoria.escrever_word(endereco, valor)
        
        elif nome == "SH":
            endereco = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            valor = self.ler_registrador(instrucao.rs2) & 0xFFFF
            self.memoria.escrever_halfword(endereco, valor)
        
        elif nome == "SB":
            endereco = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFF
            valor = self.ler_registrador(instrucao.rs2) & 0xFF
            self.memoria.escrever_byte(endereco, valor)
        
        # Branches
        elif nome == "BEQ":
            if self.ler_registrador(instrucao.rs1) == self.ler_registrador(instrucao.rs2):
                self.pc = (self.pc + instrucao.imm) & 0xFFFFFFFF
                return  # Não incrementar PC
        
        elif nome == "BNE":
            if self.ler_registrador(instrucao.rs1) != self.ler_registrador(instrucao.rs2):
                self.pc = (self.pc + instrucao.imm) & 0xFFFFFFFF
                return
        
        elif nome == "BLT":
            rs1_val = self._sinal_extendido_32(self.ler_registrador(instrucao.rs1))
            rs2_val = self._sinal_extendido_32(self.ler_registrador(instrucao.rs2))
            if rs1_val < rs2_val:
                self.pc = (self.pc + instrucao.imm) & 0xFFFFFFFF
                return
        
        elif nome == "BGE":
            rs1_val = self._sinal_extendido_32(self.ler_registrador(instrucao.rs1))
            rs2_val = self._sinal_extendido_32(self.ler_registrador(instrucao.rs2))
            if rs1_val >= rs2_val:
                self.pc = (self.pc + instrucao.imm) & 0xFFFFFFFF
                return
        
        elif nome == "BLTU":
            if self.ler_registrador(instrucao.rs1) < self.ler_registrador(instrucao.rs2):
                self.pc = (self.pc + instrucao.imm) & 0xFFFFFFFF
                return
        
        elif nome == "BGEU":
            if self.ler_registrador(instrucao.rs1) >= self.ler_registrador(instrucao.rs2):
                self.pc = (self.pc + instrucao.imm) & 0xFFFFFFFF
                return
        
        # Upper immediate
        elif nome == "LUI":
            self.escrever_registrador(instrucao.rd, instrucao.imm)
        
        elif nome == "AUIPC":
            resultado = (self.pc + instrucao.imm) & 0xFFFFFFFF
            self.escrever_registrador(instrucao.rd, resultado)
        
        # Jumps
        elif nome == "JAL":
            self.escrever_registrador(instrucao.rd, self.pc + 4)
            self.pc = (self.pc + instrucao.imm) & 0xFFFFFFFF
            return
        
        elif nome == "JALR":
            endereco_alvo = (self.ler_registrador(instrucao.rs1) + instrucao.imm) & 0xFFFFFFFE
            self.escrever_registrador(instrucao.rd, self.pc + 4)
            self.pc = endereco_alvo
            return
        
        else:
            raise Exception(f"Instrução não implementada: {nome}")
        
        # Incrementar PC para próxima instrução
        self.pc += 4
    
    def _sinal_extendido_32(self, valor):
        """Converte um valor de 32 bits para inteiro com sinal"""
        if valor & 0x80000000:
            return valor - 0x100000000
        return valor
    
    def executar(self):
        """Executa o programa até parar"""
        self.executando = True
        self.ciclos = 0
        
        try:
            while self.executando:
                # Buscar instrução
                palavra_instrucao = self.buscar_instrucao()
                
                # Decodificar instrução
                instrucao = self.decodificador.decodificar(palavra_instrucao)
                
                # Verificar se é instrução válida
                if not self.decodificador.e_valida(instrucao):
                    print(f"Instrução inválida em PC={self.pc:08x}: {palavra_instrucao:08x}")
                    break
                
                # Executar instrução
                self.executar_instrucao(instrucao)
                
                self.ciclos += 1
                
                # Verificar condições de parada
                if self.ciclos > 1000000:  # Limite de segurança
                    print("Limite de ciclos atingido!")
                    break
                
        except Exception as e:
            print(f"Erro durante execução: {e}")
            self.executando = False
    
    def executar_passo_a_passo(self):
        """Executa o programa passo a passo"""
        self.executando = True
        self.ciclos = 0
        
        try:
            while self.executando:
                print(f"\n--- Ciclo {self.ciclos + 1} ---")
                print(f"PC: {self.pc:08x}")
                
                # Buscar instrução
                palavra_instrucao = self.buscar_instrucao()
                print(f"Instrução: {palavra_instrucao:08x}")
                
                # Decodificar instrução
                instrucao = self.decodificador.decodificar(palavra_instrucao)
                print(f"Tipo: {instrucao.obter_nome_instrucao()}")
                
                # Verificar se é instrução válida
                if not self.decodificador.e_valida(instrucao):
                    print("Instrução inválida!")
                    break
                
                # Executar instrução
                self.executar_instrucao(instrucao)
                
                self.ciclos += 1
                
                # Mostrar estado
                self._imprimir_registradores_alterados()
                
                # Aguardar entrada do usuário
                entrada = input("Pressione Enter para continuar, 'q' para sair, 'r' para ver registradores: ").strip()
                if entrada.lower() == 'q':
                    break
                elif entrada.lower() == 'r':
                    self.imprimir_estado()
                
        except Exception as e:
            print(f"Erro durante execução: {e}")
            self.executando = False
    
    def _imprimir_registradores_alterados(self):
        """Imprime apenas registradores não-zero"""
        alterados = []
        for i in range(32):
            if self.registradores[i] != 0:
                alterados.append(f"x{i}: {self.registradores[i]:08x}")
        
        if alterados:
            print("Registradores alterados:", ", ".join(alterados))
    
    def imprimir_estado(self):
        """Imprime o estado completo do processador"""
        print("\n=== Estado do Processador ===")
        print(f"PC: {self.pc:08x}")
        print(f"Ciclos: {self.ciclos}")
        
        print("\nRegistradores:")
        for i in range(0, 32, 4):
            linha = []
            for j in range(4):
                if i + j < 32:
                    reg_num = i + j
                    valor = self.registradores[reg_num]
                    linha.append(f"x{reg_num:2d}: {valor:08x}")
            print("  ".join(linha))
        
        print(f"\nMemória (primeiros 256 bytes):")
        print(self.memoria.dump(0, 256))
