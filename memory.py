"""
Implementação da memória do simulador RISC-V
"""

class Memoria:
    def __init__(self, tamanho=1024*1024):  # 1MB por padrão
        self.tamanho = tamanho
        self.dados = bytearray(tamanho)
    
    def ler_byte(self, endereco):
        """Lê um byte da memória"""
        if endereco >= self.tamanho:
            raise Exception(f"Acesso à memória fora dos limites: {endereco:08x}")
        return self.dados[endereco]
    
    def escrever_byte(self, endereco, valor):
        """Escreve um byte na memória"""
        if endereco >= self.tamanho:
            raise Exception(f"Acesso à memória fora dos limites: {endereco:08x}")
        self.dados[endereco] = valor & 0xFF
    
    def ler_halfword(self, endereco):
        """Lê uma halfword (16 bits) da memória"""
        if endereco % 2 != 0:
            raise Exception(f"Acesso desalinhado à halfword: {endereco:08x}")
        
        baixo = self.ler_byte(endereco)
        alto = self.ler_byte(endereco + 1)
        return baixo | (alto << 8)
    
    def escrever_halfword(self, endereco, valor):
        """Escreve uma halfword (16 bits) na memória"""
        if endereco % 2 != 0:
            raise Exception(f"Acesso desalinhado à halfword: {endereco:08x}")
        
        self.escrever_byte(endereco, valor & 0xFF)
        self.escrever_byte(endereco + 1, (valor >> 8) & 0xFF)
    
    def ler_word(self, endereco):
        """Lê uma word (32 bits) da memória"""
        if endereco % 4 != 0:
            raise Exception(f"Acesso desalinhado à word: {endereco:08x}")
        
        byte0 = self.ler_byte(endereco)
        byte1 = self.ler_byte(endereco + 1)
        byte2 = self.ler_byte(endereco + 2)
        byte3 = self.ler_byte(endereco + 3)
        
        return byte0 | (byte1 << 8) | (byte2 << 16) | (byte3 << 24)
    
    def escrever_word(self, endereco, valor):
        """Escreve uma word (32 bits) na memória"""
        if endereco % 4 != 0:
            raise Exception(f"Acesso desalinhado à word: {endereco:08x}")
        
        self.escrever_byte(endereco, valor & 0xFF)
        self.escrever_byte(endereco + 1, (valor >> 8) & 0xFF)
        self.escrever_byte(endereco + 2, (valor >> 16) & 0xFF)
        self.escrever_byte(endereco + 3, (valor >> 24) & 0xFF)
    
    def carregar_dados(self, endereco_inicial, dados):
        """Carrega dados na memória a partir de um endereço"""
        for i, byte in enumerate(dados):
            if endereco_inicial + i >= self.tamanho:
                break
            self.dados[endereco_inicial + i] = byte
    
    def limpar(self):
        """Limpa toda a memória"""
        self.dados = bytearray(self.tamanho)
    
    def dump(self, endereco_inicial=0, tamanho=256):
        """Faz dump de uma região da memória para debug"""
        linhas = []
        for i in range(0, tamanho, 16):
            endereco = endereco_inicial + i
            if endereco >= self.tamanho:
                break
            
            # Formato hexadecimal
            hex_bytes = []
            ascii_chars = []
            
            for j in range(16):
                if endereco + j < self.tamanho:
                    byte = self.dados[endereco + j]
                    hex_bytes.append(f"{byte:02x}")
                    ascii_chars.append(chr(byte) if 32 <= byte <= 126 else '.')
                else:
                    hex_bytes.append("  ")
                    ascii_chars.append(" ")
            
            hex_str = " ".join(hex_bytes[:8]) + "  " + " ".join(hex_bytes[8:])
            ascii_str = "".join(ascii_chars)
            
            linhas.append(f"{endereco:08x}: {hex_str} |{ascii_str}|")
        
        return "\n".join(linhas)
