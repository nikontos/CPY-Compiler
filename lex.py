import os.path

import lex
import token


class Lex:
    state = ''
    digits = str([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    current_line = 1
    file_name = ''
    recognised_string = ''
    family = ''
    position = 0
    file = ''

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
            char = self.file.read(1)
            self.position = self.file.tell()
            if char == '':
                print("EOF")
                return 'EOF'
            elif char == '\n':
                self.current_line = self.current_line + 1
                continue
            elif char == " ":
                continue
            elif self.digits.count(char) and self.state == "start":
                self.state = 'digit'
                self.recognised_string = self.recognised_string + char
                while self.state == 'digit':
                    char = self.file.read(1)
                    self.position = self.file.tell()
                    if char not in self.digits or char == '' or char == ' ':
                        self.state = 'terminal'
                        # the -1 on position is very imporant to not consume the next char
                        self.file.seek(self.position)
                        if char not in self.digits and char != '' and char != '\n':
                            self.__error()
                            break
                        if self.__len_test() == 0 or int(self.recognised_string) > 9999:
                            print("Error too large number")
                            break
                        return token.Token(self.recognised_string, "dig", self.current_line)
                    self.recognised_string = self.recognised_string + char

#            return token.Token(self.recognised_string, self.family, self.current_line)

    def __error(self):
        print("There was an error at " + self.file_name + " @Line : " + str(self.current_line) + " @Pos: " + str(self.position))

    def __len_test(self):
        if len(self.recognised_string) > 30:
            return 0
        return 1