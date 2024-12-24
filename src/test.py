# from board import Board
# from zobrist import Zobrist

# board = Board()
# zobrist = Zobrist()

# board.display_board()
# print(zobrist.get_hash(board, "white"))

# piece = board.squares[6][0].piece
# final_piece = board.squares[4][0].piece
# row = 6
# col = 0
# move = (4,0)
# moved_state = piece.moved
# castling = piece.type == "king" and board.is_castling(row, col, move) 
# is_en_passant_move = piece.type == "pawn" and abs(col - move[1]) == 1 and board.squares[move[0]][move[1]].is_empty()
# pawn_promotion = piece.type == "pawn" and board.check_promotion(piece, move)
# white_checkmate = board.white_checkmate
# black_checkmate = board.black_checkmate
# white_stalemate = board.white_stalemate
# black_stalemate = board.black_stalemate
# en_passant_states = board.prev_en_passant.copy() 

# board.move(6,0, (4,0))
# board.display_board()
# print(zobrist.get_hash(board, "black"))

# board.undo_move(row, col, move[0], move[1], final_piece, castling=castling, is_en_passant_move = is_en_passant_move, en_passant_states = en_passant_states, pawn_promotion = pawn_promotion, moved_state = moved_state, white_checkmate = white_checkmate, black_checkmate = black_checkmate, white_stalemate = white_stalemate, black_stalemate = black_stalemate)
# board.display_board()
# print(zobrist.get_hash(board, "white"))

from board import Board
from zobrist import Zobrist
from const import *

def print_board_and_hash(board, zobrist,color):
    board.display_board()
    print("Hash:", zobrist.get_hash(board, color))

# Initialize the board and zobrist
board = Board()
zobrist = Zobrist()

print("=== Initial State ===")
print_board_and_hash(board, zobrist, "white")
original_hash = zobrist.get_hash(board, "white")



moves = [
    (6, 4, 4, 4),  # 1)  White Pawn e2 → e4
    (1, 4, 3, 4),  # 2)  Black Pawn e7 → e5
    (7, 6, 5, 5),  # 3)  White Knight g1 → f3
    (0, 1, 2, 2),  # 4)  Black Knight b8 → c6
    (7, 5, 4, 2),  # 5)  White Bishop f1 → c4
    (0, 5, 3, 2),  # 6)  Black Bishop f8 → c5
    (6, 2, 5, 2),  # 7)  White Pawn c2 → c3
    (1, 3, 2, 3),  # 8)  Black Pawn d7 → d6
    (6, 3, 4, 3),  # 9)  White Pawn d2 → d4
    (3, 2, 2, 1),  # 10) Black Bishop c5 → b6
    (5, 5, 3, 5),  # 11) White Knight f3 → g5
    (2, 2, 1, 4),  # 12) Black Knight c6 → e7  (FIXED to avoid self-capture)
    (3, 5, 1, 5),  # 13) White Knight g5 → f7 (possible capture)
    (2, 3, 3, 3),  # 14) Black Pawn d6 → d5
    (4, 4, 3, 3),  # 15) White Pawn e4 × d5 (capture)
    (0, 3, 3, 3),  # 16) Black Queen d8 × d5 (recapture)
    (7, 3, 5, 5),  # 17) White Queen d1 → f3
    (0, 2, 4, 6),  # 18) Black Bishop c8 → g4
    (7, 2, 4, 5),  # 19) White Bishop c1 → f4
    (4, 6, 3, 7),  # 20) Black Bishop g4 → h5
]

# moves = [
#     (6,4,4,4),  # White e2-e4
#     (1,4,3,4),  # Black e7-e5
#     (7,3,3,7),  # White Qd1-h5
#     (0,1,2,2),  # Black Nb8-c6
#     (7,5,4,2),  # White Bf1-c4
#     (0,6,2,5),  # Black Ng8-f6
#     (3,7,1,5)   # White Qh5xf7#
# ]


def get_king(board, color):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.squares[row][col].piece
            if piece is not None and piece.type == "king" and piece.color == color:
                return row, col
    return None
def get_en_passant_pos(board):
    res = []
    for row in range(ROWS):
        for col in range(COLS):
            if board.squares[row][col].piece  and board.squares[row][col].piece.type == "pawn" and board.squares[row][col].piece.en_passant:
                res.append((row, col))
    return res

# We'll store the state before each move for undo operations
move_history = []

current_color = "white"
for idx, (start_r, start_c, end_r, end_c) in enumerate(moves):

        piece = board.squares[start_r][start_c].piece
        captured_piece = board.squares[end_r][end_c].piece
        moved_state = piece.moved
        castling = piece.type == "king" and board.is_castling(start_r, start_c, (end_r, end_c))
        is_en_passant_move = (piece.type == "pawn" and abs(start_c - end_c) == 1 
                            and board.squares[end_r][end_c].is_empty())
        pawn_promotion = (piece.type == "pawn" and board.check_promotion(piece, (end_r, end_c)))
        
        # Store current states to restore later
        white_checkmate = board.white_checkmate
        black_checkmate = board.black_checkmate
        white_stalemate = board.white_stalemate
        black_stalemate = board.black_stalemate
        
        # Make the move
        en_passant_pos= board.en_passant_pos
        
        board.move(start_r, start_c, (end_r, end_c))
        print(f"=== After Move {idx+1} ({current_color}) ===")
        print_board_and_hash(board, zobrist, "black" if current_color == "white" else "white")
        board.check_match()
        
        # Save the move details for undo
        move_history.append({
            "start_row": start_r,
            "start_col": start_c,
            "end_row": end_r,
            "end_col": end_c,
            "captured_piece": captured_piece,
            "castling": castling,
            "is_en_passant_move": is_en_passant_move,
            "en_passant_pos": en_passant_pos,
            "pawn_promotion": pawn_promotion,
            "moved_state": moved_state,
            "white_checkmate": white_checkmate,
            "black_checkmate": black_checkmate,
            "white_stalemate": white_stalemate,
            "black_stalemate": black_stalemate,
            "current_color": current_color,
            "moved_piece": piece
        })
        
        # Switch color
        current_color = "black" if current_color == "white" else "white"

# Now undo the moves in reverse order
print("=== Undoing Moves ===")
for idx, move_info in enumerate(reversed(move_history)):

        board.undo_move(move_info)
    
        print(f"=== After Undo {idx+1} ===")
        print_board_and_hash(board, zobrist, move_info["current_color"])
        board.check_match()

# Finally, compare hash values
final_hash = zobrist.get_hash(board, "white")
print("=== Final Comparison ===")
if final_hash == original_hash:
    print("Success: Zobrist hash matches the original state after all undos.")
else:
    print("Error: Zobrist hash does not match the original state after undos.")

