"""
Decodificador de instruções RISC-V RV32I
"""

class Instrucao:
    def __init__(self, palavra):
        self.palavra = palavra
        self.opcode = palavra & 0x7F
        self.tipo = self._determinar_tipo()
        self._decodificar()
    
    def _determinar_tipo(self):
        """Determina o tipo da instrução baseado no opcode"""
        if self.opcode == 0b0110011:  # R-type
            return 'R'
        elif self.opcode in [0b0010011, 0b0000011, 0b1100111]:  # I-type
            return 'I'
        elif self.opcode == 0b0100011:  # S-type
            return 'S'
        elif self.opcode == 0b1100011:  # B-type
            return 'B'
        elif self.opcode in [0b0110111, 0b0010111]:  # U-type
            return 'U'
        elif self.opcode == 0b1101111:  # J-type
            return 'J'
        else:
            return 'UNKNOWN'
    
    def _decodificar(self):
        """Decodifica os campos da instrução"""
        if self.tipo == 'R':
            self.rd = (self.palavra >> 7) & 0x1F
            self.funct3 = (self.palavra >> 12) & 0x7
            self.rs1 = (self.palavra >> 15) & 0x1F
            self.rs2 = (self.palavra >> 20) & 0x1F
            self.funct7 = (self.palavra >> 25) & 0x7F
        
        elif self.tipo == 'I':
            self.rd = (self.palavra >> 7) & 0x1F
            self.funct3 = (self.palavra >> 12) & 0x7
            self.rs1 = (self.palavra >> 15) & 0x1F
            self.imm = self._sinal_extendido((self.palavra >> 20) & 0xFFF, 12)
        
        elif self.tipo == 'S':
            self.funct3 = (self.palavra >> 12) & 0x7
            self.rs1 = (self.palavra >> 15) & 0x1F
            self.rs2 = (self.palavra >> 20) & 0x1F
            imm_4_0 = (self.palavra >> 7) & 0x1F
            imm_11_5 = (self.palavra >> 25) & 0x7F
            self.imm = self._sinal_extendido((imm_11_5 << 5) | imm_4_0, 12)
        
        elif self.tipo == 'B':
            self.funct3 = (self.palavra >> 12) & 0x7
            self.rs1 = (self.palavra >> 15) & 0x1F
            self.rs2 = (self.palavra >> 20) & 0x1F
            imm_11 = (self.palavra >> 7) & 0x1
            imm_4_1 = (self.palavra >> 8) & 0xF
            imm_10_5 = (self.palavra >> 25) & 0x3F
            imm_12 = (self.palavra >> 31) & 0x1
            self.imm = self._sinal_extendido(
                (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1), 13)
        
        elif self.tipo == 'U':
            self.rd = (self.palavra >> 7) & 0x1F
            self.imm = self.palavra & 0xFFFFF000
        
        elif self.tipo == 'J':
            self.rd = (self.palavra >> 7) & 0x1F
            imm_19_12 = (self.palavra >> 12) & 0xFF
            imm_11 = (self.palavra >> 20) & 0x1
            imm_10_1 = (self.palavra >> 21) & 0x3FF
            imm_20 = (self.palavra >> 31) & 0x1
            self.imm = self._sinal_extendido(
                (imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1), 21)
    
    def _sinal_extendido(self, valor, bits):
        """Estende o sinal de um valor para 32 bits"""
        if valor & (1 << (bits - 1)):
            return valor | (0xFFFFFFFF << bits)
        return valor
    
    def obter_nome_instrucao(self):
        """Retorna o nome da instrução"""
        if self.tipo == 'R':
            if self.funct3 == 0b000:
                return "ADD" if self.funct7 == 0b0000000 else "SUB"
            elif self.funct3 == 0b001:
                return "SLL"
            elif self.funct3 == 0b010:
                return "SLT"
            elif self.funct3 == 0b011:
                return "SLTU"
            elif self.funct3 == 0b100:
                return "XOR"
            elif self.funct3 == 0b101:
                return "SRL" if self.funct7 == 0b0000000 else "SRA"
            elif self.funct3 == 0b110:
                return "OR"
            elif self.funct3 == 0b111:
                return "AND"
        
        elif self.tipo == 'I':
            if self.opcode == 0b0010011:  # Operações imediatas
                if self.funct3 == 0b000:
                    return "ADDI"
                elif self.funct3 == 0b010:
                    return "SLTI"
                elif self.funct3 == 0b011:
                    return "SLTIU"
                elif self.funct3 == 0b100:
                    return "XORI"
                elif self.funct3 == 0b110:
                    return "ORI"
                elif self.funct3 == 0b111:
                    return "ANDI"
                elif self.funct3 == 0b001:
                    return "SLLI"
                elif self.funct3 == 0b101:
                    return "SRLI" if (self.imm >> 10) & 1 == 0 else "SRAI"
            
            elif self.opcode == 0b0000011:  # Loads
                if self.funct3 == 0b000:
                    return "LB"
                elif self.funct3 == 0b001:
                    return "LH"
                elif self.funct3 == 0b010:
                    return "LW"
                elif self.funct3 == 0b100:
                    return "LBU"
                elif self.funct3 == 0b101:
                    return "LHU"
            
            elif self.opcode == 0b1100111:  # JALR
                return "JALR"
        
        elif self.tipo == 'S':
            if self.funct3 == 0b000:
                return "SB"
            elif self.funct3 == 0b001:
                return "SH"
            elif self.funct3 == 0b010:
                return "SW"
        
        elif self.tipo == 'B':
            if self.funct3 == 0b000:
                return "BEQ"
            elif self.funct3 == 0b001:
                return "BNE"
            elif self.funct3 == 0b100:
                return "BLT"
            elif self.funct3 == 0b101:
                return "BGE"
            elif self.funct3 == 0b110:
                return "BLTU"
            elif self.funct3 == 0b111:
                return "BGEU"
        
        elif self.tipo == 'U':
            if self.opcode == 0b0110111:
                return "LUI"
            elif self.opcode == 0b0010111:
                return "AUIPC"
        
        elif self.tipo == 'J':
            return "JAL"
        
        return "UNKNOWN"

class DecodificadorRISCV:
    def __init__(self):
        pass
    
    def decodificar(self, palavra_instrucao):
        """Decodifica uma palavra de instrução de 32 bits"""
        return Instrucao(palavra_instrucao)
    
    def e_valida(self, instrucao):
        """Verifica se a instrução é válida"""
        return instrucao.obter_nome_instrucao() != "UNKNOWN"
