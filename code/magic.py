import pygame
from settings import *
from random import randint

class Magic:
    def __init__(self, animation):
        self.animation = animation
        self.sounds = {
            "heal": pygame.mixer.Sound("../audio/heal.wav"),
            "flame": pygame.mixer.Sound("../audio/fire.wav")
        }
        self.sounds["heal"].set_volume(0.03)
        self.sounds["flame"].set_volume(0.03)

    def heal(self, player, strength, cost, groups):
        if player.current_energy >= cost:
            self.sounds["heal"].play()
            player.current_health += strength
            player.current_energy -= cost
            if player.current_health >= player.stats["health"]:
                player.current_health = player.stats["health"]

            self.animation.create_particles("aura", player.rect.center, groups)
            self.animation.create_particles("heal", player.rect.center + pygame.math.Vector2((0,-60)), groups)


    def flame(self, player, cost, groups):
        if player.current_energy >= cost:
            self.sounds["flame"].play()
            player.current_energy -= cost
            direction = pygame.math.Vector2((0,1))
            facing = player.status.split('_')[0]
            if facing == "right":
                direction = pygame.math.Vector2((1,0))
            elif facing == "left":
                direction = pygame.math.Vector2((-1, 0))
            elif facing == "up":
                direction = pygame.math.Vector2((0, -1))

            for i in range(1, 6):
                if direction.x:
                    offset = (direction.x * i) * TILE_SIZE
                    x = player.rect.centerx + offset + randint(-TILE_SIZE // 3, TILE_SIZE // 3)
                    y = player.rect.centery + randint(-TILE_SIZE // 3, TILE_SIZE // 3)
                    self.animation.create_particles("flame", (x, y), groups)
                else:
                    offset = (direction.y * i) * TILE_SIZE
                    x = player.rect.centerx + randint(-TILE_SIZE // 3, TILE_SIZE // 3)
                    y = player.rect.centery + offset + randint(-TILE_SIZE // 3, TILE_SIZE // 3)
                    self.animation.create_particles("flame", (x, y), groups)