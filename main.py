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

    ##############################################################
    #                                                            #
    #                            Lex                             #
    #                                                            #
    ##############################################################


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

    def token_sneak_peak(self):
        print("############# Before sneak peak" + str(self.position) + "#######################")
        tmp_pos = self.file.tell()
        tmp_tk = self.next_token()
        print("############# After sneak peak" + str(self.position) + "#######################")
        self.file.seek(tmp_pos)
        return tmp_tk

    def char_sneak_peak(self):
        tmp_pos = self.file.tell()
        tmp_char = self.file.read(1)
        self.file.seek(tmp_pos)
        return tmp_char

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

    def error(self, output):
        print('Expected keyword \'' + output + '\'' + ' at ' + str(self.current_line))

    def token_peak(self):
        tmp_pos = self.file.tell()
        tk = self.next_token()
        self.file.seek(tmp_pos)
        return tk

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
                print("Expected = instead found : " + self.recognised_string)
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
                print("Eimai stin "+str(self.current_line)+" Kai eida "+self.recognised_string)
                if self.char == '\n':
                    self.current_line += 1
                if self.char == '#':
                    print("Eida #")
                    self.recognised_string += self.char
                    self.char = self.file.read(1)
                    if self.char == '\n':
                        print("Eida new line")
                        self.current_line += 1
                    if self.char == '$':
                        print("Comment telos")
                        self.recognised_string = ''
                        # this return statement is used to ignore the comments
                        print("************"+str(self.current_line)+"***************")
                        return self.next_token()
        elif self.char in self.grouping_symbols:
            return self.grouping_symbol_token()
        elif self.char in self.alphabet:
            return self.keyword_token()

    def grouping_symbol_token(self):
        # self.state = 'grouping_symbol'
        self.recognised_string += self.char
        return Token(self.recognised_string, "grouping_symbol", self.current_line)

    def keyword_token(self):
        print("Mpika Key kai eimai "+str(self.current_line))
        self.state = 'keyword'
        while self.state == 'keyword':
            self.recognised_string += self.char
            self.char = self.file.read(1)
            self.position = self.file.tell()

            if (self.char not in self.alphabet and self.char not in self.digits) or self.char == '' or self.char == ' ':
                self.state = 'terminal'
                self.file.seek(self.position - 1)
                if self.recognised_string in self.keywords:
                    return Token(self.recognised_string, "keyword", self.current_line)
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
                # I have no idea how this condition fixed all this crap
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
        self.tk = None


    ##############################################################
    #                                                            #
    #                     Syntax Functions                       #
    #                                                            #
    ##############################################################

    def check_string_not(self, expected_word):
        self.tk = self.token.next_token()
        self.tk.__str__()
        if self.tk.recognised_string != expected_word:
            return True
        return False

    def check_family_not(self, expected_word):
        self.tk = self.token.next_token()
        if self.tk.family != expected_word:
            return True
        return False

    def start_rule(self):
        self.def_main_part()
        self.call_main_part()

    def def_main_part(self):
        self.def_main_function()

    def def_main_function(self):
        if self.check_string_not('def'):
            self.token.error('def')
        if self.check_family_not('var'):
            self.token.error('var')
        if self.check_string_not('('):
            self.token.error('Expected keyword \'(\'')
        if self.check_string_not(')'):
            self.token.error('Expected keyword \')\'')
        if self.check_string_not(':'):
            self.token.error('Expected keyword \'(:')
        if self.check_string_not('#{'):
            self.token.error('Expected keyword \'#{\'')

        
        self.declarations()
        # prepei na kanei sneak peak ena token gia na dei an tha mpei stin function
        # diaforetika katanalwnei token xwris logo
        # self.def_function()
        # self.statements()
        if self.check_string_not('#}'):
            self.token.error('Expected keyword \'#}\'')

    def def_function(self):
        # if self.check_string_not('def'):
        pass

    # self.token.error('Expected keyword \'def\'')

    # if self.check_family_not('var'):
    # self.token.error('var')

    def declarations(self):
        pos = self.token.file.tell()
        tmp_tk = self.token.token_sneak_peak()
        self.token.file.seek(pos)
        if tmp_tk.recognised_string == '#declare':
            self.declaration_line()

    def declaration_line(self):
        if self.check_string_not('#declare'):
            self.token.error('#declare')
        self.id_list()

    def id_list(self):
        if self.check_family_not('var'):
            self.token.error('var')
        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == ',':
            self.token.next_token()
            self.id_list()


    def call_main_part(self):
        pass

    def statements(self):
        pass


    ##############################################################
    #                                                            #
    #                     Program Starts Here                    #
    #                                                            #
    ##############################################################


if __name__ == '__main__':
    test = Syntax()
    test.start_rule()
