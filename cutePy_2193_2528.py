#       Nikolaos - Marios Kontos 2193
#       Alexandros Pournaras 2528

import os.path
import string
import sys
import copy


class Quad:
    """
    Creates a new quad and initialises some values
    """

    def __init__(self):
        self.label = 0
        self.temp_label = 0
        self.operator, self.source1, self.source2, self.target = None, None, None, None

    def advance_label(self):
        self.label += 1

    def advance_temp_label(self):
        self.temp_label += 1

    def to_string(self):
        print("Quad Label : " + self.label)

    def print_quad(self, quad):
        print(str(quad.label) + ': ' + quad.operator + ' ' + quad.source1 + ' ' + quad.source2 + ' ' + str(quad.target))

    '''
    Modifies the quad object we created based on the parameters
    '''

    def gen_quad(self, operator, source1, source2, target):
        self.advance_label()
        self.operator = operator
        self.source1 = source1
        self.source2 = source2
        self.target = target

    """
    Advances the label of the quad and returns its value
    """

    def next_quad(self):
        return self.label + 1

    def new_temp(self):
        self.advance_temp_label()
        return_string = '@T'+str(self.temp_label)
        return return_string
    """
    Creates and returns an empty list that will be used to store Quad labels
    """

    @staticmethod
    def empty_list():
        quad_list = []
        return quad_list

    """
    Create and return a new list that has as a UNIQUE element the label of the Quad
    """

    def make_list(self,label):
        label_list = [label]
        return label_list

    @staticmethod
    def merge_list(list1, list2):
        merged_list = []
        for i in list1:
            merged_list.append(i)
        for i in list2:
            merged_list.append(i)

        return merged_list





class Scope():
    nested_lvl = 0

    def __init__(self, level, enclsoed_scope=None):
        self.entities = list()
        self.level = level
        self.nested_lvl += 1
        self.enclosed_scope = enclsoed_scope
        self.offset = 12

    def add_entity(self, entity):
        self.entities.append(entity)

    def get_offset(self):
        tmp_offset = self.offset
        self.offset = self.offset + 4
        return tmp_offset

    def print_entities(self):
        for i in self.entities:
            print(i.name + ' Nested LvL: ' + str(self.level))

class Entity:

    def __init__(self, name, etype):
        self.name = name
        self.etype = etype


class Constant(Entity):

    def __init__(self, name, value):
        super.__init__(name, "CONSTANT")
        self.value = value


class Variable(Entity):

    def __init__(self, name, offset):
        super().__init__(name, 'VARIABLE')
        self.name = name
        self.offset = offset


class FormalParameter(Entity):
    '''
    mode = Anafora OR timi OR return value
    '''

    def __init__(self, name, mode):
        super.__init__(name, 'FORMAL_PAREMETER')
        self.mode = mode


class Procedure(Entity):

    def __init__(self, name, starting_quad, frame_length=12):
        super.__init__(name, 'PROCEDURE')
        self.starting_quad = starting_quad
        self.frame_length = frame_length


class TemporaryVariable(Entity):

    def __init__(self, name, offset=-1):
        super().__init__(name, "TMPVAR")
        self.offset = offset


class Parameter(Entity):

    def __init__(self, name, mode, offset=-1):
        super().__init__(name, "PARAMETER")
        self.mode = mode
        self.offset = mode
        self.offset = offset


class Function(Entity):

    def __init__(self, name, starting_quad, frame_length=12):
        super().__init__(name, 'FUNCTION')
        self.starting_quad, self.frame_length = starting_quad, frame_length


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
        print(
            bcolors.YELLOW + '[ERROR]' + bcolors.ENDC + bcolors.OKGREEN + ' Expected ' + bcolors.BOLD + output + bcolors.RED + ' at Line: ' + str(
                self.current_line))
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
                return Token(self.recognised_string, "dig", self.current_line)

                if self.char not in self.digits and self.char != '' and self.char != '\n' \
                        and self.char not in self.grouping_symbols and self.char not in self.delimiter_op:
                    print("TESTTTTTTTTT " + self.char + " " + self.recognised_string)
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

    ##############################################################
    #                                                            #
    #                     Syntax Functions                       #
    #                                                            #
    ##############################################################


class Syntax:
    ST = list()
    quad = Quad()
    scope = Scope(0)
    ST.append(scope)
    quad_list = list()


    def backpatch(self, list, label):
        for i in list:
            for n in self.quad_list:
                if i == n.label:
                    n.target = i

    def add_new_scope(self, scope):

        tmp_scope = self.ST[-1]
        new_scope = Scope(tmp_scope.level + 1, tmp_scope)
        self.ST.append(new_scope)


    def remove_scope(self):
        self.ST.pop()

    def add_new_function(self, name):
        tmp_scope = self.ST[-1]
        new_scope = Scope(tmp_scope.level + 1)
        self.add_new_scope(new_scope)
        tmp_func = Function(name, -1)
        self.ST[-1].add_entity(tmp_func)

    def add_func_entity(self, name):
        tmp_func = Function(name, -1)
        self.ST[-1].add_entity(tmp_func)

    def print_scopes(self,scope_list):
        for i in scope_list:
            if len(i.entities) != 0:
                print(i.entities[0].name)

    def print_quads(self, quad_list):
        for i in range(len(quad_list)):
            quad_list[i].print_quad(quad_list[i])

    def add_new_var(self):
       new_offset = self.scope[-1].entities[-1].offset + 4

    def push_new_quad(self, quad):
        deep_copie = copy.copy(quad)
        self.quad_list.append(deep_copie)

    def __init__(self, path):
        self.token = Lex(path)

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
        tmp_tk = self.token.token_sneak_peak()
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

        func_name = tmp_tk.recognised_string

        self.quad.gen_quad('begin_block',func_name, '_', '_')
        self.push_new_quad(self.quad)
        self.add_new_function(func_name)

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

        tmp_tk = self.token.token_sneak_peak()
        if self.check_string_not('#}'):
            self.token.error('Expected keyword \'#}\'')

        self.quad.gen_quad('end_block', func_name, '_', '_')
        self.push_new_quad(self.quad)
        self.ST.pop()

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

        #

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
        tmp_tk = self.token.token_sneak_peak()
        if self.check_family_not('var'):
            self.token.error('var')

        var_name = tmp_tk.recognised_string
        new_var = Variable(var_name, self.ST[-1].get_offset)
        self.ST[-1].add_entity(new_var)

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
        var_name = self.token.token_sneak_peak()
        var_name = var_name.recognised_string
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
            tmp = self.expression()
            self.quad.gen_quad('=', tmp,'_',var_name )
            self.push_new_quad(self.quad)

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

        t1 = self.term()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            op_sign = tmp_tk.recognised_string

            if op_sign == '+':
                self.token.next_token()
                t2 = self.term()
                w = self.quad.new_temp()
                self.quad.gen_quad('+', t1, t2, w)
                self.push_new_quad(self.quad)
                t1 = w
            elif op_sign == '-':
                self.token.next_token()
                t2 = self.term()
                w = self.quad.new_temp()
                self.quad.gen_quad('-', t1, t2, w)
                self.push_new_quad(self.quad)
                t1 = w
            else:
                return t1
                break

    def term(self):
        f1 = self.factor()
        while True:
            tmp_tk = self.token.token_sneak_peak()
            mul_op = tmp_tk.recognised_string
            if mul_op == '*' or mul_op == '//':
                new_token = self.token.next_token()
                if new_token.recognised_string != '*' and new_token.recognised_string != '//':
                    self.token.error('* or //')
                f2 = self.factor()
                w = copy.copy(self.quad.new_temp())
                if mul_op == '*':
                    self.quad.gen_quad('*',f1,f2,w)
                    self.push_new_quad(self.quad)
                    f1 = w
                elif mul_op == '//':
                    self.quad.gen_quad('//', f1, f2, w)
                    self.push_new_quad(self.quad)
                    f1 = w
            else:
                return f1
                break

    def factor(self):
        tmp_token = self.token.next_token()
        if tmp_token.recognised_string.isdigit() or tmp_token.recognised_string in string.ascii_letters or tmp_token.family == 'var':
            return tmp_token.recognised_string

            # self.token.error('INTEGER')

        if tmp_token.recognised_string == '(':
            exp_val = self.expression()
            if self.check_string_not(')'):
                self.token.error(')')
            return exp_val
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

        self.print_quads(self.quad_list)
        print("--")
        self.print_scopes(self.ST)
    #########################################################################

    ##############################################################
    #                                                            #
    #                     Program Starts Here                    #
    #                                                            #
    ##############################################################


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Need only 1 argument")
        sys.exit()
    b = Syntax(sys.argv[1])

    b.start_rule()
