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



# moves = [
#     (6, 4, 4, 4),  # White pawn e2-e4
#     (1, 4, 3, 4),  # Black pawn e7-e5
#     (7, 6, 5, 5),  # White knight g1-f3
#     (0, 1, 2, 2),  # Black knight b8-c6
#     (7, 5, 5, 3),  # White bishop f1-d3 (path cleared by white’s e-pawn move)
#     (0, 6, 2, 5),  # Black knight g8-f6 (instead of a blocked bishop move)
#     (7, 3, 5, 5),  # White queen d1-f3 (a short, unobstructed diagonal move)
#     (0, 3, 1, 4),  # Black queen d8-e7 (one-step diagonal, no blockage)
#     (6, 3, 4, 3),  # White pawn d2-d4
#     (3, 4, 4, 3),  # Black pawn e5xd4 (normal capture, not en passant)
#     (7, 2, 4, 5),  # White bishop c1-f4 (long diagonal, now unobstructed)
#     (2, 2, 4, 3),  # Black knight c6-d4 (a legal knight jump)
#     (7, 1, 5, 2),  # White knight b1-c3 (knight jump)
#     (0, 7, 0, 5),  # Black rook h8-f8 (now possible as g8 square is free)
#     (6, 7, 4, 7),  # White pawn h2-h4 (two-step pawn move)
#     (1, 6, 3, 6),  # Black pawn g7-g5 (two-step pawn move)
#     (7, 4, 7, 6),  # White king e1-g1 (castling kingside, path is clear)
#     (0, 4, 1, 4),  # Black king e8-e7 (a simple king move)
# ]
# moves = [
#     (6,4,4,4),  # White e2-e4
#     (1,4,3,4),  # Black e7-e5
#     (6,3,4,3),  # White d2-d4
#     (1,3,3,3),  # Black d7-d5
#     (4,4,3,3),  # White e4xd5 en passant
#     (0,6,2,5),  # Black Ng8-f6
#     (7,6,5,5),  # White Ng1-f3
#     (0,5,3,2),  # Black Bf8-c5
#     (7,5,5,3),  # White Bf1-d3
#     (7,4,7,6),  # White O-O
#     (0,4,0,6),  # Black O-O
#     (6,7,4,7),  # White h2-h4
#     (1,6,3,6),  # Black g7-g5
#     (4,7,3,6),  # White h4xg5 en passant
#     (6,0,4,0),  # White a2-a4
#     (1,0,2,0),  # Black a7-a6
#     (4,0,3,0),  # White a4xa5
#     (3,0,2,0),  # White a5-a6
#     (2,0,1,0),  # White a6-a7
#     (1,0,0,0),  # White a7-a8=Q
#     (7,3,4,6),  # White Qd1-g4+
#     (2,5,1,7),  # Black Rh8-h7
#     (0,0,0,7)   # White Qa8-h8# (checkmate)
# ]

moves = [
    (6,4,4,4),  # White e2-e4
    (1,4,3,4),  # Black e7-e5
    (7,3,3,7),  # White Qd1-h5
    (0,1,2,2),  # Black Nb8-c6
    (7,5,4,2),  # White Bf1-c4
    (0,6,2,5),  # Black Ng8-f6
    (3,7,1,5)   # White Qh5xf7#
]


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
        final_piece = board.squares[end_r][end_c].piece
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
        # print(f"In check: {board.in_check('black' if current_color == 'white' else 'white')}")
        print(f"White checkmate: {board.white_checkmate}")
        print(f"Black checkmate: {board.black_checkmate}")
        print(f"White stalemate: {board.white_stalemate}")
        print(f"Black stalemate: {board.black_stalemate}")
        
        # Save the move details for undo
        move_history.append({
            "start_r": start_r,
            "start_c": start_c,
            "end_r": end_r,
            "end_c": end_c,
            "final_piece": final_piece,
            "castling": castling,
            "is_en_passant_move": is_en_passant_move,
            "en_passant_pos": en_passant_pos,
            "pawn_promotion": pawn_promotion,
            "moved_state": moved_state,
            "white_checkmate": white_checkmate,
            "black_checkmate": black_checkmate,
            "white_stalemate": white_stalemate,
            "black_stalemate": black_stalemate,
            "current_color": current_color
        })
        
        # Switch color
        current_color = "black" if current_color == "white" else "white"

# Now undo the moves in reverse order
print("=== Undoing Moves ===")
for idx, move_info in enumerate(reversed(move_history)):

        board.undo_move(move_info["start_r"],
                        move_info["start_c"],
                        move_info["end_r"],
                        move_info["end_c"],
                        move_info["final_piece"],
                        castling=move_info["castling"],
                        is_en_passant_move=move_info["is_en_passant_move"],
                        en_passant_pos=move_info["en_passant_pos"],
                        pawn_promotion=move_info["pawn_promotion"],
                        moved_state=move_info["moved_state"],
                        white_checkmate=move_info["white_checkmate"],
                        black_checkmate=move_info["black_checkmate"],
                        white_stalemate=move_info["white_stalemate"],
                        black_stalemate=move_info["black_stalemate"])
    
        print(f"=== After Undo {idx+1} ===")
        print_board_and_hash(board, zobrist, move_info["current_color"])
        print(f"White checkmate: {board.white_checkmate}")
        print(f"Black checkmate: {board.black_checkmate}")
        print(f"White stalemate: {board.white_stalemate}")
        print(f"Black stalemate: {board.black_stalemate}")
        

# Finally, compare hash values
final_hash = zobrist.get_hash(board, "white")
print("=== Final Comparison ===")
if final_hash == original_hash:
    print("Success: Zobrist hash matches the original state after all undos.")
else:
    print("Error: Zobrist hash does not match the original state after undos.")

