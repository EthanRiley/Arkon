import game_data, game_objects 

class Game(object):

    def __init__(self, name):
        self.data = GameData("data")
        self.sprites = pygame.sprite.LayeredUpdates()
        self.window = pygame.display.setmode([680, 480])
        self.background_music = pygame.mixer.channel(0)
        pygame.display.caption(name)
    
    def set_background(self, name):
        self.window.blit(self.data.backgrounds.get_data(name))
        self.background_music.play(self.data.sounds.get_data(name))
    
    def load_sprite(self, meta_sprite):
        meta_sprite.load_data(self.data)
        self.sprites.add(meta_sprite, layer = meta_sprite.layer)
        return meta_sprite
            
    def update(self):
        self.sprites.update(self.data)
        self.sprites.draw()
        pygame.display.update()

class entity(meta_sprite):

    def __init__(self, name, basestat, **kwargs):
        self.__basestat = basestat
        for key in ordered(kwargs.keys()):
            self.basestat[key] = kwargs[key]
        self.__determination = 100
        self.__equipped = {} 
        self.__inventory = {}
        self.__moves = {}

    def add_move(self, move):
        self.__moves[move["name"]] = move

    def add_to_inventory(self, item):
        self.__inventory[item["name"]] += item["quantity"]

    def remove_from_inventory(self, item):
        self.__inventory[item["name"]] -= item["quantity"]
        if self.__inventory[item["name"]] <= 0:
            self.__inventory.pop(item["name"])

    def get_inventory(self):
        return self.__inventory
   
    def trade(self, item, item1):
        self.remove_from_inventory(item)
        self.add_to_inventory(item1)
	
    def use_item(self, itemname, game):
        for buff in self.__inventory[itemname]["buffs"]:
           self.basestat[buff] +=  self.__inventory[itemname]["buffs"][buff] * self.inventory[itemname]["potency"]
        if self.__inventory[itemname][effect] != None:
            self.__inventory[itemname][effect](game)
        if self.__inventory[itemname]["equipabble"]:
            self.__equipped[itemname] = self.__inventory[itemname]
        if self.__inventory[itemname]["equipabble"] | self.inventory[itemname]["consumable"]:
            self.remove_from_inventory(self.__inventory[itemname])

    def use_move(self, movename, game):
        for buff in self.moves[movename]["buffs"]:
            self.basestat += self.__inventory[itemname]["buffs"][buffs]
        self.temp_buffs.append(self.moves[movename]["temporary_buffs"])

    def unequip(itemname):
        self.__equipped.pop(itemname)

    def battle(self, enemy, game):
            self._imagename = imagename+"_battle"
            self.load_sprite(game.data)
            self.fighting = True
		
class player(entity):

    def __init__(self, name):
        player.name = name

    def is_player(self):
        return True;
			
class battle:
    def __init__(self, entity, entity1, game):
            entity.fight(entity1, game)
            game.set_background("battle")


