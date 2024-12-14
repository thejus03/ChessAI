from const import *

class Square:
    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece
        
    def has_piece(self):
        return self.piece != None
    
    def is_empty(self):
        return not self.has_piece() 
        
    def is_empty_or_rival(self, color):
        return not self.has_piece() or self.is_rival_piece(color)
    
    def is_my_piece(self, color):
        return self.has_piece() and self.piece.color == color
    
    def is_rival_piece(self, color):
        return self.has_piece() and self.piece.color != color