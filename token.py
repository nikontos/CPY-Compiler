class Token:
    recognised_string = ''
    family = ''
    line_number = 0

    def __init__(self, recognised_string, family, line_number):
        self.recognised_string = recognised_string
        self.family = family
        self.line_number = line_number

   # def __init__(self):
    #    pass

    def __str__(self):
        pass
