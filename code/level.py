import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import  *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import Magic
from upgrade import Upgrade


class Level:
    def __init__(self):
        self.game_paused = False
        self.player = None
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.create_map()
        self.ui = UI()
        self.upgrade = Upgrade(self.player)
        self.animation_player = AnimationPlayer()
        self.magic = Magic(self.animation_player)


    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
       if style == "heal":
           self.magic.heal(self.player, strength, cost, [self.visible_sprites])
       elif style == "flame":
           self.magic.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
            self.current_attack = None

    #runs once
    def create_map(self):
        layouts = {
            "boundary": import_csv_layout("../map/map_FloorBlocks.csv"),
            "grass": import_csv_layout("../map/map_Grass.csv"),
            "object": import_csv_layout("../map/map_Objects.csv"),
            "entities": import_csv_layout("../map/map_Entities.csv")
        }
        graphics = {
            "grass": import_folder("../graphics/grass"),
            "objects": import_folder("../graphics/objects")
        }

        i = 0
        for style,layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE
                        if style == "boundary":
                            Tile((x,y), [self.obstacle_sprites], "invisible")
                        if style == "grass":
                            random_grass = choice(graphics["grass"])
                            Tile(
                                (x,y),
                                [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
                                "grass",
                                random_grass
                            )
                        if style == "object":
                            object_surface = graphics["objects"][int(col)]
                            Tile(
                                (x, y),
                                [self.visible_sprites, self.obstacle_sprites],
                                "object",
                                object_surface
                            )
                        if style == "entities":
                            if col == "394":
                                self.player = Player(
                                    i,
                                    (x,y),
                                    [self.visible_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic
                                )
                            else:
                                if col == "390": monster_name = "bamboo"
                                elif col == "391": monster_name = "spirit"
                                elif col == "392": monster_name = "raccoon"
                                else: monster_name = "squid"
                                Enemy(
                                    i,
                                    monster_name,
                                    (x,y),
                                    [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites],
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_exp
                                )
                            i+=1

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.current_health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, self.visible_sprites)

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target in collision_sprites:
                        if target.sprite_type == "grass":
                            pos = target.rect.center
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3,5)):
                                self.animation_player.grass_particles(pos - offset, [self.visible_sprites])
                            target.kill()
                        else:
                            target.get_damage(self.player, attack_sprite.sprite_type)

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

    def add_exp(self, amount):
        self.player.exp += amount

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)
        if self.game_paused:
            self.upgrade.display()
        else:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()



class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2(0, 0)
        self.floor_surface = pygame.image.load("../graphics/tilemap/ground.png").convert()
        self.floor_rect = self.floor_surface.get_rect(topleft = (0,0))

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
        offset = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, offset)
        for sprite in sorted(self.sprites(), key = lambda sprite_y: sprite_y.rect.centery):
            offset = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset)

    def enemy_update(self, player):
        enemy_sprites = [
            sprite for sprite in self.sprites() if hasattr(sprite, "sprite_type") and sprite.sprite_type == "enemy"
        ]
        for enemy in enemy_sprites:
            enemy.enemy_update(player)


