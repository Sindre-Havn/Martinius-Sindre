import pygame
from pygame.locals import *
from pygame.math import *
import sys
import copy


# The init() function in pygame initializes the pygame engine
pygame.init()
# Creates a window
WIN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
WIN.fill(pygame.Color(255, 0, 0))
pygame.display.set_caption("Survival")
# Limits FPS. Normally 30-60. If the game is too heavy
# then the FPS may drop below the decided value.
clock = pygame.time.Clock()
FPS = 60

WIN_scroll = [0,0]

out_of_screen_distance = pygame.Vector2(WIN.get_width(), WIN.get_height())
print(out_of_screen_distance)


class Mob:
    def __init__(self,x,y,speed,size):
        self.pos = pygame.Vector2(x,y)
        self.speed = speed
        self.size = size

class Bullet(Mob):
    def __init__(self,x,y,speed,size,move_vec):
        super().__init__(x,y,speed,size)
        self.box = pygame.Rect(self.pos,(size//4, size))
        self.box.center = p.box.center
        self.direction = move_vec
        pygame.transform.rotate(WIN, p.direction.angle_to(pygame.Vector2(1,0)))
        self.box.move_ip(self.direction*p.size*1.5)

    def move(self):
        self.box.move_ip(self.direction*self.speed)

    def draw(self):
        pygame.draw.rect(WIN, (0, 255, 0), self.box)

class Player(Mob):
    def __init__(self,x,y,speed,size):
        super().__init__(x,y,speed,size)
        self.box = pygame.Rect((x,y),(size, size))
        self.direction = (pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2(self.box.center)).normalize()
        self.bullets = []
        #self.image = pygame.image.load("")
        #self.rectangle = self.image.get_rect()
        #self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)
    
    def move(self):
        move_vec = pygame.Vector2(0,0)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w]:
            move_vec.y = -1
        if pressed_keys[K_a]:
            move_vec.x = -1
        if pressed_keys[K_s]:
            move_vec.y = 1
        if pressed_keys[K_d]:
            move_vec.x = 1
        if move_vec.length() != 0:
            self.box.move_ip(move_vec.normalize() * self.speed)
        
        """for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.shoot()"""

        #if pygame.mouse.get_pressed()[0]:
        #    self.shoot()

    def update_and_draw_bullets(self):
        for bullet in self.bullets:
            if pygame.Vector2(self.box.center).distance_to(pygame.Vector2(bullet.box.center)) > out_of_screen_distance.length():
                self.bullets.remove(bullet)
                print('Remove', len(self.bullets))
            bullet.move()
            bullet.draw()

    def draw(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        pos_center = pygame.Vector2(self.box.center)
        self.direction = (mouse_pos - pos_center).normalize()
        longest_screen_dimetion = max(WIN.get_width(), WIN.get_height())
        aim_line_end = pos_center + pygame.Vector2(self.direction[0] * longest_screen_dimetion, self.direction[1] * longest_screen_dimetion)
        pygame.draw.line(WIN, (100,100,100), pos_center, aim_line_end)
        pygame.draw.rect(WIN, (0, 255, 0), self.box)

    def shoot(self):
        print("Shoot", len(self.bullets))
        self.bullets.append(Bullet(self.pos[0],self.pos[1],4,20,self.direction))

p = Player(200, 200, 2, 30)

weapon_upgraded = True
shot_interval = 2000 #ms
last_shot_time = 0
while True:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN or (weapon_upgraded and current_time - last_shot_time > shot_interval):
            p.shoot()
            last_shot_time = current_time

        

    
    p.move()
    WIN.fill((0,0,0))
    p.update_and_draw_bullets()
    p.draw()
    clock.tick(FPS)
    pygame.display.update()



