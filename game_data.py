import pygame, os, re, pygame.freetype
from pygame.locals import *

pygame.init()

class resource_handler(object):

    def get_data_from_folder(self, data_dir, extension, iterfunc):
        data = []
        for file in os.listdir(data_dir):
            if extension in file:
                data.append({ 'name': file, 
                    'data': iterfunc(os.path.join(data_dir, file))})
        return data

    def __init__(self, data_dir, extension, iterfunc):
        self.__data = self.get_data_from_folder(data_dir, extension, iterfunc);

    def get_data(self, name):
        for data in self.__data:
            if re.match(name, data['name']):
                return data['data']
        raise KeyError

    def get_data_dict(self, names):
        data = {} 
        for name in names:
            data[name] = self.get_data(name)
        return data 
    
    def get_data_dict(self, names):
        data = [] 
        for name in names:
            data.append(self.get_data(name))
        return data 

    def get_name(self, data):
        for data in self.__data:
            if data['data'] == data:
                return data['name']


def get_image(file):
    image = pygame.image.load(file)
    image.convert()
    return image

def image_data(data_dir):
    return resource_handler(data_dir, '.png', get_image)

def sound_data(data_dir):
    return resource_handler(data_dir, '.ogg', pygame.mixer.Sound)

def font_data(data_dir):
    return resource_handler(data_dir,'.ttf', pygame.freetype.Font)

class game_data(object):

    def __init__(self, data_dir):
        self.sprites = image_data(os.path.join(data_dir, "sprites"))
        self.backgrounds = image_data(os.path.join(data_dir, "backgrounds"))
        self.sounds = sound_data(os.path.join(data_dir, "sounds"))


