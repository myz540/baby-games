import pygame

ALL_COLORS = pygame.color.THECOLORS
_PRIMARY_COLOR_NAMES = ['yellow', 'blue', 'green', 'red', 'purple', 'white', 'black', 'orange']
PRIMARY_COLORS = {k: ALL_COLORS[k] for k in ALL_COLORS if k in _PRIMARY_COLOR_NAMES}
