import pygame
from pygame.locals import *
from pygame.math import *
import numpy as np
import sys

# The init() function in pygame initializes the pygame engine
pygame.init()
# Creates a window
WIN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
#WIN = pygame.display.set_mode((400,400))
WIN.fill(pygame.Color(255, 0, 0))
pygame.display.set_caption("Survival")
clock = pygame.time.Clock()
TICKS_PER_SECOND = 60

out_of_screen_distance = Vector2(WIN.get_width(), WIN.get_height())
def is_off_screen(pos, tollerance):
    x, y = pos
    return x < -tollerance or x > WIN.get_width()+tollerance or y < -tollerance or y > WIN.get_height()+tollerance

def blitRotate(surf, original_image, origin, pivot, angle, scale):
    """ Rotate image around an origin point, to a given angle, and scale it. """
    image_rect = original_image.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = (pygame.math.Vector2(origin) - image_rect.center) * scale
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotozoom_image = pygame.transform.rotozoom(original_image, angle, scale)
    rect = rotozoom_image.get_rect(center = rotated_image_center)

    surf.blit(rotozoom_image, rect)
    """pygame.draw.rect(surf, (255, 0, 0), rect, 2)"""

class Mob(pygame.sprite.Sprite):
    def __init__(self,pos,speed,size,image=None):
        super().__init__()
        if image:
            self.image = pygame.image.load(image)
        else:
            self.image = pygame.Surface(size)
            self.image.fill((0,255,0))
        
        self.rect = self.image.get_rect(center = pos)
        self.speed = speed
        self.size = size
        self.direction = Vector2()
    
    def update(self):
        self.rect.move_ip(self.direction*self.speed)


class Bullet(Mob):
    def __init__(self,pos,speed,size,trajectory):
        super().__init__(pos,speed,size)
        self.start_pos = pos
        self.direction = np.radians(trajectory.as_polar()[1])
        self.moved_distance = 0

    def update(self):
        self.moved_distance += self.speed
        self.rect.center = self.rotate_bullet(self.moved_distance, self.trajectory(self.moved_distance))
        if is_off_screen(self.rect.center, 100):
            self.kill()

    def trajectory(self, x):
        #return 0.0001*x**2
        #return 60*np.sin(0.01*x)
        return 0
    
    def rotate_bullet(self, x, y):
        # Not Optimal for looping or 90 degree trajectories since it updates in steps in x-direction, and y-direction can change a lot in a tiny x-step
        #rotation matrix formula
        #x′=xcosθ−ysinθ
        #y′=xsinθ+ycosθ
        x_rot = x*np.cos(self.direction) - y*np.sin(self.direction) + self.start_pos.x
        y_rot = x*np.sin(self.direction) + y*np.cos(self.direction) + self.start_pos.y
        return x_rot, y_rot

class Gun:
    def __init__(self, firerate, magazine_size, total_bullets, size, image):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.firerate = firerate
        self.magazine_size = magazine_size
        self.total_bullets = total_bullets
        self.size = size
        self.shot_delay = 500 #ms
        self.laser_aim = True
        self.upgraded = True
        self.aim_direction = Vector2()
        self.pos_muzzle = Vector2(19,10)
        self.angle_aimline = None


        # Relative distances 
        self.player_grip = Vector2(4,6)
        self.pivot = Vector2(4,14)
        self.muzzle = Vector2(19,10)

        self.switched_hand = False
    
    def shoot(self):
        b = Bullet(self.pos_muzzle,10,Vector2(5,5),self.aim_direction)
        bullet_group.add(b)
    
    def draw(self):
        mouse_pos = Vector2(pygame.mouse.get_pos())
        if not mouse_pos:
            return

        # Check if to switch gun from right hand to left, and left to right
        if not self.switched_hand and mouse_pos[0] < p.rect.left:
            self.player_grip.x *= -1
            self.pivot.y       = self.rect.height - self.pivot.y
            self.image = pygame.transform.flip(self.image, flip_x=False, flip_y=True)
            self.switched_hand = True
            p.image = pygame.transform.flip(p.image, flip_x=True, flip_y=False)
        elif self.switched_hand and mouse_pos[0] > p.rect.right:
            self.player_grip.x *= -1
            self.pivot.y       = self.rect.height - self.pivot.y
            self.image = pygame.transform.flip(self.image, flip_x=False, flip_y=True)
            self.switched_hand = False
            p.image = pygame.transform.flip(p.image, flip_x=True, flip_y=False)

        pivot2muzzle = self.muzzle-self.pivot
        pivot2cursor = mouse_pos-self.player_grip-p.rect.center
        if pivot2cursor.length() > pivot2muzzle.length() and not p.rect.collidepoint(mouse_pos):
            len_pivot2cursor, ang_pivot2cursor = pivot2cursor.as_polar()
            angle = np.arcsin(pivot2muzzle.y/len_pivot2cursor)
            self.angle_aimline = np.deg2rad(ang_pivot2cursor) - angle
            len_cursor2muzzle = pivot2muzzle.x-pivot2muzzle.y/np.arctan(angle)
            cursor2muzzle = Vector2(len_cursor2muzzle*np.cos(self.angle_aimline), len_cursor2muzzle*np.sin(self.angle_aimline))
            self.pos_muzzle = mouse_pos+round(cursor2muzzle, 0)
            if (mouse_pos-self.pos_muzzle).length() > 0:
                self.aim_direction = (mouse_pos-self.pos_muzzle).normalize()

        # Aim line
        if self.laser_aim:
            pygame.draw.line(WIN, (200,200,200), self.pos_muzzle, self.pos_muzzle+self.aim_direction*2000) # 2000 is just so it goes out of fullscreen

        # Gun render
        blitRotate(WIN, self.image, p.rect.center+self.player_grip, self.pivot, -np.degrees(self.angle_aimline), 1)

        # Red color dot at pivot and muzzle point on gun
        #pygame.draw.circle(WIN, (255,0,0), p.rect.center+self.player_grip, 1)
        #pygame.draw.circle(WIN, (255,0,0), self.pos_muzzle, 1)

        """
        # Code for use of controllers
        self.aim_direction = joystick direction #(pygame.mouse.get_pos() - Vector2(p.rect.center) - self.player_grip).normalize()
        angle_aimline = np.deg2rad(self.aim_direction.as_polar()[1])
        self.pos_muzzle = p.rect.center + self.player_grip + round(pivot2muzzle.length() * Vector2(np.cos(angle_aimline+np.arctan(pivot2muzzle.y/pivot2muzzle.x)), np.sin(angle_aimline+np.arctan(pivot2muzzle.y/pivot2muzzle.x))), 0)
        """

    def reload(self):
        pass


class Player(Mob):
    def __init__(self,pos,speed,size, gun, image=None):
        super().__init__(pos,speed,size, image)
        self.bullets = []
        self.gun = gun
        self.current_time = 0
        self.last_shot_time = 0

    def update(self):
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
            self.rect.center += move_vec.normalize() * self.speed     
        
        self.current_time = pygame.time.get_ticks()
        if pygame.mouse.get_pressed()[0] and self.gun.upgraded and self.current_time - self.last_shot_time > self.gun.shot_delay:
            g.shoot()
            self.last_shot_time = self.current_time

g = Gun(200, None, None, Vector2(5,5), "basic_gun.png")
p = Player(Vector2(200,200), 5, Vector2(30,30), g, "fat_geck.png")

player_group = pygame.sprite.GroupSingle(p)
bullet_group = pygame.sprite.Group()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    WIN.fill((50,50,50))
    bullet_group.update()
    player_group.update()
    bullet_group.draw(WIN)
    player_group.draw(WIN)
    g.draw()
    clock.tick(TICKS_PER_SECOND)
    pygame.display.update()

