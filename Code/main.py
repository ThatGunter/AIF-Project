from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from support import *
from data import Data
from debug import debuginfo
from ui import UI
from overworld import Overworld


clock = pygame.time.Clock()
class Game: #Game 
    def __init__(self): #Game Box
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('AIF Project')
        self.import_assets()
        self.timers = {'Game Over': Timer(500)}
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        self.game_over_started = False
        
        #Import level
        self.tmx_maps = {'omni': load_pygame(get_resource_path(join('data', 'levels', 'omni.tmx'))),
                         0: load_pygame(get_resource_path(join('data', 'levels', '0.tmx'))),
                         1: load_pygame(get_resource_path(join('data', 'levels', '1.tmx'))),
                         2: load_pygame(get_resource_path(join('data', 'levels', '2.tmx'))),
                         3: load_pygame(get_resource_path(join('data', 'levels', '3.tmx'))),
                         4: load_pygame(get_resource_path(join('data', 'levels', '4.tmx'))),
                         5: load_pygame(get_resource_path(join('data', 'levels', '5.tmx'))),
                         }
        self.tmx_overworld = load_pygame(get_resource_path(join('data', 'overworld', 'overworld.tmx')))
        self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.data, self.switch_stage)
        #self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames)

    def switch_stage(self, target, unlock = 0):
        if target == 'level':
            self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.data, self.switch_stage)
			
        else: # overworld 
            if unlock > 0:
                self.data.unlocked_level = unlock
            else:
                self.data.health -= 1
            self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)
    
    def import_assets(self):
        self.level_frames = {
            'flag': import_folder('graphics', 'level', 'flag'),
            'saw': import_folder('graphics', 'enemies', 'saw', 'animation'),
            'floor_spike': import_folder('graphics', 'enemies', 'floor_spikes'),
            'palms': import_sub_folders('graphics', 'level', 'palms'),
            'big_chain': import_folder('graphics', 'level', 'big_chains'),
            'small_chain': import_folder('graphics', 'level', 'small_chains') ,
            'window': import_folder('graphics', 'level', 'window'),
            'candle': import_folder('graphics', 'level', 'candle'),
            'candle_light': import_folder('graphics', 'level', 'candle light'),
            'player': import_sub_folders('graphics', 'player'),
            'saw': import_folder('graphics', 'enemies', 'saw', 'animation'),
            'saw_chain': import_image('graphics', 'enemies', 'saw', 'saw_chain'),
            'helicopter': import_folder('graphics', 'level', 'helicopter'),
            'boat': import_folder('graphics', 'objects', 'boat'),
            'spike': import_image('graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
            'spike_chain': import_image('graphics', 'enemies', 'spike_ball', 'spiked_chain'),
            'tooth': import_folder('graphics', 'enemies', 'tooth', 'run'), 
            'shell': import_sub_folders('graphics','enemies','shell'),
            'pearl': import_image('graphics', 'enemies', 'bullets', 'pearl'),
            'items': import_sub_folders('graphics', 'items'),
            'particle': import_folder('graphics', 'effects', 'particle'),
            'water_top': import_folder('graphics', 'level', 'water', 'top'),
            'water_body': import_image('graphics', 'level', 'water', 'body'),
            'bg_tiles': import_folder_dict('graphics', 'level', 'bg', 'tiles'),
            'cloud_small': import_folder('graphics','level', 'clouds', 'small'),
			'cloud_large': import_image('graphics','level', 'clouds', 'large_cloud'),
            
        }
        self.font = pygame.font.Font(get_resource_path(join('graphics', 'ui', 'runescape_uf.ttf')), 40)
        self.ui_frames = {
            'heart': import_folder('graphics', 'ui', 'heart'),
            'coin': import_image('graphics', 'ui', 'coin'),
        }
        self.overworld_frames = {
			'palms': import_folder('graphics', 'overworld', 'palm'),
			'water': import_folder('graphics', 'overworld', 'water'),
			'path': import_folder_dict('graphics', 'overworld', 'path'),
			'icon': import_sub_folders('graphics', 'overworld', 'icon'),
		}

    def check_game_over(self):
        if self.data.health <= 0:
            if not self.game_over_started:
                self.game_over_started = True
                self.timers['Game Over'].activate()
                self.ui.display_game_over()

            if not self.timers['Game Over'].active:
                self.restart_game()

        if self.data.unlocked_level == 6:
            if not self.game_over_started:
                self.game_over_started = True
                self.timers['Game Over'].activate()
                self.ui.displayer_game_won()

            if not self.timers['Game Over'].active:
                self.restart_game()
    
                

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    
    def restart_game(self):
        self.game_over_started = False
        if hasattr(self, 'game_over_started'):
            delattr(self, 'game_over_started')
            self.game_over_started = False
        self.data.health = 5  
        self.data.coins = 0
        self.data.unlocked_level = 0
        self.data.current_level = 0
        self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)
    

    def run(self): #Game loop
        while True:
            dt = clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.update_timers()
            self.check_game_over() 
            self.current_stage.run(dt)
            self.ui.update(dt)
            
            #debuginfo(self.data.health)
            pygame.display.update()
            
            

if __name__ == '__main__':
    game = Game()
    game.run()