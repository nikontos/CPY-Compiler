import argparse
import os.path
import string
import colorsys
import colored
import cprint


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Token:

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
    recognised_string = ''
    position = 0
    char = ''

    # This is the alphabet of allowed symbols and words
    digits = string.digits
    keywords = ['if', 'else', 'while', 'def', 'return', 'int', 'print', '#declare']
    alphabet = string.ascii_letters + '_'
    grouping_symbols = ['(', ')', '{', '}', '#{', '#}', '[', ']']
    num_op = ['+', '-', '*', '//']
    relation_op = ['<', '>', '!=', '<=', '>=', '==']
    delimiter_op = [';', ',', ':', ';']

    def __init__(self, file_name):
        self.current_line = 1
        self.file_name = file_name
        self.file = open(self.file_name, 'r')


    def __del__(self):
        return

    def token_sneak_peak(self):
        """@return: A token type object, the next token without actually consuming it"""
        tmp_line = self.current_line
        tmp_pos = self.file.tell()
        tmp_tk = self.next_token()
        self.file.seek(tmp_pos)
        self.current_line = tmp_line
        return tmp_tk

    def next_token(self):
        """Returns the next token in the file"""
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
                exit()
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
        exit()

    def error(self, output):
        print(bcolors.YELLOW + '[ERROR]' + bcolors.ENDC + bcolors.OKGREEN + ' Expected ' + bcolors.BOLD + output + bcolors.RED + ' at Line: ' + str(self.current_line))
        exit()

    def __len_test(self):
        """Returns False if the string of the token is >30 chars"""

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
        """
        Handles the '#' character and returns the token it corresponds
        Either a comment, a keyword or a grouping symbol
        """
        self.recognised_string += self.char
        self.char = self.file.read(1)
        comment_line = self.current_line

        # comments state
        if self.char == '$':
            self.state = 'comment'
            while self.state == 'comment':
                self.recognised_string += self.char
                self.char = self.file.read(1)
                if self.char == '':
                    print('Reached EOF without closing comments, comments started @Line: ' + str(comment_line))
                    exit()
                if self.char == '\n':
                    self.current_line += 1
                if self.char == '#':
                    self.recognised_string += self.char
                    self.char = self.file.read(1)
                    if self.char == '\n':
                        self.current_line += 1
                    if self.char == '$':
                        self.recognised_string = ''
                        # this return statement is used to ignore the comments
                        return self.next_token()

        elif self.char in self.grouping_symbols:
            return self.grouping_symbol_token()
        elif self.char in self.alphabet:
            return self.keyword_token()

    def grouping_symbol_token(self):
        self.recognised_string += self.char
        return Token(self.recognised_string, "grouping_symbol", self.current_line)

    def keyword_token(self):
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

    def __init__(self):
        self.token = Lex('test.cpy')

    ##############################################################
    #                                                            #
    #                     Syntax Functions                       #
    #                                                            #
    ##############################################################

    def check_string_not(self, expected_word):
        """
        @param expected_word: String: The string we will check
        @return: BOOL: True if the next token is different from the param
        """
        tk = self.token.next_token()
        # tk.__str__()
        if tk.recognised_string != expected_word:
            return True
        return False

    def check_family_not(self, expected_word):
        tk = self.token.next_token()
        # tk.__str__()
        if tk.family != expected_word:
            return True
        return False

    def start_rule(self):
        self.def_main_part()
        self.call_main_part()

    def def_main_part(self):
        self.def_main_function()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == 'def':
                self.def_main_function()
            else:
                break

    def def_main_function(self):
        if self.check_string_not('def'):
            self.token.error('def')
        if self.check_family_not('var'):
            self.token.error('var')
        if self.check_string_not('('):
            self.token.error(' \'(\'')
        if self.check_string_not(')'):
            self.token.error(' \')\'')
        if self.check_string_not(':'):
            self.token.error('Expected keyword \'(:')
        if self.check_string_not('#{'):
            self.token.error(' \'#{\'')

        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == '#declare':
                self.declarations()
            else:
                break
        # prepei na kanei sneak peak ena token gia na dei an tha mpei stin function
        # diaforetika katanalwnei token xwris logo
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == 'def':
                self.def_function()
            else:
                break
        self.statements()
        if self.check_string_not('#}'):
            self.token.error('Expected keyword \'#}\'')

    def def_function(self):
        if self.check_string_not('def'):
            self.token.error('Expected function declarion with def')
        if self.check_family_not('var'):
            self.token.error('Expected a variable')
        if self.check_string_not('('):
            self.token.error('( ')
        self.id_list()
        if self.check_string_not(')'):
            self.token.error(')')
        if self.check_string_not(':'):
            self.token.error(':')
        if self.check_string_not('#{'):
            self.token.error('#{')

        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == '#declare':
                self.declarations()
            else:
                break

        # i think some more thought required here
        # in order to distinguish declarations from def_function
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == 'def':
                self.def_function()
            else:
                break
        self.statements()
        if self.check_string_not('#}'):
            self.token.error('#}')

    def declarations(self):
        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == '#declare':
            self.declaration_line()

    def declaration_line(self):
        if self.check_string_not('#declare'):
            self.token.error('#declare')
        self.id_list()

    def id_list(self):
        if self.check_family_not('var'):
            self.token.error('var')
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == ',':
                self.token.next_token()
                self.id_list()
            else:
                break

    def statements(self):
        self.statement()

    def statement(self):
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.family == 'var' or tmp_tk.recognised_string == 'print' or tmp_tk.recognised_string == 'return':
                self.simple_statement()
            elif tmp_tk.recognised_string == 'if' or tmp_tk.recognised_string == 'while':
                self.structured_statement()
            else:
                # self.token.error('Expected Statement')
                break

    def simple_statement(self):
        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.family == 'var':
            self.assignment_stat()
        elif tmp_tk.recognised_string == 'print':
            self.print_stat()
        elif tmp_tk.recognised_string == 'return':
            self.return_stat()
        else:
            self.token.error("simple statement")

    def structured_statement(self):
        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == 'if':
            self.if_stat()
        elif tmp_tk.recognised_string == 'while':
            self.while_stat()
        else:
            self.token.error('if or while')

    def assignment_stat(self):
        if self.check_family_not('var'):
            self.token.error('ID')
        elif self.check_string_not('='):
            self.token.error('=')
        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == 'int':
            self.token.next_token()
            if self.check_string_not('('):
                self.token.error('(')
            if self.check_string_not('input'):
                self.token.error('input')
            if self.check_string_not('('):
                self.token.error('(')
            if self.check_string_not(')'):
                self.token.error(')')
            if self.check_string_not(')'):
                self.token.error(')')
            if self.check_string_not(';'):
                self.token.error(';')
        else:
            self.expression()
            if self.check_string_not(';'):
                self.token.error(';')

    def print_stat(self):
        if self.check_string_not('print'):
            self.token.error('print')
        if self.check_string_not('('):
            self.token.error('(')
        self.expression()
        if self.check_string_not(')'):
            self.token.error(')')
        if self.check_string_not(';'):
            self.token.error(';')

    def return_stat(self):
        if self.check_string_not('return'):
            self.token.error('print')
        if self.check_string_not('('):
            self.token.error('(')
        self.expression()
        if self.check_string_not(')'):
            self.token.error(')')
        if self.check_string_not(';'):
            self.token.error(';')

    def if_stat(self):
        if self.check_string_not('if'):
            self.token.error('if')
        if self.check_string_not('('):
            self.token.error('(')

        self.condition()
        if self.check_string_not(')'):
            self.token.error(')')
        if self.check_string_not(':'):
            self.token.error(':')

        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == '#{':
            self.token.next_token()
            self.statements()
            if self.check_string_not('#}'):
                self.token.error('#} @IF statement')
        else:
            self.statement()

        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == 'else':
            # consume
            self.token.next_token()
            if self.check_string_not(':'):
                self.token.error(':')
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == '#{':
                self.token.next_token()
                self.statements()
                if self.check_string_not('#}'):
                    self.token.error('#} @IF Statement')
            else:
                self.statement()

    def while_stat(self):
        if self.check_string_not('while'):
            self.token.error('while')
        if self.check_string_not('('):
            self.token.error(')')
        self.condition()
        if self.check_string_not(')'):
            self.token.error(')')
        if self.check_string_not(':'):
            self.token.error(':')
        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == '#{':
            self.token.next_token()
            self.statements()
            if self.check_string_not('#}'):
                self.token.error('#} @WHILE Statement')
        else:
            self.statement()

    def expression(self):
        tmp_token = self.token.token_sneak_peak()
        if tmp_token.recognised_string == '+' or tmp_token.recognised_string == '-':
            self.optional_sign()
        self.term()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == '+' or tmp_tk.recognised_string == '-':
                self.token.next_token()
                self.term()
            else:
                break

    def term(self):
        self.factor()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == '*' or tmp_tk.recognised_string == '//':
                new_token = self.token.next_token()
                if new_token.recognised_string != '*' and new_token.recognised_string != '//':
                    self.token.error('* or //')
                self.factor()
            else:
                break

    def factor(self):
        tmp_token = self.token.next_token()
        if tmp_token.recognised_string.isdigit():
            pass
            # self.token.error('INTEGER')

        if tmp_token.recognised_string == '(':
            self.expression()
            if self.check_string_not(')'):
                self.token.error(')')
        elif tmp_token.family == 'var':
            self.idtail()

    def idtail(self):
        tmp_token = self.token.token_sneak_peak()
        if tmp_token.recognised_string == '(':
            self.token.next_token()
            self.actual_par_list()
            if self.check_string_not(')'):
                self.token.error(')')
        else:
            return

    def actual_par_list(self):
        self.expression()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == ',':
                self.token.next_token()
                self.expression()
            else:
                break

    def optional_sign(self):
        self.token.next_token()
        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == '+' or tmp_tk.recognised_string == '-':
            self.token.error('Less + or - operations')

    def condition(self):
        self.bool_term()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == 'or':
                self.bool_term()
            else:
                break

    def bool_term(self):
        self.bool_factor()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.recognised_string == 'and':
                self.bool_factor()
            else:
                break

    def bool_factor(self):
        tmp_tk = self.token.token_sneak_peak()
        if tmp_tk.recognised_string == 'not':
            self.token.next_token()
            if self.check_string_not('['):
                self.token.error('[')
            self.condition()
            if self.check_string_not(']'):
                self.token.error(']')
        elif tmp_tk.recognised_string == '[':
            self.token.next_token()
            self.condition()
            if self.check_string_not(']'):
                self.token.error(']')
        else:
            self.expression()
            tmp_tk = self.token.next_token()
            if tmp_tk.recognised_string not in self.token.relation_op:
                self.token.error('Rel OP')
            self.expression()

    def call_main_part(self):
        if self.check_string_not('if'):
            self.token.error('if')
        if self.check_string_not('__name__'):
            self.token.error('__name__')
        if self.check_string_not('=='):
            self.token.error('==')
        if self.check_string_not('__main__'):
            self.token.error('__main__')
        if self.check_string_not(':'):
            self.token.error(':')

        self.main_function_call()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            if tmp_tk.family != 'var':
                break
            else:
                self.main_function_call()

    def main_function_call(self):
        if self.check_family_not('var'):
            self.token.error('var')
        elif self.check_string_not('('):
            self.token.error('(')
        elif self.check_string_not(')'):
            self.token.error(')')
        elif self.check_string_not(';'):
            self.token.error(';')

    ##############################################################
    #                                                            #
    #                     Program Starts Here                    #
    #                                                            #
    ##############################################################


if __name__ == '__main__':
    text = input("Provide the name or the path of .cpy programm\n")
    # parser = argparse.ArgumentParser()
    # args = parser.parse_args()
    # print(args)
    test = Lex(text)
    b = Syntax()
    # while test.file:
    #    tk = test.next_token()
    #    tk.__str__()
    b.start_rule()

    # while test.file:
    #    a = test.next_token()
    #    a.__str__()

    test.file.close()