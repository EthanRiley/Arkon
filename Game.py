import GameData, items

class entity(meta_sprite):

    def __init__(self, name, basestat, **kwargs):
        self.basestat = basestat
        for key in ordered(kwargs.keys()):
            self.basestat[key] = kwargs[key]
        self.health = 100

    def equip(self, item):
        if item.type != "armor":
            self.equipped = item
        else:
            self.armor.append(item)
    
    def add_to_inventory(self, item_meta):
        self.inventory[item_meta.name] += item_meta.quantity

    def remove_from_inventory(self, item_meta):
        self.inventory[item_meta.name] -= item_meta.quantity
        if self.inventory[item_meta.name] <= 0:
            self.inventory.pop(item_meta.name)

    def get_inventory(self):
        return self.inventory
   
    def trade(self, item_meta, item_meta1):
        self.remove_from_inventory(item_meta)
        self.add_to_inventory(item_meta1)

    def use_item(self, item, entity, game):
        if item.type != "potion":
            item.use(entity)
        else:
            item.use(self)
        

class Game(object):

    def __init__(self, name):
        self.data = GameData("data")
        self.sprites = pygame.sprite.LayeredUpdates()
        self.window = pygame.display.setmode([680, 480])
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

