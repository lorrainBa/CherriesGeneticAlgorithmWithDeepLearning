import pygame
from sys import exit

pygame.init()

screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()

test_font = pygame.font.Font(None, 50)

sky_surface = pygame.image.load('graphics/Sky.png').convert()
ground_surface = pygame.image.load('graphics/ground.png').convert()
text_surface = test_font.render('salut', True , "Black")

snail_surface = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
snail_rect = snail_surface.get_rect(midbottom = (150,300))


player_surf = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
player_rect = player_surf.get_rect(midbottom = (0,300))

snailSpeed = 2
characterSpeed = 1
while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(sky_surface,(0,0))
    screen.blit(ground_surface,(0,300))
    screen.blit(text_surface,(300,50))


    snail_rect.left -= snailSpeed
    player_rect.left += characterSpeed

    if snail_rect.left < -50:
        snail_rect.left = 800
    elif snail_rect.left > 800:
        snail_rect.left = 0
    if player_rect.left < -50:
        player_rect.left = 800
    elif player_rect.left > 800:
        player_rect.left = 0

    screen.blit(snail_surface,(snail_rect.left,268))
    screen.blit(player_surf,player_rect)

    if player_rect.colliderect(snail_rect):
        snailSpeed = -(snailSpeed) 
        characterSpeed = -characterSpeed


    pygame.display.update()
    clock.tick(144)