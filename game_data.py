import pygame, os, re
from pygame.local import *

class resource_handler(object):

    def get_data_from_folder(self, data_dir, extension, iterfunc):
        data = []
        for file in os.listdir(data_dir):
            if extension in file:
                data.append({ 'name': file, 
                    'data': iterfunc(os.path.join(data_direction, file))})
        return data

    def __init__(self, data_dir, extension, iterfunc):
        self.__data = self.get_data_from_folder(data_dir, extension, iterfunc);

    def get_data(self, name):
         for data in self.__data:
            if re.compile(name).match(data['name']):
                return data['data']

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


def get_image(self, file):
    image = pygame.image.load(file)
    image.convert()
    return image

def image_data(data_dir):
    return resource_handler(data_dir, '.png', get_image)

def sound_data(data_dir):
    return resource_handler(data_direction, '.ogg', pygame.mixer.load)

def font_data(data_dir):
    return resource_handler(data_dir,'.fft', pygame.freetype.Font)

class game_data(object):

    def __init__(self, data_dir):
        self.sprites = image_data(os.path.join(data_dir, "sprites"))
        self.backgrounds = image_data(os.path.join(data_dir, "backgrounds"))
        self.sounds = sound_data(os.path.join(data_dir, "sounds"))


