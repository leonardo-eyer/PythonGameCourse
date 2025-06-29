from pydoc_data.topics import topics

import pygame
from settings import *

class Upgrade:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attribute_number = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE)
        self.selection_idx = 0
        self.selection_time = None
        self.can_move = True
        self.height = self.display_surface.get_size()[1] * 0.8
        self.width = self.display_surface.get_size()[0] // 6
        self.item_list = []
        self.create_items()

    def input(self):
        keys = pygame.key.get_pressed()
        if self.can_move:
            if keys[pygame.K_RIGHT]:
                if self.selection_idx < self.attribute_number - 1:
                    self.selection_idx += 1
                else:
                    self.selection_idx = 0

                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT]:
                if self.selection_idx > 0:
                    self.selection_idx -= 1
                else:
                    self.selection_idx = self.attribute_number - 1

                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_idx].trigger(self.player)

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time > 300:
                self.can_move = True

    def create_items(self):
        index = 0
        for item in range(self.attribute_number):
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attribute_number
            left = (item * increment) + (increment - self.width) // 2
            top = self.display_surface.get_size()[1] * 0.1
            name = self.attribute_names[index]
            max_value = self.max_values[index]
            item = Item(left, top, self.width, self.height, index, self.font, name, max_value)
            self.item_list.append(item)
            index += 1


    def display(self):
        self.input()
        self.selection_cooldown()
        index = 0
        for item in self.item_list:
            value = self.player.get_value_by_idx(index)
            cost = self.player.get_cost_by_index(index)
            item.display(self.display_surface, self.selection_idx, value, cost)
            index += 1

class Item:
    def __init__(self, left, top, width, height, index, font, name, max_value):
        self.rect = pygame.Rect(left, top, width, height)
        self.index = index
        self.font = font
        self.name = name
        self.max_value = max_value

    def display_names(self, surface, selected, cost):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR
        title_surface = self.font.render(self.name, False, color)
        title_rect = title_surface.get_rect(midtop = self.rect.midtop + pygame.math.Vector2(0, 20))
        cost_surface = self.font.render(f"{int(cost)}", False, color)
        cost_rect = title_surface.get_rect(midbottom=self.rect.midbottom + pygame.math.Vector2(10, -20))
        surface.blit(title_surface, title_rect)
        surface.blit(cost_surface, cost_rect)

    def display(self, surface, selection_number, value, cost):
        selected = self.index == selection_number
        if selected:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, selected, cost)
        self.display_bar(surface, value, self.max_value, selected)


    def display_bar(self, surface, value, max_value, selected):
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom + pygame.math.Vector2(0, -60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR
        full_height = bottom[1] - top[1]
        relative_number = (value / max_value) * full_height
        value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative_number, 30, 10)
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    def trigger(self, player):
        upgrade_attribute = list(player.stats.keys())[self.index]
        if (
                player.exp >= player.upgrade_cost[upgrade_attribute]
                and player.stats[upgrade_attribute] < self.max_value
        ):
            player.exp -= player.upgrade_cost[upgrade_attribute]
            if player.stats[upgrade_attribute] * 1.2 > self.max_value:
                player.stats[upgrade_attribute] = self.max_value
            else:
                player.stats[upgrade_attribute] *= 1.2

            player.upgrade_cost[upgrade_attribute] *= 1.4





