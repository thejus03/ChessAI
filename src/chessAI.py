import copy
from const import *
import random
import time

class ChessAI:
    def __init__(self):
        self.board = None
        self.count = 0
        self.prune = 0
        self.depth = None
    
    def iterative_deepening(self, max_depth, time_limit):
        start_time = time.time()
        best_move = None

        for depth in range(1, max_depth + 1):
            # Perform a minimax search at the current depth
            move = self.minimax(depth, float('-inf'), float('inf'), "black", start_time, time_limit)

            # Update the best move if the search completed
            if move:
                best_move = move

            # Break if we've exceeded the time limit
            if time.time() - start_time >= time_limit:
                self.depth = depth
                break

        return best_move
    
    def eval_board(self):
        # Count the material difference between white and black
        white_score = 0
        black_score = 0
        for row in range(ROWS):
            for col in range(COLS):
                p = self.board.squares[row][col].piece
                if p:
                    if p.color == "white":
                        white_score += p.value
                    else:
                        black_score += p.value
        return white_score - black_score
    
    def move_heuristic(self, move, piece, player):
        r, c = move
        final_square = self.board.squares[r][c]
        heuristic = 0

        # Captures: Value of captured piece
        if final_square.is_rival_piece(player):
            heuristic += final_square.piece.value * 10  # Capture is highly prioritized


        # # Central control: Bonus for moves toward the center
        center_dist = abs(r - 3.5) + abs(c - 3.5)
        heuristic += (4 - center_dist)  # Closer to center gets higher score

        # Positional improvements: Adjust based on type of piece
        
       # Positional improvements: Adjust based on type of the moving piece
        if piece.type == "pawn":
            heuristic += 1  # Pawns moving forward slightly prioritized
        elif piece.type == "knight" or piece.type == "bishop":
            heuristic += 2  # Knights and bishops moving toward action zones
        elif piece.type == "rook":
            heuristic += 1.5  # Rooks slightly prioritized for activity
        elif piece.type == "queen":
            heuristic += 1.2  # Queens should remain active
        elif piece.type == "king":
            heuristic -= 2  # Avoid unnecessary king moves unless castling

        return heuristic

    
    def minimax(self, depth, alpha, beta, player, start_time = None, time_limit = None):
        if start_time and time.time() - start_time >= time_limit:
            return None  # Abort search if time is up
        
        if depth == 0:
            # Score, Move, Square
            return (self.eval_board(), None, None)     
        else:
            # if self.hash_board(self.board) in self.cache:
            #     self.counter += 1
                # return self.cache[self.hash_board(self.board)]
            best_move = None
            for row in range(ROWS):
                for col in range(COLS):
                    
                    if self.board.squares[row][col].is_my_piece(player):
                        square = self.board.squares[row][col]
                        piece = square.piece
                        
                        self.board.calc_moves(row, col)

                        # piece.moves.sort(key = lambda x: self.get_score(x, player), reverse = True)

                        # piece.moves.sort(key=lambda move: self.move_heuristic(move, piece, player), reverse = (player == "white"))

                        for move in piece.moves:
                            
                            final_piece = self.board.squares[move[0]][move[1]].piece

                            moved_state = piece.moved
                            castling = piece.type == "king" and self.board.castling(row, col, move) 
                            en_passant = piece.type == "pawn" and abs(col - move[1]) == 1 and self.board.squares[move[0]][move[1]].is_empty()
                            pawn_promotion = piece.type == "pawn" and self.board.check_promotion(piece, move)

                            # Do the move
                            self.board.move(row, col, move)    

                            res = self.minimax(depth - 1, alpha, beta, self.next_player(player), start_time, time_limit)
                            self.count += 1

                            # Undo the move                            
                            self.board.undo_move(row, col, move[0], move[1], final_piece, castling=castling, en_passant = en_passant, pawn_promotion = pawn_promotion, moved_state = moved_state)

                            if res:
                                if best_move:
                                    # Maximising player
                                    if player == "white":
                                        if (best_move[0] < res[0]):
                                            best_move = (res[0], move, square)
                                        elif (best_move[0] == res[0]):
                                            # Pick randomly between the two choices
                                            opt = random.choice([0,1])
                                            if opt == 1:
                                                best_move = (res[0], move, square)
                                        alpha = max(alpha, best_move[0])        
                                        if beta <= alpha:
                                            self.prune += 1
                                            return best_move

                                    # Minimising player
                                    else:
                                        if (best_move[0] > res[0]):
                                            best_move = (res[0], move, square)

                                        elif (best_move[0] == res[0]):
                                            # Pick randomly between the two choices
                                            opt = random.choice([0,1])
                                            if opt == 1:
                                                best_move = (res[0], move, square)
                                        beta = min(beta, best_move[0])
                                        if beta <= alpha:
                                            self.prune += 1
                                            return best_move
                                else:
                                    best_move = (res[0], move, square)
        # self.cache[self.hash_board(self.board)] = best_move
        return best_move
    
    def next_move(self, board):
        self.update_board(board)
        self.count = 0
        self.prune = 0
        start_time = time.time()
        best_move = self.minimax(depth = 4, alpha=float('-inf'), beta = float('inf'), player = "black") 
        # best_move = self.iterative_deepening(max_depth=5, time_limit=5.0)
        end_time = time.time()
        if best_move:
            sc, move, square = best_move
            print()
            print(f"ChessAI moves {square.piece.type} to {move} with a score of {sc}")
            print(f"Number of nodes searched: {self.count:,}")
            print(f"Number of nodes pruned: {self.prune:,}")
            # print(f"Deepest depth reached: {self.depth - 1}")
            print(f"Time taken: {(end_time - start_time):.2f} seconds")
            # print(f"Number of times accessed cache: {self.counter}")
            board.move(square.row, square.col, move) 
            # print(self.hash_board(self.board))
        else:
            print("WHITE WINS")
            
            
    def create_board_copy(self, board):
        return copy.deepcopy(board)
    
    def update_board(self, board):
        self.board = self.create_board_copy(board)
    
    def next_player(self, player):
        return "white" if player == "black" else "white"
         
         
     