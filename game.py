import game_data, game_objects 
import threading

def concat_dicts(*dicts, **kwargs):
    output = {}
    for dic in dicts:
        if len(dic) > 0:
            keys = output.keys() | dic.keys()
            output = {k: output.get(k, kwargs["default"]) + dic.get(k, kwargs["default"]) for k in keys }
    return output

def deconcat_dicts(*dicts): 
    output = {}
    for dic in dicts:
        if len(dic) > 0:
            keys = output.keys() | dic.keys()
            output = {k: output.get(k, kwargs["default"]) - dic.get(k, kwargs["default"]) for k in keys }
    return output

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
        self.__temp_buffs = {}
        self.__stats = {}
        self.__stats_needs_update = True 

    def get_buffs_from_dict(self, dictbuff):
        buffs = []
        for item in dictbuff:
            buffs.append(item["buffs"])
        return concat_dicts(*buffs, default = 0)
      
    def get_basestats(self):
        return self.__basestat
   
    def __update_stats(self):
        self.__stats = concat_dicts(self.__basestat, 
                self.get_buffs_from_dict(self.__temp_buffs), 
                    self.get_buffs_from_dict(self.__equipped), default = 0) 

    def get_stats(self):
        if self.__stats_needs_update:
            self.__update_stats()
            self.__stats_needs_update = False
        return self.__stats
    
    def add_move(self, move):
        self.__moves[move["name"]] = move

    def get_moves(self):
        return self.__moves

    def unequip(itemname):
        self.__stats_needs_update =  True
        self.inventory[itemname] = self.__equipped[itemname]
        self.__equipped.pop(itemname)

    def equip(itemname):
        self.__stats_needs_update =  True
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
        self.__stats_needs_update =  True
        for buff in self.__inventory[itemname]["buffs"]:
           self.basestat[buff] +=  self.__inventory[itemname]["buffs"][buff] * self.inventory[itemname]["potency"]
        if self.__inventory[itemname][effect] != None:
            self.__inventory[itemname][effect](game)
        if self.__inventory[itemname]["equipabble"]:
            self.equip(itemname)
        if  self.inventory[itemname]["consumable"]:
            self.remove_from_inventory(self.__inventory[itemname])

    def use_move(self, movename, game):
        self.__stats_needs_update =  True
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
			
class battle_entity:
   
    def __init__(self, entity, game):
        entity.load_battle_assets(game)
        self.__entity = entity
        self.__func_queue = collections.Deque()

    def use_item(self, itemname):
        self.__func_queue.append({"func" : self.__entity.use_item,"args" : itemname})

    def use_move(self, movename):
        self.__func_queue.append({"func" : self.__entity.use_move, "args" : movename})

    def do_queued(self):
            function = self.queue.pop()
            function["func"]("args")
            self.turns += 1

    def ready(self):
        if len(self.__func_queue) > 0:
            return True
        return False

    def get_stats(self):
        return self.__entity.get_stats()

class battle(threading.Thread):
    def __init__(self, entity, entity1, game):
            threading.Thread.__init__(self)
            self.entity = battle_entity(entity, game)
            self.entity1 = battle_entity(entity1, game)
            game.set_background("battle")   
            self.start()

    def run(self): 
        if self.__entity_turn & self.entity.ready():
            self.entity.do_queued()
        if not self.__entity_turn & self.entity1.ready():
            self.entity1.do_queued()

