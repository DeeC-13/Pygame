import pygame
import random

from pygame import mixer

pygame.init()

FPS = 60
player_vel = 5
food_vel = 5
block_size = 64
s_height = 768  # 12 tiles high
s_width = 768  # 12 tiles wide
dx = 0
dy = 0
count = 0
game_over = False

# Creates Display
screen = pygame.display.set_mode((s_width, s_height))

# stores the time when the game starts
start_time = pygame.time.get_ticks()

# creates screen caption and icon
pygame.display.set_caption("duck")
icon = pygame.image.load('img/duck.png')
pygame.display.set_icon(icon)

# background music
mixer.music.load('sounds/quack.mp3')
mixer.music.play(-1)


# creates the screen background
def get_background(name):
    image = pygame.image.load('img/bg.png', name).convert_alpha()
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(s_width // width + 1):
        for j in range(s_height // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


# creates the food sprite
class Food(pygame.sprite.Sprite):
    def __init__(self, name='food'):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.image = pygame.image.load('img/crackers.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, s_width - self.rect.width)
        self.rect.y = -self.rect.height
        self.vel_x = 0
        self.vel_y = random.randrange(3, 5)
        self.spawn_timer = random.randrange(10, 120)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if self.rect.top > s_height:
            self.kill()


food = Food()


# spawns the food
class FoodSpawner:
    def __init__(self):
        self.food_group = pygame.sprite.Group()
        self.spawn_timer = random.randrange(30, 120)

    def update(self):
        self.food_group.update()
        if self.spawn_timer == 0:
            self.spawn_food()
            self.spawn_timer = random.randrange(30, 90)
        else:
            self.spawn_timer -= 1

    def spawn_food(self):
        new_food = Food()
        self.food_group.add(new_food)

    def draw(self):
        for f in self.food_group:
            food_spawner.food_group.update()


food_spawner = FoodSpawner()


# creates the player sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/duck2.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.transformed_image = pygame.transform.flip(self.image, True, False)
        self.direction = True
        self.rect.x = s_width // 2
        self.rect.y = 525
        self.x_vel = 0
        self.y_vel = 0
        self.gravity = 1
        self.fall_count = 0
        self.jump_count = 0
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        self.y_vel = -self.gravity * 8
        self.jump_count += 1
        if self.jump_count == 2:
            self.fall_count = 8
            self.y_vel = -5
            self.gravity = 8

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.rect.x -= vel
        self.direction = False
        if self.rect.left < dx:
            self.rect.left = dx

    def move_right(self, vel):
        self.rect.x += vel
        self.direction = True
        if self.rect.right > s_width:
            self.rect.right = s_width

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.gravity)
        self.move(self.x_vel, self.y_vel)
        self.fall_count += 1
        self.jump_count = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > s_height:
            self.rect.bottom = s_height

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.y_vel *= -1

    def draw(self, screen, background, bg_image, player, objects):
        # draws background tiles to the screen
        for tile in background:
            screen.blit(bg_image, tile)

        # draws player to screen
        screen.blit(pygame.transform.flip(self.image, self.direction, False), player)

        # draws block objects to the screen
        for obj in objects:
            obj.draw(screen)


# checks vertical collisions with objects
def handle_vertical_collision(player, objects, dy):
    collided_objects = []

    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            if player.rect.top < obj.rect.top:
                player.x_vel = 0
                player.y_vel = 0
                player.fall_count = 1
                player.jump_count = 0
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

        collided_objects.append(obj)

    return collided_objects


# checks horizontal collisions with objects
def collide(player, objects, dx):
    global count
    player.move(dx, 0)
    collided_objects = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_objects = obj
            break

    # checks for collisions between player and food and adds to score
    if pygame.sprite.groupcollide(sprite_group, food_spawner.food_group, False, True):
        collision_sound = mixer.Sound('sounds/crunch.mp3')
        collision_sound.play()
        count += 1

    player.move(-dx, 0)
    return collided_objects


# handles left and right player movement
def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0

    collide_left = collide(player, objects, -player_vel * 3)
    collide_right = collide(player, objects, player_vel * 3)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(player_vel)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(player_vel)

    handle_vertical_collision(player, objects, player.y_vel)


player = Player()
sprite_group = pygame.sprite.Group()
sprite_group.add(player)


# creates block objects
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        image = pygame.image.load('img/dirt tile.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.image.blit(image, (0, 0))


class Block1(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        image = pygame.image.load('img/grass tile.png').convert_alpha()
        self.image.blit(image, (0, 0))


class Block2(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        image = pygame.image.load('img/platform.png').convert_alpha()
        self.image.blit(image, (0, 0))


# creates the scoring system
class Score:
    def __init__(self):
        self.score_count = count
        self.font = pygame.font.Font('freesansbold.ttf', 25)
        self.text = self.font.render("Score: " + str(self.score_count), True, (255, 255, 255))

    def draw(self, screen):
        screen.blit(self.text, (20, 700))

    def update(self):
        self.text = self.font.render("Score: " + str(count), True, (255, 255, 255))


score = Score()


# creates the countdown for the level
class Countdown:
    def __init__(self):
        self.game_time = 30
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = self.game_time - self.start_time
        self.text_font = pygame.font.Font('freesansbold.ttf', 25)
        self.text = self.text_font.render("Countdown: " + str(start_time), True, (255, 255, 255))

    def draw(self):
        countdown.timer()

    # creates the countdown timer
    def timer(self):
        global game_over, seconds
        game_over = False
        seconds = (round(self.game_time - pygame.time.get_ticks() // 1000))
        screen.blit(self.text_font.render(f"Countdown: {seconds}", True, (255, 255, 255)), (520, 700))

        # tells the timer to stop if less than 0 and draw the game over screen
        if seconds <= -1:
            game_over = True
            pygame.mixer.music.stop()
            gameover.draw()
            return


countdown = Countdown()


# creates the gameover function
class Gameover:
    def __init__(self):
        self.over_font = pygame.font.Font('freesansbold.ttf', 100)
        self.over = self.over_font.render("GAME OVER!", True, (255, 255, 255))
        self.quit_font = pygame.font.Font('freesansbold.ttf', 30)
        self.quit = self.quit_font.render(f"Press Q or Close Window to Quit", True, (255, 255, 255))
        self.score_font = pygame.font.Font('freesansbold.ttf', 25)
        self.final_score = self.score_font.render(f"You Scored: {score.score_count}", True, (255, 255, 255))

    def draw(self):
        gameover.update()

    def update(self):
        self.final_score = self.score_font.render(f"You Scored: {count}", True, (255, 255, 255))
        screen.fill((0, 0, 70))
        screen.blit(self.over, (55, s_height // 3))
        screen.blit(self.final_score, (290, 380))
        screen.blit(self.quit, (147, 440))


gameover = Gameover()


# Game Loop
def main(screen):
    global game_over, begin

    # Create a clock object
    clock = pygame.time.Clock()

    # creates the background image for background tiles
    background, bg_image = get_background('bg.png')

    # creates the block objects
    floor = [Block(i * block_size, s_height - block_size, block_size)
             for i in range(-s_width // block_size, s_width // block_size)]
    objects = [*floor, Block1(0, s_height - block_size * 2, block_size),
               Block1(64, s_height - block_size * 2, block_size),
               Block1(128, s_height - block_size * 2, block_size),
               Block1(192, s_height - block_size * 2, block_size),
               Block1(256, s_height - block_size * 2, block_size),
               Block1(320, s_height - block_size * 2, block_size),
               Block1(384, s_height - block_size * 2, block_size),
               Block1(448, s_height - block_size * 2, block_size),
               Block1(512, s_height - block_size * 2, block_size),
               Block1(576, s_height - block_size * 2, block_size),
               Block1(640, s_height - block_size * 2, block_size),
               Block1(704, s_height - block_size * 2, block_size),
               Block2(576, s_height - block_size * 4, block_size),
               Block2(640, s_height - block_size * 4, block_size),
               Block2(704, s_height - block_size * 4, block_size),
               Block2(64, s_height - block_size * 4.55, block_size),
               Block2(128, s_height - block_size * 4.55, block_size),
               Block2(192, s_height - block_size * 4.55, block_size),
               Block2(244, s_height - block_size * 7, block_size),
               Block2(308, s_height - block_size * 7, block_size),
               Block2(372, s_height - block_size * 7, block_size),
               Block2(436, s_height - block_size * 7, block_size),
               Block2(25, s_height - block_size * 8.5, block_size),
               Block2(340, s_height - block_size * 9, block_size),
               Block2(524, s_height - block_size * 10, block_size),
               Block2(588, s_height - block_size * 10, block_size),
               Block2(576, s_height - block_size * 10, block_size),
               Block2(160, s_height - block_size * 10.75, block_size),
               Block2(704, s_height - block_size * 11, block_size)
               ]

    running = True

    while running:

        while game_over:

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q or event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        # creates the quit function to close the window
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

            # sets the double jump variable
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        # calls, draws and updates the functions on the screen
        player.loop(FPS)
        handle_move(player, objects)
        player.draw(screen, background, bg_image, player, objects)
        food_spawner.update()
        food_spawner.food_group.draw(screen)
        score.update()
        score.draw(screen)
        countdown.draw()

        # #updates the display
        pygame.display.update()

        # sets frames per second to 60
        clock.tick(FPS)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(screen)
