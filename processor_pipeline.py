#!/usr/bin/env python3
"""
Simulador do processador RISC-V RV32I com Pipeline de 5 estágios
"""

from decoder import DecodificadorRISCV
from memory import Memoria
from dataclasses import dataclass
from typing import Optional, Dict, List
import sys

@dataclass
class PipelineRegister:
    """Registrador de pipeline entre estágios"""
    pc: int = 0
    instrucao: int = 0
    rs1: int = 0
    rs2: int = 0
    rd: int = 0
    imm: int = 0
    alu_result: int = 0
    mem_data: int = 0
    controle: Dict = None
    valido: bool = False
    nome_instrucao: str = "NOP"
    
    def __post_init__(self):
        if self.controle is None:
            self.controle = {}

class RISCVPipelineProcessor:
    def __init__(self, debug=False):
        # Registradores (x0 sempre zero)
        self.registradores = [0] * 32
        
        # Program Counter
        self.pc = 0
        
        # Memória
        self.memoria = Memoria()
        
        # Decodificador
        self.decodificador = DecodificadorRISCV()
        
        # Debug
        self.debug = debug
        
        # Contadores de ciclos
        self.ciclos = 0
        self.instrucoes_executadas = 0
        
        # Pipeline registers
        self.if_id = PipelineRegister()
        self.id_ex = PipelineRegister()
        self.ex_mem = PipelineRegister()
        self.mem_wb = PipelineRegister()
        
        # Controle de hazards
        self.stall = False
        self.flush = False
        
        # Histórico para saída
        self.historico_pipeline = []
        self.programa_carregado = []
        
        # Arquivo de saída
        self.arquivo_saida = None
        
    def reset(self):
        """Reinicia o processador"""
        self.registradores = [0] * 32
        self.pc = 0
        self.memoria.limpar()
        self.ciclos = 0
        self.instrucoes_executadas = 0
        
        # Resetar pipeline
        self.if_id = PipelineRegister()
        self.id_ex = PipelineRegister()
        self.ex_mem = PipelineRegister()
        self.mem_wb = PipelineRegister()
        
        self.stall = False
        self.flush = False
        self.historico_pipeline = []
        
    def carregar_programa(self, instrucoes):
        """Carrega um programa (lista de instruções de 32 bits) na memória"""
        self.programa_carregado = instrucoes.copy()
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
    
    def abrir_arquivo_saida(self, nome_arquivo="saida.out"):
        """Abre arquivo de saída"""
        self.arquivo_saida = open(nome_arquivo, 'w', encoding='utf-8')
        
    def fechar_arquivo_saida(self):
        """Fecha arquivo de saída"""
        if self.arquivo_saida:
            self.arquivo_saida.close()
    
    def escrever_saida(self, texto):
        """Escreve no arquivo de saída"""
        if self.arquivo_saida:
            self.arquivo_saida.write(texto + '\n')
        if self.debug:
            print(texto)
    
    def detectar_hazards(self):
        """Detecta hazards de dados e controle"""
        # Hazard de dados RAW (Read After Write)
        if (self.id_ex.valido and self.id_ex.controle.get('reg_write', False) and
            self.if_id.valido):
            
            # Verificar se há dependência
            if (self.id_ex.rd != 0 and 
                (self.id_ex.rd == self.if_id.rs1 or self.id_ex.rd == self.if_id.rs2)):
                return True
                
        # Hazard de dados com EX/MEM
        if (self.ex_mem.valido and self.ex_mem.controle.get('reg_write', False) and
            self.if_id.valido):
            
            if (self.ex_mem.rd != 0 and 
                (self.ex_mem.rd == self.if_id.rs1 or self.ex_mem.rd == self.if_id.rs2)):
                return True
        
        return False
    
    def forwarding(self, reg_num, estagio):
        """Implementa forwarding para resolver hazards"""
        valor = self.ler_registrador(reg_num)
        
        # Forward do estágio MEM/WB
        if (self.mem_wb.valido and self.mem_wb.controle.get('reg_write', False) and
            self.mem_wb.rd == reg_num and reg_num != 0):
            if self.mem_wb.controle.get('mem_to_reg', False):
                valor = self.mem_wb.mem_data
            else:
                valor = self.mem_wb.alu_result
        
        # Forward do estágio EX/MEM
        if (self.ex_mem.valido and self.ex_mem.controle.get('reg_write', False) and
            self.ex_mem.rd == reg_num and reg_num != 0):
            valor = self.ex_mem.alu_result
        
        return valor
    
    def estagio_if(self):
        """Estágio Instruction Fetch"""
        if self.stall:
            return
            
        try:
            # Buscar instrução da memória
            instrucao = self.memoria.ler_word(self.pc)
            
            # Preparar registrador IF/ID
            novo_if_id = PipelineRegister()
            novo_if_id.pc = self.pc
            novo_if_id.instrucao = instrucao
            novo_if_id.valido = True
            
            # Atualizar PC
            self.pc += 4
            
            return novo_if_id
            
        except:
            # End of program
            novo_if_id = PipelineRegister()
            novo_if_id.valido = False
            return novo_if_id
    
    def estagio_id(self):
        """Estágio Instruction Decode"""
        if not self.if_id.valido:
            return PipelineRegister()
        
        # Decodificar instrução
        try:
            instrucao_obj = self.decodificador.decodificar(self.if_id.instrucao)
            nome = instrucao_obj.obter_nome_instrucao()
        except:
            return PipelineRegister()
        
        # Preparar registrador ID/EX
        novo_id_ex = PipelineRegister()
        novo_id_ex.pc = self.if_id.pc
        novo_id_ex.instrucao = self.if_id.instrucao
        novo_id_ex.rs1 = getattr(instrucao_obj, 'rs1', 0)
        novo_id_ex.rs2 = getattr(instrucao_obj, 'rs2', 0)
        novo_id_ex.rd = getattr(instrucao_obj, 'rd', 0)
        novo_id_ex.imm = getattr(instrucao_obj, 'imm', 0)
        novo_id_ex.nome_instrucao = nome
        novo_id_ex.valido = True
        
        # Gerar sinais de controle
        novo_id_ex.controle = self.gerar_sinais_controle(nome)
        
        return novo_id_ex
    
    def gerar_sinais_controle(self, nome_instrucao):
        """Gera sinais de controle baseado no nome da instrução"""
        controle = {
            'reg_write': False,
            'mem_read': False,
            'mem_write': False,
            'mem_to_reg': False,
            'alu_src': False,
            'branch': False,
            'jump': False
        }
        
        # Instruções tipo R
        if nome_instrucao in ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'SLL', 'SRL', 'SRA', 'SLT', 'SLTU']:
            controle['reg_write'] = True
            
        # Instruções tipo I (aritméticas)
        elif nome_instrucao in ['ADDI', 'SLTI', 'SLTIU', 'XORI', 'ORI', 'ANDI', 'SLLI', 'SRLI', 'SRAI']:
            controle['reg_write'] = True
            controle['alu_src'] = True
            
        # Loads
        elif nome_instrucao in ['LW', 'LH', 'LHU', 'LB', 'LBU']:
            controle['reg_write'] = True
            controle['mem_read'] = True
            controle['mem_to_reg'] = True
            controle['alu_src'] = True
            
        # Stores
        elif nome_instrucao in ['SW', 'SH', 'SB']:
            controle['mem_write'] = True
            controle['alu_src'] = True
            
        # Branches
        elif nome_instrucao in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
            controle['branch'] = True
            
        # Upper immediate
        elif nome_instrucao in ['LUI', 'AUIPC']:
            controle['reg_write'] = True
            
        # Jumps
        elif nome_instrucao in ['JAL', 'JALR']:
            controle['reg_write'] = True
            controle['jump'] = True
        
        return controle
    
    def estagio_ex(self):
        """Estágio Execute"""
        if not self.id_ex.valido:
            return PipelineRegister()
        
        # Ler operandos com forwarding
        rs1_val = self.forwarding(self.id_ex.rs1, 'EX')
        rs2_val = self.forwarding(self.id_ex.rs2, 'EX')
        
        # Calcular resultado da ALU
        alu_result = self.calcular_alu(self.id_ex.nome_instrucao, rs1_val, rs2_val, self.id_ex.imm, self.id_ex.pc)
        
        # Preparar registrador EX/MEM
        novo_ex_mem = PipelineRegister()
        novo_ex_mem.pc = self.id_ex.pc
        novo_ex_mem.instrucao = self.id_ex.instrucao
        novo_ex_mem.rs2 = rs2_val  # Para stores
        novo_ex_mem.rd = self.id_ex.rd
        novo_ex_mem.alu_result = alu_result
        novo_ex_mem.controle = self.id_ex.controle.copy()
        novo_ex_mem.nome_instrucao = self.id_ex.nome_instrucao
        novo_ex_mem.valido = True
        
        # Verificar branches
        if self.id_ex.controle.get('branch', False):
            branch_taken = self.verificar_branch(self.id_ex.nome_instrucao, rs1_val, rs2_val)
            if branch_taken:
                self.pc = (self.id_ex.pc + self.id_ex.imm) & 0xFFFFFFFF
                self.flush = True
        
        # Verificar jumps
        if self.id_ex.controle.get('jump', False):
            if self.id_ex.nome_instrucao == 'JAL':
                novo_ex_mem.alu_result = self.id_ex.pc + 4
                self.pc = (self.id_ex.pc + self.id_ex.imm) & 0xFFFFFFFF
                self.flush = True
            elif self.id_ex.nome_instrucao == 'JALR':
                novo_ex_mem.alu_result = self.id_ex.pc + 4
                self.pc = (rs1_val + self.id_ex.imm) & 0xFFFFFFFE
                self.flush = True
        
        return novo_ex_mem
    
    def calcular_alu(self, nome, rs1_val, rs2_val, imm, pc):
        """Calcula resultado da ALU"""
        if nome == "ADD" or nome == "ADDI":
            return (rs1_val + (rs2_val if nome == "ADD" else imm)) & 0xFFFFFFFF
        elif nome == "SUB":
            return (rs1_val - rs2_val) & 0xFFFFFFFF
        elif nome == "AND" or nome == "ANDI":
            return rs1_val & (rs2_val if nome == "AND" else (imm & 0xFFFFFFFF))
        elif nome == "OR" or nome == "ORI":
            return rs1_val | (rs2_val if nome == "OR" else (imm & 0xFFFFFFFF))
        elif nome == "XOR" or nome == "XORI":
            return rs1_val ^ (rs2_val if nome == "XOR" else (imm & 0xFFFFFFFF))
        elif nome == "SLL" or nome == "SLLI":
            shift = (rs2_val if nome == "SLL" else imm) & 0x1F
            return (rs1_val << shift) & 0xFFFFFFFF
        elif nome == "SRL" or nome == "SRLI":
            shift = (rs2_val if nome == "SRL" else imm) & 0x1F
            return rs1_val >> shift
        elif nome == "SRA" or nome == "SRAI":
            shift = (rs2_val if nome == "SRA" else imm) & 0x1F
            if rs1_val & 0x80000000:
                return ((rs1_val >> shift) | (0xFFFFFFFF << (32 - shift))) & 0xFFFFFFFF
            else:
                return rs1_val >> shift
        elif nome == "SLT" or nome == "SLTI":
            rs1_signed = self._sinal_extendido_32(rs1_val)
            rs2_signed = self._sinal_extendido_32(rs2_val if nome == "SLT" else imm)
            return 1 if rs1_signed < rs2_signed else 0
        elif nome == "SLTU" or nome == "SLTIU":
            return 1 if rs1_val < (rs2_val if nome == "SLTU" else (imm & 0xFFFFFFFF)) else 0
        elif nome == "LUI":
            return imm & 0xFFFFFFFF
        elif nome == "AUIPC":
            return (pc + imm) & 0xFFFFFFFF
        elif nome in ["LW", "LH", "LHU", "LB", "LBU", "SW", "SH", "SB"]:
            return (rs1_val + imm) & 0xFFFFFFFF
        else:
            return 0
    
    def verificar_branch(self, nome, rs1_val, rs2_val):
        """Verifica se branch deve ser tomado"""
        if nome == "BEQ":
            return rs1_val == rs2_val
        elif nome == "BNE":
            return rs1_val != rs2_val
        elif nome == "BLT":
            return self._sinal_extendido_32(rs1_val) < self._sinal_extendido_32(rs2_val)
        elif nome == "BGE":
            return self._sinal_extendido_32(rs1_val) >= self._sinal_extendido_32(rs2_val)
        elif nome == "BLTU":
            return rs1_val < rs2_val
        elif nome == "BGEU":
            return rs1_val >= rs2_val
        return False
    
    def estagio_mem(self):
        """Estágio Memory Access"""
        if not self.ex_mem.valido:
            return PipelineRegister()
        
        # Preparar registrador MEM/WB
        novo_mem_wb = PipelineRegister()
        novo_mem_wb.pc = self.ex_mem.pc
        novo_mem_wb.instrucao = self.ex_mem.instrucao
        novo_mem_wb.rd = self.ex_mem.rd
        novo_mem_wb.alu_result = self.ex_mem.alu_result
        novo_mem_wb.controle = self.ex_mem.controle.copy()
        novo_mem_wb.nome_instrucao = self.ex_mem.nome_instrucao
        novo_mem_wb.valido = True
        
        # Acessar memória se necessário
        if self.ex_mem.controle.get('mem_read', False):
            endereco = self.ex_mem.alu_result
            if self.ex_mem.nome_instrucao == "LW":
                novo_mem_wb.mem_data = self.memoria.ler_word(endereco)
            elif self.ex_mem.nome_instrucao == "LH":
                valor = self.memoria.ler_halfword(endereco)
                if valor & 0x8000:
                    valor |= 0xFFFF0000
                novo_mem_wb.mem_data = valor
            elif self.ex_mem.nome_instrucao == "LHU":
                novo_mem_wb.mem_data = self.memoria.ler_halfword(endereco)
            elif self.ex_mem.nome_instrucao == "LB":
                valor = self.memoria.ler_byte(endereco)
                if valor & 0x80:
                    valor |= 0xFFFFFF00
                novo_mem_wb.mem_data = valor
            elif self.ex_mem.nome_instrucao == "LBU":
                novo_mem_wb.mem_data = self.memoria.ler_byte(endereco)
        
        elif self.ex_mem.controle.get('mem_write', False):
            endereco = self.ex_mem.alu_result
            valor = self.ex_mem.rs2
            if self.ex_mem.nome_instrucao == "SW":
                self.memoria.escrever_word(endereco, valor)
            elif self.ex_mem.nome_instrucao == "SH":
                self.memoria.escrever_halfword(endereco, valor & 0xFFFF)
            elif self.ex_mem.nome_instrucao == "SB":
                self.memoria.escrever_byte(endereco, valor & 0xFF)
        
        return novo_mem_wb
    
    def estagio_wb(self):
        """Estágio Write Back"""
        if not self.mem_wb.valido:
            return
        
        # Escrever resultado no registrador
        if self.mem_wb.controle.get('reg_write', False):
            if self.mem_wb.controle.get('mem_to_reg', False):
                self.escrever_registrador(self.mem_wb.rd, self.mem_wb.mem_data)
            else:
                self.escrever_registrador(self.mem_wb.rd, self.mem_wb.alu_result)
        
        self.instrucoes_executadas += 1
    
    def _sinal_extendido_32(self, valor):
        """Converte um valor de 32 bits para inteiro com sinal"""
        if valor & 0x80000000:
            return valor - 0x100000000
        return valor
    
    def imprimir_estado_pipeline(self):
        """Imprime estado atual do pipeline"""
        texto = f"\n=== Ciclo {self.ciclos + 1} ==="
        self.escrever_saida(texto)
        
        # Instruções em cada estágio
        texto = "Estágios do Pipeline:"
        self.escrever_saida(texto)
        
        texto = f"  IF: {'NOP' if not self.if_id.valido else self.if_id.nome_instrucao}"
        self.escrever_saida(texto)
        
        texto = f"  ID: {'NOP' if not self.id_ex.valido else self.id_ex.nome_instrucao}"
        self.escrever_saida(texto)
        
        texto = f"  EX: {'NOP' if not self.ex_mem.valido else self.ex_mem.nome_instrucao}"
        self.escrever_saida(texto)
        
        texto = f"  MEM: {'NOP' if not self.mem_wb.valido else self.mem_wb.nome_instrucao}"
        self.escrever_saida(texto)
        
        # Registradores
        texto = "\nRegistradores:"
        self.escrever_saida(texto)
        for i in range(0, 32, 8):
            linha = []
            for j in range(8):
                if i + j < 32:
                    reg_num = i + j
                    valor = self.registradores[reg_num]
                    linha.append(f"x{reg_num:2d}:{valor:08x}")
            texto = "  " + " ".join(linha)
            self.escrever_saida(texto)
        
        # Memória (apenas posições não-zero)
        texto = "\nMemória (posições preenchidas):"
        self.escrever_saida(texto)
        
        memoria_preenchida = []
        for endereco in range(0, self.memoria.tamanho, 4):
            try:
                valor = self.memoria.ler_word(endereco)
                if valor != 0:
                    memoria_preenchida.append((endereco, valor))
            except:
                pass
        
        if memoria_preenchida:
            for endereco, valor in memoria_preenchida:
                texto = f"  {endereco:08x}: {valor:08x}"
                self.escrever_saida(texto)
        else:
            texto = "  (nenhuma posição preenchida)"
            self.escrever_saida(texto)
        
        self.escrever_saida("")
    
    def executar_com_pipeline(self):
        """Executa programa com pipeline"""
        self.abrir_arquivo_saida()
        
        try:
            while True:
                # Imprimir estado antes do ciclo
                self.imprimir_estado_pipeline()
                
                # Executar estágios (ordem reversa para evitar conflitos)
                self.estagio_wb()
                novo_mem_wb = self.estagio_mem()
                novo_ex_mem = self.estagio_ex()
                novo_id_ex = self.estagio_id()
                novo_if_id = self.estagio_if()
                
                # Atualizar registradores de pipeline
                if not self.stall:
                    self.mem_wb = novo_mem_wb
                    self.ex_mem = novo_ex_mem
                    self.id_ex = novo_id_ex
                    
                    if self.flush:
                        # Flush pipeline em caso de branch/jump
                        self.if_id = PipelineRegister()
                        self.id_ex = PipelineRegister()
                        self.flush = False
                    else:
                        self.if_id = novo_if_id
                
                self.ciclos += 1
                
                # Verificar condições de parada
                if (not self.if_id.valido and not self.id_ex.valido and 
                    not self.ex_mem.valido and not self.mem_wb.valido):
                    break
                
                if self.ciclos > 1000:  # Limite de segurança
                    texto = "Limite de ciclos atingido!"
                    self.escrever_saida(texto)
                    break
            
            texto = f"\nExecução concluída:"
            self.escrever_saida(texto)
            texto = f"Ciclos totais: {self.ciclos}"
            self.escrever_saida(texto)
            texto = f"Instruções executadas: {self.instrucoes_executadas}"
            self.escrever_saida(texto)
            if self.instrucoes_executadas > 0:
                cpi = self.ciclos / self.instrucoes_executadas
                texto = f"CPI: {cpi:.2f}"
                self.escrever_saida(texto)
        
        finally:
            self.fechar_arquivo_saida()
    
    def carregar_arquivo_asm(self, nome_arquivo):
        """Carrega arquivo .asm e executa"""
        from assembler import RISCVAssembler
        
        try:
            with open(nome_arquivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            assembler = RISCVAssembler()
            instrucoes = assembler.assemblar(codigo)
            self.carregar_programa(instrucoes)
            
            print(f"Programa carregado: {len(instrucoes)} instruções")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            return False
    
    def carregar_arquivo_bin(self, nome_arquivo):
        """Carrega arquivo binário"""
        try:
            with open(nome_arquivo, 'rb') as f:
                dados = f.read()
            
            # Converter bytes para words de 32 bits
            instrucoes = []
            for i in range(0, len(dados), 4):
                if i + 3 < len(dados):
                    word = (dados[i] | (dados[i+1] << 8) | 
                           (dados[i+2] << 16) | (dados[i+3] << 24))
                    instrucoes.append(word)
            
            self.carregar_programa(instrucoes)
            print(f"Programa binário carregado: {len(instrucoes)} instruções")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar arquivo binário: {e}")
            return False
