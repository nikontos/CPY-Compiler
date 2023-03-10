import os.path
import string


class Token:
    recognised_string = ''
    family = ''
    line_number = 1

    def __init__(self, recognised_string, family, line_number):
        self.recognised_string = recognised_string
        self.family = family
        self.line_number = line_number

    # def __init__(self):
    #    pass

    def __str__(self):
        print_at_line = "at line"
        print(f"{self.recognised_string : <30} {self.family :<25} {print_at_line: <7} {self.line_number: >4}")
        pass


class Lex:
    state = ''
    digits = string.digits
    keywords = ['if', 'while', 'def', 'return', 'int', 'print']
    alphabet = string.ascii_letters + '_'
    grouping_symbols = ['(', ')', '{', '}', '#{', '#}', '[', ']']
    num_op = ['+', '-', '*', '//']
    relation_op = ['<', '>', '!=', '<=', '>=', '==']
    delimiter_op = [';', ',', ':', ';']
    current_line = 1
    file_name = ''
    recognised_string = ''
    family = ''
    position = 0
    file = ''
    char = ''

    def __init__(self, file_name):
        self.current_line = 1
        self.file_name = file_name
        self.file = open(self.file_name, 'r')

    def __del__(self):
        return

    def next_token(self):
        if not os.path.isfile(self.file_name):
            print("Wrong file path")
            return

        self.state = 'start'

        while self.state == 'start':
            self.recognised_string = ''
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char == '':
                print("EOF")
                return 'EOF'
            elif self.char == '\n':
                self.current_line += 1
                self.file.seek(self.position)
                continue
            elif self.char == " ":
                continue
            elif self.digits.count(self.char) and self.state == "start":
                return self.digit_token()
            elif self.char in self.alphabet and self.state == 'start':
                return self.keyword_token()
            elif self.char in self.grouping_symbols and self.state == 'start':
                return self.grouping_symbol_token()
            elif self.char == '#' and self.state == 'start':
                return self.rem()
            elif self.char in self.delimiter_op and self.state == 'start':
                return self.delimeter_token()
            elif (self.char in self.relation_op or self.char == '!') and self.state == 'start':
                return self.relation_op_token()
            elif self.char == '=' and self.state == 'start':
                return self.assign_token()
            elif self.char in self.num_op or self.char == '/' and self.state == 'start':
                return self.num_op_token()

    def __error(self):
        print("There was an error at " + self.file_name + " @Line : " + str(self.current_line))

    def error(self,output):
        print(output)



    def __len_test(self):
        if len(self.recognised_string) > 30:
            return 0
        return 1

    def num_op_token(self):
        self.recognised_string += self.char
        if self.char == '+':
            return Token(self.recognised_string, 'addOP', self.current_line)
        elif self.char == '-':
            return Token(self.recognised_string, 'minusOP', self.current_line)
        elif self.char == '*':
            return Token(self.recognised_string, 'multiOP', self.current_line)
        elif self.char == '/':
            self.recognised_string += self.char
            self.char = self.file.read(1)
            if self.char == '/':
                return Token(self.recognised_string, 'divisionOP', self.current_line)
            else:
                self.position = self.file.tell()
                self.file.seek(self.position - 1)
                print("Expected // Division")
                self.__error()

    def assign_token(self):
        self.state = 'asgn'
        self.recognised_string += self.char
        self.char = self.file.read(1)
        self.position = self.file.tell()
        if self.char == '=':
            self.recognised_string += self.char
            return Token(self.recognised_string, 'isEqual', self.current_line)
        else:
            self.file.seek(self.position - 1)
            return Token(self.recognised_string, 'asgn', self.current_line)

    def relation_op_token(self):
        self.recognised_string += self.char
        self.char = self.file.read(1)
        if self.char == '<':
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char == '=':
                self.recognised_string += self.char
                return Token(self.recognised_string, 'lessEqual', self.current_line)
            else:
                self.file.seek(self.position - 1)
                return Token(self.recognised_string, 'lessThan', self.current_line)
        if self.char == '>':
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char == '=':
                self.recognised_string += self.char
                return Token(self.recognised_string, 'greaterEqual', self.current_line)
            else:
                self.file.seek(self.position - 1)
                return Token(self.recognised_string, 'greaterThan', self.current_line)
        if self.char == '!':
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char == '=':
                self.recognised_string += self.char
                return Token(self.recognised_string, 'notEqual', self.current_line)
            else:
                self.recognised_string += self.char
                self.file.seek(self.position - 1)
                print("Expected ! instead found : " + self.recognised_string)
                self.__error()

    def delimeter_token(self):
        self.recognised_string += self.char
        self.state = 'delimeter'
        return Token(self.recognised_string, 'del', self.current_line)

    def rem(self):
        self.recognised_string += self.char
        self.char = self.file.read(1)
        # comments state
        if self.char == '$':
            self.state = 'comment'
            while self.state == 'comment':
                self.recognised_string += self.char
                self.char = self.file.read(1)
                self.position = self.file.tell()
                if self.char == '#':
                    self.recognised_string += self.char
                    self.char = self.file.read(1)
                    if self.char == '\n':
                        self.current_line += 1
                    if self.char == '$':
                        self.recognised_string = ''
                        # this return statement is used to ignore the comments
                        return self.next_token()
                    self.file.seek(self.position)
        elif self.char in self.grouping_symbols:
            self.grouping_symbol_token()
            return Token(self.recognised_string, 'grouping', self.current_line)
        elif self.char in self.alphabet:
            self.keyword_token()
            return Token(self.recognised_string, 'declare', self.current_line)

    def grouping_symbol_token(self):
        # self.state = 'grouping_symbol'
        self.recognised_string += self.char
        return Token(self.recognised_string, "grouping_symbol", self.current_line)

    def keyword_token(self):
        self.state = 'keyword'
        while self.state == 'keyword':
            self.recognised_string = self.recognised_string + self.char
            self.char = self.file.read(1)
            self.position = self.file.tell()

            if (self.char not in self.alphabet and self.char not in self.digits) or self.char == '' or self.char == ' ':
                self.state = 'terminal'
                if self.recognised_string in self.keywords:
                    self.file.seek(self.position - 1)
                    return Token(self.recognised_string, "keyword", self.current_line)
                self.file.seek(self.position - 1)
                return Token(self.recognised_string, "var", self.current_line)

    def digit_token(self):
        self.state = 'digit'
        self.recognised_string = self.recognised_string + self.char
        while self.state == 'digit':
            self.char = self.file.read(1)
            self.position = self.file.tell()
            if self.char not in self.digits or self.char == '' or self.char == ' ' \
                    or self.char in self.grouping_symbols:
                self.state = 'terminal'
                # the -1 on position is very important to not consume the next char
                self.file.seek(self.position - 1)
                if self.char not in self.digits and self.char != '' and self.char != '\n' \
                        and self.char not in self.grouping_symbols and self.char not in self.delimiter_op:
                    self.__error()
                    break
                # i have no idea how this condition fixed all this crap
                if self.char == '':
                    self.file.seek(self.position)
                if self.__len_test() == 0 or int(self.recognised_string) > 9999:
                    print("Error too large number")
                    break
                if self.char in self.grouping_symbols:
                    return Token(self.recognised_string, "dig", self.current_line)

                return Token(self.recognised_string, "dig", self.current_line)


class Syntax:
    token = None

    def __init__(self):
        self.token = Lex('test.cpy')

    def start_rule(self):
        self.def_main_part()
        self.call_main_part()

    def def_main_part(self):
        self.def_main_function()

    def def_main_function(self):
        tk = self.token.next_token()
        if tk.recognised_string != 'def':
            self.token.error('Expected keyword \'def\'')
        tk = self.token.next_token()
        if tk.family != 'var':
            self.token.error('Expected keyword \'var\'')
        tk = self.token.next_token()
        if tk.recognised_string != '(':
            self.token.error('Expected keyword \'(\'')
        tk = self.token.next_token()
        if tk.recognised_string != ')':
            self.token.error('Expected keyword \')\'')
        tk = self.token.next_token()
        if tk.recognised_string != ':':
            self.token.error('Expected keyword \'(:')
        tk = self.token.next_token()
        if tk.recognised_string != '#{':
            self.token.error('Expected keyword \'#{\'')
        tk = self.token.next_token()
        self.declarations()
        self.def_function()
        self.statements()
        if tk.recognised_string != '#}':
            self.token.error('Expected keyword \'#}\'')
        tk = self.token.next_token()
        tk.__str__()



    def def_function(self):
        pass

    def declarations(self):
        pass

    def call_main_part(self):
        pass

    def statements(self):
        pass


if __name__ == '__main__':
    test = Syntax()
    test.start_rule()

