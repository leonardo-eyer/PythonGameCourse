import pygame
from support import import_folder
from random import choice

class AnimationPlayer:
    def __init__(self):
        self.frames = {
            "flame": import_folder("../graphics/particles/flame/frames"),
            "aura": import_folder("../graphics/particles/aura"),
            "heal": import_folder("../graphics/particles/heal/frames"),
            "claw": import_folder("../graphics/particles/claw"),
            "slash": import_folder("../graphics/particles/slash"),
            "sparkle": import_folder("../graphics/particles/sparkle"),
            "leaf_attack": import_folder("../graphics/particles/leaf_attack"),
            "thunder": import_folder("../graphics/particles/thunder"),
            "squid": import_folder("../graphics/particles/smoke_orange"),
            "raccoon": import_folder("../graphics/particles/raccoon"),
            "spirit": import_folder("../graphics/particles/nova"),
            "bamboo": import_folder("../graphics/particles/bamboo"),
            "leaf":(
                import_folder("../graphics/particles/leaf1"),
                import_folder("../graphics/particles/leaf2"),
                import_folder("../graphics/particles/leaf3"),
                import_folder("../graphics/particles/leaf4"),
                import_folder("../graphics/particles/leaf5"),
                import_folder("../graphics/particles/leaf6"),
                self.reflect_images(import_folder("../graphics/particles/leaf1")),
                self.reflect_images(import_folder("../graphics/particles/leaf2")),
                self.reflect_images(import_folder("../graphics/particles/leaf3")),
                self.reflect_images(import_folder("../graphics/particles/leaf4")),
                self.reflect_images(import_folder("../graphics/particles/leaf5")),
                self.reflect_images(import_folder("../graphics/particles/leaf6"))
            )
        }


    def reflect_images(self, frames):
        new_frames = []
        for frame in frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            new_frames.append(flipped_frame)

        return new_frames

    def grass_particles(self, pos, groups):
        animation_frames = choice(self.frames["leaf"])
        Particle(pos, animation_frames, groups)

    def create_particles(self, animation_type, pos, groups):
        animation_frames = self.frames[animation_type]
        Particle(pos, animation_frames, groups)

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, animation_frames, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.sprite_type = "magic"


    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()
