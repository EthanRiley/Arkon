from collections import namedtuple
import json, time

class effector:

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

           
class alchol(potion):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [ 
            buff("speed", -5),
            buff("attack", 5)
        ]

    def effect(self, player):
        pygame.transform.rotate(player.game.window, 360);

class health(potion):

    def __init__(self, quantity, name, potency):
        item_meta.__init__(self, quantity, name, potency)
        self.buffs = [
            buff("health", 10)
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
            buff("hope", 5), 
            buff("enlightenment", 2)
        ]

    def effect(self, game): 
        game.window.get_rect().move(0, 5)
        time.sleep(0.25)
        game.window.get_rect().move(0, -5)

class mysterious(potion):

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


