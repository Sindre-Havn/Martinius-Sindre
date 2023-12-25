import pygame
from pygame.locals import *
from pygame.math import *
import numpy as np
import sys

# The init() function in pygame initializes the pygame engine
pygame.init()
# Creates a window
WIN = pygame.display.set_mode((0,0), pygame.FULLSCREEN) #WIN = pygame.display.set_mode((400,400)) #
WIN.fill(pygame.Color(255, 0, 0))
pygame.display.set_caption("Survival")
clock = pygame.time.Clock()
TICKS_PER_SECOND = 60

out_of_screen_distance = Vector2(WIN.get_width(), WIN.get_height())
def is_off_screen(pos):
    x, y = pos
    return x < 0 or x > WIN.width or y < 0 or y > WIN.height


class Mob:
    def __init__(self,pos,speed,size,image=None):
        if image == None:
            self.box = pygame.Rect(pos, size)
        else:
             self.image = pygame.image.load("")
             self.box = self.image.get_rect()
        self.box.center = pos
        self.pos = self.box.center
        self.speed = speed
        self.size = size
        self.direction = Vector2()
    
    def move(self):
        self.box.move_ip(self.direction*self.speed)

    def draw(self):
        pygame.draw.rect(WIN, (0, 255, 0), self.box)


class Bullet(Mob):
    def __init__(self,pos,speed,size,trajectory):
        super().__init__(pos,speed,size)
        self.start_pos = pos
        self.direction = np.radians(trajectory.as_polar()[1])
        self.moved_distance = 0
        print(self.direction)
    
    def move(self):
        self.moved_distance += self.speed*1
        self.box.center = self.rotate_bullet(self.moved_distance, self.trajectory(self.moved_distance))
        self.pos = self.box.center

    def trajectory(self, x):
        #return 0.0001*x**2
        return 60*np.sin(0.01*x)
    
    def rotate_bullet(self, x, y):
        #rotation matrix formula
        #x′=xcosθ−ysinθ
        #y′=xsinθ+ycosθ
        x_rot = x*np.cos(self.direction) - y*np.sin(self.direction) + self.start_pos.x
        y_rot = x*np.sin(self.direction) + y*np.cos(self.direction) + self.start_pos.y
        return x_rot, y_rot

class Gun:
    def __init__(self, firerate, magazine_size, total_bullets, size, image, pos_on_player):
        self.image = pygame.image.load(image)
        self.box = self.image.get_rect()
        self.firerate = firerate
        self.magazine_size = magazine_size
        self.total_bullets = total_bullets
        self.size = size
        self.upgraded = True
        self.shot_delay = 500 #ms
        self.pos_on_player = pos_on_player
    
    def shoot(self):
        b = Bullet(Vector2(p.pos),10,Vector2(5,5),p.aim_direction)
        p.bullets.append(b)

    def reload(self):
        pass


class Player(Mob):
    def __init__(self,pos,speed,size, gun):
        super().__init__(pos,speed,size)
        self.aim_direction = (Vector2(pygame.mouse.get_pos()) - Vector2(self.box.center)).normalize()
        self.bullets = []
        self.gun = gun
        self.current_time = 0
        self.last_shot_time = 0

    def move(self):
        move_vec = Vector2(0,0)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w]:
            move_vec.y = -1
        if pressed_keys[K_a]:
            move_vec.x = -1
        if pressed_keys[K_s]:
            move_vec.y = 1
        if pressed_keys[K_d]:
            move_vec.x = 1
        if pressed_keys[K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if move_vec.length() != 0:
            self.box.center += move_vec.normalize() * self.speed
            self.pos = self.box.center
            #if self.direction.x < 1:
            #    self.gun.box.right = self.box.left
                
        
        self.current_time = pygame.time.get_ticks()
        if pygame.mouse.get_pressed()[0] and self.gun.upgraded and self.current_time - self.last_shot_time > self.gun.shot_delay:
            g.shoot()
            self.last_shot_time = self.current_time

    def update_and_draw_bullets(self):
        for bullet in self.bullets:
            if Vector2(self.box.center).distance_to(Vector2(bullet.box.center)) > out_of_screen_distance.length():
                self.bullets.remove(bullet)
                print('Remove', len(self.bullets))
            bullet.move()
            bullet.draw()

    def draw(self):
        mouse_pos = Vector2(pygame.mouse.get_pos())
        pos_center = Vector2(self.box.center)
        self.aim_direction = (mouse_pos - pos_center).normalize()
        longest_screen_dimetion = max(WIN.get_width(), WIN.get_height())
        aim_line_end = pos_center + self.aim_direction * longest_screen_dimetion
        pygame.draw.line(WIN, (100,100,100), pos_center, aim_line_end)

        super().draw()
        WIN.blit(pygame.transform.flip(self.gun.image, False, False), self.box.topleft+self.gun.pos_on_player)

g = Gun(200, None, None, Vector2(5,5), "basic_gun.png", Vector2(27,5))
p = Player(Vector2(200,200), 5, Vector2(30,30), g)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    WIN.fill((50,50,50))
    p.move()
    p.draw()
    p.update_and_draw_bullets()
    clock.tick(TICKS_PER_SECOND)
    pygame.display.update()

