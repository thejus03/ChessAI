from const import *
from square import Square
from piece import *
import copy
import time

class Board:
    def __init__(self):
        self.squares = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move = None
        self.prev_en_passant = []
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
                    self.prev_en_passant.append((row, col))
                    self.squares[row][col].piece.en_passant = False
    
    def set_back_en_passant(self, en_passant_states):
        """
            Set back en passant to the previous state
        """
        for row, col in en_passant_states:
            self.squares[row][col].piece.en_passant = True
     
    def calc_moves(self, row, col):
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
        check = self.in_check(piece.color)
        # Pawn moves 
        if piece.type == "pawn":
            ## Adding all moves
            all_moves = []
            if piece.moved:
                if self.within_bounds(row + piece.dir, col) and self.squares[row + piece.dir][col].is_empty(): 
                    all_moves.append((row + piece.dir, col))
            else:
                if self.within_bounds(row + piece.dir, col) and self.squares[row + piece.dir][col].is_empty():
                    all_moves.append((row + piece.dir, col))
                    if self.within_bounds(row + 2 * piece.dir, col) and self.squares[row + 2 * piece.dir][col].is_empty():
                        all_moves.append((row + 2 * piece.dir, col))

            # all_moves = [move for move in all_moves if self.within_bounds(move[0], move[1]) and self.squares[move[0]][move[1]].is_empty()]

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
    
    def can_castle(self, king, side):
        if king.moved:
            return False

        if king.color == "white":
            row = 0
            
        else:
            row = 7
                
        if side == "queen":
            col = 0
            left_rook = self.squares[row][col].piece
            if left_rook and not left_rook.moved:
                return True
            else:
                return False
        else:
            col = 7
            right_rook = self.squares[row][col].piece
            if right_rook and not right_rook.moved:
                return True
            else:
                return False
 
    def is_castling(self, row, col, next_move):
        """
            Check if the move is a castling move
        """
        return abs(col - next_move[1]) == 2

    def is_en_passant_move(self, row, col, next_move):
        """
            Check if the move is an en passant move
        """
        return abs(row - next_move[0]) == 2

    def still_in_check(self, row, col , move):
        """
            Check if the move puts the player in check
        """
        board_copy = copy.deepcopy(self)
        piece = board_copy.squares[row][col].piece 
        board_copy.move(row, col, move)
        res = board_copy.in_check(piece.color)
        return res

    
    
    def move(self, row, col, move, simulate = False):
        piece = self.squares[row][col].piece
        
        # Check for en passant by checking if moving diagonal and is empty square and remove rival piece
        if piece.type == "pawn": 
            # Move diagonal to an empty space means en passant
            if abs(col - move[1]) == 1 and self.squares[move[0]][move[1]].is_empty():
                    self.squares[row][move[1]].piece = None
        
        # Move piece                    
        self.squares[row][col].piece = None
        self.squares[move[0]][move[1]].piece = piece
        
        if piece.type == "pawn":
            # Check if pawn moved by 2 rows
            if self.is_en_passant_move(row, col, move):
               piece.en_passant = True 

            else:
                # Check for pawn promotion
                if self.check_promotion(piece, move): 
                    self.squares[move[0]][move[1]].piece = Queen(piece.color)
                
        # King castling
        if piece.type == "king" and self.is_castling(row, col, move):
            diff = move[1] - col 
            # Move the rook
            self.move(row, 0 if diff < 0 else 7, (row, move[1] + 1 if diff < 0 else move[1] - 1), simulate)
            
        

        piece.moved = True
        
        self.last_move = {
            "initial": (row, col),
            "final": move 
        }
        
        # Remove en passant from all pawns from rival player
        self.prev_en_passant.clear()
        self.set_en_passant_false(self.rival_player(piece.color))
        
        
    def check_promotion(self, piece, move):
        if ( (move[0] == 0 and piece.color == "white") or (move[0] == 7 and piece.color == "black") ):
            return True
    
    def valid_move(self, piece, move):
        return move in piece.moves
    
    def undo_move(self, start_row, start_col, end_row, end_col, captured_piece, castling, is_en_passant_move, en_passant_states, pawn_promotion, moved_state):
        # Move the piece back to the start position
        self.set_back_en_passant(en_passant_states)
        piece = self.squares[end_row][end_col].piece
        self.squares[end_row][end_col].piece = captured_piece
        self.squares[start_row][start_col].piece = piece
        piece.moved = moved_state
        
        if pawn_promotion:
            self.squares[start_row][start_col].piece = Pawn(piece.color)
            self.squares[start_row][start_col].piece.moved = True
        
        if is_en_passant_move: 
            self.squares[end_row][end_col].piece = None
            self.squares[start_row][end_col].piece = Pawn(self.rival_player(piece.color))
            self.squares[start_row][end_col].piece.en_passant = True
        
        if castling:

            diff = end_col - start_col # Finds if queen side castling or king side castling
            rook = self.squares[start_row][3 if diff < 0 else 5].piece
            self.squares[start_row][3 if diff < 0 else 5].piece = None
            self.squares[start_row][0 if diff < 0 else 7].piece = rook
            rook.moved = False
        
            

    def in_check(self, color):
        # Find the king's position
        king_position = None
        for r in range(ROWS):
            for c in range(COLS):
                if self.squares[r][c].piece and self.squares[r][c].piece.type == "king" and self.squares[r][c].piece.color == color:
                    king_position = (r, c)
                    break
            if king_position:
                break

        if not king_position:
            return False  # King not found, assume not in check (edge case)

        king_row, king_col = king_position

        # Check for threats from knights
        knight_moves = [
            (king_row - 2, king_col - 1), (king_row - 2, king_col + 1),
            (king_row + 2, king_col - 1), (king_row + 2, king_col + 1),
            (king_row - 1, king_col - 2), (king_row - 1, king_col + 2),
            (king_row + 1, king_col - 2), (king_row + 1, king_col + 2),
        ]
        for move in knight_moves:
            r, c = move
            if self.within_bounds(r, c) and self.squares[r][c].is_rival_piece(color) and self.squares[r][c].piece.type == "knight":
                return True

        # Check for threats from pawns
        pawn_dir = -1 if color == "white" else 1  # Direction of pawn attack
        pawn_attacks = [(king_row + pawn_dir, king_col - 1), (king_row + pawn_dir, king_col + 1)]
        for r, c in pawn_attacks:
            if self.within_bounds(r, c) and self.squares[r][c].is_rival_piece(color) and self.squares[r][c].piece.type == "pawn":
                return True

        # Check for sliding piece threats (rooks, bishops, queens)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Rook directions (vertical, horizontal)
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop directions (diagonals)
        ]
        for dr, dc in directions:
            r, c = king_row + dr, king_col + dc
            while self.within_bounds(r, c):
                if self.squares[r][c].is_empty():
                    r += dr
                    c += dc
                    continue
                if self.squares[r][c].is_rival_piece(color):
                    piece = self.squares[r][c].piece
                    # Check if the piece can attack in the given direction
                    if (dr == 0 or dc == 0) and piece.type in ["rook", "queen"]:
                        return True  # Rook or queen attacking
                    if (dr != 0 and dc != 0) and piece.type in ["bishop", "queen"]:
                        return True  # Bishop or queen attacking
                break  # Blocked by another piece

        # Check for threats from the opposing king
        king_moves = [
            (king_row - 1, king_col - 1), (king_row - 1, king_col), (king_row - 1, king_col + 1),
            (king_row, king_col - 1),                           (king_row, king_col + 1),
            (king_row + 1, king_col - 1), (king_row + 1, king_col), (king_row + 1, king_col + 1)
        ]
        for move in king_moves:
            r, c = move
            if self.within_bounds(r, c) and self.squares[r][c].is_rival_piece(color) and self.squares[r][c].piece.type == "king":
                return True

        return False

    def rival_player(self, player):
        return "white" if player == "black" else "black"