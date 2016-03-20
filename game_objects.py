from collections import namedtuple
import time

class move(game_object):

    def __init__(self, name, buffs, temp_buffs, turns, **kwargs):
        game_object.__init__(name, **kwargs)
        self.buffs = buffs
        self.temp_buffs = temp_buffs
        self.turns = turns
        
buff = namedtuple('buff', ['stat', 'buff'])

def alchol_effect(self, player):
    pygame.transform.rotate(player.game.window, 360);

def hope_effect(self, game): 
    game.window.get_rect().move(0, 5)
    time.sleep(0.25)
    game.window.get_rect().move(0, -5)

def mysterious_effect(self, player):
    fun = os.path.join("data", "fun") 
    temmie = get_image(os.path.join(fun, "temmie.png"))
    temmie_sound = pygame.mixer.Sound(os.path.join(fun, "temmie.ogg"))
    for sprite in game.sprites.sprites:
        sprite.image = temmie
    self.window.blit(temmie)
    pygame.transform.rotate(player.window, 360*4000)
