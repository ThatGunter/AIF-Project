from settings import *
from sprites import AnimatedSprite
from random import randint


class UI:
    def __init__(self, font, frames):
        self.display_surface = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font
        self.game_over_text = False

        #health
        self.heart_frames = frames['heart']
        self.heart_surf_width = self.heart_frames[0].get_width()
        self.heart_padding = 5

        #coins
        self.coin_amount = 0
        self.coin_timer = Timer(1000)
        self.coin_surf = frames['coin']

        #game over
        self.game_over_timer = Timer(1000)
        self.restart_timer = Timer(1000)
        self.game_won_timer = Timer(1000)

    def create_hearts(self, amount):
        for sprite in self.sprites:
            sprite.kill()
        for heart in range(amount):
            x = 10 + heart * (self.heart_surf_width + self.heart_padding)
            y = 10
            Heart((x,y), self.heart_frames, self.sprites)
    
    def display_text(self):
        if self.coin_timer.active:
            text_surf = self.font.render(str(self.coin_amount), False, '#33323d')
            text_rect = text_surf.get_frect(topleft = (16,34))
            self.display_surface.blit(text_surf, text_rect)

            coin_rect = self.coin_surf.get_frect(center = text_rect.bottomleft).move(0, -6)
            self.display_surface.blit(self.coin_surf, coin_rect)

    def display_game_over(self):
        self.game_over_timer.activate()

    def display_game_won(self):
        self.game_won_timer.activate()

    def show_coins(self, amount):
        self.coin_amount = amount
        self.coin_timer.activate()

    def update(self, dt):
        self.coin_timer.update()
        self.game_over_timer.update()
        self.restart_timer.update()
        self.game_won_timer.update()
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        self.display_text()

        #Game Over Text
        if self.game_over_timer.active:
            text_surf = self.font.render("GAME OVER", False, 'white')
            text_rect = text_surf.get_frect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            
            padding = 20
            bg_rect = pygame.Rect(
                text_rect.x - padding,
                text_rect.y - padding,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            
            pygame.draw.rect(self.display_surface, 'black', bg_rect)
            
            self.display_surface.blit(text_surf, text_rect)
            self.game_over_text = True

        #You Won
        if self.game_won_timer.active:
            text_surf = self.font.render("YOU WON", False, 'green')
            text_rect = text_surf.get_frect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            
            padding = 20
            bg_rect = pygame.Rect(
                text_rect.x - padding,
                text_rect.y - padding,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            
            pygame.draw.rect(self.display_surface, 'black', bg_rect)
            
            self.display_surface.blit(text_surf, text_rect)
            self.game_over_text = True
            

        #Restarting
        if self.game_over_text and not self.game_over_timer.active or self.game_over_text and not self.game_won_timer:
            self.restart_timer.activate()
            self.game_over_text = False

        if self.restart_timer.active:
            text_surf = self.font.render("RESTARTING", False, 'white')
            text_rect = text_surf.get_frect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            
            padding = 20
            bg_rect = pygame.Rect(
                text_rect.x - padding,
                text_rect.y - padding,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            
            pygame.draw.rect(self.display_surface, 'black', bg_rect)
            
            self.display_surface.blit(text_surf, text_rect)
        

class Heart(AnimatedSprite):
    def __init__ (self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.active = False

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = False
            self.frame_index = 0

    def update(self, dt):
        if self.active:
            self.animate(dt)
        else:
            if randint(0,1000) == 1:
                self.active = True

