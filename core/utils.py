<<<<<<< HEAD
import pygame
import math
import random
import os
from pygame.locals import *

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set the height and width of the screen
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700


class Block(pygame.sprite.Sprite):

    def __init__(self, color):
        super().__init__()

        self.image = pygame.Surface([20, 15])
        self.image.fill(color)

        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.Surface([20, 20])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - 50

    def update(self):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.move_left()
        elif keys[pygame.K_d]:
            self.move_right()
        elif keys[pygame.K_w]:
            self.move_up()
        elif keys[pygame.K_s]:
            self.move_down()

    def move_left(self):
        if self.rect.x > 0:
            self.rect.x -= 10

    def move_right(self):
        if self.rect.x < SCREEN_WIDTH - 20:
            self.rect.x += 10

    def move_up(self):
        if self.rect.y > 0:
            self.rect.y -= 10

    def move_down(self):
        if self.rect.y < SCREEN_HEIGHT - 20:
            self.rect.y += 10


class Projectile(pygame.sprite.Sprite):

    def __init__(self, start_x, start_y, dest_x, dest_y, color=WHITE):
        super().__init__()

        self.image = pygame.Surface([4, 10])
        self.image.fill(color)
        self.rect = self.image.get_rect()

        # Move the bullet to our starting location
        self.rect.x = start_x
        self.rect.y = start_y

        # Because rect.x and rect.y are automatically converted
        # to integers, we need to create different variables that
        # store the location as floating point numbers. Integers
        # are not accurate enough for aiming.
        self.floating_point_x = start_x
        self.floating_point_y = start_y

        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        velocity = 5
        self.change_x = math.cos(angle) * velocity
        self.change_y = math.sin(angle) * velocity

    def update(self):
        # The floating point x and y hold our more accurate location.
        self.floating_point_y += self.change_y
        self.floating_point_x += self.change_x

        # The rect.x and rect.y are converted to integers.
        self.rect.y = int(self.floating_point_y)
        self.rect.x = int(self.floating_point_x)

        # If the bullet flies of the screen, get rid of it.
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            self.kill()


def load_image(file_name):
    if os.path.isfile and os.path.exists(file_name):
        image = pygame.image.load(file_name).convert_alpha()
        return image



=======
import pygame
import math
import random
import os
from pygame.locals import *

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set the height and width of the screen
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700


class Block(pygame.sprite.Sprite):

    def __init__(self, color):
        super().__init__()

        self.image = pygame.Surface([20, 15])
        self.image.fill(color)

        self.left_boundary = 0
        self.right_boundary = 0
        self.top_boundary = 0
        self.bottom_boundary = 0

        # Instance variables for our current speed and direction
        self.change_x = 0
        self.change_y = 0

        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x += self.change_x
        self.rect.y += self.change_y

        if self.rect.right >= self.right_boundary or self.rect.left <= self.left_boundary:
            self.change_x *= -1

        if self.rect.bottom >= self.bottom_boundary or self.rect.top <= self.top_boundary:
            self.change_y *= -1


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.Surface([20, 20])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - 50

    def update(self):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.move_left()
        elif keys[pygame.K_d]:
            self.move_right()
        elif keys[pygame.K_w]:
            self.move_up()
        elif keys[pygame.K_s]:
            self.move_down()

    def move_left(self):
        if self.rect.x > 0:
            self.rect.x -= 10

    def move_right(self):
        if self.rect.x < SCREEN_WIDTH - 20:
            self.rect.x += 10

    def move_up(self):
        if self.rect.y > 0:
            self.rect.y -= 10

    def move_down(self):
        if self.rect.y < SCREEN_HEIGHT - 20:
            self.rect.y += 10


class Projectile(pygame.sprite.Sprite):

    def __init__(self, start_x, start_y, dest_x, dest_y):
        super().__init__()

        self.image = pygame.Surface([4, 10])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

        # Move the bullet to our starting location
        self.rect.x = start_x
        self.rect.y = start_y

        # Because rect.x and rect.y are automatically converted
        # to integers, we need to create different variables that
        # store the location as floating point numbers. Integers
        # are not accurate enough for aiming.
        self.floating_point_x = start_x
        self.floating_point_y = start_y

        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        velocity = 5
        self.change_x = math.cos(angle) * velocity
        self.change_y = math.sin(angle) * velocity

    def update(self):
        # The floating point x and y hold our more accurate location.
        self.floating_point_y += self.change_y
        self.floating_point_x += self.change_x

        # The rect.x and rect.y are converted to integers.
        self.rect.y = int(self.floating_point_y)
        self.rect.x = int(self.floating_point_x)

        # If the bullet flies of the screen, get rid of it.
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            self.kill()


def load_image(file_name):
    if os.path.isfile and os.path.exists(file_name):
        image = pygame.image.load(file_name).convert_alpha()
        return image



>>>>>>> d0c0549a364e626a7cf9d273e38c9e3a8c65f9b3
