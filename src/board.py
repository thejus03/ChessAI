from const import *
from square import Square
from piece import *
from zobrist import Zobrist
import copy
import time

class Board:
    def __init__(self):
        self.squares = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move = None
        self.white_check = False
        self.black_check = False
        self.white_checkmate = False
        self.black_checkmate = False
        self.white_stalemate = False
        self.black_stalemate = False
        self.en_passant_pos = None

        # Create and add pieces to the board
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
    
    def set_en_passant_false(self):
        """
            Set en passant to false for en passant pawns
        """
       
        if self.en_passant_pos:
            row,col = self.en_passant_pos
            self.en_passant_pos = None
            self.squares[row][col].piece.en_passant = False
        else:
            self.en_passant_pos = None

    def set_back_en_passant(self, pos):
        """
            Set back en passant to the previous state
        """
        if pos:
            row, col = pos
            self.squares[row][col].piece.en_passant = True
            self.en_passant_pos = (row, col)
        else:
            self.en_passant_pos = None
        
    def calc_all_moves(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].is_my_piece(color):
                    self.calc_moves(row, col)

    def check_gamestate(self, attack_info):
        """
            Check if the game is in checkmate or stalemate
        """
        if attack_info["checks"] >= 2:
            king_pos = attack_info["king_pos"]
            king = self.squares[king_pos[0]][king_pos[1]].piece
            self.calc_moves(king_pos[0], king_pos[1], attack_info)
            if not king.moves:
                
                if attack_info["player"] == "white":
                    self.white_checkmate = True
                else:
                    self.black_checkmate = True
                
        elif attack_info["checks"] == 1:
            bool = False
            for r in range(ROWS):
                for c in range(COLS):
                    if self.squares[r][c].is_my_piece(attack_info["player"]):
                        piece = self.squares[r][c].piece
                        self.calc_moves(r, c, attack_info)
                        if piece.moves: 
                            bool = True
                            break
            if not bool:
                if attack_info["player"] == "white":
                    self.white_checkmate = True
                else:
                    self.black_checkmate = True
                
        else:
            bool = False
            for r in range(ROWS):
                for c in range(COLS):
                    if self.squares[r][c].is_my_piece(attack_info["player"]):
                        piece = self.squares[r][c].piece
                        self.calc_moves(r, c, attack_info)
                        if piece.moves:
                            bool = True
                            break
            if not bool:
                if attack_info["player"] == "white":
                    self.white_stalemate = True
                else:
                    self.black_stalemate = True
        
        
    def get_attack_info(self, king_pos): 
        try:
            king = self.squares[king_pos[0]][king_pos[1]].piece
        except TypeError:
            self.display_board()
            
        color = self.rival_player(king.color)
        atk_squares = set()
        capturing_squares = set()
        checks = 0
        knight_moves = [(-2, 1), (-2, -1), (2, 1), (2, -1),
                    (-1, 2), (-1, -2), (1, 2), (1, -2)]
        king_moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        
        rook_directions = [(1,0), (-1,0), (0,1), (0,-1)]
        bishop_directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
        queen_directions = rook_directions + bishop_directions
        
        # Pawn attack directions depend on color
        pawn_attack_dir = [( -1, -1), ( -1, 1)] if color == "white" else [( 1, -1), ( 1, 1)]
        
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col].piece
                if piece: 
                    if piece.color == color:
                        p_type = piece.type
                        if p_type == "pawn":
                            # Mark attacked squares diagonally in front of the pawn
                            for dr, dc in pawn_attack_dir:
                                r, c = row + dr, col + dc
                                if self.within_bounds(r, c):
                                    atk_squares.add((r, c))
                                    if (r,c) == king_pos:
                                        capturing_squares.add((row, col))
                                        checks += 1

                        elif p_type == "knight":
                            for dr, dc in knight_moves:
                                r, c = row + dr, col + dc
                                if self.within_bounds(r, c):
                                    atk_squares.add((r, c))
                                    if (r,c) == king_pos:
                                        capturing_squares.add((row, col))
                                        checks += 1
                        
                        elif p_type == "king":
                            for dr, dc in king_moves:
                                r, c = row + dr, col + dc
                                if self.within_bounds(r, c):
                                    atk_squares.add((r, c))
                                    if (r,c) == king_pos:
                                        capturing_squares.add((row, col))
                                        checks += 1
                        
                        elif p_type in {"queen", "rook", "bishop"}:
                            if p_type == "queen":
                                directions = queen_directions
                            elif p_type == "rook":
                                directions = rook_directions
                            else:
                                directions = bishop_directions
                                
                            for dr, dc in directions:
                                r, c = row, col
                                possible_moves = set()
                                king_encountered = False
                                while True:
                                    r += dr
                                    c += dc
                                    if not self.within_bounds(r, c):
                                        break
                                    
                                    if self.squares[r][c].piece:
                                        if king_encountered:
                                            break
                                        
                                        if self.squares[r][c].is_rival_piece(color):
                                            atk_squares.add((r, c))
                                            if (r,c) == king_pos:
                                                capturing_squares.update(possible_moves)
                                                capturing_squares.add((row, col))
                                                checks += 1
                                                king_encountered = True
                                            elif not king_encountered:
                                                break
                                        else:
                                            atk_squares.add((r, c))
                                            break
                                        
                                    else:
                                        atk_squares.add((r, c))
                                        possible_moves.add((r, c))
                                        
                if checks >= 2:
                    break
            if checks >= 2:
                break

        data = dict()
        # squares getting attacked by rival 
        data["atk_squares"] = atk_squares
        # squares that are attacking the our king
        data["capturing_squares"] = capturing_squares
        # number of checks
        data["checks"] = checks
        # our king pos
        data["king_pos"] = king_pos
        
        data["player"] = king.color
        
        data["pinned_pieces"] = dict()

        if checks <= 1:
            data["pinned_pieces"] = self.get_pinned_pieces(king_pos)
        
        return data
    
    def get_pinned_pieces(self, king_pos):
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        king = self.squares[king_pos[0]][king_pos[1]].piece
        color = king.color
        
        pinned_pieces = dict()
        for dr,dc in directions:
            r,c = king_pos
            potential_pinned_piece = None
            while True:
                r += dr
                c += dc
                potential_moves = set()
                if self.within_bounds(r,c):
                    piece = self.squares[r][c].piece
                    if piece:
                        if potential_pinned_piece:
                            if piece.color != color:
                                if piece.type in ["rook", "bishop", "queen"]:
                                    potential_moves.add((r,c))
                                    break
                                else:
                                    potential_pinned_piece = None
                                    potential_moves = set()
                                    break
                            else:
                                potential_pinned_piece = None
                                potential_moves = set()
                                break
                        else:
                            if piece.color == color:
                                potential_pinned_piece = (r,c)
                            else:
                                potential_pinned_piece = None
                                potential_moves = set()
                                break
                    else: 
                        potential_moves.add((r,c))
                else:
                    potential_pinned_piece = None
                    potential_moves = set()
                    break

            if potential_pinned_piece:
                pinned_pieces[potential_pinned_piece] =  potential_moves

        return pinned_pieces
                
    
    def calc_moves(self, row, col, attack_info):
        """
            Calculates all possible moves given a specific row and cols and piece
        """
        # info -> {squares_targetting_king, pinned_pieces-> {piece, direction}}
        
        def get_rook_moves():
            if checks >= 2:
                return []
            
            possible_moves = []
            rook_directions = [(1,0), (-1,0), (0,1), (0,-1)]
            
            for dr, dc in rook_directions:
                r, c = row, col
                while True:
                    r += dr
                    c += dc
                    if not self.within_bounds(r, c):
                        break
                    
                    if self.squares[r][c].piece:
                        if self.squares[r][c].is_rival_piece(piece.color):
                            possible_moves.append((r, c))
                        break
                    else:
                        possible_moves.append((r, c))
            if (row,col) in pinned_pieces:
                possible_moves = [move for move in possible_moves if move in pinned_pieces[(row,col)]]

            if in_check:
                possible_moves = [move for move in possible_moves if move in capturing_squares]
            # possible_moves = [move for move in possible_moves if not self.still_in_check(row, col, move)]
            
            return possible_moves

        def get_bishop_moves():
            if checks >= 2:
                return []
            
            possible_moves = []
            bishop_directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
            for dr, dc in bishop_directions:
                r, c = row, col
                while True:
                    r += dr
                    c += dc
                    if not self.within_bounds(r, c):
                        break
                    
                    if self.squares[r][c].piece:
                        if self.squares[r][c].is_rival_piece(piece.color):
                            possible_moves.append((r, c))
                        break
                    else:
                        possible_moves.append((r, c))

            if (row,col) in pinned_pieces:
                possible_moves = [move for move in possible_moves if move in pinned_pieces[(row,col)]]
            
            # possible_moves = [move for move in possible_moves if not self.still_in_check(row, col, move)]
            if in_check:
                possible_moves = [move for move in possible_moves if move in capturing_squares]
                
            return possible_moves
                 
        piece = self.squares[row][col].piece
        if not piece:
            return []

        atk_squares = attack_info["atk_squares"]
        capturing_squares  = attack_info["capturing_squares"]
        checks = attack_info["checks"]
        king_pos = attack_info["king_pos"]
        pinned_pieces = attack_info["pinned_pieces"]
        
        in_check = checks > 0
        
        # Pawn moves 
        if piece.type == "pawn":
            if checks >= 2:
                piece.moves = []
                return
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
                    possible_moves.append(move)

            if (row,col) in pinned_pieces:
                possible_moves = [move for move in possible_moves if move in pinned_pieces[(row,col)]]
                
            if in_check:
                possible_moves = [move for move in possible_moves if move in capturing_squares]
                
            piece.moves = possible_moves
            
        # Knight moves
        elif piece.type == "knight":
            if checks >= 2:
                piece.moves = []
                return
            
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
                    possible_moves.append(move)
                    
            if (row,col) in pinned_pieces:
                possible_moves = [move for move in possible_moves if move in pinned_pieces[(row,col)]]
                
            if in_check:
                possible_moves = [move for move in possible_moves if move in capturing_squares]
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
            
            # possible_moves = [move for move in possible_moves if not self.still_in_check(row, col, move)]
            
            possible_moves = [move for move in possible_moves if move not in atk_squares]
 
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
            if left_rook and left_rook.type == "rook" and not left_rook.moved:
                if self.squares[row][1].is_empty() and self.squares[row][2].is_empty() and self.squares[row][3].is_empty():
                    return True 
                return False
            else:
                return False
        else:
            col = 7
            right_rook = self.squares[row][col].piece
            if right_rook and right_rook.type == "rook" and not right_rook.moved:
                if self.squares[row][5].is_empty() and self.squares[row][6].is_empty():
                    return True
                return False
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

    def move(self, row, col, move):
        # Remove en passant from all pawns from player
        self.set_en_passant_false()

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
                self.en_passant_pos = (move[0], move[1])
                piece.en_passant = True 

            else:
                # Check for pawn promotion
                if self.check_promotion(piece, move): 
                    self.squares[move[0]][move[1]].piece = Queen(piece.color)
                
        # King castling
        if piece.type == "king" and self.is_castling(row, col, move):
            diff = move[1] - col 
            # Move the rook
            rook = self.squares[row][0 if diff < 0 else 7].piece
            self.squares[row][0 if diff < 0 else 7].piece = None
            self.squares[move[0]][move[1] + 1 if diff < 0 else move[1] - 1].piece = rook
            rook.moved = True
            
        piece.moved = True

        self.last_move = {
            "initial": (row, col),
            "final": move 
        }
        
        
    def check_promotion(self, piece, move):
        if ( (move[0] == 0 and piece.color == "white") or (move[0] == 7 and piece.color == "black") ):
            return True
    
    def valid_move(self, piece, move):
        return move in piece.moves
    
    def undo_move(self, prev_state):
        
        start_row = prev_state["start_row"]
        start_col = prev_state["start_col"]
        end_row = prev_state["end_row"]
        end_col = prev_state["end_col"]
        captured_piece = prev_state["captured_piece"]
        castling = prev_state["castling"]
        is_en_passant_move = prev_state["is_en_passant_move"]
        en_passant_pos = prev_state["en_passant_pos"]
        pawn_promotion = prev_state["pawn_promotion"]
        moved_state = prev_state["moved_state"]
        white_checkmate = prev_state["white_checkmate"]
        black_checkmate = prev_state["black_checkmate"]
        white_stalemate = prev_state["white_stalemate"]
        black_stalemate = prev_state["black_stalemate"]
        
        self.set_en_passant_false()
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
        
        self.set_back_en_passant(en_passant_pos)
        self.white_checkmate = white_checkmate
        self.black_checkmate = black_checkmate
        self.white_stalemate = white_stalemate
        self.black_stalemate = black_stalemate

        

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
            return True  # King not found, assume in check (edge case)

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

    def display_board(self):
        board_visual = ""
        for row in range(ROWS):
            board_visual += f"{row} "  # Add row numbers (chess-style)
            for col in range(COLS):
                square = self.squares[row][col]
                if square.is_empty():
                    board_visual += ". "  # Empty square
                else:
                    piece = square.piece
                    if piece.type == "king":
                        if piece.color == "white":
                            board_visual += "♔ "
                        else:
                            board_visual += "♚ "
                    if piece.type == "queen":
                        if piece.color == "white":
                            board_visual += "♕ "
                        else:
                            board_visual += "♛ "
                    if piece.type == "rook":
                        if piece.color == "white":
                            board_visual += "♖ "
                        else:
                            board_visual += "♜ "
                    if piece.type == "bishop":
                        if piece.color == "white":
                            board_visual += "♗ "
                        else:
                            board_visual += "♝ "
                    if piece.type == "knight":
                        if piece.color == "white":
                            board_visual += "♘ "
                        else:
                            board_visual += "♞ "
                    if piece.type == "pawn":
                        if piece.color == "white":
                            board_visual += "♙ "
                        else:
                            board_visual += "♟ "
            board_visual += "\n"
        board_visual += "  0 1 2 3 4 5 6 7"  # Add column labels (chess-style)
        print(board_visual)
        print()

    def king_pos(self, color):
        if color == "white":
            for row in range(ROWS - 1, -1, -1):
                for col in range(COLS):
                    if self.squares[row][col].piece and self.squares[row][col].piece.type == "king" and self.squares[row][col].piece.color == "white":
                        return (row, col)
        
        else:
            for row in range(ROWS):
                for col in range(COLS):
                    if self.squares[row][col].piece and self.squares[row][col].piece.type == "king" and self.squares[row][col].piece.color == "black":
                        return (row, col)