from collections import namedtuple
import json, time

class item:

    def __init__(self, quantity, name, **kwargs):
        self.quantity = quantity
        self.name = name
        self.is_consumable = False
        if 'discription' in sorted(kwargs.keys()):
            self.discription = kwargs['discription']

buff = namedtuple('buff', ['stat', 'buff'])

class uniques(item):
    
    def __init__(self, name, buffs, **kwargs):
        item.__init__(self, 1, name, **kwargs)
        
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
            buff("zen", 5)
        ]

    def effect(self, player):
        pygame.transform.rotate(player.game.window, 360);
 
class health(consumable):

    def __init__(self, quantity, name, potency):
        consumable.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("health", 10)
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
        for sprite in game.data.sprites.sprites:
            sprite = temmie
        for background in game.data.backgrounds:
            background = temmie
        pygame.transform.rotate(player.window, 360*4000)


