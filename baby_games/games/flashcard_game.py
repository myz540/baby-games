import sys
import pygame
from collections import deque
import os
import glob
import random
from static.consts import ALL_COLORS, PRIMARY_COLORS
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
        self.DEFAULT_SUBSAMPLE_SIZE = 5 # 100
        self.DEFAULT_RECYCLE_FLASHCARDS = False

        self._running = False

        self._test = os.environ.get("DEBUG")

        self.surface = None
        self.clock = None

        self.current_card_idx = 0
        self.flash_card_pile = None

        self.main_menu = None
        self.play_menu = None
        self.play_submenu = None

        self.size = self.width, self.height = (800, 600)
        #self.size = self.width, self.height = (1920, 1080)
        if self._test:
            print("Using test flashcard sources")
            self.flashcard_sources = glob.glob("static/test/alphabet/*")
        else:
            print("Using default flashcard sources with subsampling")
            self.flashcard_sources = glob.glob("static/flashcards/**/*")

        self.flashcard_sources = set(self.flashcard_sources)
        self.fresh_sources = self.flashcard_sources.copy()

        self.params = dict()
        self.params['mode'] = self.DEFAULT_MODE
        self.params['color_schema'] = self.DEFAULT_COLOR_SCHEMA
        self.params['dara_face'] = self.DEFAULT_DARA_FACE
        self.params['recycle_flashcards'] = self.DEFAULT_RECYCLE_FLASHCARDS

    def main(self):

        while True:
            self.clock.tick(self.FPS)

            self.main_background()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            self.main_menu.mainloop(events)


    def play_game(self):
        card = self.flash_card_pile[self.current_card_idx]
        card = pygame.transform.scale(card, self.size)

        while 1:
            for event in pygame.event.get():
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
                        card.blit(dara_face, pygame.mouse.get_pos())
                    else:
                        if self.MOUSE_COUNTER % 5 == 0:
                            # This ensures local_color is always set, probably not the best...
                            local_color = self.get_color()
                            self.MOUSE_COUNTER = 0

                        self.MOUSE_COUNTER += 1

                        pygame.mouse.set_cursor(*pygame.cursors.diamond)
                        pygame.draw.circle(card, local_color, (pygame.mouse.get_pos()), 60)
                self.surface.blit(card, (0, 0))

                pygame.display.flip()

    def draw_card(self, event=None):
        print(len(self.flash_card_pile))
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
        self.current_card_idx += 1
        if self.current_card_idx >= len(self.flash_card_pile):
            if self.params['recycle_flashcards']:
                print("Out of cards, reshuffling the flash card pile...")
                random.shuffle(self.flash_card_pile)
            else:
                print("Out of cards, creating a new flash card pile...")
                self.init_flashcards()
            self.current_card_idx = 0

        print("draw_card {}".format(self.current_card_idx))
        card = self.flash_card_pile[self.current_card_idx]
        return card

    def _draw_previous_card(self):
        if self.current_card_idx > 0:
            self.current_card_idx -= 1
        card = self.flash_card_pile[self.current_card_idx]
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
        self.surface = pygame.display.set_mode(self.size)
        #self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def init_clock(self):
        self.clock = pygame.time.Clock()

    def init_flashcards(self):
        # flash_card_pile is a deque<Surface> objects
        # if too many flashcards are used, the system freezes trying to load them all into memory
        # quick and dirty subsampling
        if len(self.flashcard_sources) > self.DEFAULT_SUBSAMPLE_SIZE:
            try:
                sources = set(random.sample(self.fresh_sources, self.DEFAULT_SUBSAMPLE_SIZE))
                self.fresh_sources = self.fresh_sources - sources
            except ValueError:
                print("Not enough fresh flashcards left, exiting...")
                sys.exit()

        else:
            sources = self.flashcard_sources

        self.flash_card_pile = deque([pygame.image.load(s).convert() for s in sources])
        self.current_card_idx = 0

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

    def toggle_recycle(self, value, _bool):
        if _bool == 'YES':
            self.params['recycle_flashcards'] = True
        else:
            self.params['recycle_flashcards'] = False

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
        self.play_menu.add_selector('Recycle flashcards?',
                                    [('No', 'NO'),
                                     ('Yes', 'YES')],
                                    onchange=self.toggle_recycle,
                                    selector_id='recycle_flashcards')
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


def main():
    # Init pygame
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    game = FlashcardGame()
    game.init_surface()
    game.init_clock()
    game.init_flashcards()
    game.init_menu()
    game.main()

if __name__ == '__main__':
    main()
    
