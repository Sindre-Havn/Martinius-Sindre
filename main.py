import pygame
from pygame.locals import *
from pygame.math import *
import numpy as np
import sys

# The init() function in pygame initializes the pygame engine
pygame.init()
# Creates a window
WIN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
#WIN = pygame.display.set_mode((400,400)) #
WIN.fill(pygame.Color(255, 0, 0))
pygame.display.set_caption("Survival")
clock = pygame.time.Clock()
TICKS_PER_SECOND = 4

out_of_screen_distance = Vector2(WIN.get_width(), WIN.get_height())
def is_off_screen(pos):
    x, y = pos
    return x < 0 or x > WIN.width or y < 0 or y > WIN.height

def blitRotate(surf, original_image, origin, pivot, angle, scale):

    image_rect = original_image.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = (pygame.math.Vector2(origin) - image_rect.center) * scale
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotozoom_image = pygame.transform.rotozoom(original_image, angle, scale)
    rect = rotozoom_image.get_rect(center = rotated_image_center)

    surf.blit(rotozoom_image, rect)
    """pygame.draw.rect(surf, (255, 0, 0), rect, 2)"""

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
    def __init__(self, firerate, magazine_size, total_bullets, size, image, pos_on_player, rotation_point):
        self.image = pygame.image.load(image)
        self.box = self.image.get_rect()
        self.firerate = firerate
        self.magazine_size = magazine_size
        self.total_bullets = total_bullets
        self.size = size
        self.upgraded = True
        self.shot_delay = 500 #ms

        self.pos_on_player = pos_on_player
        self.rotation_point = rotation_point
        self.pos_barrel = Vector2(33,-2)
        self.laser_aim = True
    
    def shoot(self):
        b = Bullet(Vector2(p.pos),10,Vector2(5,5),p.aim_direction)
        p.bullets.append(b)
    
    def draw(self):
        mouse_pos = Vector2(pygame.mouse.get_pos())
        rotation_point_to_barrel = Vector2(- self.pos_on_player.x, self.pos_barrel.y-self.pos_on_player.y)
        rotation_point_to_target = mouse_pos-p.pos+rotation_point_to_barrel
        len_rot_to_target, ang_rot_to_target = rotation_point_to_target.as_polar()
        angle = np.arcsin(rotation_point_to_barrel.y/len_rot_to_target)

        angle_of_aimline = np.deg2rad(ang_rot_to_target)-angle
        length = len_rot_to_target - np.tan(angle)*rotation_point_to_barrel.y + rotation_point_to_barrel.x
        target_to_middle = Vector2(length*np.cos(angle_of_aimline), length*np.sin(angle_of_aimline))

        end_barrel = p.pos+self.pos_on_player+rotation_point_to_target-target_to_middle
        direction = (mouse_pos-end_barrel).normalize()
        
        # Aim line
        pygame.draw.line(WIN, (200,200,200), end_barrel, end_barrel+direction*2000) # 2000 is just so it goes out of fullscreen
        # Gun render
        blitRotate(WIN, self.image, p.pos+self.pos_on_player, self.rotation_point, -np.degrees(angle_of_aimline), 1)

        """
        # End of gun, to mouse:
        pygame.draw.line(WIN, (200,200,200), end_barrel, mouse_pos)
        # Debugging point on player
        pygame.draw.circle(WIN, (255,0,0), p.pos+self.pos_on_player+rotation_point_to_target-target_to_middle, 1)
        pygame.draw.circle(WIN, (0,0,255), p.pos+self.pos_on_player+Vector2(-rotation_point_to_barrel.x, rotation_point_to_barrel.y), 1)
        pygame.draw.line(WIN, (200,200,200), p.pos+self.pos_on_player, p.pos+self.pos_on_player+Vector2(-rotation_point_to_barrel.x, rotation_point_to_barrel.y))

        # Gun points
        pygame.draw.circle(WIN, (255,0,0), p.pos+self.pos_barrel, 1)
        pygame.draw.circle(WIN, (255,0,0), p.pos+self.pos_on_player, 1)
        pygame.draw.circle(WIN, (255,0,0), mouse_pos-target_to_middle, 1)

        # Debugging vectors
        pygame.draw.line(WIN, (200,200,200), Vector2(50,350), Vector2(50-rotation_point_to_barrel.x,350+rotation_point_to_barrel.y))
        pygame.draw.line(WIN, (200,200,200), Vector2(50, 350), Vector2(50, 350)+rotation_point_to_target)
        pygame.draw.line(WIN, (200,200,200), Vector2(50, 350)+rotation_point_to_target, Vector2(50, 350)+rotation_point_to_target-target_to_middle)
        pygame.draw.circle(WIN, (255,0,0), Vector2(50, 350), 1)
        pygame.draw.circle(WIN, (255,0,0), Vector2(50, 350)+rotation_point_to_target-target_to_middle, 1)
        pygame.draw.circle(WIN, (0,0,255), Vector2(50, 350)+Vector2(-rotation_point_to_barrel.x, rotation_point_to_barrel.y), 1)
        """

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
        super().draw()
        self.gun.draw()

g = Gun(200, None, None, Vector2(5,5), "basic_gun.png", Vector2(15,2), Vector2(4,14))
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

