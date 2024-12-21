import copy
from const import *
import random
import time
from zobrist import Zobrist

class ChessAI:
    def __init__(self, board):
        self.board = board
        self.zobrist = Zobrist()
        self.cache = {}
        self.nodes_searched = 0
        self.cache_hits = 0
        self.nodes_pruned= 0
    
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

        if self.board.white_checkmate:
            return float('-inf')
        elif self.board.white_stalemate or self.board.black_stalemate:
            return 0
        elif self.board.black_checkmate:
            return float('inf')

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
        return round(white_score - black_score, 2)
     
    def move_heuristic(self, move, piece, player, attack_info):
        r, c = move
        final_square = self.board.squares[r][c]
        heuristic = 0

        # Positional heurisitcs in terms of white (from stockfish)
        pawn = [
            [0,   0,   0,   0,   0,   0,   0,   0],
            [5,  10,  10, -20, -20,  10,  10,   5],
            [5,  -5, -10,   0,   0, -10,  -5,   5],
            [0,   0,   0,  20,  20,   0,   0,   0],
            [5,   5,  10,  25,  25,  10,   5,   5],
            [10,  10,  20,  30,  30,  20,  10,  10],
            [50,  50,  50,  50,  50,  50,  50,  50],
            [0,   0,   0,   0,   0,   0,   0,   0]
        ]
        
        knight = [
          [-50, -40, -30, -30, -30, -30, -40, -50],
          [-40, -20,   0,   0,   0,   0, -20, -40],
          [-30,   0,  10,  15,  15,  10,   0, -30],
          [-30,   5,  15,  20,  20,  15,   5, -30],
          [-30,   0,  15,  20,  20,  15,   0, -30],
          [-30,   5,  10,  15,  15,  10,   5, -30],
          [-40, -20,   0,   5,   5,   0, -20, -40],
          [-50, -40, -30, -30, -30, -30, -40, -50]
        ]
        
        bishop = [
          [-20, -10, -10, -10, -10, -10, -10, -20],
          [-10,   0,   0,   0,   0,   0,   0, -10],
          [-10,   0,   5,  10,  10,   5,   0, -10],
          [-10,   5,   5,  10,  10,   5,   5, -10],
          [-10,   0,  10,  10,  10,  10,   0, -10],
          [-10,  10,  10,  10,  10,  10,  10, -10],
          [-10,   5,   0,   0,   0,   0,   5, -10],
          [-20, -10, -10, -10, -10, -10, -10, -20]
        ]
        
        rook = [
            [0, 0, 0, 5, 5, 0, 0, 0],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        queen = [
            [-20, -10, -10,  -5,  -5, -10, -10, -20],
            [-10,   0,   5,   0,   0,   0,   0, -10],
            [-10,   5,   5,   5,   5,   5,   0, -10],
            [ -5,   0,   5,   5,   5,   5,   0,  -5],
            [ -5,   0,   5,   5,   5,   5,   0,  -5],
            [-10,   0,   5,   5,   5,   5,   0, -10],
            [-10,   0,   0,   0,   0,   0,   0, -10],
            [-20, -10, -10,  -5,  -5, -10, -10, -20]
        ]
        
        king = [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [ 20,  20,   0,   0,   0,   0,  20,  20],
            [ 20,  30,  10,   0,   0,  10,  30,  20]
        ]
        
        # Captures: Value of captured piece - value of moving piece 
        if final_square.is_rival_piece(player):
            heuristic += final_square.piece.value * 10 - piece.value  # Capture is highly prioritized

        # Promoting a pawn is highly prioritized
        if piece.type == "pawn":
            if piece.color == "white" and r == 0:
                heuristic += 80 # Queen value minus pawn
            elif piece.color == "black" and r == 7:
                heuristic += 80

        # Moving to a square that is attacked by the opponent is discouraged
        atk_squares = attack_info["atk_squares"]
        if (r,c) in atk_squares:
            heuristic -= piece.value

        # Positional heuristics
        if piece.type == "pawn":
            if piece.color == "white":
                heuristic += pawn[r][c]            
            else:
                heuristic += pawn[7 - r][c]
        elif piece.type == "knight":
            if piece.color == "white":
                heuristic += knight[r][c]
            else:
                heuristic += knight[7 - r][c]
        elif piece.type == "bishop":
            if piece.color == "white":
                heuristic += bishop[r][c]
            else:
                heuristic += bishop[7 - r][c]
        elif piece.type == "rook":
            if piece.color == "white":
                heuristic += rook[r][c]
            else:
                heuristic += rook[7 - r][c]
        elif piece.type == "queen":
            if piece.color == "white":
                heuristic += queen[r][c]
            else:
                heuristic += queen[7 - r][c]
        elif piece.type == "king":
            if piece.color == "white":
                heuristic += king[r][c]
            else:
                heuristic += king[7 - r][c]

        return heuristic

    
    def minimax(self, depth, alpha, beta, player, attack_info, zobrist_hash, start_time = None, time_limit = None):
        """
            Minimax algorithm with alpha-beta pruning + zobrist hasing + move ordering + other optimisations
        """
        if start_time and time.time() - start_time >= time_limit:
            return None  # Abort search if time is up
        
        if depth == 0 or self.board.white_checkmate or self.board.black_checkmate or self.board.black_stalemate or self.board.white_stalemate:
            # Score, Move, Square
            return (self.eval_board(), None, None)     
        else:
            
            if zobrist_hash in self.cache:
                self.cache_hits += 1
                
                info = self.cache[zobrist_hash]
                depth_stored = info["depth"]
                score_stored = info["score"]
                move_stored = info["best_move"]
                flag_stored = info["flag"]
                
                if depth_stored >= depth:
                    if flag_stored == "exact":
                        return move_stored
                    elif flag_stored == "lowerbound":
                        alpha = max(alpha, score_stored)
                    elif flag_stored == "upperbound":
                        beta = min(beta, score_stored)
                    
                    if alpha >= beta:
                        return move_stored
                
            best_move = None
            original_alpha = alpha
            original_beta = beta
            for row in range(ROWS):
                for col in range(COLS):
                    
                    if self.board.squares[row][col].is_my_piece(player):
                        
                        square = self.board.squares[row][col]
                        piece = square.piece
                        
                        self.board.calc_moves(row, col, attack_info)
                        
                        piece.moves.sort(key=lambda move: self.move_heuristic(move, piece, player, attack_info), reverse = True)

                        piece_moves = piece.moves[:] 
                        for move in piece_moves:

                            captured_piece = self.board.squares[move[0]][move[1]].piece
                            moved_state = piece.moved
                            castling = piece.type == "king" and self.board.is_castling(row, col, move) 
                            is_en_passant_move = piece.type == "pawn" and abs(col - move[1]) == 1 and self.board.squares[move[0]][move[1]].is_empty()
                            pawn_promotion = piece.type == "pawn" and self.board.check_promotion(piece, move)
                            white_checkmate = self.board.white_checkmate
                            black_checkmate = self.board.black_checkmate
                            white_stalemate = self.board.white_stalemate
                            black_stalemate = self.board.black_stalemate
                            en_passant_pos = self.board.en_passant_pos                      

                            # save the state of board
                            prev_state = {
                                "start_row": row,
                                "start_col": col,
                                "end_row": move[0],
                                "end_col": move[1],
                                "captured_piece": captured_piece,
                                "moved_state": moved_state,
                                "castling": castling,
                                "is_en_passant_move": is_en_passant_move,
                                "en_passant_pos": en_passant_pos,
                                "pawn_promotion": pawn_promotion,
                                "white_checkmate": white_checkmate,
                                "black_checkmate": black_checkmate,
                                "white_stalemate": white_stalemate,
                                "black_stalemate": black_stalemate
                            }
                            
                            # Do the move
                            self.board.move(row, col, move)    

                            next_zobrist_hash = self.zobrist.get_hash(self.board, self.next_player(player))
                            if next_zobrist_hash in self.cache:
                                next_attack_info = self.cache[next_zobrist_hash]["attack_info"]
                                self.white_checkmate = self.cache[next_zobrist_hash]["white_checkmate"]
                                self.black_checkmate = self.cache[next_zobrist_hash]["black_checkmate"]
                                self.white_stalemate = self.cache[next_zobrist_hash]["white_stalemate"]
                                self.black_stalemate = self.cache[next_zobrist_hash]["black_stalemate"]
                            else:
                                next_attack_info = self.board.get_attack_info(self.board.king_pos(self.next_player(player)))
                                self.board.check_gamestate(next_attack_info)
                            
                            res = self.minimax(depth - 1, alpha, beta, self.next_player(player), next_attack_info, next_zobrist_hash, start_time, time_limit)
                            
                            self.nodes_searched += 1

                            # Undo the move         
                            self.board.undo_move(prev_state)

                            if res:
                                if best_move:
                                    # Maximising player
                                    if player == "white":
                                        if (best_move[0] < res[0]):
                                            best_move = (res[0], move, square)
                                        
                                        alpha = max(alpha, best_move[0])        
                                        if beta <= alpha:
                                            self.nodes_pruned += 1
                                            break

                                    # Minimising player
                                    else:
                                        if (best_move[0] > res[0]):
                                            best_move = (res[0], move, square)
                                        
                                        beta = min(beta, best_move[0])
                                        if beta <= alpha:
                                            self.nodes_pruned += 1
                                            break
                                else:
                                    best_move = (res[0], move, square)
                
                    if beta <= alpha:
                        break   
                if beta <= alpha:
                    break
                
        score = best_move[0]
        
        if score <= original_alpha:
            flag = "upperbound"
        elif score >= original_beta:
            flag = "lowerbound"
        else:
            flag = "exact"
        
        
        self.cache[zobrist_hash] = {
            "best_move":best_move,
            "depth": depth,
            "score": score,
            "flag": flag,
            "attack_info": attack_info,
            "white_checkmate": self.board.white_checkmate,
            "black_checkmate": self.board.black_checkmate,
            "white_stalemate": self.board.white_stalemate,
            "black_stalemate": self.board.black_stalemate
        }
        
        return best_move
    
    def next_move(self, board):
        """
            Make the next move for the AI
        """
        self.count = 0
        self.nodes_pruned = 0
        self.cache_hits = 0
        self.nodes_searched = 0

        attack_info = self.board.get_attack_info(self.board.king_pos("black"))
        zobrist_hash = self.zobrist.get_hash(self.board, "black")
        start_time = time.time()
        best_move = self.minimax(depth = 5, alpha=float('-inf'), beta = float('inf'), player = "black", attack_info=attack_info, zobrist_hash=zobrist_hash) 
        # best_move = self.iterative_deepening(max_depth=10, time_limit=10.0)
        end_time = time.time()
        if best_move:
            sc, move, square = best_move
            print()
            print(f"ChessAI moves {square.piece.type} to {move} with a score of {sc}")
            print(f"Number of nodes searched: {self.nodes_searched:,}")
            print(f"Number of nodes pruned: {self.nodes_pruned:,}")
            print(f"Time taken: {(end_time - start_time):.2f} seconds")
            print(f"Number of times accessed cache: {self.cache_hits}")
            print(f"Size of cache: {len(self.cache)}")
            board.move(square.row, square.col, move) 
    
    def next_player(self, player):
        return "white" if player == "black" else "black"
         
         
     