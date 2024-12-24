import pygame
import sys
from const import *
from game import Game
from chessAI import ChessAI

class Main:
    def __init__(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load("images/chess.png"))
        # Set screen size
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
        # Create Game object
        self.game = Game()
        self.board = self.game.board
        # Set name of window
        pygame.display.set_caption('ChessAI')
        self.dragger = self.game.dragger
        self.ChessAI = ChessAI(self.board)
        self.mode = None
        
        self.game_over = False
         
    def start(self):
        attack_info = None
        # move_info = None
        while True:
            if not self.mode:
                self.game.show_mode(self.screen)
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if 370 < pos[1] <= 432:
                            self.mode = "pvp"
                        elif 470 < pos[1] < 532:
                            self.mode = "chessai"
                        else:
                            continue
                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            elif self.game_over:
                if self.game_over == "white_checkmate":
                    self.game.show_checkmate(self.screen, "black")
                elif self.game_over == "black_checkmate":
                    self.game.show_checkmate(self.screen, "white")
                elif self.game_over == "stalemate":
                    self.game.show_stalemate(self.screen)
                
                for event in pygame.event.get():
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.game.reset()
                            self.board = self.game.board
                            self.dragger = self.game.dragger
                            self.mode = None
                            self.game_over = False

                        # Quit Game    
                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            else:
                self.game.show_bg(self.screen)
                self.game.show_last_move(self.screen)
                self.game.show_moves(self.screen)
                self.game.show_pieces(self.screen)

                if not self.mode: self.game.show_mode(self.screen)

                if self.dragger.dragging:
                    self.dragger.update_blit(self.screen)

                if self.mode == "chessai" and self.game.player == "black":
                    pygame.display.update()
                    
                    self.ChessAI.next_move(self.game.player)

                    attack_info = self.board.get_attack_info(self.board.king_pos(self.board.rival_player(self.game.player)))
                    move_info = self.board.get_move_info(self.board.rival_player(self.game.player),attack_info)
                    self.board.check_gamestate(attack_info, move_info)
                    # Check for checkmate or stalemate
                    if self.board.white_checkmate: # White loses
                        self.game_over = "white_checkmate"
                    elif self.board.black_checkmate: # Black loses
                        self.game_over = "black_checkmate"
                    elif self.board.black_stalemate or self.board.white_stalemate:
                        self.game_over = "stalemate"
                    
                    # Change player
                    self.game.next_player()
                else:
                    
                    for event in pygame.event.get():
                        # Clicked
                        if event.type == pygame.MOUSEBUTTONDOWN:
                        
                            self.dragger.update_pos(event.pos) # Note: event.pos gives (x,y) 
                            clicked_row = self.dragger.posY // SQ_SIZE
                            clicked_col  = self.dragger.posX // SQ_SIZE
                        
                            # checks if clicked square has a piece 
                            if (self.board.squares[clicked_row][clicked_col].has_piece()):
                                piece = self.board.squares[clicked_row][clicked_col].piece

                                # Check if valid piece is being moved
                                if piece.color == self.game.player:
                                    if not attack_info:
                                        king_pos = self.board.king_pos(self.game.player)
                                        attack_info = self.board.get_attack_info(king_pos)
                                    self.board.calc_moves(clicked_row, clicked_col, attack_info)
                                    self.dragger.start_drag(piece) 
                                    self.dragger.save_init(event.pos)
                                    
                                    # show moves
                                    self.game.show_bg(self.screen)
                                    self.game.show_last_move(self.screen)
                                    self.game.show_moves(self.screen)
                                    self.game.show_pieces(self.screen)
                        
                        # Moving mouse        
                        elif event.type == pygame.MOUSEMOTION:
                            if self.dragger.dragging:
                                self.dragger.update_pos(event.pos) # Note: event.pos gives (x,y) 
                                self.game.show_bg(self.screen)
                                self.game.show_last_move(self.screen)
                                self.game.show_moves(self.screen)
                                self.game.show_pieces(self.screen)
                                self.dragger.update_blit(self.screen)
                            
                        # Released click
                        elif event.type == pygame.MOUSEBUTTONUP:
                            if self.dragger.dragging:
                                self.dragger.update_pos(event.pos)

                                piece = self.dragger.dragging_piece 
                                released_row = self.dragger.posY // SQ_SIZE
                                released_col  = self.dragger.posX // SQ_SIZE

                                if self.board.valid_move(piece, (released_row, released_col)):
                                    self.board.move(self.dragger.initialRow, self.dragger.initialCol, (released_row, released_col))
                                    attack_info = self.board.get_attack_info(self.board.king_pos(self.board.rival_player(self.game.player)))
                                    move_info = self.board.get_move_info(self.board.rival_player(self.game.player), attack_info )
                                    self.board.check_gamestate(attack_info, move_info)
                                    # Check for checkmate or stalemate
                                    if self.board.white_checkmate: # White loses
                                        self.game_over = "white_checkmate"
                                    elif self.board.black_checkmate: # Black loses
                                        self.game_over = "black_checkmate"
                                    elif self.board.black_stalemate or self.board.white_stalemate:
                                        self.game_over = "stalemate"
                                    
                                    # Change player
                                    self.game.next_player()
                            
                                    
                                self.dragger.stop_drag()


                        # Key press to change Theme
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_t:
                                self.game.theme.change_theme()
                            
                            if event.key == pygame.K_r:
                                self.game.reset()
                                self.board = self.game.board
                                self.dragger = self.game.dragger
                                self.mode = None
                                attack_info = None

                        # Quit Game    
                        elif event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
            
            pygame.display.update()

if __name__ == "__main__":
    print(r"""
    
      ___         ___         ___         ___         ___                   ___               
     /  /\       /__/\       /  /\       /  /\       /  /\                 /  /\      ___     
    /  /:/       \  \:\     /  /:/_     /  /:/_     /  /:/_               /  /::\    /  /\    
   /  /:/         \__\:\   /  /:/ /\   /  /:/ /\   /  /:/ /\             /  /:/\:\  /  /:/    
  /  /:/  ___ ___ /  /::\ /  /:/ /:/_ /  /:/ /::\ /  /:/ /::\           /  /:/~/::\/__/::\    
 /__/:/  /  //__/\  /:/\:/__/:/ /:/ //__/:/ /:/\:/__/:/ /:/\:\         /__/:/ /:/\:\__\/\:\__ 
 \  \:\ /  /:\  \:\/:/__\\  \:\/:/ /:\  \:\/:/~/:\  \:\/:/~/:/         \  \:\/:/__\/  \  \:\/\
  \  \:\  /:/ \  \::/     \  \::/ /:/ \  \::/ /:/ \  \::/ /:/           \  \::/        \__\::/
   \  \:\/:/   \  \:\      \  \:\/:/   \__\/ /:/   \__\/ /:/             \  \:\        /__/:/ 
    \  \::/     \  \:\      \  \::/      /__/:/      /__/:/               \  \:\       \__\/  
     \__\/       \__\/       \__\/       \__\/       \__\/                 \__\/              
    
    """)
    main = Main()
    main.start()