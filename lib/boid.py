import pygame
import numpy as np
from random import randint
from lib.utils import update_boid


class Boid(pygame.sprite.Sprite):
    """
    This code is inspired from Boids simulation - github.com/Nikorasu/PyNBoids
    """
    def __init__(self, id, data, screen, isFish=False, cHSV=None):
        super().__init__()
        self.data = data
        self.id = id
        self.screen = screen
        self.image = pygame.Surface((15, 15)).convert()
        self.image.set_colorkey(0)
        self.color = pygame.Color(0)  # preps color so we can use hsva
        self.color.hsva = (randint(0,360), 90, 90) if cHSV is None else cHSV # randint(5,55) #4goldfish
        if isFish:  # (randint(120,300) + 180) % 360  #4noblues
            pygame.draw.polygon(self.image, self.color, ((7,0),(12,5),(3,14),(11,14),(2,5),(7,0)), width=3)
            self.image = pygame.transform.scale(self.image, (16, 24))
        else: 
            pygame.draw.polygon(self.image, self.color, ((7,0), (13,14), (7,11), (1,14), (7,0)))
        self.bSize = 22 if isFish else 17

        self.orig_image = pygame.transform.rotate(self.image.copy(), -90)
        maxW, maxH = self.screen.get_size()
        self.rect = self.image.get_rect(center=(randint(50, maxW - 50), randint(50, maxH - 50)))
        self.pos = np.array((self.rect.center), dtype=np.float64)

        self.data.set_pos(self.id, self.pos)  # sets up forward direction
        self.data.set_ang(self.id, randint(0, 360))  # random start angle, & position ^
    
    def update(self):
        self.image = pygame.transform.rotate(self.orig_image, -self.data.get_ang(self.id))
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        # Actually update position of boid
        self.rect.center = self.data.get_pos(self.id)


class BoidArray():  # Holds array to store positions and angles
    def __init__(self, size, bSize, wrap, maxW, maxH, margin):
        self.array = np.zeros((size, 4), dtype=np.float64)
        self.bSize = bSize
        self.wrap = wrap
        self.maxW = maxW
        self.maxH = maxH
        self.margin = margin

    def update(self, dt, speed):
        x, y = pygame.mouse.get_pos()
        mouse_pos = np.array( [(x, y, 0.0, 0.0)], dtype=np.float64)
        mouse_pressed = pygame.mouse.get_pressed()[0]
        update_boid(self.array, self.bSize*10, self.bSize, self.bSize*5, self.wrap, self.maxW, self.maxH, self.margin, dt, speed, mouse_pos, mouse_pressed)
    
    def set_pos(self, id, pos):
        self.array[id,:2] = np.copy(pos)

    def set_ang(self, id, ang):
        self.array[id,2] = ang

    def get_pos(self, id):
        return self.array[id,:2]
        
    def get_ang(self, id):
        return self.array[id,2]
        
class BoidSim():
    def __init__(self, size, screen, isFish=False, wrap=False):
        maxW, maxH = screen.get_size()
        self.dataArray = BoidArray(size, 22, wrap, maxW, maxH, 42)
        self.nBoids = pygame.sprite.Group()
        self.screen = screen
        for id in range(size):
            self.nBoids.add(Boid(id, self.dataArray, screen))  # spawns desired # of boidz

    def update(self, dt, speed):
        self.dataArray.update(dt, speed)
        self.nBoids.update()
        self.nBoids.draw(self.screen)