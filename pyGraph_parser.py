# -*- coding: utf-8 -*-
# Build the lexer
import ply.lex as lex
from pyGP2.pyGraph import GP2_Graph, GP2_Node, GP2_Edge
from pyGP2.pyLabel import Mark, GP2_Atom

def make_graph_parser():

    # -----------------------------------------------------------------------------
    # calc.py
    #
    # A simple calculator with variables -- all in one file.
    # -----------------------------------------------------------------------------

    tokens = (
        'LPAREN',
        'RPAREN',
        'LSQUARE',
        'RSQUARE',
        'COLON',
        'COMMA',
        'MID',
        'NUMBER',
        'STRING',
        'CHAR',
        'EMPTY',
        'MARK_RED',
        'MARK_GREEN',
        'MARK_BLUE',
        'MARK_GREY',
        'MARK_DASHED',
        'ROOT',
        )

    t_LPAREN  = r'\('

    t_RPAREN  = r'\)'

    t_LSQUARE  = r'\['

    t_RSQUARE  = r'\]'

    t_COLON  = r'\:'

    t_MID = r'\|'

    t_COMMA = r'\,'

    t_EMPTY = r'empty'

    t_MARK_RED = r'\#red'

    t_MARK_GREEN = r'\#green'

    t_MARK_BLUE = r'\#blue'

    t_MARK_GREY = r'\#grey'

    t_MARK_DASHED = r'\#dashed'

    t_ROOT = r'\(R\)'


    def t_NUMBER(t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %d", t.value)
            t.value = 0
        return t

    def t_STRING(t):
        r'\"[a-zA-Z0-9_ ]*\"'
        t.value = str(t.value)
        return t

    def t_CHAR(t):
        r'\'[a-zA-Z0-9_]\''
        t.value = str(t.value)
        return t


    # Ignored characters
    t_ignore = " \t"

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    import ply.lex
    lexer = lex.lex()

    def p_graph(t):
        '''graph : LSQUARE nodelist MID edgelist RSQUARE
                       | LSQUARE nodelist MID RSQUARE
                       | LSQUARE MID RSQUARE'''
        g = GP2_Graph()
        if len(t) > 4:
            for n in t[2]:
                g.add_node(n)
            if len(t) > 5:
                for e in t[4]:
                    (source, target, label, mark) = e
                    g.add_edge(t.parser.node_map[source], t.parser.node_map[target], label=label, mark=mark)
        t[0] = g

    def p_nodelist(t):
        '''nodelist : node nodelist
                      | node'''
        if len(t) == 3:
            t[2].insert(0, t[1])
            t[0] = t[2]
        else:
            t[0] = [t[1]]

    def p_edgelist(t):
        '''edgelist : edge edgelist
                      | edge'''
        if len(t) == 3:
            t[2].insert(0, t[1])
            t[0] = t[2]
        else:
            t[0] = [t[1]]

    def p_node(t):
        '''node : LPAREN NUMBER ROOT COMMA label mark RPAREN
                       | LPAREN NUMBER COMMA label mark RPAREN
                       | LPAREN NUMBER ROOT COMMA label RPAREN
                       | LPAREN NUMBER COMMA label RPAREN'''
        if len(t) == 8:
            t[0] = GP2_Node(label = t[5], mark=t[6], root=True)
        elif len(t) == 7:
            print("Length 7:")
            print(t[3])
            print(t[5])
            if t[3] == '(R)':
                t[0] = GP2_Node(label = t[5], root=True)
            else:
                t[0] = GP2_Node(label = t[4], mark=t[5])
        else:
            t[0] = GP2_Node(label = t[4])
        t.parser.node_map[int(t[2])] = t[0]

    def p_edge(t):
        '''edge : LPAREN NUMBER COMMA NUMBER COMMA NUMBER COMMA label mark RPAREN
                       | LPAREN NUMBER COMMA NUMBER COMMA NUMBER COMMA label RPAREN'''
        m = Mark.NONE
        if len(t) == 11:
            m = t[9]
        source = int(t[4])
        target = int(t[6])
        t[0] = (source, target, t[8], m)

    def p_label(t):
        '''label : atom COLON label
                      | atom
                      | EMPTY'''
        if len(t) == 4:
            t[3].insert(0, t[1])
            t[0] = t[3]
        elif t[1] == 'empty':
            t[0] = []
        else:
            t[0] = [t[1]]


    def p_atom(t):
        '''atom : NUMBER
                      | STRING
                      | CHAR'''
        i = False
        try:
            t[0] = GP2_Atom(num = int(t[1]))
            i = True
        except ValueError:
            i = False
        if not i and t[1][0] == '"':
            t[0] = GP2_Atom(string = t[1][1:len(t[1]) -1 ])
        elif not i and t[1][0] == '\'':
            t[0] = GP2_Atom(ch = t[1][1:len(t[1]) -1 ])

    def p_mark(t):
        ''' mark : MARK_RED
                      | MARK_GREEN
                      | MARK_BLUE
                      | MARK_GREY
                      | MARK_DASHED'''
        if t[1] == '#red':
            t[0] = Mark.RED
        elif t[1] == '#green':
            t[0] = Mark.GREEN
        elif t[1] == '#blue':
            t[0] = Mark.BLUE
        elif t[1] == '#grey':
            t[0] = Mark.GREY
        elif t[1] == '#dashed':
            t[0] = Mark.DASHED
        else:
            print("Not recognized: \"" + t[1] + "\"")

    def p_error(t):
        print("Syntax error at '%s'" % t.value)
        print(t.lineno)


    import ply.yacc as yacc
    parser = yacc.yacc()
    return parser
