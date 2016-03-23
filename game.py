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
        meta_sprite.__init__(self, name, True)
        self.__basestat = basestat
        for key in ordered(kwargs.keys()):
            self.basestat[key] = kwargs[key]
        self.__basestat['determination'] = 100
        self.__equipped = {} 
        self.__inventory = {}
        self.__moves = {}

    def get_basestats(self):
        return self.__basestat

    def add_move(self, move):
        self.__moves[move["name"]] = move

    def get_moves(self):
        return self.__move

    def unequip(itemname):
        self.inventory[itemname] = self.__equppped[itemname]
        for buff in self.inventory[itemname]:
            self.basestat[buff] -= self.__inventory[itemname]["buffs"][buff] * self.inventory[itemname]["potency"]
        self.__equipped.pop(itemname)

    def equip(itemname):
        self.__equipped[itemname] = self.__inventory[itemname]
        self.__inventory.pop(itemname)
        
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
            self.equip(itemname)
        if  self.inventory[itemname]["consumable"]:
            self.remove_from_inventory(self.__inventory[itemname])

    def use_move(self, movename, game):
        for buff in self.moves[movename]["buffs"]:
            self.basestat += self.moves[movename]["buffs"][buffs]
        self.temp_buffs.append(self.moves[movename]["temporary_buffs"])

    def load_battle_assets(self, game):
            self._imagename = imagename+"_battle"
            self.load_sprite(game.data)
            self.fighting = True

class player(entity):

    def __init__(self, name):
        player.name = name

    def is_player(self):
        return True;
			
class battle_entity(Thread):
   
    def __init__(self, entity):
        self.__entity = entity
        self.__func_queue = queue.Queue()

    def use_item(self, itemname):
        self.__entity.use_item(itemname)

    def use_move(self, movename):
        self.__entity.use_move(movename)

    def get_basestats(self):
        return self.__basestat

class battle:
    def __init__(self, entity, entity1, game):
            entity.load_battle_assets(entity1, game)
            game.set_background("battle")   
            entity1.load_battle_assets(entity, game)
            entity_queuefuncs = []
            entity1_queuefuncs = []
            if entity.get_basestats()["speed"] < entity1.get_basestats()["speed"]:
                self.entity_turn = False
            else:
                self.entity_turn = True

    def entity_do(self, entityNo, do_func):
            self.entity_queuefuncs.append(do_func)
