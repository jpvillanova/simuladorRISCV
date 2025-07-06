"""
Assembler simples para RISC-V RV32I
Converte código assembly para instruções de máquina
"""

import re

class RISCVAssembler:
    def __init__(self):
        # Mapeamento de registradores
        self.registradores = {
            'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7,
            's0': 8, 'fp': 8, 's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
            's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
            't3': 28, 't4': 29, 't5': 30, 't6': 31
        }
        
        # Adicionar registradores x0-x31
        for i in range(32):
            self.registradores[f'x{i}'] = i
        
        # Labels
        self.labels = {}
        
        # Instruções implementadas
        self.opcodes = {
            # Tipo R
            'add': (0b0110011, 0b000, 0b0000000),
            'sub': (0b0110011, 0b000, 0b0100000),
            'sll': (0b0110011, 0b001, 0b0000000),
            'slt': (0b0110011, 0b010, 0b0000000),
            'sltu': (0b0110011, 0b011, 0b0000000),
            'xor': (0b0110011, 0b100, 0b0000000),
            'srl': (0b0110011, 0b101, 0b0000000),
            'sra': (0b0110011, 0b101, 0b0100000),
            'or': (0b0110011, 0b110, 0b0000000),
            'and': (0b0110011, 0b111, 0b0000000),
            
            # Tipo I
            'addi': (0b0010011, 0b000),
            'slti': (0b0010011, 0b010),
            'sltiu': (0b0010011, 0b011),
            'xori': (0b0010011, 0b100),
            'ori': (0b0010011, 0b110),
            'andi': (0b0010011, 0b111),
            'slli': (0b0010011, 0b001),
            'srli': (0b0010011, 0b101),
            'srai': (0b0010011, 0b101),
            
            # Loads
            'lb': (0b0000011, 0b000),
            'lh': (0b0000011, 0b001),
            'lw': (0b0000011, 0b010),
            'lbu': (0b0000011, 0b100),
            'lhu': (0b0000011, 0b101),
            
            # Stores
            'sb': (0b0100011, 0b000),
            'sh': (0b0100011, 0b001),
            'sw': (0b0100011, 0b010),
            
            # Branches
            'beq': (0b1100011, 0b000),
            'bne': (0b1100011, 0b001),
            'blt': (0b1100011, 0b100),
            'bge': (0b1100011, 0b101),
            'bltu': (0b1100011, 0b110),
            'bgeu': (0b1100011, 0b111),
            
            # Upper immediate
            'lui': (0b0110111,),
            'auipc': (0b0010111,),
            
            # Jumps
            'jal': (0b1101111,),
            'jalr': (0b1100111, 0b000),
        }
        
        # Pseudo-instruções (traduzidas para instruções reais)
        self.pseudo_instrucoes = {
            'ble': 'bge',  # ble rs1, rs2, offset -> bge rs2, rs1, offset
            'bgt': 'blt',  # bgt rs1, rs2, offset -> blt rs2, rs1, offset
            'bgtu': 'bltu', # bgtu rs1, rs2, offset -> bltu rs2, rs1, offset
            'bleu': 'bgeu', # bleu rs1, rs2, offset -> bgeu rs2, rs1, offset
            'nop': 'addi',  # nop -> addi x0, x0, 0
            'li': 'addi',   # li rd, imm -> addi rd, x0, imm
            'mv': 'add',    # mv rd, rs -> add rd, rs, x0
        }
    
    def _parsear_registrador(self, reg_str):
        """Converte string de registrador para número"""
        reg_str = reg_str.strip().lower()
        if reg_str in self.registradores:
            return self.registradores[reg_str]
        raise ValueError(f"Registrador inválido: {reg_str}")
    
    def _parsear_imediato(self, imm_str, endereco_atual=0):
        """Converte string de imediato para número"""
        imm_str = imm_str.strip()
        
        # Verificar se é um label
        if imm_str in self.labels:
            return self.labels[imm_str] - endereco_atual
        
        # Hexadecimal
        if imm_str.startswith('0x') or imm_str.startswith('0X'):
            return int(imm_str, 16)
        
        # Binário
        if imm_str.startswith('0b') or imm_str.startswith('0B'):
            return int(imm_str, 2)
        
        # Decimal
        return int(imm_str)
    
    def _gerar_tipo_r(self, opcode, funct3, funct7, rd, rs1, rs2):
        """Gera instrução tipo R"""
        return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    def _gerar_tipo_i(self, opcode, funct3, rd, rs1, imm):
        """Gera instrução tipo I"""
        imm = imm & 0xFFF  # 12 bits
        return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    def _gerar_tipo_s(self, opcode, funct3, rs1, rs2, imm):
        """Gera instrução tipo S"""
        imm = imm & 0xFFF  # 12 bits
        imm_11_5 = (imm >> 5) & 0x7F
        imm_4_0 = imm & 0x1F
        return (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_0 << 7) | opcode
    
    def _gerar_tipo_b(self, opcode, funct3, rs1, rs2, imm):
        """Gera instrução tipo B"""
        imm = imm & 0x1FFF  # 13 bits (mas bit 0 é sempre 0)
        imm_12 = (imm >> 12) & 0x1
        imm_11 = (imm >> 11) & 0x1
        imm_10_5 = (imm >> 5) & 0x3F
        imm_4_1 = (imm >> 1) & 0xF
        return (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode
    
    def _gerar_tipo_u(self, opcode, rd, imm):
        """Gera instrução tipo U"""
        imm = imm & 0xFFFFF000  # 20 bits superiores
        return imm | (rd << 7) | opcode
    
    def _gerar_tipo_j(self, opcode, rd, imm):
        """Gera instrução tipo J"""
        imm = imm & 0x1FFFFF  # 21 bits
        imm_20 = (imm >> 20) & 0x1
        imm_19_12 = (imm >> 12) & 0xFF
        imm_11 = (imm >> 11) & 0x1
        imm_10_1 = (imm >> 1) & 0x3FF
        return (imm_20 << 31) | (imm_19_12 << 12) | (imm_11 << 20) | (imm_10_1 << 21) | (rd << 7) | opcode
    
    def _primeira_passada(self, linhas):
        """Primeira passada: encontrar labels"""
        endereco = 0
        for linha in linhas:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue
            
            if linha.endswith(':'):
                # É um label
                label = linha[:-1].strip()
                self.labels[label] = endereco
            else:
                # É uma instrução
                endereco += 4
    
    def _segunda_passada(self, linhas):
        """Segunda passada: gerar código de máquina"""
        instrucoes = []
        endereco = 0
        
        for linha in linhas:
            linha = linha.strip()
            
            # Ignorar linhas vazias e comentários
            if not linha or linha.startswith('#'):
                continue
            
            # Ignorar labels
            if linha.endswith(':'):
                continue
            
            # Remover comentários inline
            if '#' in linha:
                linha = linha[:linha.index('#')].strip()
            
            # Parsear instrução
            try:
                instrucao = self._parsear_instrucao(linha, endereco)
                instrucoes.append(instrucao)
                endereco += 4
            except Exception as e:
                raise ValueError(f"Erro na linha '{linha}': {e}")
        
        return instrucoes
    
    def _parsear_instrucao(self, linha, endereco):
        """Parseia uma linha de instrução"""
        # Dividir em tokens
        tokens = re.split(r'[,\s]+', linha.strip())
        tokens = [t for t in tokens if t]  # Remover tokens vazios
        
        if not tokens:
            raise ValueError("Linha vazia")
        
        nome_instr = tokens[0].lower()
        
        # Verificar se é uma pseudo-instrução
        if nome_instr in self.pseudo_instrucoes:
            return self._expandir_pseudo_instrucao(nome_instr, tokens, endereco)
        
        if nome_instr not in self.opcodes:
            raise ValueError(f"Instrução desconhecida: {nome_instr}")
        
        info_opcode = self.opcodes[nome_instr]
        
        # Tipo R
        if nome_instr in ['add', 'sub', 'sll', 'slt', 'sltu', 'xor', 'srl', 'sra', 'or', 'and']:
            if len(tokens) != 4:
                raise ValueError(f"Instrução {nome_instr} requer 3 operandos")
            
            rd = self._parsear_registrador(tokens[1])
            rs1 = self._parsear_registrador(tokens[2])
            rs2 = self._parsear_registrador(tokens[3])
            
            opcode, funct3, funct7 = info_opcode
            return self._gerar_tipo_r(opcode, funct3, funct7, rd, rs1, rs2)
        
        # Tipo I (operações imediatas)
        elif nome_instr in ['addi', 'slti', 'sltiu', 'xori', 'ori', 'andi']:
            if len(tokens) != 4:
                raise ValueError(f"Instrução {nome_instr} requer 3 operandos")
            
            rd = self._parsear_registrador(tokens[1])
            rs1 = self._parsear_registrador(tokens[2])
            imm = self._parsear_imediato(tokens[3], endereco)
            
            opcode, funct3 = info_opcode
            return self._gerar_tipo_i(opcode, funct3, rd, rs1, imm)
        
        # Shifts imediatos
        elif nome_instr in ['slli', 'srli', 'srai']:
            if len(tokens) != 4:
                raise ValueError(f"Instrução {nome_instr} requer 3 operandos")
            
            rd = self._parsear_registrador(tokens[1])
            rs1 = self._parsear_registrador(tokens[2])
            shamt = self._parsear_imediato(tokens[3], endereco) & 0x1F
            
            opcode, funct3 = info_opcode
            if nome_instr == 'srai':
                shamt |= 0x400  # Bit 10 para distinguir de SRLI
            return self._gerar_tipo_i(opcode, funct3, rd, rs1, shamt)
        
        # Loads
        elif nome_instr in ['lb', 'lh', 'lw', 'lbu', 'lhu']:
            if len(tokens) != 3:
                raise ValueError(f"Instrução {nome_instr} requer 2 operandos")
            
            rd = self._parsear_registrador(tokens[1])
            
            # Parsear offset(base)
            operando = tokens[2]
            if '(' in operando and ')' in operando:
                offset_str = operando[:operando.index('(')]
                base_str = operando[operando.index('(')+1:operando.index(')')]
                
                offset = self._parsear_imediato(offset_str, endereco) if offset_str else 0
                rs1 = self._parsear_registrador(base_str)
            else:
                raise ValueError(f"Formato inválido para load: {operando}")
            
            opcode, funct3 = info_opcode
            return self._gerar_tipo_i(opcode, funct3, rd, rs1, offset)
        
        # Stores
        elif nome_instr in ['sb', 'sh', 'sw']:
            if len(tokens) != 3:
                raise ValueError(f"Instrução {nome_instr} requer 2 operandos")
            
            rs2 = self._parsear_registrador(tokens[1])
            
            # Parsear offset(base)
            operando = tokens[2]
            if '(' in operando and ')' in operando:
                offset_str = operando[:operando.index('(')]
                base_str = operando[operando.index('(')+1:operando.index(')')]
                
                offset = self._parsear_imediato(offset_str, endereco) if offset_str else 0
                rs1 = self._parsear_registrador(base_str)
            else:
                raise ValueError(f"Formato inválido para store: {operando}")
            
            opcode, funct3 = info_opcode
            return self._gerar_tipo_s(opcode, funct3, rs1, rs2, offset)
        
        # Branches
        elif nome_instr in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']:
            if len(tokens) != 4:
                raise ValueError(f"Instrução {nome_instr} requer 3 operandos")
            
            rs1 = self._parsear_registrador(tokens[1])
            rs2 = self._parsear_registrador(tokens[2])
            offset = self._parsear_imediato(tokens[3], endereco)
            
            opcode, funct3 = info_opcode
            return self._gerar_tipo_b(opcode, funct3, rs1, rs2, offset)
        
        # Upper immediate
        elif nome_instr in ['lui', 'auipc']:
            if len(tokens) != 3:
                raise ValueError(f"Instrução {nome_instr} requer 2 operandos")
            
            rd = self._parsear_registrador(tokens[1])
            imm = self._parsear_imediato(tokens[2], endereco)
            
            opcode = info_opcode[0]
            return self._gerar_tipo_u(opcode, rd, imm)
        
        # JAL
        elif nome_instr == 'jal':
            if len(tokens) == 2:
                # JAL offset (rd implícito = ra)
                rd = 1  # ra
                offset = self._parsear_imediato(tokens[1], endereco)
            elif len(tokens) == 3:
                # JAL rd, offset
                rd = self._parsear_registrador(tokens[1])
                offset = self._parsear_imediato(tokens[2], endereco)
            else:
                raise ValueError("Instrução JAL requer 1 ou 2 operandos")
            
            opcode = info_opcode[0]
            return self._gerar_tipo_j(opcode, rd, offset)
        
        # JALR
        elif nome_instr == 'jalr':
            if len(tokens) == 2:
                # JALR rs1 (rd implícito = ra, offset = 0)
                rd = 1  # ra
                rs1 = self._parsear_registrador(tokens[1])
                offset = 0
            elif len(tokens) == 3:
                # JALR rd, rs1 ou JALR rs1, offset
                try:
                    rd = self._parsear_registrador(tokens[1])
                    rs1 = self._parsear_registrador(tokens[2])
                    offset = 0
                except:
                    rd = 1  # ra
                    rs1 = self._parsear_registrador(tokens[1])
                    offset = self._parsear_imediato(tokens[2], endereco)
            elif len(tokens) == 4:
                # JALR rd, rs1, offset
                rd = self._parsear_registrador(tokens[1])
                rs1 = self._parsear_registrador(tokens[2])
                offset = self._parsear_imediato(tokens[3], endereco)
            else:
                raise ValueError("Instrução JALR requer 1, 2 ou 3 operandos")
            
            opcode, funct3 = info_opcode
            return self._gerar_tipo_i(opcode, funct3, rd, rs1, offset)
        
        else:
            raise ValueError(f"Instrução não implementada: {nome_instr}")
    
    def _expandir_pseudo_instrucao(self, nome_instr, tokens, endereco):
        """Expande pseudo-instruções para instruções reais"""
        if nome_instr == 'ble':
            # ble rs1, rs2, offset -> bge rs2, rs1, offset
            if len(tokens) != 4:
                raise ValueError(f"Instrução {nome_instr} requer 3 operandos")
            
            rs1 = self._parsear_registrador(tokens[1])
            rs2 = self._parsear_registrador(tokens[2])
            offset = self._parsear_imediato(tokens[3], endereco)
            
            # Trocar rs1 e rs2 e usar bge
            opcode, funct3 = self.opcodes['bge']
            return self._gerar_tipo_b(opcode, funct3, rs2, rs1, offset)
        
        elif nome_instr == 'bgt':
            # bgt rs1, rs2, offset -> blt rs2, rs1, offset
            if len(tokens) != 4:
                raise ValueError(f"Instrução {nome_instr} requer 3 operandos")
            
            rs1 = self._parsear_registrador(tokens[1])
            rs2 = self._parsear_registrador(tokens[2])
            offset = self._parsear_imediato(tokens[3], endereco)
            
            # Trocar rs1 e rs2 e usar blt
            opcode, funct3 = self.opcodes['blt']
            return self._gerar_tipo_b(opcode, funct3, rs2, rs1, offset)
        
        elif nome_instr == 'bgtu':
            # bgtu rs1, rs2, offset -> bltu rs2, rs1, offset
            if len(tokens) != 4:
                raise ValueError(f"Instrução {nome_instr} requer 3 operandos")
            
            rs1 = self._parsear_registrador(tokens[1])
            rs2 = self._parsear_registrador(tokens[2])
            offset = self._parsear_imediato(tokens[3], endereco)
            
            # Trocar rs1 e rs2 e usar bltu
            opcode, funct3 = self.opcodes['bltu']
            return self._gerar_tipo_b(opcode, funct3, rs2, rs1, offset)
        
        elif nome_instr == 'bleu':
            # bleu rs1, rs2, offset -> bgeu rs2, rs1, offset
            if len(tokens) != 4:
                raise ValueError(f"Instrução {nome_instr} requer 3 operandos")
            
            rs1 = self._parsear_registrador(tokens[1])
            rs2 = self._parsear_registrador(tokens[2])
            offset = self._parsear_imediato(tokens[3], endereco)
            
            # Trocar rs1 e rs2 e usar bgeu
            opcode, funct3 = self.opcodes['bgeu']
            return self._gerar_tipo_b(opcode, funct3, rs2, rs1, offset)
        
        elif nome_instr == 'nop':
            # nop -> addi x0, x0, 0
            opcode, funct3 = self.opcodes['addi']
            return self._gerar_tipo_i(opcode, funct3, 0, 0, 0)
        
        elif nome_instr == 'li':
            # li rd, imm -> addi rd, x0, imm
            if len(tokens) != 3:
                raise ValueError(f"Instrução {nome_instr} requer 2 operandos")
            
            rd = self._parsear_registrador(tokens[1])
            imm = self._parsear_imediato(tokens[2], endereco)
            
            opcode, funct3 = self.opcodes['addi']
            return self._gerar_tipo_i(opcode, funct3, rd, 0, imm)
        
        elif nome_instr == 'mv':
            # mv rd, rs -> add rd, rs, x0
            if len(tokens) != 3:
                raise ValueError(f"Instrução {nome_instr} requer 2 operandos")
            
            rd = self._parsear_registrador(tokens[1])
            rs = self._parsear_registrador(tokens[2])
            
            opcode, funct3, funct7 = self.opcodes['add']
            return self._gerar_tipo_r(opcode, funct3, funct7, rd, rs, 0)
        
        else:
            raise ValueError(f"Pseudo-instrução não implementada: {nome_instr}")
    
    def assemblar(self, codigo_assembly):
        """Assembla código assembly para instruções de máquina"""
        self.labels = {}
        
        # Dividir em linhas
        linhas = codigo_assembly.split('\n')
        
        # Primeira passada: encontrar labels
        self._primeira_passada(linhas)
        
        # Segunda passada: gerar código
        instrucoes = self._segunda_passada(linhas)
        
        return instrucoes
