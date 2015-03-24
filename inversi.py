# -*- coding: utf-8 -*-
"""
author: Bernd Schmidt
lizence: GPL2
code style: Python PEP8
"""

import copy 
import random
import datetime
from itertools import product
import sys

random.seed(0) 

class Inversi():
    SIZE = 6
    INVERTED_ADD = 2
        
    ICONS = {0: "x", 2: "X", 1: "o", 3: "O"}
    
    def __init__(self):
        self.stones = [Inversi.INVERTED_ADD, Inversi.INVERTED_ADD + True]
        self.turns = []
        self.board = []
                
        for x in range(0, Inversi.SIZE):
            self.board.append([])
            for y in range(0, Inversi.SIZE):
                self.board[x].append((x + y) % 2)

    '''
    erstellt eine Kopie des Inversi Objekts
    '''
    def copy(self):
        inversi = Inversi()

        inversi.__dict__ = copy.deepcopy(self.__dict__)
        return inversi
    
    '''
    Setzt den Stein an der Position, nimmt den stein und geht dann in Richtung "Direction",
    bis er auserhalb des Spielfelds kommt. Gibt dann den letzt genommen Stein zurück.
    '''
    def _replace_line(self, position, direction, new_stone):
        for add in range(0, Inversi.SIZE):
            x = position[0] + direction[0] * add
            y = position[1] + direction[1] * add
            self.board[x][y], new_stone = new_stone, self.board[x][y]
                
        return new_stone

    '''
    Prüft und Platziert einen Stein. Gibt bei ungültigen Zügen einen Fehler zurück
    '''
    def place(self, turn, player):
        position, direction = turn
        if not self.is_turn_possible(turn, player):
            raise Exception("Invalid Turn")
        old_stone = self.stones[player]
        new_stone = self._replace_line(position, direction, old_stone)
        self.turns.append((position, direction, new_stone))
        
        self.stones[player] = self.invert_stone(new_stone)

    '''
    Dreht den Stein rum, wenn er noch nicht rumgedreht wurde
    '''
    def invert_stone(self, stone):
        if stone < Inversi.INVERTED_ADD:
            return stone + Inversi.INVERTED_ADD
        return stone

    def get_last_position(self, position, direction):
        x = position[0] + direction[0] * (Inversi.SIZE - 1)
        y = position[1] + direction[1] * (Inversi.SIZE - 1)
        return x, y
        
    '''
    Nimmt den zuletzt gemachten Zug zurück
    '''
    def undo(self):
        position, direction, new_stone = self.turns.pop(len(self.turns) - 1)
        last_position = self.get_last_position(position, direction)
        new_direction = [- direction[0], - direction[1]]
        self._replace_line(last_position, new_direction, new_stone)
        
    '''
    Prüft ob der Zug gültig ist, indem überprüft wird, ob das letzte Feld in der Linie
    ein Nicht-Umgedrehter Stein oder ein umgedrehter Stein des eigenen Spielers ist
    True: Wenn der Zug möglich ist
    '''
    def is_turn_possible(self, turn, player):
        position, direction = turn
        x, y = self.get_last_position(position, direction)
        field = self.board[x][y]
        
        return (field < Inversi.INVERTED_ADD or field == (player + Inversi.INVERTED_ADD))
            
    '''
    Gibt eine Liste aller möglichen Züge zurück
    '''
    def possible_turns(self, player):
        turns = []
        max_size = Inversi.SIZE - 1
        
        for direction in (0, 1), (1, 0), (0, -1), (-1, 0):
            for edge in range(0, Inversi.SIZE):
                position = [edge, edge]
                
                if direction[0] == 1:    position[0] = 0
                elif direction[0] == -1: position[0] = max_size
                
                if direction[1] == 1:    position[1] = 0
                elif direction[1] == -1: position[1] = max_size
                
                if self.is_turn_possible((position, direction), player):
                    turns.append((position, direction))
                    
        return turns

    def play(self, X, O):
        functions = (X, O)
        player = False
        
        while not self.has_ended():
            output(r.board, Inversi.ICONS[player])
            turn = functions[player](self.copy(), player)
            if turn:                
                self.place(turn, player)
                output(r.board, Inversi.ICONS[player])
            player = not player
                
    def has_ended(self):
        p1 = p0 = False
        for x, y in product(range(Inversi.SIZE), repeat=2):
            p0 = p0 or self.board[x][y] == 0
            p1 = p1 or self.board[x][y] == 1

        return not (p0 and p1)

def calc_points(board, weights, player):
    summ = [0, 0]
    for x, y in product(range(Inversi.SIZE), repeat=2):
        field = board[x][y]
        summ[field % 2] += weights[field][x][y]
    return summ[player] - summ[not player]
    
def ki_random(inversi, player):
    turns = inversi.possible_turns(player)
    if turns:
        return random.choice(turns)

def ki_none(inversi, player):
    return None

def ki_minimax(inversi, player):
    weights = (GLOBAL_WEIGHTS[player], GLOBAL_WEIGHTS[not player],
               GLOBAL_WEIGHTS[player + Inversi.INVERTED_ADD], GLOBAL_WEIGHTS[(not player) + Inversi.INVERTED_ADD])    
    
    points, turn = ki_minimax_recursion(inversi, player, weights, 3)
    return turn

def ki_minimax_recursion(inversi, player, weights, recursion):
    possible_turns = inversi.possible_turns(player)    
    if recursion <= 0 or not possible_turns:
        value = calc_points(inversi.board, weights, player)
        return value, None
    
    best_turn = None
    max_value = -sys.maxint
    for turn in possible_turns:
        inversi.place(turn, player)

	# Rückgabe [0] ist die Bewertung
        value = -ki_minimax_recursion(inversi, not player, weights, recursion - 1)[0] 
        inversi.undo()
        
        if value > max_value:
            best_turn = turn
            max_value = value
    
    return max_value, best_turn

def ki_alpha_beta(inversi, player):
    weights = (GLOBAL_WEIGHTS[player], GLOBAL_WEIGHTS[not player],
               GLOBAL_WEIGHTS[player + Inversi.INVERTED_ADD], GLOBAL_WEIGHTS[(not player) + Inversi.INVERTED_ADD])    
    
    points, turn = ki_alpha_beta_recursion(inversi, player, weights, 3, -sys.maxint, sys.maxint)
    return turn
    

def ki_alpha_beta_recursion(inversi, player, weights, recursion, alpha, beta):
    possible_turns = inversi.possible_turns(player)    
    if recursion <= 0 or not possible_turns:
        value = calc_points(inversi.board, weights, player)
        return value, None
    
    best_turn = None
    max_value = alpha
    for turn in possible_turns:
        inversi.place(turn, player)

	# Rückgabe [0] ist die Bewertung
        value = -ki_alpha_beta_recursion(inversi, not player,
                                         weights, recursion - 1,
                                         -beta, -max_value)[0]
        inversi.undo()
        
        if value > max_value:
            max_value = value
            best_turn = turn
            if max_value >= beta:
                break
    
    return max_value, best_turn
    
def ki(inversi, player):
    weights = (GLOBAL_WEIGHTS[player], WEIGHTS_NULL, WEIGHTS_NULL, WEIGHTS_NULL)

    points, turn = ki_minimax_recursion(inversi, player, weights, 1)
    return turn

def player(inversi, player):
    while True:
        #print "Moegliche Zuege:"
        turns = r.possible_turns(player)
        for nr in range(len(turns)):
            print "[" + str(nr) + "] ", turns[nr][0], turns[nr][1]
        
        nr = raw_input("Zugnummer eingeben: ")
       
        return turns[int(nr)]

def output(board, player):
    print 
    print '#'*8, player, '#'*8
    print 
    line = ""
    for x in range(0, Inversi.SIZE):        
        line = ""
        for y in range(0, Inversi.SIZE):        
            line += Inversi.ICONS[board[y][x]]
        print line

if __name__ == '__main__':
    WEIGHTS_NULL = ((0,) * Inversi.SIZE, ) * Inversi.SIZE    

    WEIGHTS_P0 = (  (-5,  -6,  -7,  -7,  -6, -5),
                    (-6, -11, -21,  -21, -11, -6),
                    (-7, -21, -40,  -40, -21, -7),
                    (-7, -21, -40,  -40, -21, -7),
                    (-6, -11, -21,  -21, -11, -6),
                    (-5, -6,  -7,   -7,  -6, -5))    

    WEIGHTS_IP0 = ( (2, 1, 1, 1, 1, 2),
                    (1, 0, 0, 0, 0, 1),
                    (1, 0, -5, -5, 0, 1),
                    (1, 0, -5, -5, 0, 1),
                    (1, 0, 0, 0, 0, 1),
                    (2, 1, 1, 1, 1, 2))    

    WEIGHTS_P1 = (  (4,  4,  4,   4,  4, 4),
                    (4, -2, -5,  -5, -2, 4),
                    (4, -5, -9,  -9, -5, 4),
                    (4, -5, -9,  -9, -5, 4),
                    (4, -2, -5,  -5, -2, 4),
                    (4, 4, 4,  4,  4, 4))

    WEIGHTS_IP1 = ( (2, 1, 1, 1, 1, 2),
                    (1, 0, 0, 0, 0, 1),
                    (1, 0, -5, -5, 0, 1),
                    (1, 0, -5, -5, 0, 1),
                    (1, 0, 0, 0, 0, 1),
                    (2, 1, 1, 1, 1, 2))
                    
    GLOBAL_WEIGHTS = (WEIGHTS_P0, WEIGHTS_IP0, WEIGHTS_P1, WEIGHTS_IP1)
    #GLOBAL_WEIGHTS = (WEIGHTS_P0, WEIGHTS_NULL, WEIGHTS_P1, WEIGHTS_NULL)
    
    r = Inversi()
    r.play(X = ki_alpha_beta, O = ki_random) # alpha-beta recursion: 3
    #r.play(X = ki_minimax, O = ki_random) # Minimax recursion: 3
    #r.play(X = ki_minimax, O = ki) # Gewichtung recursion: 1
    ###
