import pygame
from const import *
from board import Board
from dragger import Dragger
from themes import Themes

class Game:
    def __init__(self):
        self.board = Board()
        self.dragger = Dragger()
        self.player = "white"
        self.theme = Themes()
        
    def show_mode(self, screen):
        # pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        screen.fill((0,0,0))
        start_y = 300
        # print(pygame.font.get_fonts())
        font_address = pygame.font.match_font("copperplate", bold=True, italic=False)
        font = pygame.font.Font(font_address, 64)
        
        text = "Mode"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH//2, start_y))
        screen.blit(text_surface, text_rect)

        font_address = pygame.font.match_font("chalkduster", bold=False, italic=False)
        font = pygame.font.Font(font_address, 32)
        
        text = "Player vs Player"
        text_surface = font.render(text, True, (255, 255, 255))        
        text_rect = text_surface.get_rect(center=(WIDTH//2, start_y + 100))
        screen.blit(text_surface, text_rect)
        pygame.draw.rect(screen, (177,127,84), (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20), 4, border_radius=20)
        
        text= "Player vs ChessAI"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH//2, start_y + 200))
        screen.blit(text_surface, text_rect)
        pygame.draw.rect(screen, (99,168,248), (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20), 4, border_radius=20)
        
    
    def show_bg(self, screen):
        theme = self.theme.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    color = theme.light_bg
                else:
                    color = theme.dark_bg
                
                rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(screen, color, rect)

    def show_pieces(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    if piece is not self.dragger.dragging_piece: 
                        img = pygame.image.load(piece.image)
                        img_center = (col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2) # Recall this is needed since the image is drawn from the top left corner
                        piece.image_rect = img.get_rect(center=img_center)
                        
                        screen.blit(img, piece.image_rect) 
    def show_moves(self, screen):
        theme = self.theme.theme
        
        if self.dragger.dragging:
            piece = self.dragger.dragging_piece
            for move in piece.moves:
                finalRow, finalCol = move
                color = theme.dark_trace if (finalRow + finalCol) % 2 == 0 else theme.light_trace 
                rect = (finalCol * SQ_SIZE, finalRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(screen, color, rect)

    def show_last_move(self, screen):
        theme = self.theme.theme
        
        if self.board.last_move:
            initial = self.board.last_move["initial"]
            final = self.board.last_move["final"]
            
            rect_initial = (initial[1] * SQ_SIZE, initial[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            rect_final = (final[1] * SQ_SIZE, final[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE)

            pygame.draw.rect(screen, theme.light_moves, rect_initial)
            pygame.draw.rect(screen, theme.dark_moves, rect_final)
        
    def next_player(self):
        self.player = "white" if self.player == "black" else "black"
        
    def reset(self):
        self.__init__()
    
              