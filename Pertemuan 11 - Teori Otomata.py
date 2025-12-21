import sys

# ==================== AST Node Classes ====================

class NumberNode:
    def __init__(self, token):
        self.value = float(token.value) if '.' in token.value else int(token.value)
        self.token = token
    
    def __repr__(self):
        return f"NumberNode({self.value})"


class BinOpNode:
    def __init__(self, left, op_token, right):
        self.left = left
        self.op = op_token.type
        self.op_token = op_token
        self.right = right
    
    def __repr__(self):
        return f"BinOpNode({self.op_token.value}, {self.left}, {self.right})"


# ==================== Token Classes ====================

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


# ==================== Lexer ====================

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    
    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def integer(self):
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token('FLOAT', result)
        
        return Token('INTEGER', result)
    
    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isdigit():
                return self.integer()
            
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
            
            raise Exception(f"Invalid character: {self.current_char}")
        
        return Token('EOF', None)


# ==================== Parser ====================

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self):
        raise Exception("Invalid syntax")
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    
    def factor(self):
        """factor : INTEGER | FLOAT | LPAREN expr RPAREN"""
        token = self.current_token
        
        if token.type in ('INTEGER', 'FLOAT'):
            self.eat(token.type)
            return NumberNode(token)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        else:
            self.error()
    
    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()
        
        while self.current_token.type in ('MUL', 'DIV'):
            op_token = self.current_token
            self.eat(op_token.type)
            right = self.factor()
            node = BinOpNode(node, op_token, right)
        
        return node
    
    def expr(self):
        """expr : term ((PLUS | MINUS) term)*"""
        node = self.term()
        
        while self.current_token.type in ('PLUS', 'MINUS'):
            op_token = self.current_token
            self.eat(op_token.type)
            right = self.term()
            node = BinOpNode(node, op_token, right)
        
        return node
    
    def parse(self):
        return self.expr()


# ==================== Main Function ====================

def main():
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = input("Expression: ")
    
    lexer = Lexer(text)
    parser = Parser(lexer)
    
    try:
        ast = parser.parse()
        print("\nAST Structure:")
        print(ast)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()