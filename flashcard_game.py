import sys
import pygame
from pygame.locals import *
from collections import deque
import os
import glob
import random
from consts import ALL_COLORS, PRIMARY_COLORS
import pygameMenu
import traceback


class FlashcardGame:

    def __init__(self, **kwargs):
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_WHITE = (255, 255, 255)
        self.MENU_BACKGROUND_COLOR = (228, 55, 36)
        self.FPS = 30.0
        self.MOUSE_COUNTER = 0
        self.DEFAULT_MODE = 'NORMAL'
        self.DEFAULT_COLOR_SCHEMA = 'PRIMARY'
        self.DEFAULT_DARA_FACE = False
        self.DEFAULT_SUBSAMPLE_SIZE = 100

        self._running = False

        self._test = os.environ.get("DEBUG")
        #self._test = True # for now...

        self.main_menu = None
        self.surface = None
        self.clock = None

        self.current_card = None
        self.flash_card_pile = None
        self.remaining_flash_card_pile = None
        self.discard_flash_card_pile = None

        self.main_menu = None
        self.play_menu = None
        self.play_submenu = None

        #self.size = self.width, self.height = (800, 600)
        self.size = self.width, self.height = (1920, 1080)
        if self._test:
            print("Using test flashcard sources")
            self.flashcard_sources = glob.glob("static/flashcards/alphabet/*")
        else:
            print("Using default flashcard sources with subsampling")
            self.flashcard_sources = glob.glob("static/flashcards/**/*")

        self.params = dict()
        self.params['mode'] = self.DEFAULT_MODE
        self.params['color_schema'] = self.DEFAULT_COLOR_SCHEMA
        self.params['dara_face'] = self.DEFAULT_DARA_FACE

    def main(self):

        while True:
            self.clock.tick(self.FPS)

            self.main_background()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            self.main_menu.mainloop(events)

            pygame.display.flip()

    def play_game(self):
        card = self.draw_card()
        card = pygame.transform.scale(card, self.size)
        cardrect = card.get_rect()

        while 1:
            for event in pygame.event.get():
                dara_face = None
                if event.type == pygame.QUIT:
                    sys.exit()

                # ToDo implement feature where for alphabet flash cards, the correct key needs to be pressed to move on
                if event.type == pygame.KEYDOWN:
                    print(pygame.key.name(event.key))
                    try:
                        card = self.draw_card(event)
                    except IndexError as e:
                        traceback.print_exc()
                    card = pygame.transform.scale(card, self.size)
                    cardrect = card.get_rect()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    print(event.button)
                    print(type(event.button))

                    if self.params['dara_face'] and event.button == 1:
                        print("HERE")
                        dara_face = pygame.image.load("static/dara_face.jpg").convert()
                        dara_face = pygame.transform.scale(dara_face, (140, 210))
                        dara_face_rect = dara_face.get_rect()
                        card.blit(dara_face, pygame.mouse.get_pos())
                    else:
                        if self.MOUSE_COUNTER % 5 == 0:
                            local_color = self.get_color()
                            self.MOUSE_COUNTER = 0

                        self.MOUSE_COUNTER += 1

                        pygame.mouse.set_cursor(*pygame.cursors.diamond)
                        pygame.draw.circle(card, local_color, (pygame.mouse.get_pos()), 60)
                self.surface.blit(card, (0, 0))

                pygame.display.flip()

    def draw_card(self, event=None):
        mode = self.params['mode']
        if mode == 'NOREPEATS':
            if isinstance(event, pygame.event.EventType) and event.key == pygame.K_LEFT:
                card = self._draw_previous_card()
            else:
                card = self._draw_new_card()
        else:
            card = random.choice(self.flash_card_pile)
        return card

    def _draw_new_card(self):
        if len(self.remaining_flash_card_pile) == 0:
            print("Out of cards, resetting the flash card pile")
            self.remaining_flash_card_pile = deque(self.flash_card_pile.copy())
            random.shuffle(self.remaining_flash_card_pile)
            self.discard_flash_card_pile = deque()

        card = self.remaining_flash_card_pile.popleft()
        self.discard_flash_card_pile.append(card)
        return card

    def _draw_previous_card(self):
        card = self.discard_flash_card_pile.pop()
        self.remaining_flash_card_pile.appendleft(card)
        return card

    def get_color(self, color_tuple=None):
        color_schema = self.params['color_schema']
        if color_tuple and len(color_tuple) == 3:
            color = pygame.Color(*color_tuple)
        elif color_schema == 'PRIMARY':
            _primary_color = random.choice(list(PRIMARY_COLORS.values()))
            color = pygame.Color(*_primary_color)
        elif color_schema == 'BLACK':
            color = self.COLOR_BLACK
        else:
            _random_color = random.choice(list(ALL_COLORS.values()))
            color = pygame.Color(*_random_color)
        print(color)
        return color

    def init_surface(self):
        #self.surface = pygame.display.set_mode(self.size)
        self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def init_clock(self):
        self.clock = pygame.time.Clock()

    def init_flashcards(self):
        # flash_card_pile is a list<Surface> objects
        # if too many flashcards are used, the system freezes trying to load them all into memory
        # quick and dirty subsampling
        if len(self.flashcard_sources) > self.DEFAULT_SUBSAMPLE_SIZE:
            sources = random.sample(self.flashcard_sources, self.DEFAULT_SUBSAMPLE_SIZE)
        else:
            sources = self.flashcard_sources
        # ToDo the unaddressed issue here is to sample a different set of flashcards when the first set has been cycled,
        self.flash_card_pile = [pygame.image.load(s) for s in sources]
        self.remaining_flash_card_pile = deque(self.flash_card_pile.copy())
        random.shuffle(self.remaining_flash_card_pile)
        self.discard_flash_card_pile = deque()

    def change_mode(self, value, mode):
        self.params['mode'] = mode
        print(mode)

    def change_color_schema(self, value, color_schema):
        self.params['color_schema'] = color_schema
        print(color_schema)

    def toggle_dara_face(self, value, _bool):
        if _bool == 'YES':
            self.params['dara_face'] = True
        else:
            self.params['dara_face'] = False

    def init_menu(self):
        # Play menu
        self.play_menu = pygameMenu.Menu(self.surface,
                                         bgfun=self.main_background,
                                         color_selected=self.COLOR_WHITE,
                                         font=pygameMenu.font.FONT_BEBAS,
                                         font_color=self.COLOR_BLACK,
                                         font_size=30,
                                         menu_alpha=100,
                                         menu_color=self.MENU_BACKGROUND_COLOR,
                                         menu_height=int(self.height * 0.7),
                                         menu_width=int(self.width * 0.7),
                                         onclose=pygameMenu.events.DISABLE_CLOSE,
                                         option_shadow=False,
                                         title='Play menu',
                                         window_height=self.height,
                                         window_width=self.width
                                         )

        self.play_submenu = pygameMenu.Menu(self.surface,
                                            bgfun=self.main_background,
                                            color_selected=self.COLOR_WHITE,
                                            font=pygameMenu.font.FONT_BEBAS,
                                            font_color=self.COLOR_BLACK,
                                            font_size=30,
                                            menu_alpha=100,
                                            menu_color=self.MENU_BACKGROUND_COLOR,
                                            menu_height=int(self.height * 0.5),
                                            menu_width=int(self.width * 0.7),
                                            onclose=pygameMenu.events.DISABLE_CLOSE,
                                            option_shadow=False,
                                            title='Sub menu',
                                            window_height=self.height,
                                            window_width=self.width
                                            )
        self.play_submenu.add_option('Back', pygameMenu.events.BACK)

        self.play_menu.add_option('Start',  # When pressing return -> self.play_game()
                                  self.play_game
                                  )
        self.play_menu.add_selector('Select mode',
                                    [('1 - Normal Mode', 'NORMAL'),
                                     ('2 - No Repeats', 'NOREPEATS'),
                                     ('3 - Alphabet Only', 'ALPHABET')],
                                    onchange=self.change_mode,
                                    selector_id='select_mode')
        self.play_menu.add_selector('Select color schema',
                                    [('1 - All colors', 'ALL'),
                                     ('2 - Primary colors', 'PRIMARY'),
                                     ('3 - Black', 'BLACK')],
                                    onchange=self.change_color_schema,
                                    selector_id='select_color_schema')
        self.play_menu.add_selector('Dara face???',
                                    [('No', 'NO'),
                                     ('Yes', 'YES')],
                                    onchange=self.toggle_dara_face,
                                    selector_id='dara_face')
        self.play_menu.add_option('Another menu', self.play_submenu)
        self.play_menu.add_option('Return to main menu', pygameMenu.events.BACK)

        # Main menu
        self.main_menu = pygameMenu.Menu(self.surface,
                                         bgfun=self.main_background,
                                         color_selected=self.COLOR_WHITE,
                                         font=pygameMenu.font.FONT_BEBAS,
                                         font_color=self.COLOR_BLACK,
                                         font_size=30,
                                         menu_alpha=100,
                                         menu_color=self.MENU_BACKGROUND_COLOR,
                                         menu_height=int(self.height * 0.6),
                                         menu_width=int(self.width * 0.6),
                                         onclose=pygameMenu.events.DISABLE_CLOSE,
                                         option_shadow=False,
                                         title='Main menu',
                                         window_height=self.height,
                                         window_width=self.width
                                         )

        self.main_menu.add_option('Play', self.play_menu)
        self.main_menu.add_option('Quit', pygameMenu.events.EXIT)

        # Configure main menu
        self.main_menu.set_fps(self.FPS)

    def main_background(self):
        self.surface.fill(self.COLOR_BLACK)


if __name__ == '__main__':

    # Init pygame
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    game = FlashcardGame()
    game.init_surface()
    game.init_clock()
    game.init_flashcards()
    game.init_menu()
    game.main()
