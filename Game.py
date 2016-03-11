import GameData

class entity(meta_sprite):
    
    def itemused(self, item):
        if item.type == "weapon":
            if self.takes_damage:
                self.health -= item.attack
        elif item.type == "quest":
            self.questDone(item.questname)
            

class Game(object):

    def __init__(self, name):
        self.data = GameData("data")
        self.sprites = pygame.sprite.LayeredUpdates()
        self.window = pygame.display.setmode([480, 680])
        pygame.display.caption(name)
    
    def set_background(self, name):
        self.window.blit(self.data.backgrounds.get_data(name))
    
    def init_meta_sprite(self, meta_sprite):
        meta_sprite.image = self.data.sprites.get_data(meta_sprite.imagename)
        meta_sprite.rect = sprite.image.get_rect()
        meta_sprite.sounds = self.data.sounds.get_data_array(meta_sprite.sounds)
        
        self.sprites.add(meta_sprite, layer = meta_sprite.layer)
        return meta_sprite
            
    def update(self):
        self.sprites.draw()
        pygame.display.update()
