import pygame
from settings import *
from support import *
from entity import Entity

class Player(Entity):
    def __init__(self, id, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(id, "Player", groups)
        self.image  = pygame.image.load("../graphics/test/player.png").convert_alpha()
        self.rect   = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET["player"])
        self.obstacle_sprites = obstacle_sprites
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200
        self.weapon_keys = list(weapon_data.keys())
        self.weapon = self.weapon_keys[self.weapon_index]
        self.magic_index = 0
        self.magic_keys = list(magic_data.keys())
        self.magic_values = list(magic_data.values())
        self.magic = self.magic_keys[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None
        self.create_magic = create_magic
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.status = "down"
        self.animations = {
            "up": [],
            "down": [],
            "left": [],
            "right": [],
            "right_idle": [],
            "left_idle": [],
            "up_idle": [],
            "down_idle": [],
            "right_attack": [],
            "left_attack": [],
            "up_attack": [],
            "down_attack": []
        }
        self.import_player_assets()
        self.stats = {
            "health": 100,
            "energy": 60,
            "attack":10,
            "magic":4,
            "speed":6
        }
        self.max_stats = {
            "health": 300,
            "energy": 140,
            "attack": 20,
            "magic": 10,
            "speed": 10
        }
        self.upgrade_cost = {
            "health": 100,
            "energy": 100,
            "attack": 100,
            "magic": 100,
            "speed": 100
        }
        self.current_health = self.stats["health"]
        self.current_energy = self.stats["energy"]
        self.exp = 500
        self.current_speed = self.stats["speed"]
        self.hurt_time = None
        self.vulnerable = True
        self.invincibility_time = 500

    def get_full_damage(self, attack_type):
        damage = 0
        if attack_type == "weapon":
            damage =  self.stats["attack"] + weapon_data[self.weapon]["damage"]
        elif attack_type == "magic":
            damage =  self.stats["magic"] + magic_data[self.magic]["strength"]

        return damage

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        alpha = 255
        if not self.vulnerable:
            alpha = self.wave_value()

        self.image.set_alpha(alpha)

    def get_value_by_idx(self, index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        return list(self.upgrade_cost.values())[index]

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0 and "idle" not in self.status:
            if "attack" in self.status:
                self.status = self.status.replace("_attack", "_idle")
            else:
                self.status = self.status + "_idle"

        if self.attacking:
            if "attack" not in self.status:
                self.direction.x = 0
                self.direction.y = 0
                if "idle" in self.status:
                    self.status = self.status.replace("_idle", "_attack")
                else:
                    self.status += "_attack"
        else:
            if "attack" in self.status:
                self.status = self.status.replace("_attack", '')

    def energy_regen(self):
        if self.current_energy < self.stats["energy"]:
            self.current_energy += 0.01 * self.stats["magic"]
        else:
            self.current_energy = self.stats["energy"]


    def import_player_assets(self):
        folder_path = "../graphics/player/"
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(folder_path + animation)

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = "up"
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = "down"
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = "right"
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = "left"
            else:
                self.direction.x = 0

            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = self.magic_keys[self.magic_index]
                strength = self.magic_values[self.magic_index]["strength"] + self.stats["magic"]
                cost = self.magic_values[self.magic_index]["cost"]
                self.create_magic(style, strength, cost)

            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                if self.weapon_index < len(self.weapon_keys) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0

                self.weapon = list(weapon_data.keys())[self.weapon_index]

            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()
                if self.magic_index < len(self.magic_keys) - 1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0

                self.magic = self.magic_keys[self.magic_index]

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking and (current_time - self.attack_time) >= self.attack_cooldown + weapon_data[self.weapon]["cooldown"]:
            self.attacking = False
            self.destroy_attack()

        if not self.can_switch_weapon and (current_time - self.weapon_switch_time) >= self.switch_duration_cooldown:
            self.can_switch_weapon = True

        if not self.can_switch_magic and (current_time - self.magic_switch_time) >= self.switch_duration_cooldown:
            self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invincibility_time:
                self.vulnerable = True

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats["speed"])
        self.energy_regen()