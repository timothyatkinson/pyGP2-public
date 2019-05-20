from enum import Enum

class Type(Enum):
     NUM = 0
     CHAR = 1
     STRING = 2

class GP2_Atom():
    def __init__(self, num=None,ch=None,string=None):
        if(num == ch == string == None):
            raise ValueError("Invalid GP2_Atom. Requires one of positional arguments 'num', 'ch' and 'string'")
        self.num = num
        self.ch = ch
        self.string = string
        if not self.verify():
            raise ValueError("Invalid GP2_Atom.")

    def get_type(self):
        if(self.num != None):
            return Type.NUM
        if(self.ch != None):
            return Type.CHAR
        if(self.string != None):
            return Type.STRING

    def verify(self):
        if(self.num != None and type(self.num) != int):
            print("Invalid GP2_Atom. Not a valid number (num): " + str(self))
        if(self.ch != None and (type(self.ch) != str or len(self.ch) > 1)):
            print("Invalid GP2_Atom. Not a valid char (ch): " + str(self))
        if(self.string != None and type(self.string) != str):
            print("Invalid GP2_Atom. Not a valid string: " + str(self))
        if self.num == self.ch == self.string == None:
            print("Invalid GP2_Atom. All data types (num, char and string) are None: " + str(self))
            return False
        if [self.num, self.ch, self.string].count(None) < 2:
            print("Invalid GP2_Atom. Multiple data types detected: " + str(self))
            return False
        return True

    def __str__(self):
        string = ""
        if(self.num != None):
            string += str(self.num)
        if(self.ch != None):
            string += "'" + str(self.ch) + "'"
        if(self.string != None):
            string += "\"" + str(self.string) + "\""
        return string

    def set_num(self, num):
        self.num = num
        self.ch = None
        self.string = None

    def set_ch(self, ch):
        self.ch = ch
        self.num = None
        self.string = None

    def set_string(self, string):
        self.string = string
        self.num = None
        self.ch = None

    def copy(self):
        return GP2_Atom(num=self.num, string=self.string, ch=self.ch)

def validate_mark(mark):
    values = set(item.value for item in Mark)
    return mark in values

class Mark(Enum):
     NONE = 0
     RED = 1
     GREEN = 2
     BLUE = 3
     GREY = 4
     DASHED = 5

def validate_label(label):
    for atom in label:
        if atom == None:
            print("Atom " + str(atom) + " is None.")
            return False
        if not isinstance(atom, GP2_Atom):
            print("Atom " + str(atom) + " is not GP2 Atom.")
            return False
        if not atom.verify():
            print("Atom " + str(atom) + " is valid.")
            return False
    return True

def label_string(label):
    if len(label) == 0:
        return "empty"
    try:
        string = ""
        for i in range(len(label)):
            if i != 0:
                string += ":"
            string += str(label[i])
        string += ""
        return string
    except:
        return str(label)

def mark_string(mark):
    if mark == Mark.NONE:
        return ""
    elif mark == Mark.RED:
        return "#red"
    elif mark == Mark.GREEN:
        return "#green"
    elif mark == Mark.BLUE:
        return "#blue"
    elif mark == Mark.GREY:
        return "#grey"
    elif mark == Mark.DASHED:
        return "#dashed"
    else:
        raise ValueError(str(mark) + " is not a valid mark.")

def list_to_label(ls):
    label = []
    for l in ls:
        if(type(l) == int):
            label.append(GP2_Atom(num = l))
        elif(type(l) == str):
            label.append(GP2_Atom(string=l))
        else:
            raise ValueError("Object " + str(l) + " is not a valid label.")
    return label


def copy_label(label):
    return [atom.copy() for atom in label]
