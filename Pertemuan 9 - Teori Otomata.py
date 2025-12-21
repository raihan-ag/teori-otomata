class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    
    def advance(self):
        """Pindah ke karakter berikutnya"""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
    
    def skip_whitespace(self):
        """Lewati spasi, tab, newline"""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def integer(self):
        """Baca integer multi-digit"""
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token('INTEGER', int(result))
    
    def get_next_token(self):
        """Tokenizer (Lexical Analyzer)"""
        while self.current_char:
            # Lewati spasi
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Integer multi-digit
            if self.current_char.isdigit():
                return self.integer()
            
            # Operator dan tanda kurung
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+')
            
            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-')
            
            if self.current_char == '*':
                self.advance()
                return Token('MUL', '*')
            
            if self.current_char == '/':
                self.advance()
                return Token('DIV', '/')
            
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(')
            
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')
            
            # Jika karakter tidak dikenali
            raise Exception(f"Karakter tidak valid: '{self.current_char}'")
        
        # End of file
        return Token('EOF', None)


def tokenize_expression(expression):
    """Fungsi untuk menghasilkan list token dari ekspresi"""
    lexer = Lexer(expression)
    tokens = []
    
    while True:
        token = lexer.get_next_token()
        tokens.append(token)
        if token.type == 'EOF':
            break
    
    # Hapus token EOF dari output
    return tokens[:-1]


# Test dengan contoh input
if __name__ == "__main__":
    test_expression = "(10 + 2 ) * 5"
    print(f"Input: '{test_expression}'")
    print("Output Token List:")
    
    tokens = tokenize_expression(test_expression)
    for token in tokens:
        print(token)
    
    # Contoh output:
    # Token(LPAREN, '(')
    # Token(INTEGER, 10)
    # Token(PLUS, '+')
    # Token(INTEGER, 2)
    # Token(RPAREN, ')')
    # Token(MUL, '*')
    # Token(INTEGER, 5)