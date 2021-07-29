from lark import Lark

parser = Lark(r"""
        root: test_token | "dummy"
        
        test_token: "Top of one " words "batting"
        
        words: (WORD WS)* WORD

        %import common.WORD
        %import common.WS
        %ignore WS
        """, start='root', debug=True, lexer='dynamic_complete',
              ambiguity='explicit')

result = parser.parse("Top of one Philly Pies batting")

print(result)
