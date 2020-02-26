import sys
import pygame
import numpy as np
from pygame.locals import *
from collections import deque
import os
import glob
import random
from consts import ALL_COLORS, PRIMARY_COLORS

pygame.init()

size = width, height = (1000, 800)
black = (0, 0, 0)
speed = [0, 0]

starting_pos = (width / 2, height - 100)

screen = pygame.display.set_mode(size)

ball = pygame.image.load("static/intro_ball.gif")
ballrect = ball.get_rect(center=starting_pos)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            ballrect = ball.get_rect(center=starting_pos)
            mouse_pos = pygame.mouse.get_pos()
            # create a trajectory from starting pos to mouse_pos
            vector = np.array([mouse_pos[0] - starting_pos[0], mouse_pos[1] - starting_pos[1]], dtype='float')
            print(vector)
            v_hat = 2 * (vector / np.linalg.norm(vector))
            print(v_hat)
            speed = v_hat

    ballrect = ballrect.move(speed)
    screen.fill(black)
    screen.blit(ball, starting_pos)
    screen.blit(ball, ballrect)
    pygame.display.flip()
