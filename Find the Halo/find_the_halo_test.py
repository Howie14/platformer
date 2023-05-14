import pygame

pygame.init()
info = pygame.display.Info()

HEIGHT = info.current_h
WIDTH = info.current_w
ASPECT_RATIO = WIDTH / HEIGHT

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Find the Halo")

clock = pygame.time.Clock()
FPS = 60

gravity = 0.75
damage = 1
ROWS = 16
COLS = 150
TILE_SIZE = HEIGHT // ROWS
TILE_TYPE = 6

virtual_surface = pygame.Surface((WIDTH, HEIGHT))
current_size = window.get_size()

moving_left = False
moving_right = False
shoot = False

rock_img = pygame.image.load('images/rock.png').convert_alpha()
item_img = pygame.image.load('images/rock.png').convert_alpha()
bg = (125, 199, 172)
red = (255, 0, 0)

font = pygame.font.Font("font/EightBits.ttf", 40)


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    virtual_surface.blit(img, (x, y))


def draw_bg():
    virtual_surface.fill(bg)
    pygame.draw.line(virtual_surface, red, (0, 700), (WIDTH, 700))


class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, speed, ammo, health):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = health
        self.max_health = self.health
        self.lose_health = True
        self.lose_counter = 3
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        for i in range(6):
            img = pygame.image.load(f'images/{self.char_type}/stand/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (img.get_width(), img.get_height()))
            self.animation_list.append(img)
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):

        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        for grass_block in block_group:
            if grass_block.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if grass_block.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = grass_block.bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = grass_block.top - self.rect.bottom

        if self.rect.bottom + dy > 700:
            dy = 700 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            rock = Rock(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery,
                        self.direction)
            rock_group.add(rock)
            self.ammo -= 1

    def update_animation(self):

        animation_cooldown = 140

        self.image = self.animation_list[self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False

    def draw(self):
        virtual_surface.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def ai(self):
        if self.alive and angel.alive:
            if self.direction == 1:
                ai_moving_right = True
            else:
                ai_moving_right = False
            ai_moving_left = not ai_moving_right
            self.move(ai_moving_left, ai_moving_right)
            self.move_counter += 1

            if self.move_counter > TILE_SIZE:
                self.direction *= -1
                self.move_counter *= -1


class World():
    def __init__(self):
        self.obstacle_list = []


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(f"images/blocks/{block_type}.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = item_img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self, angel):
            angel.ammo += 5
            self.kill()


class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = rock_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):

        self.rect.x += (self.direction * self.speed)

        if self.rect.right < 0 or self.rect.left > WIDTH:
            if angel.alive:
                self.kill()

        for rat in rat_group:

            if pygame.sprite.spritecollide(rat, rock_group, False):
                if rat.alive:
                    rat.health -= 1
                    self.kill()


rock_group = pygame.sprite.Group()
rat_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
block_group = pygame.sprite.Group()

item = Item(800, 650)
item_group.add(item)

grass_block = Block(100, 100, 'grass')
ground_block = Block(200, 100, 'ground')
block_group.add(grass_block)
block_group.add(ground_block)

angel = Player('angel', 500, 700, 7, 7, 3)
rat = Player('angel', 900, 645, 7, 0, 1)
rat_group.add(rat)

run = True
world = World()

while run:

    clock.tick(FPS)

    draw_bg()
    draw_text(f'Health: {angel.health}', font, (255, 255, 255), 40, 35)
    draw_text(f'Rocks: {angel.ammo}', font, (255, 255, 255), 40, 70)

    angel.update()
    angel.draw()
    for rat in rat_group:
        rat.ai()
        rat.update()
        rat.draw()
        if pygame.sprite.spritecollide(angel, rat_group, False):
            if angel.alive and rat.alive:
                angel.health -= damage
                angel.lose_health = False

    rock_group.update()
    rock_group.draw(virtual_surface)
    item_group.update()
    item_group.draw(virtual_surface)

    if rat.alive:

        if shoot:
            rat.shoot()

    if angel.alive:

        if shoot:
            angel.shoot()
        angel.move(moving_left, moving_right)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.VIDEORESIZE:
            new_width = event.w
            new_height = int(new_width / ASPECT_RATIO)
            window = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            current_size = window.get_size()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and angel.alive:
                moving_left = True
            if event.key == pygame.K_d and angel.alive:
                moving_right = True
            if event.key == pygame.K_e and angel.alive:
                shoot = True
            if event.key == pygame.K_SPACE and angel.alive:
                angel.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_e:
                shoot = False

    scaled_surface = pygame.transform.scale(virtual_surface, current_size)
    window.blit(scaled_surface, (0, 0))
    pygame.display.update()

pygame.quit()
