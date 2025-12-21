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
        return Token('INT', int(result))
    
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


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self, message="Syntax error"):
        raise Exception(f"{message} pada token: {self.current_token}")
    
    def eat(self, token_type):
        """Mengonsumsi token jika sesuai, atau error"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")
    
    def factor(self):
        """factor : INT | LPAREN expr RPAREN"""
        token = self.current_token
        
        if token.type == 'INT':
            self.eat('INT')
            return True
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            # Parse ekspresi di dalam kurung
            if not self.expr():
                return False
            self.eat('RPAREN')
            return True
        else:
            self.error("Expected INT or LPAREN")
            return False
    
    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        # Parse faktor pertama
        if not self.factor():
            return False
        
        # Parse faktor berikutnya dengan operator * atau /
        while self.current_token.type in ('MUL', 'DIV'):
            self.eat(self.current_token.type)
            if not self.factor():
                return False
        
        return True
    
    def expr(self):
        """expr : term ((PLUS | MINUS) term)*"""
        # Parse term pertama
        if not self.term():
            return False
        
        # Parse term berikutnya dengan operator + atau -
        while self.current_token.type in ('PLUS', 'MINUS'):
            self.eat(self.current_token.type)
            if not self.term():
                return False
        
        return True
    
    def parse(self):
        """Mulai parsing dari root grammar (expr)"""
        try:
            result = self.expr()
            # Pastikan semua token sudah diproses
            if self.current_token.type != 'EOF':
                self.error("Unexpected tokens at the end")
                return False
            return result
        except Exception as e:
            print(f"Parsing error: {e}")
            return False


def validate_expression(expression):
    """Fungsi untuk memvalidasi ekspresi aritmatika"""
    print(f"Validasi: '{expression}'")
    
    try:
        lexer = Lexer(expression)
        parser = Parser(lexer)
        
        if parser.parse():
            print("✅ Valid\n")
            return True
        else:
            print("❌ Invalid\n")
            return False
    except Exception as e:
        print(f"❌ Invalid - Error: {e}\n")
        return False


# Test cases
if __name__ == "__main__":
    print("=" * 50)
    print("VALIDASI EKSPRESI ARITMATIKA")
    print("=" * 50)
    
    # Test case 1: Valid
    test1 = "10 + 2 * (5 - 3)"
    validate_expression(test1)
    
    # Test case 2: Invalid
    test2 = "10 + * "
    validate_expression(test2)
    
    # Test case 3: Valid
    test3 = "(10 + 2) * 5"
    validate_expression(test3)
    
    # Test case 4: Valid - nested parentheses
    test4 = "((2 + 3) * (4 - 1)) / 2"
    validate_expression(test4)
    
    # Test case 5: Invalid - missing operand
    test5 = "10 + "
    validate_expression(test5)
    
    # Test case 6: Invalid - unmatched parentheses
    test6 = "10 + (2 * 3"
    validate_expression(test6)
    
    # Test case 7: Valid - complex expression
    test7 = "1 + 2 * 3 - 4 / 2"
    validate_expression(test7)
    
    # Test case 8: Invalid - two operators in a row
    test8 = "10 * * 2"
    validate_expression(test8)
    
    # Test case 9: Valid - multiple parentheses
    test9 = "((1 + 2) * 3) - (4 / (2 + 2))"
    validate_expression(test9)
    
    # Test case 10: Invalid - empty parentheses
    test10 = "10 + ()"
    validate_expression(test10)