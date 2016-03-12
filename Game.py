import GameData
from collections import namedtuple
import json

class item_meta:
    def __init__(self, quantity, name):
        self.quantity = quantity
        self.name = name

buff = namedtuple('buff', ['stat', 'buff'])

class potion(item_meta):
    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, name)
        self.type = "potion"
        self.potion = self.__class__.__name__
        self.potency = potency

    def drink(self, entity):
        for buff in self.buffs:
            entity.basestat[buff.stat] += buff.value * potency
        if entity.player:
            self.potion_effect(entity)
        

class alchol(potion):
    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [ 
            buff("speed", -5),
            buff("attack", 5)
        ]

    def potion_effect(player):
        pygame.transform.rotate(pygame.window, 360);


class mysterious(potion):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("speed", 4000),
            buff("attack", 4000)
        ]

    def potion_effect(player):
        fun = os.path.join("data", "fun") 
        temmie = get_image(os.path.join(fun, "temmie.png"))
        temmie_sound = pygame.mixer.Sound(os.path.join(fun, "temmie.ogg"))
        for sprite in player.game.data.sprites.spites:
            sprite = temmie
        for background in player.game.data.backgrounds:
            background = temmie
        pygame.rotate 

class entity(meta_sprite):

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
        if item.type == "weapon":
            if entity.takes_damage:
                entity.damage(item.attack)
        elif item.type == "potion":
            if item.potion == "speed":
                self.basestat.speed += item.buff
            elif item.potion == "alcohol":
                self.basestat.speed -= item.debuff
                self.basestat.attack += item.buff
                self.setEffect("drunk")
            elif item.potion == "health":
                self.recover(item.buff)
            elif item.potion == "magic":
                self.setEffect("high")
            else:
                if takes_damage:
                    self.damage(item.debuff)
        elif entity.speech:
            entity.dialog(item.name)
        

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
