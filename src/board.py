from const import *
from square import Square
from piece import *
import copy

class Board:
    def __init__(self):
        self.squares = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def _create(self):
        """
            Initialise all squares on the board with Square object
        """
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        """
            Initialise board with Pieces object
        """

        (rowPawn, rowRest) = (6, 7) if color == 'white' else (1, 0)

        for row in range(ROWS):
            for col in range(COLS):
                if (row == rowPawn):
                    self.squares[row][col] = Square(row, col, Pawn(color))

                if (row == rowRest): 
                    if (col == 0 or col == 7):
                        self.squares[row][col] = Square(row, col, Rook(color))
                    elif (col == 1 or col == 6):
                        self.squares[row][col] = Square(row, col, Knight(color))
                    elif (col == 2 or col == 5):
                        self.squares[row][col] = Square(row, col, Bishop(color))
                    elif (col == 3):
                        self.squares[row][col] = Square(row, col, Queen(color))
                    else:
                        self.squares[row][col] = Square(row, col, King(color))
                        
    def within_bounds(self, row, col):
        return 0 <= row < ROWS and 0 <= col < COLS
    
    def set_en_passant_false(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].is_my_piece(color) and self.squares[row][col].piece.type == "pawn":
                    self.squares[row][col].piece.en_passant = False
     
    def calc_moves(self, row, col, check = True):
        """
            Calculates all possible moves given a specific row and cols and piece
        """
        def get_rook_moves():
            possible_moves = []
            
            # Traverse up 
            r = row - 1
            while self.within_bounds(r,col):
                if self.squares[r][col].is_empty():
                    possible_moves.append((r,col))
                else:
                    if self.squares[r][col].is_rival_piece(piece.color):
                        possible_moves.append((r,col))
                    break 
                r -= 1
            
            # Traverse down
            r = row + 1
            while self.within_bounds(r, col):
                if self.squares[r][col].is_empty():
                    possible_moves.append((r,col))
                else:
                    if self.squares[r][col].is_rival_piece(piece.color):
                        possible_moves.append((r,col))
                    break 
                r += 1
            
            # Traverse right
            c = col + 1
            while self.within_bounds(row, c):
                if self.squares[row][c].is_empty():
                    possible_moves.append((row,c))
                else:
                    if self.squares[row][c].is_rival_piece(piece.color):
                        possible_moves.append((row,c))
                    break 
                c += 1
            
            # Traverse left
            c = col - 1  
            while self.within_bounds(row, c):
                if self.squares[row][c].is_empty():
                    possible_moves.append((row,c))
                else:
                    if self.squares[row][c].is_rival_piece(piece.color):
                        possible_moves.append((row,c))
                    break 
                c -= 1

            if check:    
                possible_moves = [move for move in possible_moves if not self.still_in_check(row, col, move)]
            
            return possible_moves

        def get_bishop_moves():
            possible_moves = []
            # Traverse top left
            r = row - 1
            c = col - 1
            while self.within_bounds(r,c):
                if self.squares[r][c].is_empty():
                    possible_moves.append((r,c))
                else:
                    if self.squares[r][c].is_rival_piece(piece.color):
                        possible_moves.append((r,c))
                    break 
                r -= 1
                c -= 1
                
            # Traverse top right
            r = row - 1
            c = col + 1
            while self.within_bounds(r,c):
                if self.squares[r][c].is_empty():
                    possible_moves.append((r,c))
                else:
                    if self.squares[r][c].is_rival_piece(piece.color):
                        possible_moves.append((r,c))
                    break 
                r -= 1
                c += 1
                 
            # Traverse bottom left
            r = row + 1
            c = col - 1
            while self.within_bounds(r,c):
                if self.squares[r][c].is_empty():
                    possible_moves.append((r,c))
                else:
                    if self.squares[r][c].is_rival_piece(piece.color):
                        possible_moves.append((r,c))
                    break 
                r += 1
                c -= 1

            # Traverse bottom right
            r = row + 1
            c = col + 1
            while self.within_bounds(r,c):
                if self.squares[r][c].is_empty():
                    possible_moves.append((r,c))
                else:
                    if self.squares[r][c].is_rival_piece(piece.color):
                        possible_moves.append((r,c))
                    break 
                r += 1
                c += 1
            
            if check:
                possible_moves = [move for move in possible_moves if not self.still_in_check(row, col, move)]

            return possible_moves
                 
        piece = self.squares[row][col].piece
        if not piece:
            return []
        
        # Pawn moves 
        if piece.type == "pawn":
            ## Adding all moves
            if piece.moved:
                all_moves = [(row + piece.dir, col)] 
            else:
                all_moves = [(row + piece.dir, col), (row + 2 * piece.dir, col)] 

            all_moves = [move for move in all_moves if self.within_bounds(move[0], move[1]) and self.squares[move[0]][move[1]].is_empty()]

            if self.within_bounds(row + piece.dir, col + 1) and self.squares[row + piece.dir][col + 1].is_rival_piece(piece.color):
                all_moves.append((row + piece.dir, col + 1))
            if self.within_bounds(row + piece.dir, col - 1) and self.squares[row + piece.dir][col - 1].is_rival_piece(piece.color):
                all_moves.append((row + piece.dir, col - 1))
            
            ## Filtering out of bounds moves 
            moves_within_bounds = all_moves
            
            # en passant moves
            r = 3 if piece.color == "white" else 4
            if row == r:
                # left en passant
                if self.within_bounds(r, col - 1) and self.squares[r][col - 1].is_rival_piece(piece.color) and self.squares[r][col-1].piece.type == "pawn" and self.squares[r][col - 1].piece.en_passant:
                    moves_within_bounds.append((row + piece.dir, col - 1))
                # right en passant
                if self.within_bounds(r, col + 1) and self.squares[r][col + 1].is_rival_piece(piece.color) and self.squares[r][col+1].piece.type == "pawn" and self.squares[r][col + 1].piece.en_passant:
                    moves_within_bounds.append((row + piece.dir, col + 1))
                
            possible_moves = []
            for move in moves_within_bounds:
                if self.squares[move[0]][move[1]].is_empty_or_rival(piece.color):
                    if check:
                        if not self.still_in_check(row, col, move):
                            possible_moves.append(move)
                    else:
                        possible_moves.append(move)
            piece.moves = possible_moves
            
        # Knight moves
        elif piece.type == "knight":
            # 8 total moves
            all_moves = [
                (row-2, col+1), 
                (row-2, col-1),
                (row+2, col+1),
                (row+2, col-1),
                (row-1, col+2),
                (row-1, col-2),
                (row+1, col+2),
                (row+1, col-2)
            ]
            
            # Check if out of bounds
            moves_within_bounds = [move for move in all_moves if self.within_bounds(move[0], move[1])]
            # Finds if the move is empty or has a rival piece 
            possible_moves = []
            for move in moves_within_bounds:
                if self.squares[move[0]][move[1]].is_empty_or_rival(piece.color):
                    if check:
                        if not self.still_in_check(row, col, move):
                            possible_moves.append(move)
                    else:
                        possible_moves.append(move)
            piece.moves = possible_moves
        
        elif piece.type == "rook":
            piece.moves = get_rook_moves()
        
        elif piece.type == "bishop":
            piece.moves = get_bishop_moves()
            
        elif piece.type == "queen":
            # Combine rook and bishop moves
            possible_moves = []
            for move in get_rook_moves():
                possible_moves.append(move)
            for move in get_bishop_moves():
                possible_moves.append(move) 
            piece.moves = possible_moves

        else: # King
            all_moves = [
                (row + 1, col),
                (row + 1, col + 1),
                (row + 1, col - 1),
                (row - 1, col + 1),
                (row - 1, col - 1),
                (row - 1, col),
                (row, col + 1),
                (row, col - 1),
            ]
            possible_moves = [] 
            for move in all_moves:
                if self.within_bounds(move[0],move[1]):
                    if self.squares[move[0]][move[1]].is_empty() or self.squares[move[0]][move[1]].is_rival_piece(piece.color):
                       possible_moves.append(move) 
            
            # Castling
            if not piece.moved:
                # Queen castling
                left_rook = self.squares[row][0].piece
                if left_rook and left_rook.type == "rook" and not left_rook.moved:
                    for c in range(1,4):
                        if not self.squares[row][c].is_empty():
                            break
                        if c == 3:
                            piece.left_rook = left_rook
                            possible_moves.append((row, 2))
                            
                
                # King castling
                right_rook = self.squares[row][7].piece
                if right_rook and right_rook.type == "rook" and not right_rook.moved:
                    for c in range(5,7):
                        if not self.squares[row][c].is_empty():
                            break
                        if c == 6:
                            piece.right_rook = right_rook
                            possible_moves.append((row, 6))
            if check:
                possible_moves = [move for move in possible_moves if not self.still_in_check(row, col, move)]

            piece.moves = possible_moves

    def castling(self, row, col, next_move):
        """
            Check if the move is a castling move
        """
        return abs(col - next_move[1]) == 2

    def en_passant(self, row, col, next_move):
        """
            Check if the move is an en passant move
        """
        return abs(row - next_move[0]) == 2

    def in_check(self, color):
        for r in range(ROWS):
            for c in range(COLS):
                if self.squares[r][c].is_rival_piece(color):
                    piece = self.squares[r][c].piece
                    self.calc_moves(r,c, False)
                    
                    for m in piece.moves:
                        if self.squares[m[0]][m[1]].piece and self.squares[m[0]][m[1]].piece.type == "king":
                            return True
        return False
    
    def still_in_check(self, row, col , move):
        """
            Check if the move puts the player in check
        """
        board_copy = copy.deepcopy(self)
        piece = board_copy.squares[row][col].piece 
        board_copy.move(row, col, move)
        for r in range(ROWS):
            for c in range(COLS):
                if board_copy.squares[r][c].is_rival_piece(piece.color):
                    p = board_copy.squares[r][c].piece
                    board_copy.calc_moves(r,c, False)
                    
                    for m in p.moves:
                        if board_copy.squares[m[0]][m[1]].piece and board_copy.squares[m[0]][m[1]].piece.type == "king":
                            return True
        return False

    def move(self, row, col, move):
        piece = self.squares[row][col].piece
        
        
        # Pawn promotion
        if piece.type == "pawn":
            # Check for en passant
            if self.en_passant(row, col, move):
               piece.en_passant = True 

            else:
                # Check for pawn promotion
                self.check_promotion(piece, move)
                
                # Check for en passant by checking if moving diagonal and is empty square and remove rival piece
                if abs(col - move[1]) == 1 and self.squares[move[0]][move[1]].is_empty():
                    self.squares[row][move[1]].piece = None
        
        # King castling
        if piece.type == "king" and self.castling(row, col, move):
            diff = move[1] - col 
            # Move the rook
            self.move(row, 0 if diff < 0 else 7, (row, move[1] + 1 if diff < 0 else move[1] - 1))
            
        self.squares[row][col].piece = None
        self.squares[move[0]][move[1]].piece = piece
        piece.moved = True
        
        self.last_move = {
            "initial": (row, col),
            "final": move 
        }
        
    def check_promotion(self, piece, move):
        if (move[0] == 0 or move[0] == 7):
            self.squares[move[0]][move[1]].piece = Queen(piece.color)
    
    def valid_move(self, piece, move):
        return move in piece.moves