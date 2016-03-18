from collections import namedtuple
import json, time

class game_object:

    def __init__(self, name, **kwargs):
        self.name = name
        self.buffs = []
        if 'discription' in sorted(kwargs.keys()):
            self.discription = kwargs['discription']

class item(game_object):

    def __init__(self, quantity, name, **kwargs):
        game_object.__init__(self, name, kwargs)
        self.quantity = quantity
        self.is_consumable = False
        
buff = namedtuple('buff', ['stat', 'buff'])

class equipabble(item):
    
    def __init__(self, name, buffs, **kwargs):
        item.__init__(self, 1, name, **kwargs)
        self.buffs = buffs
        item.is_equipabble = True
                
class consumable(item):

    def __init__(self, quantity, name, potency):
        item.__init__(self, quantity, name)
        item.is_consumable = True
        self.potency = potency

class alchol(consumable):

    def __init__(self, quantity, name, potency):
        consumable.__init__(self, quantity, name, potency)
        self.buffs = [ 
            buff("speed", -5),
            buff("determination", 5),
            buff("enlightenment", -5)
        ]

    def effect(self, player):
        pygame.transform.rotate(player.game.window, 360);
 
class health(consumable):

    def __init__(self, quantity, name, potency):
        consumable.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("determination", 10)
        ]

class speed(consumable):

    def __init__(self, quantity, name, potency):
        consumable.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("speed", 5)
        ]

class hope(consumable):

    def __init__(self, quantity, name, potency):
        consumable.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("hope", 5), 
            buff("enlightenment", 2)
        ]

    def effect(self, game): 
        game.window.get_rect().move(0, 5)
        time.sleep(0.25)
        game.window.get_rect().move(0, -5)

class mysterious(consumable):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("enligtenment", 100)
        ]

    def effect(self, player):
        fun = os.path.join("data", "fun") 
        temmie = get_image(os.path.join(fun, "temmie.png"))
        temmie_sound = pygame.mixer.Sound(os.path.join(fun, "temmie.ogg"))
        for sprite in game.sprites.sprites:
            sprite.image = temmie
        self.window.blit(temmie)
        pygame.transform.rotate(player.window, 360*4000)
