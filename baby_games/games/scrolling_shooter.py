import pygame
import random
from core.utils import Player, Block, Projectile
from core.utils import SCREEN_HEIGHT, SCREEN_WIDTH, BLACK, WHITE, BLUE, RED


# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

friendly_projectile_group = pygame.sprite.Group()

enemy_block_group = pygame.sprite.Group()

# This is a list of every sprite. All blocks and the player block as well.
all_sprites_group = pygame.sprite.Group()

for i in range(50):
    # This represents a block
    block = Block(RED)

    # Set a random location for the block
    block.rect.x = random.randrange(SCREEN_WIDTH)
    block.rect.y = random.randrange(350)

    # Set bounds for bouncing blocks
    block.change_x = random.randrange(-3, 4)
    block.change_y = random.randrange(-3, 4)
    block.left_boundary = 0
    block.top_boundary = 0
    block.right_boundary = SCREEN_WIDTH
    block.bottom_boundary = SCREEN_HEIGHT

    # Add the block to the list of objects
    enemy_block_group.add(block)
    all_sprites_group.add(block)


player = Player()
all_sprites_group.add(player)

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# kill counter
kill_count = 0

# set up background for scrolling
background = pygame.image.load('static/background/seamless-bg2.jpg').convert()
background = pygame.transform.scale(background, [SCREEN_WIDTH, SCREEN_HEIGHT*2])
y = 0

# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x = mouse_pos[0]
            mouse_y = mouse_pos[1]

            projectile = Projectile(player.rect.x, player.rect.y, mouse_x, mouse_y)
            projectile.rect.x = player.rect.x
            projectile.rect.y = player.rect.y
            friendly_projectile_group.add(projectile)
            all_sprites_group.add(projectile)

    # events are handled
    all_sprites_group.update()

    # check if friendly projectiles destroyed an enemy block
    for _projectile in friendly_projectile_group:

        block_hit_list = pygame.sprite.spritecollide(_projectile, enemy_block_group, True)

        for block in block_hit_list:
            friendly_projectile_group.remove(_projectile)
            all_sprites_group.remove(_projectile)
            kill_count += 1
            print(kill_count)

        if _projectile.rect.y < -10:
            friendly_projectile_group.remove(_projectile)
            all_sprites_group.remove(_projectile)

    # check if enemy block hits player
    player_hit = pygame.sprite.spritecollide(player, enemy_block_group, True)
    if player_hit:
        print("You died!")
        done = True

    # Clear the screen
    screen.fill(WHITE)

    # scroll background here
    rel_y = y % background.get_rect().height
    screen.blit(background, (0, rel_y - background.get_rect().height / 2.0))
    print(rel_y, y)
    y += 2
    if rel_y >= SCREEN_HEIGHT:
        screen.blit(background, (0, -background.get_rect().height / 2.0))
        y = 0

    pygame.draw.line(screen, (255, 0, 0), (0, rel_y), (SCREEN_WIDTH, rel_y), 3)

    # Draw all the spites
    all_sprites_group.draw(screen)

    # Limit to 60 frames per second
    clock.tick(60)

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

pygame.quit()