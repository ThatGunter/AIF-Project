
from settings import *

class KeybindsUI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        
        self.box_width = 220
        self.box_height = 160
        self.margin = 20
        self.padding = 15
        
        
        self.box_rect = pygame.Rect(
            WINDOW_WIDTH - self.box_width - self.margin,
            self.margin,
            self.box_width,
            self.box_height
        )
        
        
        self.bg_color = (0, 0, 0, 180)  
        self.border_color = (255, 255, 255, 200)  
        self.text_color = (255, 255, 255)
        self.key_color = (255, 255, 100)  
        
        self.keybinds = [
            ("Arrow Keys", "Move"),
            ("Up Arrow", "Jump"),
            ("Down Arrow", "Fall Through"),
            ("X / Click", "Swing Sword"),
            ("Enter", "Select/Confirm")
        ]
        
        
        self.create_ui_surface()
    
    def create_ui_surface(self):
        self.ui_surface = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)
        
        
        pygame.draw.rect(self.ui_surface, self.bg_color, 
                        (0, 0, self.box_width, self.box_height), border_radius=8)
        pygame.draw.rect(self.ui_surface, self.border_color, 
                        (0, 0, self.box_width, self.box_height), width=2, border_radius=8)
        
        
        title_surf = self.font.render("CONTROLS", True, self.text_color)
        title_rect = title_surf.get_rect(centerx=self.box_width // 2, y=self.padding)
        self.ui_surface.blit(title_surf, title_rect)
        
        
        y_offset = title_rect.bottom + 10
        line_height = 22
        
        for key_text, action_text in self.keybinds:
            
            key_surf = self.small_font.render(key_text, True, self.key_color)
            
            action_surf = self.small_font.render(f": {action_text}", True, self.text_color)
            
            
            key_rect = key_surf.get_rect(x=self.padding, y=y_offset)
            self.ui_surface.blit(key_surf, key_rect)
            
            
            action_rect = action_surf.get_rect(x=key_rect.right, y=y_offset)
            self.ui_surface.blit(action_surf, action_rect)
            
            y_offset += line_height
    
    def draw(self):
        self.display_surface.blit(self.ui_surface, self.box_rect.topleft)
    
    def toggle_position(self):
        
        if self.box_rect.right == WINDOW_WIDTH - self.margin:
            
            self.box_rect.x = self.margin
        else:
            
            self.box_rect.x = WINDOW_WIDTH - self.box_width - self.margin
    
    def set_position(self, position="top-right"):
        if position == "top-right":
            self.box_rect.topleft = (WINDOW_WIDTH - self.box_width - self.margin, self.margin)
        elif position == "top-left":
            self.box_rect.topleft = (self.margin, self.margin)
        elif position == "bottom-right":
            self.box_rect.topleft = (WINDOW_WIDTH - self.box_width - self.margin, 
                                   WINDOW_HEIGHT - self.box_height - self.margin)
        elif position == "bottom-left":
            self.box_rect.topleft = (self.margin, WINDOW_HEIGHT - self.box_height - self.margin)
    
    def update_keybinds(self, new_keybinds):
        self.keybinds = new_keybinds
        self.create_ui_surface()