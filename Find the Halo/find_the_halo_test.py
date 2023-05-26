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
scroll_thresh = 700
damage = 1
ROWS = 16
COLS = 150
TILE_SIZE = HEIGHT // ROWS
screen_scroll = 0
TILE_TYPES = 6

virtual_surface = pygame.Surface((WIDTH, HEIGHT))
current_size = window.get_size()

moving_left = False
moving_right = False
shoot = False

rock_img = pygame.image.load('images/rock/rock.png').convert_alpha()
item_img = pygame.image.load('images/items/item.png').convert_alpha()
bg = (177, 231, 248)
red = (255, 0, 0)

font = pygame.font.Font("font/EightBits.ttf", 40)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    virtual_surface.blit(img, (x, y))


def draw_bg():
    virtual_surface.fill(bg)


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
        self.image = pygame.image.load(f'images/{self.char_type}/Idle/0.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.disable = 0
        self.scrolling = False

    def update(self):
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):

        screen_scroll = 0
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
            if grass_block.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if grass_block.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = grass_block.rect.bottom - self.rect.top
                    self.in_air = False
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = grass_block.rect.top - self.rect.bottom
                    self.in_air = False

        for ground_block in block_group:
            if ground_block.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if ground_block.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = ground_block.rect.bottom - self.rect.top
                    self.in_air = False
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = ground_block.rect.top - self.rect.bottom
                    self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

        if self.char_type == 'angel':
            if self.rect.right > WIDTH - scroll_thresh or self.rect.left < scroll_thresh:
                self.scrolling = True
                self.rect.x -= dx
                screen_scroll = -dx
            else:
                self.scrolling = False

        return screen_scroll

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

            if self.move_counter > TILE_SIZE / 4:
                self.direction *= -1
                self.move_counter *= -1


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
        self.rect.midtop = (x + TILE_SIZE // 4, y + (TILE_SIZE - self.image.get_height()))

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
fire_group = pygame.sprite.Group()

item = Item(3215 - (55 * 9) + 15, 671 - (55 * 6) + 30)
item_group.add(item)


x1 = 80
x2 = 960
x3 = 960
x4 = -580
x5 = -580
x6 = -580
x7 = -580
x8 = -580
x9 = 1785
x10 = 1840 - (55 * 7)
x11 = 1785
x12 = 2500 + (55 * 10)
x13 = 3380

for i in range(13):
    ground_block = Block(x4, 836, 'ground')
    block_group.add(ground_block)
    x4 += 55

for i in range(12):
    ground_block = Block(x5, 781, 'ground')
    block_group.add(ground_block)
    x5 += 55

for i in range(12):
    ground_block = Block(x6, 726, 'ground')
    block_group.add(ground_block)
    x6 += 55

for i in range(12):
    ground_block = Block(x7, 671, 'ground')
    block_group.add(ground_block)
    x7 += 55

for i in range(12):
    grass_block = Block(x8, 671, 'grass')
    block_group.add(grass_block)
    x8 += 55

for i in range(16):
    grass_block = Block(x1, 836, 'grass')
    block_group.add(grass_block)
    x1 += 55

for i in range(85):
    ground_block = Block(x2, 836, 'ground')
    block_group.add(ground_block)
    x2 += 55

for i in range(15):
    grass_block = Block(x3, 836 - 55, 'grass')
    block_group.add(grass_block)
    x3 += 55

for i in range(29):
    ground_block = Block(x3, 836 - 55, 'ground')
    block_group.add(ground_block)
    x3 += 55

for i in range(8):
    fire3 = Player('fire', x13 - (55 * 7), 836 - 55, 0, 0, 999999)
    fire_group.add(fire3)
    x13 -= 110

for i in range(2):
    grass_block = Block(x9, 726, 'grass')
    block_group.add(grass_block)
    x9 += 55

for i in range(6):
    ground_block = Block(x9, 726, 'ground')
    block_group.add(ground_block)
    x9 += 55

for i in range(6):
    ground_block = Block(x11 + 110, 671, 'ground')
    block_group.add(ground_block)
    x11 += 55

for i in range(4):
    grass_block = Block(x10, 726 - (55 * 2), 'grass')
    block_group.add(grass_block)
    x10 += 55

for i in range(6):
    ground_block = Block(x11 - (55 * 4), 671 - 55, 'ground')
    block_group.add(ground_block)
    x11 += 55

for i in range(6):
    grass_block = Block(x11 - (55 * 10), 671 - (55 * 2), 'grass')
    block_group.add(grass_block)
    x11 += 55

for i in range(4):
    grass_block = Block(x11 - (55 * 8), 671 - (55 * 3), 'grass')
    block_group.add(grass_block)
    x11 += 55

for i in range(4):
    grass_block = Block(x11 - (55 * 6), 671 - (55 * 4), 'grass')
    block_group.add(grass_block)
    x11 += 55

for i in range(6):
    ground_block = Block(x11 - (55 * 3), 726, 'ground')
    block_group.add(ground_block)
    x11 += 55

for i in range(6):
    ground_block = Block(x12, 726 - 55, 'ground')
    block_group.add(ground_block)
    x12 += 55

for i in range(6):
    ground_block = Block(x12 - (55 * 6), 726 - (55 * 2), 'ground')
    block_group.add(ground_block)
    x12 += 55

for i in range(6):
    ground_block = Block(x12 - (55 * 12), 726 - (55 * 3), 'ground')
    block_group.add(ground_block)
    x12 += 55

for i in range(6):
    grass_block = Block(x12 - (55 * 18), 726 - (55 * 4), 'grass')
    block_group.add(grass_block)
    x12 += 55

fire2 = Player('fire', x12 - (55 * 19), 726 - (55 * 4), 0, 0, 999999)
fire_group.add(fire2)

for i in range(7):
    grass_block = Block(x12 - (55 * 16), 726 - (55 * 6), 'grass')
    block_group.add(grass_block)
    x12 += 55

rat = Player('rat', x12 - (55 * 20), 726 - (55 * 6), 5, 0, 1)
rat_group.add(rat)

for i in range(30):
    grass_block = Block(x12 - (55 * 14), 726 - (55 * 4), 'grass')
    block_group.add(grass_block)
    x12 += 55

for i in range(30):
    ground_block = Block(x12 - (55 * 44), 726 - (55 * 3), 'ground')
    block_group.add(ground_block)
    x12 += 55

for i in range(30):
    ground_block = Block(x12 - (55 * 74), 726 - (55 * 2), 'ground')
    block_group.add(ground_block)
    x12 += 55

for i in range(30):
    ground_block = Block(x12 - (55 * 104), 726 - 55, 'ground')
    block_group.add(ground_block)
    x12 += 55

for i in range(30):
    ground_block = Block(x12 - (55 * 134), 726, 'ground')
    block_group.add(ground_block)
    x12 += 55

for i in range(30):
    ground_block = Block(x12 - (55 * 164), 726 + 55, 'ground')
    block_group.add(ground_block)
    x12 += 55


angel = Player('angel', 700, 700, 7, 0, 3)
fire1 = Player('fire', 1785 + (55 * 4), 671 - (55 * 2), 0, 0, 999999)
fire_group.add(fire1)

run = True

while run:

    clock.tick(FPS)

    draw_bg()

    draw_text(f'Health: {angel.health}', font, (0, 60, 154), 40, 35)
    draw_text(f'Rocks: {angel.ammo}', font, (0, 60, 154), 40, 70)

    angel.update()
    angel.draw()

    for rat in rat_group:
        rat.ai()
        rat.update()
        rat.draw()
        if angel.disable <= 0:
            if pygame.sprite.spritecollide(angel, rat_group, False):
                if angel.alive and rat.alive:
                    angel.health -= damage
                    angel.lose_health = False
                    angel.disable = 90
        else:
            angel.disable -= 1

    for fire in fire_group:
        fire.ai()
        fire.update()
        fire.draw()
        if angel.disable <= 0:
            if pygame.sprite.spritecollide(angel, fire_group, False):
                if angel.alive:
                    angel.health -= damage
                    angel.lose_health = False
                    angel.disable = 90
        else:
            angel.disable -= 1

    rock_group.update()
    rock_group.draw(virtual_surface)
    item_group.update()
    item_group.draw(virtual_surface)
    block_group.update()
    block_group.draw(virtual_surface)

    if rat.alive:

        if shoot:
            rat.shoot()

    if angel.alive:

        if shoot:
            angel.shoot()
        screen_scroll = angel.move(moving_left, moving_right)

    for element in rock_group:
        element.rect.x += screen_scroll
    for element in item_group:
        element.rect.x += screen_scroll
    for element in block_group:
        element.rect.x += screen_scroll
    for element in fire_group:
        element.rect.x += screen_scroll
    for element in rat_group:
        element.rect.x += screen_scroll

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
