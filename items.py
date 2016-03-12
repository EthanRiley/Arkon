from collections import namedtuple
import json, time

class item_meta:

    def __init__(self, quantity, name):
        self.quantity = quantity
        self.name = name

    def use(self, entity):
        pass

buff = namedtuple('buff', ['stat', 'buff'])

class potion(item_meta):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, name)
        self.type = "potion"
        self.potion = self.__class__.__name__
        self.potency = potency

    def use(self, entity):
        for buff in self.buffs:
            if buff.stat != "health":
                entity.basestat[buff.stat] += buff.value * potency
            else:
                entitiy.recover(buff.value * potency)
        if entity.is_player():
            self.potion_effect(entity)
        
class alchol(potion):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [ 
            buff("speed", -5),
            buff("attack", 5)
        ]

    def potion_effect(self, player):
        pygame.transform.rotate(player.game.window, 360);

class health(potion):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("health", 5)
        ]

class speed(potion):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("speed", 5)
        ]

class hope(potion):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("hope", 5)
        ]

    def potion_effect(self, player): 
        player.game.window.get_rect().move(0, 5)
        time.sleep(0.25)
        player.game.window.get_rect().move(0, -5)

class mysterious(potion):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("speed", 4000),
            buff("attack", 4000)
        ]

    def potion_effect(self, player):
        fun = os.path.join("data", "fun") 
        temmie = get_image(os.path.join(fun, "temmie.png"))
        temmie_sound = pygame.mixer.Sound(os.path.join(fun, "temmie.ogg"))
        for sprite in player.game.data.sprites.spites:
            sprite = temmie
        for background in player.game.data.backgrounds:
            background = temmie
        pygame.transform.rotate(player.window, 360*4000)


