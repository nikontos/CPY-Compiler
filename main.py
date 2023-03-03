import lex

if __name__ == '__main__':
    print("hi")
    test = lex.Lex('test.cpy')
    b = test.next_token()

    while b != "EOF":
        print("Token: " + b.recognised_string + " Line: " + str(b.line_number) + " Family: " + b.family + " Pos:" + str(
            test.position))
        print("The int number is :: " + str(int(b.recognised_string) + 420))
        b = test.next_token()



