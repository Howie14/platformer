from pygame import *
import pygame

pygame.init()
info = display.Info()
clock = time.Clock()

HEIGHT = info.current_h
WIDTH = info.current_w
ASPECT_RATIO = WIDTH / HEIGHT
fps = 60

back = (106, 245, 168)

window = display.set_mode((WIDTH, HEIGHT), RESIZABLE)
display.set_caption("Find the Halo")

virtual_surface = Surface((WIDTH, HEIGHT))
virtual_surface.fill(back)
current_size = window.get_size()

game = True

number_rocks = 10000


class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, x, y, width, height, speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_image), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def reset(self):
        virtual_surface.blit(self.image, (self.rect.x, self.rect.y))


class Rock(GameSprite):
    def __init__(self, x, y):
        super().__init__("images/rock.png", x, y, 30, 30, 10)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x <= -HEIGHT // 25:
            self.kill()


class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__("images/angel.png", x, y, 110, 110, 7)

    def update_pos(self):
        global number_rocks
        keys_pressed = key.get_pressed()
        if keys_pressed[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x < WIDTH - HEIGHT // 6 - 5:
            self.rect.x += self.speed
        if keys_pressed[K_e] and number_rocks > 0:
            self.fire()
            number_rocks -= 1

    def fire(self):
        rock = Rock(self.rect.centerx - HEIGHT // 60, angel.rect.top)
        rocks.add(rock)


angel = Player(700, 600)
rocks = sprite.Group()

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                game = False
        if e.type == VIDEORESIZE:
            new_width = e.w
            new_height = int(new_width / ASPECT_RATIO)
            window = display.set_mode((new_width, new_height), RESIZABLE)
            current_size = window.get_size()

    virtual_surface.fill(back)
    angel.reset()
    angel.update_pos()

    rocks.update()
    rocks.draw(virtual_surface)

    scaled_surface = transform.scale(virtual_surface, current_size)
    window.blit(scaled_surface, (0, 0))
    display.update()
    clock.tick(fps)
