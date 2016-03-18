import GameData, items

class entity(meta_sprite):

    def __init__(self, name, basestat, **kwargs):
        self.basestat = basestat
        for key in ordered(kwargs.keys()):
            self.basestat[key] = kwargs[key]
        self.determination = 100
        self.equipped = []
	
    def equip(self, item):
        if item.is_equipabble:
            self.equipped.append(item)

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
	
    def use_item(self, item, game):
        for buff in self.buffs:
           self.basestat[buff.stat] += buff.value * potency
        item.effect(game)
        if item.type == "consumable":
            del item 
                        
    def fight(self, enemy, game):
            self.imagename = imagename+"_battle"
            self.update_sprites()
            
    def attack(self, enemy, game):
            enemy.fight(self, game)
            self.fight(enemy, game)
            

class Game(object):

    def __init__(self, name):
        self.data = GameData("data")
        self.sprites = pygame.sprite.LayeredUpdates()
        self.window = pygame.display.setmode([680, 480])
        pygame.display.caption(name)
    
    def set_background(self, name):
        self.window.blit(self.data.backgrounds.get_data(name))
    
    def init_meta_sprite(self, meta_sprite):
        meta_sprite.rect = meta_sprite.image.get_rect()
        meta_sprite.rect.x = meta_sprite.pos.x
        meta_sprite.rect.y = meta_sprite.pos.y

        del meta_sprite.pos

        meta_sprite.sounds = self.data.sounds.get_data_array(meta_sprite.sounds)
        
        self.sprites.add(meta_sprite, layer = meta_sprite.layer)
        return meta_sprite
            
    def set_sprite(self, sprite, name):
        sprite.image = self.data.sprites.get_data(name)
            
    def update(self):
        self.sprites.update(self.data)
        self.sprites.draw()
        pygame.display.update()
			
class player(entity):

    def __init__(self, name):
        player.name = name

    def is_player(self):
        return True;
			
