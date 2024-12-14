import os

class Piece:
    def __init__(self, piece_type, color, value):
       self.type = piece_type 
       self.color = color

        # value_sign = -1 if color == 'white' else 1 # value sign is positive for white and negative for black
       self.value = value 
       self.image = None
       self.image_rect = None
       self.set_image()
       
       self.moves = []
       self.moved = False
    
    def set_image(self, size=80):
        self.image = os.path.join(f'images/imgs-{size}px/{self.color}_{self.type}.png')

    def add_move(self, move):
        self.moves.append(move)

class Pawn(Piece):
    def __init__(self, color):
        super().__init__('pawn', color, 1.0) # pawn has value 1 for minimax
        self.dir = -1 if color == 'white' else 1
        self.en_passant = False

class Knight(Piece):
    def __init__(self, color):
        super().__init__('knight', color, 3.05) # knight has value 3 for minimax

class Bishop(Piece):
    def __init__(self, color):
        super().__init__('bishop', color, 3.33) # bishop has value 3 for minimax
        
class Rook(Piece):
    def __init__(self, color):
        super().__init__('rook', color, 5.63) # rook has value 5 for minimax

class Queen(Piece):
    def __init__(self, color):
        super().__init__('queen', color, 9.5) # queen has value 9 for minimax

class King(Piece):
    def __init__(self, color):
        self.left_rook = None  
        self.right_rook = None
        super().__init__('king', color, 200) # King has a very high value for minimax
