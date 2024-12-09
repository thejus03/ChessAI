from const import *
import pygame

class Dragger:
    def __init__(self):
        self.posX = 0
        self.posY = 0
        self.dragging = False
        self.dragging_piece = None
        self.initialRow = None
        self.initialCol = None
        
    def update_pos(self,pos):
        self.posX, self.posY = pos
    
    def start_drag(self, piece):
        self.dragging = True 
        self.dragging_piece = piece
        
    def stop_drag(self):
        self.dragging = False
        self.dragging_piece.set_image()
        self.dragging_piece = None
        
    
    def save_init(self, pos):
        self.initialRow, self.initialCol = pos[1] // SQ_SIZE, pos[0] // SQ_SIZE # event.pos was given in (x,y)
   
    def update_blit(self, screen):
        self.dragging_piece.set_image(size=128)
        # Load image of piece
        img = pygame.image.load(self.dragging_piece.image)
        # Set to mouse pos
        img_center = (self.posX, self.posY)
        # Image rect
        self.dragging_piece.image_rect = img.get_rect(center=img_center)
        # Display image  
        screen.blit(img, self.dragging_piece.image_rect) 