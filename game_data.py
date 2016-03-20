import pygame, os, re
from collections import namedtuple
from pygame.local import *

class resource_handler(object):

    def get_data_from_folder(self, data_direction, extension, iterfunc):
        data = []
        for file in os.listdirection(data_dir):
            if extension in file:
                data.append({ 'name': file, 
                    'data': iterfunc(os.path.join(data_direction, file))})
        return data

    def __init__(self, data_direction, extension, iterfunc):
        self.__data = self.get_data_from_folder(data_direction, extension, iterfunc);

    def get_data(self, name):
         for data in self.__data:
            if re.compile(name).match(data['name']):
                return data['data']

    def get_data_array(self, names):
        data = [];
        for name in names:
            data.append(self.get_data(name))
        return data 

    def get_name(self, data):
        for data in self.__data:
            if data['data'] == data:
                return data['name']


def get_image(self, file):
    image = pygame.image.load(file)
    image.convert()
    return image

def image_data(data_direction):
    return resource_handler(data_direction, '.png', get_image)

def sound_data(data_direction):
    return resource_handler(data_direction, '.ogg', pygame.mixer.load)
    
def boundboxcol(rect, rect1):
    if rect1.left <= rect.right & rect1.top >= rect.bottom:
        if rect1.right >= rect.left & rect1.bottom <= rect.top:
            return True;
    return False;

class game_data(object):

    def __init__(self, data_direction):
        self.sprites = image_data(os.path.join(data_direction, "sprites"))
        self.backgrounds = image_data(os.path.join(data_direction, "backgrounds"))
        self.sounds = sound_data(os.path.join(data_direction, "sounds"))

position = namedtuple("position", ['x', 'y'])

class meta_sprite(pygame.sprite.Sprite):

    def __init__(self, imagename, is_animated, layer, pos, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        
        self._imagename = imagename
        self.animated = is_animated
        self.layer = layer 
        self.__pos = pos
        self.__frame = 0;

        if 'sounds' in sorted(kwargs.keys()):
            self.sounds = kwargs['sounds']
    
    def load_data(self, data):
        self.image = data.sprites.get_data(self._imagename)
        self.rect = self.image.get_rect()

        self.rect.x = self.__pos.x 
        self.rect.y = self.__pos.y
        del self.__pos
        
        if self.animated:
            directions = [
                    "right",
                    "forward"
            ]

            self.animation = {}
            for direction in directions:        
                self.animation[direction] = data.get_data_array(self._imagename 
                        + "_anim_" + direction + "_\d")

        self.sounds = data.sounds.get_data_array(self.sounds)

    def facing(direction):
        self.facing = direction 

    def move(self, dx, dy, sprites):
        rect = self.get_rect()
        for sprite in sprites:
            rect1 = sprite.get_rect()
            if rect1.left <= rect.right + dx & rect1.top >= rect.bottom + dy:
                if rect1.right >= rect.left + dx & rect1.bottom <= rect.top + dy:
                    return False
        self.rect.move(dx, dy)
        self.moving = True
        return True

    def animate_frame(self, direction,  flipped_dir):
        if self.facing == direction | self.facing == flipped_dir:
            self.image.blit(self.animation[direction][self.__frame])
            if self.facing == direction ^ self.flipped:
                pygame.transform.flip(self.image, True, False)
                self.flipped = True
            elif self.flipped:
                pygame.transform.flip(self.image, True, False)
                self.flipped = False
            ++self.__frame%len(self.animation[direction])

    def update(self, *args):
        if self.is_animated & moving:
            self.animate_frame("right", "left")
            self.animate_frame("forward", "backward") 
