import time

import pygame
from menu import *
from rating import Rating
from mini_game import *

class Game:
    def __init__(self):
        pygame.init()
        self.running, self.playing, self.game_mode, self.start_time = True, False, False, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY = False, False, False, False, False

        self.display = pygame.Surface((1280, 720))
        self.DISPLAY_W, self.DISPLAY_H = self.display.get_size()
        self.window = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))

        self.font_name = './assets/Font/8-BIT WONDER.TTF'
        self.BLACK, self.WHITE, self.BLUE, self.GREEN, self.RED, self.ORANGE = (0, 0, 0), (255, 255, 255), (0, 0, 128), (1, 50, 32), (139, 0, 0), (199, 110, 0)
        self.BG = pygame.transform.scale(pygame.image.load("assets/Background/bg.png"), (self.DISPLAY_W, self.DISPLAY_H))

        self.main_menu = MainMenu(self)
        self.difficulties = DifficultyMenu(self)
        self.mini_game_menu = MiniGameMenu(self)
        self.rating = Rating(self)

        self.cur_menu = self.main_menu

        self.cur_minigame = False


    def game_loop(self):
        while self.playing:
            self.display.fill(self.BLACK)
            self.check_events()

            # print(1)
            # todo let the user select mini game that he wants to play (rock paper scissors, Hangman, binary to digit)
                # todo show options
                # todo track events and move cursor
                # todo check for selection and set cur_mini_game
            self.mini_game_menu.display_menu()

            # todo start mini game based on selection
            # todo print game rules
            # todo let user play the game

            # print(2)

            self.window.blit(self.display, (0,0))
            pygame.display.update()

            self.reset_keys()



    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing, self.rating.rating, self.cur_menu.run_display = False, False, False, False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True
                if event.key == pygame.K_ESCAPE:
                    self.ESC_KEY = True


    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY = False, False, False, False, False


    def draw_text(self, text, size, x, y, color = None, **kwargs):
        if not color:
            color = self.WHITE

        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        position = 'topleft'
        if 'position' in kwargs:
            position = kwargs['position']

        setattr(text_rect, position, (x, y))

        self.display.blit(text_surface, text_rect)


    def start_game(self, difficulty):
        self.playing = True
        self.game_mode = difficulty
        self.start_time = int(time.time())