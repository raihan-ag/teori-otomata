# ==================== TOKEN TYPES ====================
TT_INT        = 'INT'
TT_FLOAT      = 'FLOAT'
TT_PLUS       = 'PLUS'
TT_MINUS      = 'MINUS'
TT_MUL        = 'MUL'
TT_DIV        = 'DIV'
TT_LPAREN     = 'LPAREN'
TT_RPAREN     = 'RPAREN'
TT_IDENTIFIER = 'IDENTIFIER'
TT_EQ         = 'EQ'          # Token untuk assignment '='
TT_EOF        = 'EOF'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"


# ==================== LEXER ====================

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
        
        # Cek apakah ada titik desimal
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token(TT_FLOAT, float(result))
        
        return Token(TT_INT, int(result))
    
    def identifier(self):
        """Baca identifier (nama variabel)"""
        result = ''
        # Karakter pertama harus huruf atau underscore
        if self.current_char and (self.current_char.isalpha() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Karakter berikutnya bisa huruf, angka, atau underscore
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        return Token(TT_IDENTIFIER, result)
    
    def get_next_token(self):
        """Tokenizer (Lexical Analyzer)"""
        while self.current_char:
            # Lewati spasi
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Integer atau float
            if self.current_char.isdigit():
                return self.integer()
            
            # Identifier (dimulai dengan huruf atau underscore)
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            # Operator dan tanda kurung
            if self.current_char == '+':
                self.advance()
                return Token(TT_PLUS, '+')
            
            if self.current_char == '-':
                self.advance()
                return Token(TT_MINUS, '-')
            
            if self.current_char == '*':
                self.advance()
                return Token(TT_MUL, '*')
            
            if self.current_char == '/':
                self.advance()
                return Token(TT_DIV, '/')
            
            if self.current_char == '(':
                self.advance()
                return Token(TT_LPAREN, '(')
            
            if self.current_char == ')':
                self.advance()
                return Token(TT_RPAREN, ')')
            
            if self.current_char == '=':
                self.advance()
                return Token(TT_EQ, '=')
            
            # Jika karakter tidak dikenali
            raise Exception(f"Karakter tidak valid: '{self.current_char}'")
        
        # End of file
        return Token(TT_EOF, None)


# ==================== AST NODE CLASSES ====================

class NumberNode:
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __repr__(self):
        return f"NumberNode({self.value})"


class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
    
    def __repr__(self):
        return f"BinOpNode({self.op_token.value}, {self.left_node}, {self.right_node})"


class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node
    
    def __repr__(self):
        return f"VarAssignNode({self.var_name_token.value}, {self.value_node})"


class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token
    
    def __repr__(self):
        return f"VarAccessNode({self.var_name_token.value})"


# ==================== PARSER ====================

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
    
    def atom(self):
        """atom : INT | FLOAT | IDENTIFIER | LPAREN expr RPAREN"""
        token = self.current_token
        
        if token.type == TT_INT or token.type == TT_FLOAT:
            self.eat(token.type)
            return NumberNode(token)
        
        elif token.type == TT_IDENTIFIER:
            self.eat(TT_IDENTIFIER)
            return VarAccessNode(token)
        
        elif token.type == TT_LPAREN:
            self.eat(TT_LPAREN)
            expr_node = self.expr()
            self.eat(TT_RPAREN)
            return expr_node
        
        else:
            self.error("Expected INT, FLOAT, IDENTIFIER, or LPAREN")
    
    def factor(self):
        """factor : (PLUS | MINUS) factor | atom"""
        token = self.current_token
        
        if token.type in (TT_PLUS, TT_MINUS):
            self.eat(token.type)
            factor_node = self.factor()
            # Untuk unary minus/plus, kita buat BinOpNode dengan 0
            zero_token = Token(TT_INT, 0)
            zero_node = NumberNode(zero_token)
            return BinOpNode(zero_node, token, factor_node)
        
        return self.atom()
    
    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()
        
        while self.current_token.type in (TT_MUL, TT_DIV):
            op_token = self.current_token
            self.eat(op_token.type)
            right = self.factor()
            node = BinOpNode(node, op_token, right)
        
        return node
    
    def expr(self):
        """expr : term ((PLUS | MINUS) term)*"""
        node = self.term()
        
        while self.current_token.type in (TT_PLUS, TT_MINUS):
            op_token = self.current_token
            self.eat(op_token.type)
            right = self.term()
            node = BinOpNode(node, op_token, right)
        
        return node
    
    def statement(self):
        """statement : IDENTIFIER EQ expr | expr"""
        # Lookahead untuk membedakan assignment vs access
        if self.current_token.type == TT_IDENTIFIER:
            var_name_token = self.current_token
            
            # Cek token berikutnya tanpa mengonsumsinya
            temp_pos = self.lexer.pos
            temp_char = self.lexer.current_char
            temp_token = self.lexer.get_next_token()  # Token sementara
            
            # Reset lexer ke posisi sebelumnya
            self.lexer.pos = temp_pos
            self.lexer.current_char = temp_char
            
            # Jika token berikutnya adalah '=', ini adalah assignment
            if temp_token.type == TT_EQ:
                self.eat(TT_IDENTIFIER)
                self.eat(TT_EQ)
                expr_node = self.expr()
                return VarAssignNode(var_name_token, expr_node)
        
        # Jika bukan assignment, parse sebagai ekspresi biasa
        return self.expr()
    
    def parse(self):
        """Parse statement"""
        try:
            ast = self.statement()
            # Pastikan semua token sudah diproses
            if self.current_token.type != TT_EOF:
                self.error("Unexpected tokens at the end")
            return ast
        except Exception as e:
            print(f"Parsing error: {e}")
            return None


# ==================== TESTING ====================

def test_lexer(text):
    """Test lexer untuk menampilkan token list"""
    print(f"\nTokenizing: '{text}'")
    lexer = Lexer(text)
    tokens = []
    
    while True:
        token = lexer.get_next_token()
        if token.type == TT_EOF:
            break
        tokens.append(token)
    
    for token in tokens:
        print(f"  {token}")

def test_parser(text):
    """Test parser untuk menghasilkan AST"""
    print(f"\nParsing: '{text}'")
    
    try:
        lexer = Lexer(text)
        parser = Parser(lexer)
        ast = parser.parse()
        
        if ast:
            print(f"AST: {ast}")
            return True
        else:
            print("❌ Failed to parse")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("LEXER & PARSER DENGAN VARIABLE ASSIGNMENT")
    print("=" * 60)
    
    # Test Lexer
    print("\n" + "="*30 + " LEXER TESTS " + "="*30)
    test_lexer("a = 100")
    test_lexer("x = 10 + y * 2")
    test_lexer("_var123 = (a + b) * c")
    test_lexer("3.14 + 2.5")
    
    # Test Parser
    print("\n" + "="*30 + " PARSER TESTS " + "="*30)
    
    # Test 1: Simple assignment
    print("\n1. Simple Assignment:")
    test_parser("a = 100")
    
    # Test 2: Assignment dengan ekspresi
    print("\n2. Assignment dengan Ekspresi:")
    test_parser("x = 10 + 20")
    
    # Test 3: Access variable dalam ekspresi
    print("\n3. Access Variable:")
    test_parser("a + 5")
    
    # Test 4: Assignment dengan variable lain
    print("\n4. Assignment dengan Variable:")
    test_parser("y = x * 2")
    
    # Test 5: Complex expression
    print("\n5. Complex Expression:")
    test_parser("result = (a + b) * (c - d) / 2")
    
    # Test 6: Multiple operations
    print("\n6. Multiple Operations:")
    test_parser("total = price * quantity + tax")
    
    # Test 7: Float numbers
    print("\n7. Float Numbers:")
    test_parser("pi = 3.14")
    test_parser("radius = 5.0")
    test_parser("area = pi * radius * radius")
    
    # Test 8: Variable names dengan underscore
    print("\n8. Variable dengan Underscore:")
    test_parser("_temp = _value1 + _value2")
    
    # Test 9: Error cases
    print("\n9. Error Cases:")
    test_parser("= 100")  # Missing identifier
    test_parser("a = ")   # Missing value
    test_parser("123 = x") # Number sebagai identifier