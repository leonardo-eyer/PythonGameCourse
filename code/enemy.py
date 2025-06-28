import pygame
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, death_particles):
        super().__init__(groups)
        self.sprite_type = "enemy"
        self.animations = {
            "idle": [],
            "move": [],
            "attack": []
        }
        self.import_graphics(monster_name)
        self.status = "idle"
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0,-10)
        self.obstacle_sprites = obstacle_sprites
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info["health"]
        self.exp = monster_info["exp"]
        self.speed = monster_info["speed"]
        self.damage = monster_info["damage"]
        self.resistance = monster_info["resistance"]
        self.attack_radius = monster_info["attack_radius"]
        self.notice_radius = monster_info["notice_radius"]
        self.attack_type = monster_info["attack_type"]
        self.can_attack = True
        self.attack_cooldown = 400
        self.attack_time = None
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_time = 350
        self.damage_player = damage_player
        self.death_particles = death_particles

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.direction = self.get_player_position(player)[1]
            if attack_type == "weapon":
                self.health -= player.get_full_damage()
            else:
                pass #magic

            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def hit_reaction(self):
        if not self.vulnerable:
            #knockback
            self.direction *= -self.resistance

    def check_death(self):
        if self.health <= 0:
            self.death_particles(self.rect.center, self.monster_name)
            self.kill()

    def import_graphics(self, name):
        folder_path = f"../graphics/monsters/{name}/"
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(folder_path + animation)

    def get_player_position(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance_squared = (player_vec - enemy_vec).magnitude_squared()
        if distance_squared > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2(0, 0)

        return distance_squared, direction

    def get_status(self, player):
        distance_squared = self.get_player_position(player)[0]

        if distance_squared < (self.attack_radius * self.attack_radius) and self.can_attack:
            if self.status != "attack":
                self.frame_index = 0
            self.status = "attack"
        elif distance_squared <= (self.notice_radius * self.notice_radius):
            self.status = "move"
        else:
            self.status = "idle"

    def actions(self, player):
        if self.status == "attack":
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.damage, self.attack_type)
        elif self.status == "move":
            self.direction = self.get_player_position(player)[1]
        else:
            self.direction = pygame.math.Vector2((0,0))

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == "attack":
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        alpha = 255
        if not self.vulnerable:
            alpha = self.wave_value()

        self.image.set_alpha(alpha)


    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_time:
                self.vulnerable = True


    def update(self):
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldown()
        self.check_death()

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
