############################################################
# Sudoku Solver
############################################################

student_name = "Brendan McCaffrey"

############################################################
# Imports
############################################################

import copy
import numpy as np
import random

############################################################
# Sudoku Solver
############################################################

def sudoku_cells():
    cells = []
    for y in range(9):
        for x in range(9):
            cells.append((y,x))
    return cells

def box(cell):
    # check left three boxes
    if cell[0] < 3:
        if cell[1] < 3:
            return (0,0)
        elif cell[1] < 6:
            return (0,1)
        elif cell[1] < 9:
            return (0,2)
        else:
            print("Invalid cell")
    # check middle three
    elif cell[0] < 6:
        if cell[1] < 3:
            return (1,0)
        elif cell[1] < 6:
            return (1,1)
        elif cell[1] < 9:
            return (1,2)
        else:
            print("Invalid cell")
    # check right three
    elif cell[0] < 9:
        if cell[1] < 3:
            return (2,0)
        elif cell[1] < 6:
            return (2,1)
        elif cell[1] < 9:
            return (2,2)
        else:
            print("Invalid cell")
    else:
        print("Invalid cell")


# return list of arc constraints
def sudoku_arcs():
    cells = sudoku_cells()
    arcs = []
    for cell1 in cells:
        for cell2 in cells:
            if cell1 != cell2:
                if cell1[0] == cell2[0]:
                    arcs.append((cell1, cell2))
                elif cell1[1] == cell2[1]:
                    arcs.append((cell1, cell2))
                elif box(cell1) == box(cell2):
                    arcs.append((cell1, cell2))
    return arcs

# find constraints to c1 not including c2
def neighbors(c1, c2):
    neighbors = []
    for cell in sudoku_cells():
        if c1 != cell and c2 != cell:
            if c1[0] == cell[0]:
                neighbors.append((cell, c1))
            elif c1[1] == cell[1]:
                neighbors.append((cell, c1))
            elif box(c1) == box(cell):
                neighbors.append((cell, c1))
    return neighbors


# create game board given csv
def read_board(path):
    board = {}
    file1 = open(path, "r")
    rows = file1.readlines()
    y = 0
    x = 0
    for row in rows:
        for elt in row:
            if elt != "\n":
                if elt == "*":
                    board[(y,x)] = {'1','2','3','4','5','6','7','8','9'}
                else:
                    board[(y,x)] = {elt}
            x += 1
        y += 1
        x = 0
    return board

# Sudoku class
class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    # create Sudoku instance
    def __init__(self, board):
        self.my_board = board

    # return value possibilities for cell
    def get_values(self, cell):
        return self.my_board[cell]

    # narrow possibilities
    def remove_inconsistent_values(self, cell1, cell2):
        if len(self.my_board[cell2]) == 1:
            c2_val = list(self.my_board[cell2])[0]
            if c2_val in self.my_board[cell1]:
                self.my_board[cell1].remove(c2_val)
                return True
        return False

    # return unsolved cell with least amount of possible values
    def find_most_constrained(self):
        most_constrained = (None, None)
        min_poss = 10
        for cell in Sudoku.CELLS:
            if len(self.my_board[cell]) > 1 and len(self.my_board[cell]) < min_poss:
                min_poss = len(self.my_board[cell])
                most_constrained = cell
        return most_constrained

    # solve by inference through row
    def row_inference(self, cell):
        arc_options = set()
        if (len(self.my_board[cell]) == 1):
            return True
        else:
            for c2 in Sudoku.CELLS:
                if cell != c2:
                    if cell[0] == c2[0]:
                        for elt in self.my_board[c2]:
                            arc_options.add(elt)
        if len(self.my_board[cell].difference(arc_options)) > 0:
            for x in self.my_board[cell].intersection(arc_options):
                self.my_board[cell].remove(x)
            if len(self.my_board[cell]) == 1:
                return True
        return False

    # solve by inference through col
    def col_inference(self, cell):
        arc_options = set()
        if (len(self.my_board[cell]) == 1):
            return True
        else:
            for c2 in Sudoku.CELLS:
                if cell != c2:
                    if cell[1] == c2[1]:
                        for elt in self.my_board[c2]:
                            arc_options.add(elt)
        if len(self.my_board[cell].difference(arc_options)) > 0:
            for x in self.my_board[cell].intersection(arc_options):
                self.my_board[cell].remove(x)
            if len(self.my_board[cell]) == 1:
                return True
        return False         

    # solve by inference through box
    def box_inference(self, cell):
        arc_options = set()
        if (len(self.my_board[cell]) == 1):
            return True
        else:
            for c2 in Sudoku.CELLS:
                if cell != c2:
                    if box(cell) == box(c2):
                        for elt in self.my_board[c2]:
                            arc_options.add(elt)
        if len(self.my_board[cell].difference(arc_options)) > 0:
            for x in self.my_board[cell].intersection(arc_options):
                self.my_board[cell].remove(x)
            if len(self.my_board[cell]) == 1:
                return True
        return False

    # solve with basic ac3 search algo
    def infer_ac3(self):
        queue = copy.deepcopy(Sudoku.ARCS)
        while len(queue) > 0:
            (c1, c2) = queue.pop()
            if self.remove_inconsistent_values(c1,c2):
                for x in neighbors(c1, c2):
                    if x not in queue:
                        queue.append(x)

    # improve ac3 to infer across mutliple constraints
    def infer_improved(self):
        count = 0
        while not self.isSolved() and count < 100:
            count += 1
            self.infer_ac3()
            for cell in Sudoku.CELLS:
                if len(self.my_board[cell]) > 1:
                    if not self.row_inference(cell):
                        if not self.col_inference(cell):
                            self.box_inference(cell)
        return self.isSolved()

    # improve inference to guess and check if need be
    def infer_with_guessing(self):
        if self.infer_improved():
            return True

        og = copy.deepcopy(self.my_board)
        cell = self.find_most_constrained()

        if (cell[0] == None or cell[1] == None):
            return False

        options = copy.deepcopy(self.my_board[cell])
        val = set()

        for num in options:
            val.add(num)
            self.my_board[cell] = val
            if self.infer_with_guessing():
                return True
            self.my_board = copy.deepcopy(og)
            val.remove(num)
        return False

    # print function helper to show current state of sudoku board
    def pretty_print(self):
        for y in range(9):
            for x in range(9):
                if len(self.my_board[(y,x)]) > 1:
                    print("*", end='')
                elif len(self.my_board[(y,x)]) == 1:
                    elem = self.my_board[(y,x)].pop()
                    print(elem, end='')
                    self.my_board[(y,x)].add(elem)
                else:
                    print((y,x), " ", self.my_board[(y,x)])
            print()

    # check is solved
    def isSolved(self):
        for x in Sudoku.CELLS:
            if len(self.my_board[x]) != 1:
                # print(x, self.get_values(x))
                return False
        return True

############################################################
# Dominoes Game
############################################################

# below is a similar game solver for a domino game wherein 
# p1 and p2 place vertical and horizontal pieces, respectively
# first player with no moves left loses

def create_dominoes_game(rows, cols):
    board = [[False for i in range(cols)] for j in range(rows)]
    return DominoesGame(board)

class DominoesGame(object):

    # Required
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])

    def get_board(self):
        return self.board

    def reset(self):
        self.board = [[False for i in range(self.cols)] for j in range(self.rows)]

    def is_legal_move(self, row, col, vertical):
        if vertical:
            if row < self.rows - 1 and row >= 0:
                return (not self.board[row][col]) and (not self.board[row+1][col])
            return False
        else:
            if col < self.cols - 1 and col >= 0:
                return (not self.board[row][col]) and (not self.board[row][col+1])

    def legal_moves(self, vertical):
        for y in range(self.rows):
            for x in range(self.cols):
                if self.is_legal_move(y, x, vertical):
                    yield (y,x)


    def perform_move(self, row, col, vertical):
        if self.is_legal_move(row, col, vertical):
            if vertical:
                self.board[row][col] = True
                self.board[row+1][col] = True
            if not vertical:
                self.board[row][col] = True
                self.board[row][col+1] = True

    def game_over(self, vertical):
        return len(list(self.legal_moves(vertical))) == 0

    def copy(self):
        newboard = [row[:] for row in self.board]
        return DominoesGame(newboard)

    def successors(self, vertical):
        for r, c in self.legal_moves(vertical):
            duplicate = self.copy()
            duplicate.perform_move(r, c, vertical)
            yield ((r, c), duplicate)

    def get_random_move(self, vertical):
        moves = list(self.legal_moves(vertical))
        return random.choice(moves)

    def value(self, vertical):
        curr_moves = len(list(self.legal_moves(vertical)))
        opp_moves = len(list(self.legal_moves(not vertical)))
        return curr_moves - opp_moves

    def get_best_move(self, vertical, limit):
        if limit == 0:
            return ("no move available")
        v = -9999
        best_m = None
        if len(list(self.legal_moves(vertical))) > 0:
            for m, new_g in self.successors(vertical):
                if new_g.maxVal(vertical, limit - 1, 0)[0] > v:
                    v = new_g.minVal(vertical, limit - 1, 0)
            self.perform_move(best_m[0], best_m[1], vertical)
            return (best_m, self.maxVal(vertical, limit - 1, 0)[0], self.maxVal(vertical, limit - 1, 0)[1])           
        else:
            return ("no move available")

    def maxVal(self, vertical, limit, leaves):
        if limit == 0:
            return (self.value(vertical), leaves)
        v = -9999
        if len(list(self.legal_moves(vertical))) > 0:
            for m, new_g in self.successors(vertical):
                if new_g.minVal(vertical, limit - 1)[0] > v:
                    v = new_g.minVal(vertical, limit - 1, leaves)
            self.perform_move(best_m[0], best_m[1], vertical)
            return (self.minVal(vertical, limit - 1, leaves))           
        else:
            return (self.value(vertical), leaves + 1)
        
        

    def minVal(self, vertical, limit, leaves):
        if limit == 0:
            return (0 - self.value(vertical), leaves + 1)
        v = 9999
        if len(list(self.legal_moves(vertical)))[0] > 0:
            for m, new_g in self.successors(vertical):
                if new_g.maxVal(vertical, limit - 1) < v:
                    v = new_g.minVal(vertical, limit - 1)
            self.perform_move(best_m[0], best_m[1], vertical)
            return (self.maxVal(vertical, limit - 1, leaves))           
        else:
            return (self.value(vertical), leaves + 1)
        
        
        
############################################################
# Sandbox calls
############################################################



if __name__ == "__main__": 
    
    b = read_board("sudoku_boards/hard2.txt")
    sudoku = Sudoku(b)
    print("We are going to attempt to solve the hard sudoku puzzle shown below:")
    sudoku.pretty_print()
    print("Solving ...")
    print("The success of our solution is", sudoku.infer_with_guessing())
    sudoku.pretty_print()

    # for col in [0,1,4]:
    #     removed = sudoku.remove_inconsistent_values((0,3), (0,col))
    #     print(removed, sudoku.get_values((0,3)))

    # sudoku.infer_improved()

    # sudoku.box_inference((0,7))

    # print(neighbors((0,0), (0,1)))

    # print(sudoku_cells())

    # print(((0, 0), (2, 1)) in sudoku_arcs())
    # print(((2, 3), (0, 0)) in sudoku_arcs())

    
