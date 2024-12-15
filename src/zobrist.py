import random
from const import *

class Zobrist:
    def __init__(self):
        self.zobrist_table = [ [ [random.getrandbits(64) for _ in range(COLS)] for _ in range(ROWS) ]  for _ in range(NUM_PIECES)]

        self.zobrist_castling = [random.getrandbits(64) for _ in range(4)] # 2 for white, 2 for black
        
        # Indexes for specific pieces
        self.pieces = {
            "white": {
                "pawn": 0,
                "knight": 1,
                "bishop": 2,
                "rook": 3,
                "queen": 4,
                "king": 5
            },
            "black": {
                "pawn": 6,
                "knight": 7,
                "bishop": 8,
                "rook": 9,
                "queen": 10,
                "king": 11
            }
        }
        
        self.zobrist_en_passant = [ [random.getrandbits(64) for _ in range(COLS) ] for _ in range(ROWS)]
        self.zobrist_turn = random.getrandbits(64) # For black's turn
        
    def _piece_index(self, piece):
        return self.pieces[piece.color][piece.type]
    
    def get_hash(self, board, player):
        """
            Generates Hash value of board using the Zobrist Hashing algorithm
        """
        
        hash_value = 0
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                piece = square.piece
                if piece is not None:
                    piece_index = self._piece_index(piece)
                    hash_value ^= self.zobrist_table[piece_index][row][col]

                    # En passant
                    if piece.type == "pawn" and piece.en_passant:
                        hash_value = self.zobrist_en_passant[row][col]     
                    
                    if piece.type == "king":
                        rights = self._get_castling_rights(board, piece)
                        
                        if rights & 1: # White kingside
                            hash_value ^= self.zobrist_castling[0]
                        if rights & 2: # White queenside
                            hash_value ^= self.zobrist_castling[1]
                        if rights & 4: # Black kingside
                            hash_value ^= self.zobrist_castling[2]
                        if rights & 8: # Black queenside
                            hash_value ^= self.zobrist_castling[3]
                           
        # Player's turn
        if player == "black":
            hash_value ^= self.zobrist_turn
        
        return hash_value
    
    def _get_castling_rights(self, board, piece):
        """
            Returns castling rights of the board
        """
        rights = 0
        
        if board.can_castle(piece, "king"):
            if piece.color == "white":
                rights |= 1 
            else:
                rights |= 4
        
        if board.can_castle(piece, "queen"):
            if piece.color == "white":
                rights |= 2
            else:
                rights |= 8
        
        return rights