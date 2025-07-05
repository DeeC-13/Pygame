import random
import math

import gravity
import pygame
from pygame import mixer

#Intialises pygame
pygame.init()

#Creates Display
screen = pygame.display.set_mode((800, 700))

#background music
mixer.music.load('quack.mp3')
mixer.music.play(-1)

#Title and Icon
pygame.display.set_caption("Oh Qwackers")
icon = pygame.image.load('duck.png')
pygame.display.set_icon(icon)

#Player
playerImg = pygame.image.load('duck2.png')
playerX = 350
playerY = 500
playerX_move = 0

#Food
foodImg = []
foodX = []
foodY = []
foodX_move = []
foodY_move = []
num_of_food = 3

for i in range(num_of_food):
    foodImg.append(pygame.image.load('crackers.png'))
    foodX.append(random.randint(0, 750))
    foodY.append(random.randint(50, 460))
    foodX_move.append(0.05)
    foodY_move.append(0.1)

#score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 25)
textX = 20
textY = 650

def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))

def player(x, y):
    screen.blit(playerImg, (x, y))

def food(x, y, i):
    screen.blit(foodImg[i], (x, y))

def iscollision(playerX, playerY, foodX, foodY):
    distance = math.sqrt((math.pow(playerX - foodX, 2)) + (math.pow(playerY - foodY, 2)))
    if distance < 27:
        return True
    else:
        return False

#Game Loop
running = True
while running:

    screen.fill((25, 125, 150))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #checks for keystrokes
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_move = -0.2
            if event.key == pygame.K_RIGHT:
                playerX_move = 0.2

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_move = 0

    #player movement
    playerX += playerX_move

    if playerX <= 0:
        playerX = 0
    if playerX >= 736:
        playerX = 736

    #food movement
    for i in range(num_of_food):

        foodX[i] += foodX_move[i]
        foodY[i] += foodY_move[i]

        if foodX[i] <= 50:
            foodX_move[i] = 0.05
        if foodX[i] >= 750:
            foodX_move[i] = -0.05
        if foodY[i] <= 50:
            foodY_move[i] = 0.1
        if foodY[i] >= 555:
            foodY_move[i] = -0.1

        food(foodX[i], foodY[i], i)

        #collision
        collision = iscollision(playerX, playerY, foodX[i], foodY[i])

        if collision:
            collision_sound = mixer.Sound('crunch.mp3')
            collision_sound.play()
            score_value += 1
            foodX[i] = random.randint(0, 750)
            foodY[i] = random.randint(50, 550)

    player(playerX, playerY)
    show_score(textX, textY)

    pygame.display.update()
