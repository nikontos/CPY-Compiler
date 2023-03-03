import lex

if __name__ == '__main__':
    print("hi")
    test = lex.Lex('test.cpy')
    b = test.next_token()

    print("Token: " + b.recognised_string + " Line: " + str(b.line_number) + " Family: " + b.family)
    b = test.next_token()
    print("Token: " + b.recognised_string + " Line: " + str(b.line_number) + " Family: " + b.family)

