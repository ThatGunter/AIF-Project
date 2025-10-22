from settings import *
from os.path import join
from math import sin

#Creating Player
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, frames, data):
        # general setup
        super().__init__(groups)
        self.z = Z_LAYERS['main']
        self.data = data
        #image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frame_index]

        
        # rects
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox_rect.copy()

        self.start_pos = pos
        self.original_x = pos[0]
        self.original_y = pos[1]

        # Actually moving
        self.direction = vector()
        self.speed = 250
        self.gravity = 1300
        self.jump = False
        self.jumpheight = 725
        #collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surface = {'floor': False, 'left': False, 'right': False}
        self.platform = None
        self.attacking = False
        
        #timer
        self.timers = {
            'wall jump': Timer(500),
            'wall slide delay': Timer(100),
            'platform skip': Timer(300),
            'attack block': Timer(750),
            'hit': Timer(400),
        }

    def input(self):
        Inputs = pygame.key.get_pressed()
        Mouse_Click = pygame.mouse.get_pressed()
        input_vector = vector(0,0)
        if not self.timers['wall jump'].active:

            if Inputs[pygame.K_RIGHT]:
                input_vector.x += 1
                self.facing_right = True
            if Inputs[pygame.K_LEFT]:
                input_vector.x -= 1
                self.facing_right = False
            self.direction.x = input_vector.normalize().x if input_vector else input_vector.x
            if Inputs[pygame.K_DOWN]:
                self.timers['platform skip'].activate()
            if any((Mouse_Click[0], Inputs[pygame.K_x])):
                self.attack()
            if pygame.key.get_just_pressed()[pygame.K_F1]:
                self.show_keybinds = not self.show_keybinds

        if Inputs[pygame.K_UP]:
            self.jump = True     
        if Inputs[pygame.K_SPACE]:
            self.hitbox_rect.x = self.original_x
            self.hitbox_rect.y = self.original_y
            self.rect.center = self.hitbox_rect.center
            self.platform = None
    
    def attack(self):
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frame_index = 0
            self.timers['attack block'].activate()
            
            
    
    def platform_move(self, dt): 
        # Only move with platform if we're on the floor AND not jumping
        if self.platform and self.on_surface['floor'] and self.direction.y >= 0:
            # Move with platform in both directions, but handle them differently
            platform_movement = self.platform.direction * self.platform.speed * dt
            
            if self.platform.direction.y > 0:  # Platform moving down
                # Move player down with platform
                self.hitbox_rect.y += platform_movement.y
            elif self.platform.direction.y < 0:  # Platform moving up
                # Move player up with platform - don't rely on collision
                self.hitbox_rect.y += platform_movement.y
                
            # Always move horizontally with the platform
            if self.platform.direction.x != 0:
                self.hitbox_rect.x += platform_movement.x
           
    def movement(self, dt):
        time_elapsed = pygame.time.get_ticks()    

        if time_elapsed >= 2000:
        
            # Horizontal movement
            self.hitbox_rect.x += self.direction.x * self.speed * dt
            self.collision('horizontal', dt)
            
            # Jumping
            if self.jump:
                if self.on_surface['floor']:
                    self.direction.y = -self.jumpheight
                    self.timers['wall slide delay'].activate()
                    self.hitbox_rect.bottom -= 1
                    # If jumping from a platform, temporarily disconnect from it
                    if self.platform:
                        self.platform = None
                elif any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall slide delay'].active:
                    self.timers['wall jump'].activate()
                    self.direction.y = -self.jumpheight
                    if self.on_surface['left']: 
                        self.direction.x = 1
                    elif self.on_surface['right']:
                        self.direction.x = -1
                self.jump = False

            # Vertical movement - modified to handle platforms
            if not self.on_surface['floor'] and any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall jump'].active and not self.timers['wall slide delay'].active:
                # Wall sliding
                self.direction.y = 0
                self.hitbox_rect.y += self.gravity / 10 * dt
            elif self.platform and self.on_surface['floor'] and self.direction.y >= 0:
                # On a moving platform - only disable gravity if not jumping (direction.y >= 0)
                self.direction.y = 0
            else:
                # Normal gravity application (including when jumping from platform)
                self.direction.y += self.gravity / 2 * dt
                self.hitbox_rect.y += self.direction.y * dt
                self.direction.y += self.gravity / 2 * dt
            
            self.collision('vertical', dt)
            self.semi_collision()
            self.rect.center = self.hitbox_rect.center

    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft,(self.hitbox_rect.width,4))  # Slightly larger detection area
        top_rect = pygame.Rect(self.hitbox_rect.topleft,(self.hitbox_rect.width,4))
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0,self.hitbox_rect.height / 4),(2,self.hitbox_rect.height / 2))
        left_rect = pygame.Rect(self.hitbox_rect.topleft + vector(-2,self.hitbox_rect.height / 4 ),(2,self.hitbox_rect.height / 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]
        
        #collisions
        semi_floor_collision = floor_rect.collidelist(semi_collide_rect) >= 0 and self.direction.y >= 0 and not self.timers['platform skip'].active
        
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 or semi_floor_collision else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['top'] = True if top_rect.collidelist(collide_rects) >= 0 else False

        # Find platform - check this AFTER updating on_surface
        old_platform = self.platform
        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()

        if self.on_surface['floor'] and not self.timers['platform skip'].active:  # Don't attach to platform when skipping
            for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
                if sprite.rect.colliderect(floor_rect):
                    self.platform = sprite
                    break
                
        # If we lost platform contact but were just on one, try to stick to it
        if old_platform and not self.platform and self.on_surface['floor'] and not self.timers['platform skip'].active:
            # Check if we're still close to the old platform
            if old_platform.rect.colliderect(pygame.Rect(self.rect.bottomleft,(self.rect.width,8))):
                self.platform = old_platform

    def collision(self, axis, dt):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'horizontal':
                    #right
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox_rect.left = sprite.rect.right
                    
                    #left
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left

                else: # Vertical Collisions
                    #bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                        self.direction.y = 0
                        
                    #top
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        self.direction.y = 0 
                        if hasattr(sprite, 'moving') and sprite.moving:
                            self.platform = None
                            self.hitbox_rect.top += 6
                            if hasattr(sprite, 'move_dir') and sprite.move_dir != 'x':
                                self.hitbox_rect.top += sprite.speed * dt


    def semi_collision(self):
        if not self.timers['platform skip'].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= sprite.old_rect.top:
                        self.hitbox_rect.bottom = sprite.rect.top
                        if self.direction.y > 0 :
                            self.direction.y = 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.state == 'attack' and self.frame_index >= len(self.frames[self.state]):
            self.state = 'idle'
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False

    def get_state(self):
        if self.on_surface['floor']:
            if self.attacking:
                self.state = 'attack'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'run'
        else:
            if self.attacking:
                self.state = 'air_attack'
            else:
                if any((self.on_surface['left'], self.on_surface['right'])):
                    self.state = 'wall'
                else:
                    self.state = 'jump' if self.direction.y < 0 else 'fall'

    def get_damage(self):
        if not self.timers['hit'].active:
            self.data.health -= 1
            self.timers['hit'].activate()

    def flickers(self):
        if self.timers['hit'].active and sin(pygame.time.get_ticks()) * 100 >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    def update(self, dt):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()
        self.input()
        
        # Check contact BEFORE any movement
        self.check_contact()
        
        # Apply player movement first
        self.movement(dt)
        
        # Then move with platform (this happens after collision detection in movement)
        self.platform_move(dt)
        
        # Check contact again to ensure platform detection is current
        self.check_contact()
        self.get_state()
        self.animate(dt)
        self.flickers()