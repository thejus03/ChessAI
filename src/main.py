import pygame
import sys
from const import *
from game import Game
from chessAI import ChessAI
import time
import threading

class Main:
    def __init__(self):
        pygame.init()
        # Set screen size
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
        # Create Game object
        self.game = Game()
        self.board = self.game.board
        # Set name of window
        pygame.display.set_caption('Chess')
        self.dragger = self.game.dragger
        self.ChessAI = ChessAI()
        self.mode = None
         
    def start(self):
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
                    self.ChessAI.next_move(self.board)
                    self.game.next_player()

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
                                # if self.board.in_check(self.game.player):
                                    # self.board.calc_moves(clicked_row, clicked_col)
                                # else:
                                self.board.calc_moves(clicked_row, clicked_col)
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

                    # Quit Game    
                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            
            pygame.display.update()

if __name__ == "__main__":
    main = Main()
    main.start()